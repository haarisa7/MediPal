import streamlit as st
import datetime
from data.medication_tracker.patient_medications import get_all_patient_medication_entries, update_patient_medication
from data.medication_tracker.medications import get_drug_display_name
from data.medication_tracker.adherence_stats import get_adherence_for_patient_med_id
from data.medication_tracker.medication_requests import create_medication_request
from components.medication_tracker.medication_card import render_medication_card
from utils.medication_helpers import render_page_header, render_back_button, build_medication_dict, is_clinician


def _cleanup_edit_session():
    """Clean up edit medication session state."""
    st.session_state['show_edit_med'] = False
    st.session_state['edit_selected_med'] = None


def _render_medication_selection(meds):
    """Render medication cards for selection."""
    st.markdown("### 📋 Select a medication to edit")
    for med in meds:
        medication = build_medication_dict(med)
        active = med.get('status', 'active') == 'active'
        adherence_rate = get_adherence_for_patient_med_id(med['id'])
        render_medication_card(medication, med['id'], status=None, context='edit', adherence_rate=adherence_rate, active=active)
        if st.button('✅ Select this medication', key=f"select_med_{med['id']}", use_container_width=True):
            st.session_state['edit_selected_med'] = med['id']
            st.rerun()


def _render_edit_form(selected_med):
    """Render the edit form for selected medication."""
    st.markdown(f"### 💊 Editing {get_drug_display_name(selected_med['drug_id'])}")
    st.markdown("---")
    
    # Show current medication card
    adherence_rate = get_adherence_for_patient_med_id(selected_med['id'])
    medication = build_medication_dict(selected_med)
    active = selected_med.get('status', 'active') == 'active'
    render_medication_card(medication, selected_med['id'], status=None, context='edit', adherence_rate=adherence_rate, active=active)
    
    # Edit form
    st.markdown("### 📋 Update Details")
    col1, col2 = st.columns(2)
    with col1:
        dose = st.text_input('💊 Dosage', value=selected_med.get('dose', ''), key='edit_med_dose')
    with col2:
        doctor = st.text_input('👨‍⚕️ Prescribing Doctor', value=selected_med.get('prescribed_by', ''), key='edit_med_doctor')
    
    instructions = st.text_area('📝 Instructions', value=selected_med.get('instructions', ''), key='edit_med_instructions', height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('📅 Start Date', value=selected_med.get('start_date', datetime.date.today()), key='edit_med_start')
    with col2:
        end_date = st.date_input('📅 End Date', value=selected_med.get('end_date', datetime.date.today()), key='edit_med_end')
    
    TIME_OPTIONS = ['Morning', 'Afternoon', 'Evening']
    timing_val = selected_med.get('timing', 'Morning')
    timing_val = timing_val if timing_val in TIME_OPTIONS else 'Morning'
    timing = st.selectbox('⏰ Timing', TIME_OPTIONS, index=TIME_OPTIONS.index(timing_val), key='edit_med_timing')
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.button('✅ Save Changes', type='primary', key='edit_med_save', use_container_width=True):
            _save_changes(selected_med, dose, instructions, start_date, end_date, doctor, timing)
    with col2:
        if st.button('❌ Cancel', key='cancel_edit_med_form', use_container_width=True):
            _cleanup_edit_session()
            st.rerun()


def _save_changes(selected_med, dose, instructions, start_date, end_date, doctor, timing):
    """Save medication changes (direct or via request)."""
    if is_clinician():
        # Clinician: send edit request for approval
        patient_id = st.session_state.get('authorized_patient_id')
        clinician_id = st.session_state.get('current_id')
        drug_id = selected_med['drug_id']
        ok = create_medication_request(
            patient_id, clinician_id, drug_id, dose, instructions, 
            start_date, end_date, timing, request_type='edit', patient_med_id=selected_med['id']
        )
        if ok:
            st.success('✅ Edit request sent to patient for approval!')
            st.balloons()
            _cleanup_edit_session()
            st.rerun()
        else:
            st.error('❌ Failed to send edit request.')
    else:
        # Patient: update directly
        success = update_patient_medication(selected_med['id'], dose, instructions, start_date, end_date, doctor, timing)
        if success:
            st.success('✅ Medication updated successfully!')
            st.balloons()
            _cleanup_edit_session()
            st.rerun()
        else:
            # Error is stored in session state, will be shown on rerun
            st.rerun()


def show_edit_medication_overlay(patient_id, on_select=None):
    # Show DB error if present
    if st.session_state.get('db_update_error'):
        st.error("❌ Failed to save edit. Please try again.")
        st.session_state['db_update_error'] = None
    
    # Header and back button
    render_page_header(
        'Edit Medication',
        'Select a medication to update',
        '✏️',
        'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
    )
    render_back_button('Back to Medications', 'show_edit_med', _cleanup_edit_session)
    st.markdown("---")
    
    # Get medications
    meds = get_all_patient_medication_entries(patient_id)
    if not meds:
        st.info('📊 No medications found. Add a medication first to edit it.')
        return
    
    # Check if medication is selected
    selected_id = st.session_state.get('edit_selected_med')
    selected_med = next((med for med in meds if selected_id == med['id']), None)
    
    if selected_med:
        _render_edit_form(selected_med)
    else:
        _render_medication_selection(meds)

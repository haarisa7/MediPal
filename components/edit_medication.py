import streamlit as st
from data.patient_medications import get_all_patient_medication_entries
from data.medications import get_drug_display_name
from components.medication_card import render_medication_card

def show_edit_medication_overlay(patient_id, on_select=None):
    st.markdown('## Edit Medication')
    meds = get_all_patient_medication_entries(patient_id)
    if not meds:
        st.info('No medications found.')
        if st.button('Cancel', key='cancel_edit_med_overlay'):
            st.session_state['show_edit_med'] = False
            st.experimental_rerun()
        return

    selected_id = st.session_state.get('edit_selected_med')
    selected_med = None
    for med in meds:
        if selected_id == med['id']:
            selected_med = med

    if selected_med:
        # Show edit form pre-filled with selected_med
        st.markdown(f"### Editing {get_drug_display_name(selected_med['drug_id'])}")
        from data.adherence_stats import get_overall_adherence_for_med_id
        adherence_rate = get_overall_adherence_for_med_id(selected_med['drug_id'])
        medication = {
            'drug_name': get_drug_display_name(selected_med['drug_id']),
            'dose': selected_med.get('dose', ''),
            'instructions': selected_med.get('instructions', ''),
            'prescribed_by': selected_med.get('prescribed_by', ''),
            'timing': selected_med.get('timing', ''),
        }
        active = selected_med.get('status', 'active') == 'active'
        render_medication_card(medication, selected_med['id'], status=None, context='edit', adherence_rate=adherence_rate, active=active)
        import datetime
        dose = st.text_input('Dosage', value=selected_med.get('dose', ''), key='edit_med_dose')
        instructions = st.text_area('Instructions', value=selected_med.get('instructions', ''), key='edit_med_instructions')
        start_date = st.date_input('Start date', value=selected_med.get('start_date', datetime.date.today()), key='edit_med_start')
        end_date = st.date_input('End date', value=selected_med.get('end_date', datetime.date.today()), key='edit_med_end')
        doctor = st.text_input('Prescribing Doctor', value=selected_med.get('prescribed_by', ''), key='edit_med_doctor')
        TIME_OPTIONS = ['Morning', 'Afternoon', 'Evening']
        timing_val = selected_med.get('timing', 'Morning')
        if timing_val not in TIME_OPTIONS:
            timing_val = 'Morning'
        timing = st.selectbox('Timing', TIME_OPTIONS, index=TIME_OPTIONS.index(timing_val), key='edit_med_timing')
        if st.button('Save Changes', key='edit_med_save'):
            from data.patient_profile import get_user_role
            from data.medication_requests import create_medication_request
            from data.patient_medications import update_patient_medication
            role = get_user_role(st.session_state.get('current_id'))
            if role == 1:
                # Clinician: send edit request for approval
                patient_id = st.session_state.get('authorized_patient_id')
                clinician_id = st.session_state.get('current_id')
                drug_id = selected_med['drug_id']
                from data.medication_requests import create_medication_request
                ok = create_medication_request(
                    patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type='edit', patient_med_id=selected_med['id']
                )
                if ok:
                    st.success('Edit request sent to patient for approval.')
                else:
                    st.error('Failed to send edit request.')
            else:
                # Patient: update directly
                update_patient_medication(selected_med['id'], dose, instructions, start_date, end_date, doctor, timing)
                st.success('Medication updated.')
            st.session_state['show_edit_med'] = False
            st.session_state['edit_selected_med'] = None
            st.experimental_rerun()
        if st.button('Cancel', key='cancel_edit_med_overlay'):
            st.session_state['show_edit_med'] = False
            st.session_state['edit_selected_med'] = None
            st.experimental_rerun()
        return

    for med in meds:
        drug_name = get_drug_display_name(med['drug_id'])
        medication = {
            'drug_name': drug_name,
            'dose': med.get('dose', ''),
            'instructions': med.get('instructions', ''),
            'prescribed_by': med.get('prescribed_by', ''),
            'timing': med.get('timing', ''),
        }
        active = med.get('status', 'active') == 'active'
        from data.adherence_stats import get_overall_adherence_for_med_id
        adherence_rate = get_overall_adherence_for_med_id(med['drug_id'])
        render_medication_card(medication, med['id'], status=None, context='edit', adherence_rate=adherence_rate, active=active)
        if st.button('Select', key=f"select_med_{med['id']}"):
            if on_select:
                on_select(med)
            st.session_state['edit_selected_med'] = med['id']
            st.experimental_rerun()

    # Cancel button at the bottom
    if st.button('Cancel', key='cancel_edit_med_overlay'):
        st.session_state['show_edit_med'] = False
        st.session_state['edit_selected_med'] = None
        st.experimental_rerun()

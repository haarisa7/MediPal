import streamlit as st
from datetime import date
from data.medications import get_drugs_by_search
from data.patient_medications import insert_patient_medication
from data.medication_requests import create_medication_request
from components.search_component import render_search_interface, clear_search_selection
from utils.medication_helpers import render_page_header, render_back_button, render_info_box, is_clinician


def _initialize_session_defaults():
    """Initialize session state with default values."""
    st.session_state.setdefault('add_med_times_list', ['Morning'])
    st.session_state.setdefault('add_med_dosage', '')
    st.session_state.setdefault('add_med_instructions', '')
    st.session_state.setdefault('add_med_start', date.today())
    st.session_state.setdefault('add_med_end', date.today())
    st.session_state.setdefault('add_med_doctor', '')


def _search_medications(search_term):
    """Wrapper to format medication search results."""
    results = get_drugs_by_search(search_term, limit=10)
    return [{'display_name': drug['display_name'], 'value': drug['drug_id']} for drug in results]


def _render_time_selector(times_list):
    """Render time selector with add/remove buttons."""
    TIME_OPTIONS = ['Morning', 'Afternoon', 'Evening']
    for i, t in enumerate(times_list):
        cols = st.columns([8, 1, 1])
        with cols[0]:
            new_time = st.selectbox(
                f'Time {i+1}', TIME_OPTIONS, 
                index=TIME_OPTIONS.index(t) if t in TIME_OPTIONS else 0,
                key=f'add_med_time_{i}', label_visibility='collapsed'
            )
            times_list[i] = new_time
        with cols[1]:
            if st.button('➕', key=f'add_time_{i}', help='Add another time', use_container_width=True):
                times_list.insert(i+1, 'Morning')
                st.session_state['add_med_times_list'] = times_list
                st.rerun()
        with cols[2]:
            if len(times_list) > 1:
                if st.button('➖', key=f'remove_time_{i}', help='Remove this time', use_container_width=True):
                    times_list.pop(i)
                    st.session_state['add_med_times_list'] = times_list
                    st.rerun()
    st.session_state['add_med_times_list'] = times_list


def _save_medication(resolve_user_id, selected_drug_id):
    """Handle saving medication (direct or via request)."""
    if not selected_drug_id:
        st.error('❌ Please select a medication from the search results.')
        return
    
    dose = st.session_state.get('add_med_dosage', '')
    if not dose:
        st.error('❌ Please enter a dosage.')
        return
    
    instructions = st.session_state.get('add_med_instructions', '')
    start_date = st.session_state.get('add_med_start')
    end_date = st.session_state.get('add_med_end')
    times_list = st.session_state.get('add_med_times_list', ['Morning'])
    
    if is_clinician():
        # Clinician: send medication request for each time
        patient_id = st.session_state.get('authorized_patient_id')
        clinician_id = st.session_state.get('current_id')
        for time_label in times_list:
            create_medication_request(
                patient_id, clinician_id, selected_drug_id, dose, instructions, 
                start_date, end_date, time_label, request_type='add', patient_med_id=None
            )
        st.success('✅ Medication request sent to patient for approval!')
    else:
        # Patient: add directly
        user_id = resolve_user_id()
        doctor_name = st.session_state.get('add_med_doctor', '')
        for time_label in times_list:
            insert_patient_medication(
                user_id, selected_drug_id, dose, instructions, 
                start_date, end_date, doctor_name, time_label
            )
        st.success('✅ Medication(s) added successfully!')
    
    st.balloons()
    st.session_state['show_add_med'] = False
    clear_search_selection('add_med_search')
    st.rerun()


def show_add_medication_overlay(resolve_user_id):
    if not st.session_state.get('show_add_med'):
        return
    
    # Header and back button
    render_page_header(
        'Add New Medication', 
        'Add a medication to your treatment plan',
        '💊',
        'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)'
    )
    render_back_button('Back to Medications', 'show_add_med', 
                      lambda: clear_search_selection('add_med_search'))
    st.markdown("---")
    
    _initialize_session_defaults()
    
    # Medication search
    st.markdown('### 🔍 Search for Medication')
    selected_drug_id, _ = render_search_interface(
        search_function=_search_medications,
        placeholder_text="e.g., Aspirin, Ibuprofen, Metformin...",
        label="",
        help_text="Type at least 2 characters to search for medications",
        min_chars=2,
        session_key="add_med_search",
        num_columns=1,
        show_count=True
    )
    st.markdown("---")
    
    # Medication details
    st.markdown('### 📋 Medication Details')
    col1, col2 = st.columns(2)
    with col1:
        st.text_input('💊 Dosage', value=st.session_state['add_med_dosage'], 
                     key='add_med_dosage', placeholder='e.g., 500mg, 1 tablet')
    with col2:
        st.text_input('👨‍⚕️ Prescribing Doctor', value=st.session_state['add_med_doctor'], 
                     key='add_med_doctor', placeholder='Doctor name (optional)')
    
    st.text_area('📝 Instructions', value=st.session_state['add_med_instructions'], 
                key='add_med_instructions', 
                placeholder='Special instructions (e.g., take with food, avoid alcohol...)', height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        st.date_input('📅 Start Date', value=st.session_state['add_med_start'], key='add_med_start')
    with col2:
        st.date_input('📅 End Date', value=st.session_state['add_med_end'], key='add_med_end')
    
    st.markdown("---")
    
    # Times section
    st.markdown('### ⏰ When to Take')
    st.caption('Add the times you need to take this medication each day')
    times_list = st.session_state.get('add_med_times_list', ['Morning'])
    _render_time_selector(times_list)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button('✅ Add Medication', type='primary', key='add_med_confirm', use_container_width=True):
            _save_medication(resolve_user_id, selected_drug_id)
    with col2:
        if st.button('❌ Cancel', key='add_med_cancel', use_container_width=True):
            st.session_state['show_add_med'] = False
            clear_search_selection('add_med_search')
            st.rerun()
    
    # Helpful tips
    st.markdown("---")
    render_info_box('Helpful Tips', [
        'Make sure to enter the correct dosage as prescribed',
        'You can add multiple times per day using the ➕ button',
        'Set reminders in the notification settings to never miss a dose',
        'Keep your medication list up to date for better tracking'
    ])

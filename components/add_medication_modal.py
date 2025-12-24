import streamlit as st
from datetime import date
from data.medications import get_drugs_by_search, get_drug_id_by_name
from data.patient_medications import insert_patient_medication
from data.patient_profile import get_user_role
from data.medication_requests import create_medication_request

def show_add_medication_overlay(resolve_user_id):
    if st.button('➕ Add'):
        st.session_state['show_add_med'] = True

    if not st.session_state.get('show_add_med'):
        return  # Only show the add medication UI if flag is set

    # --- Add Medication Page ---
    st.markdown('## Add Medication')
    if st.button('← Back', key='add_med_back'):
        st.session_state['show_add_med'] = False
        st.rerun()

    # initialize modal session fields
    st.session_state.setdefault('add_med_name', '')
    st.session_state.setdefault('add_med_selected_id', None)
    st.session_state.setdefault('add_med_times_list', ['09:00'])
    st.session_state.setdefault('add_med_dosage', '')
    st.session_state.setdefault('add_med_instructions', '')
    st.session_state.setdefault('add_med_start', date.today())
    st.session_state.setdefault('add_med_end', date.today())
    st.session_state.setdefault('add_med_doctor', '')

    # --- Fix: update add_med_name before widget instantiation ---
    if st.session_state.get('add_med_name_update', False):
        st.session_state['add_med_name'] = st.session_state['add_med_name_update_val']
        st.session_state['add_med_selected_id'] = st.session_state.get('add_med_selected_id_update', None)
        st.session_state['add_med_name_update'] = False
        st.session_state['add_med_name_update_val'] = ''
        st.session_state['add_med_selected_id_update'] = None
        st.rerun()

    # search input
    name_input = st.text_input('Search medication', value=st.session_state['add_med_name'], key='add_med_name')
    suggestions = []
    if name_input and len(name_input.strip()) >= 2:
        suggestions = get_drugs_by_search(name_input.strip(), limit=10)
    if suggestions:
        st.markdown('**Select a medication**')
        for s in suggestions:
            if st.button(s['display_name'], key=f"drug_{s['drug_id']}"):
                st.session_state['add_med_name_update'] = True
                st.session_state['add_med_name_update_val'] = s['display_name']
                st.session_state['add_med_selected_id_update'] = s['drug_id']
                st.rerun()

    # times list with dropdown for Morning, Afternoon, Evening
    st.markdown('**Times to take**')
    TIME_OPTIONS = ['Morning', 'Afternoon', 'Evening']
    times_list = st.session_state.get('add_med_times_list', ['Morning'])
    for i, t in enumerate(times_list):
        cols = st.columns([6,1,1])
        new_time = cols[0].selectbox(f'Time {i+1}', TIME_OPTIONS, index=TIME_OPTIONS.index(t) if t in TIME_OPTIONS else 0, key=f'add_med_time_{i}')
        times_list[i] = new_time
        if cols[1].button('➕', key=f'add_time_{i}'):
            times_list.insert(i+1, 'Morning')
            st.session_state['add_med_times_list'] = times_list
            st.rerun()
        if len(times_list) > 1:
            if cols[2].button('➖', key=f'remove_time_{i}'):
                times_list.pop(i)
                st.session_state['add_med_times_list'] = times_list
                st.rerun()
    st.session_state['add_med_times_list'] = times_list

    st.text_input('Dosage', value=st.session_state['add_med_dosage'], key='add_med_dosage')
    st.text_area('Instructions', value=st.session_state['add_med_instructions'], key='add_med_instructions')
    st.date_input('Start date', value=st.session_state['add_med_start'], key='add_med_start')
    st.date_input('End date', value=st.session_state['add_med_end'], key='add_med_end')
    st.text_input('Prescribing Doctor', value=st.session_state['add_med_doctor'], key='add_med_doctor')

    if st.button('Add Medication', key='add_med_confirm'):
        user_id = resolve_user_id()
        drug_name = st.session_state.get('add_med_name')
        drug_id = get_drug_id_by_name(drug_name)
        dose = st.session_state.get('add_med_dosage', '')
        instructions = st.session_state.get('add_med_instructions', '')
        start_date = st.session_state.get('add_med_start')
        end_date = st.session_state.get('add_med_end')
        doctor_name = st.session_state.get('add_med_doctor', '')
        times_list = st.session_state.get('add_med_times_list', ['Morning'])
        # Check role
        role = get_user_role(st.session_state.get('current_id'))
        if role == 1:
            # Clinician: send medication request for each time
            patient_id = st.session_state.get('authorized_patient_id')
            clinician_id = st.session_state.get('current_id')
            for time_label in times_list:
                ok = create_medication_request(
                    patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, time_label, request_type='add', patient_med_id=None
                )
            st.success('Medication request sent to patient for approval.')
        else:
            # Patient: add directly
            for time_label in times_list:
                insert_patient_medication(
                    user_id, drug_id, dose, instructions, start_date, end_date, doctor_name, time_label
                )
            st.success('Medication(s) added')
        st.session_state['show_add_med'] = False
        st.rerun()
    if st.button('Cancel', key='add_med_cancel'):
        st.session_state['show_add_med'] = False
        st.rerun()
        st.text_area('Instructions', value=st.session_state['add_med_instructions'], key='add_med_instructions')
        st.date_input('Start date', value=st.session_state['add_med_start'], key='add_med_start')
        st.date_input('End date', value=st.session_state['add_med_end'], key='add_med_end')
        st.text_input('Prescribing Doctor', value=st.session_state['add_med_doctor'], key='add_med_doctor')

        if st.button('Add Medication', key='add_med_confirm'):
            user_id = resolve_user_id()
            drug_name = st.session_state.get('add_med_name')
            drug_id = get_drug_id_by_name(drug_name)
            dose = st.session_state.get('add_med_dosage', '')
            instructions = st.session_state.get('add_med_instructions', '')
            start_date = st.session_state.get('add_med_start')
            end_date = st.session_state.get('add_med_end')
            doctor_name = st.session_state.get('add_med_doctor', '')
            times_list = st.session_state.get('add_med_times_list', ['Morning'])
            for time_label in times_list:
                insert_patient_medication(
                    user_id, drug_id, dose, instructions, start_date, end_date, doctor_name, time_label
                )
            st.success('Medication(s) added')
            st.session_state['show_add_med'] = False
            st.rerun()
        if st.button('Cancel', key='add_med_cancel'):
            st.session_state['show_add_med'] = False
            st.rerun()

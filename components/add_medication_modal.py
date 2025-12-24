import streamlit as st
from datetime import date
from data.medications import get_drugs_by_search, get_drug_id_by_name
from data.patient_medications import insert_patient_medication
from data.patient_profile import get_user_role
from data.medication_requests import create_medication_request
from components.search_component import render_search_interface, clear_search_selection

def show_add_medication_overlay(resolve_user_id):
    if not st.session_state.get('show_add_med'):
        return  # Only show the add medication UI if flag is set

    # --- Add Medication Page ---
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px;'>
        <div style='font-size: 28px; font-weight: 700; margin-bottom: 8px;'>💊 Add New Medication</div>
        <div style='font-size: 16px; opacity: 0.9;'>Add a medication to your treatment plan</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button('← Back to Medications', key='add_med_back', use_container_width=False):
        st.session_state['show_add_med'] = False
        clear_search_selection('add_med_search')
        st.rerun()
    
    st.markdown("---")

    # initialize modal session fields
    st.session_state.setdefault('add_med_times_list', ['09:00'])
    st.session_state.setdefault('add_med_dosage', '')
    st.session_state.setdefault('add_med_instructions', '')
    st.session_state.setdefault('add_med_start', date.today())
    st.session_state.setdefault('add_med_end', date.today())
    st.session_state.setdefault('add_med_doctor', '')

    # Medication search using the reusable search component
    st.markdown('### 🔍 Search for Medication')
    
    # Wrapper function that returns medication data in the format the search component expects
    def search_medications(search_term):
        results = get_drugs_by_search(search_term, limit=10)
        # Convert to format: [{display_name, value}]
        return [{
            'display_name': drug['display_name'],
            'value': drug['drug_id']  # Store drug_id as the value
        } for drug in results]
    
    selected_drug_id, search_query = render_search_interface(
        search_function=search_medications,
        placeholder_text="e.g., Aspirin, Ibuprofen, Metformin...",
        label="",
        help_text="Type at least 2 characters to search for medications",
        min_chars=2,
        session_key="add_med_search",
        num_columns=1,
        show_count=True
    )

    st.markdown("---")
    
    # Medication details section
    st.markdown('### 📋 Medication Details')
    
    # Dosage and instructions in columns
    col1, col2 = st.columns(2)
    with col1:
        st.text_input('💊 Dosage', value=st.session_state['add_med_dosage'], key='add_med_dosage', placeholder='e.g., 500mg, 1 tablet')
    with col2:
        st.text_input('👨‍⚕️ Prescribing Doctor', value=st.session_state['add_med_doctor'], key='add_med_doctor', placeholder='Doctor name (optional)')
    
    st.text_area('📝 Instructions', value=st.session_state['add_med_instructions'], key='add_med_instructions', 
                 placeholder='Special instructions (e.g., take with food, avoid alcohol...)', height=100)
    
    # Date inputs in columns
    col1, col2 = st.columns(2)
    with col1:
        st.date_input('📅 Start Date', value=st.session_state['add_med_start'], key='add_med_start')
    with col2:
        st.date_input('📅 End Date', value=st.session_state['add_med_end'], key='add_med_end')
    
    st.markdown("---")

    # Times section
    st.markdown('### ⏰ When to Take')
    st.caption('Add the times you need to take this medication each day')
    
    TIME_OPTIONS = ['Morning', 'Afternoon', 'Evening']
    times_list = st.session_state.get('add_med_times_list', ['Morning'])
    for i, t in enumerate(times_list):
        cols = st.columns([8, 1, 1])
        with cols[0]:
            new_time = st.selectbox(
                f'Time {i+1}', 
                TIME_OPTIONS, 
                index=TIME_OPTIONS.index(t) if t in TIME_OPTIONS else 0, 
                key=f'add_med_time_{i}',
                label_visibility='collapsed'
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
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button('✅ Add Medication', type='primary', key='add_med_confirm', use_container_width=True):
            user_id = resolve_user_id()
            drug_id = selected_drug_id
            
            if not drug_id:
                st.error('❌ Please select a medication from the search results.')
                return
            
            dose = st.session_state.get('add_med_dosage', '')
            if not dose:
                st.error('❌ Please enter a dosage.')
                return
            
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
                st.success('✅ Medication request sent to patient for approval!')
                st.balloons()
            else:
                # Patient: add directly
                for time_label in times_list:
                    insert_patient_medication(
                        user_id, drug_id, dose, instructions, start_date, end_date, doctor_name, time_label
                    )
                st.success('✅ Medication(s) added successfully!')
                st.balloons()
            
            st.session_state['show_add_med'] = False
            clear_search_selection('add_med_search')
            st.rerun()
    
    with col2:
        if st.button('❌ Cancel', key='add_med_cancel', use_container_width=True):
            st.session_state['show_add_med'] = False
            clear_search_selection('add_med_search')
            st.rerun()
    
    with col3:
        st.markdown("<div style='padding: 8px;'></div>", unsafe_allow_html=True)
    
    # Helpful reminder
    st.markdown("---")
    st.markdown("""
    <div style='background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px;'>
        <div style='font-weight: 700; color: #1e40af; margin-bottom: 8px;'>💡 Helpful Tips</div>
        <div style='color: #1e40af; font-size: 14px;'>
            • Make sure to enter the correct dosage as prescribed<br>
            • You can add multiple times per day using the ➕ button<br>
            • Set reminders in the notification settings to never miss a dose<br>
            • Keep your medication list up to date for better tracking
        </div>
    </div>
    """, unsafe_allow_html=True)

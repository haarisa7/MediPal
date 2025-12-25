import streamlit as st
from datetime import datetime, date, time


def _initialize_session_defaults():
    """Initialize session state with default values for form."""
    st.session_state.setdefault('add_event_type', 'Procedure')
    st.session_state.setdefault('add_event_name', '')
    st.session_state.setdefault('add_event_description', '')
    st.session_state.setdefault('add_event_date', date.today())
    st.session_state.setdefault('add_event_time', time(9, 0))
    st.session_state.setdefault('add_event_location', '')
    st.session_state.setdefault('add_event_doctor', '')
    st.session_state.setdefault('add_event_status', 'Routine')
    st.session_state.setdefault('add_event_notes', '')
    st.session_state.setdefault('add_event_successful', False)


def _clear_form_state():
    """Clear all form session state."""
    keys_to_clear = [
        'add_event_type', 'add_event_name', 'add_event_description',
        'add_event_date', 'add_event_time', 'add_event_location',
        'add_event_doctor', 'add_event_status', 'add_event_notes', 'add_event_successful'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def show_add_medical_event_overlay(user_id):
    """Show overlay for adding a new medical event."""
    
    if not st.session_state.get('show_add_event_form'):
        return
    
    # Show DB error if present
    if st.session_state.get('db_insert_error'):
        st.error(f"Database Error: {st.session_state['db_insert_error']}")
        st.session_state['db_insert_error'] = None
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 10px; 
                color: white; 
                text-align: center;
                margin-bottom: 1rem;'>
        <h2 style='margin: 0; color: white;'>➞ Add New Medical Event</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Fill out the form below to add a new event to your medical history</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Medical History", use_container_width=True):
        st.session_state['show_add_event_form'] = False
        _clear_form_state()
        st.rerun()
    
    st.markdown("---")
    
    # Initialize defaults
    _initialize_session_defaults()
    
    st.write("")
    st.markdown("### 📋 Event Information")
    
    # Event type selection
    event_type = st.selectbox(
        "Event Type *",
        ["Procedure", "Hospital Stay", "Appointment", "Test/Lab", "Surgery", "Other"],
        index=["Procedure", "Hospital Stay", "Appointment", "Test/Lab", "Surgery", "Other"].index(st.session_state['add_event_type']) if st.session_state['add_event_type'] in ["Procedure", "Hospital Stay", "Appointment", "Test/Lab", "Surgery", "Other"] else 0,
        key='add_event_type',
        help="Select the type of medical event"
    )
    
    # Event name
    event_name = st.text_input(
        "Event Name *",
        value=st.session_state['add_event_name'],
        key='add_event_name',
        placeholder="e.g., Annual Physical Exam",
        help="Brief name for this event"
    )
    
    # Description
    event_description = st.text_area(
        "Description",
        value=st.session_state['add_event_description'],
        key='add_event_description',
        placeholder="Brief description of the event...",
        help="Optional description"
    )
    
    st.markdown("---")
    st.markdown("### 📅 Date & Time")
    
    # Date and time
    col1, col2 = st.columns(2)
    with col1:
        event_date = st.date_input(
            "Event Date *",
            value=st.session_state['add_event_date'],
            key='add_event_date',
            help="Date the event occurred"
        )
    with col2:
        event_time = st.time_input(
            "Event Time",
            value=st.session_state['add_event_time'],
            key='add_event_time',
            help="Time the event occurred"
        )
    
    st.markdown("---")
    st.markdown("### 🏥 Location & Provider")
    
    # Location and doctor
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input(
            "Location/Facility",
            value=st.session_state['add_event_location'],
            key='add_event_location',
            placeholder="e.g., General Hospital",
            help="Where the event took place (optional)"
        )
    with col2:
        doctor = st.text_input(
            "Doctor/Provider",
            value=st.session_state['add_event_doctor'],
            key='add_event_doctor',
            placeholder="e.g., Dr. Smith",
            help="Healthcare provider involved (optional)"
        )
    
    st.markdown("---")
    st.markdown("### 📝 Additional Details")
    
    # Status
    status = st.selectbox(
        "Status",
        ["Routine", "Urgent", "Follow-Up", "Completed"],
        index=["Routine", "Urgent", "Follow-Up", "Completed"].index(st.session_state['add_event_status']),
        key='add_event_status',
        help="Current status of this event"
    )
    
    # Additional notes
    notes = st.text_area(
        "Additional Notes",
        value=st.session_state['add_event_notes'],
        key='add_event_notes',
        placeholder="Any additional information, instructions, or observations...",
        help="Optional notes"
    )
    
    # Successful checkbox
    successful = st.checkbox(
        "Mark as Successful",
        value=st.session_state['add_event_successful'],
        key='add_event_successful',
        help="Check this if the event was successful or had a positive outcome"
    )
    
    st.markdown("---")
    st.write("")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("✅ Save Event", type="primary", key='add_event_save', use_container_width=True):
            if not event_name:
                st.error("❌ Please enter an event name.")
            else:
                # Combine date and time
                event_datetime = datetime.combine(event_date, event_time)
                
                # Save to database
                from data.medical_events import insert_medical_event
                success = insert_medical_event(
                    user_id=user_id,
                    event_type=event_type,
                    event_name=event_name,
                    event_description=event_description or None,
                    event_date=event_datetime,
                    location=location or None,
                    doctor_name=doctor or None,
                    status=status,
                    notes=notes or None,
                    successful=successful
                )
                
                if success:
                    st.success(f"✅ Medical event '{event_name}' added successfully!")
                    st.balloons()
                    st.session_state['show_add_event_form'] = False
                    _clear_form_state()
                    st.rerun()
                else:
                    # Error is already stored in session state by insert function
                    st.rerun()
    
    with col2:
        if st.button("❌ Cancel", key='add_event_cancel', use_container_width=True):
            st.session_state['show_add_event_form'] = False
            _clear_form_state()
            st.rerun()

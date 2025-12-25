import streamlit as st
import datetime
from data.medical_events import get_medical_events, update_medical_event
from components.medical_event_card import render_medical_event_card


def _cleanup_edit_session():
    """Clean up edit medical event session state."""
    st.session_state['show_edit_event'] = False
    st.session_state['edit_selected_event'] = None


def _initialize_session_defaults(event):
    """Initialize session state with event values."""
    if 'edit_event_type' not in st.session_state:
        st.session_state['edit_event_type'] = event.get('event_type', 'Appointment')
    if 'edit_event_name' not in st.session_state:
        st.session_state['edit_event_name'] = event.get('event_name', '')
    if 'edit_event_description' not in st.session_state:
        st.session_state['edit_event_description'] = event.get('event_description', '')
    if 'edit_event_date' not in st.session_state:
        event_date = event.get('event_date')
        if isinstance(event_date, datetime.datetime):
            st.session_state['edit_event_date'] = event_date.date()
        else:
            st.session_state['edit_event_date'] = datetime.date.today()
    if 'edit_event_time' not in st.session_state:
        event_date = event.get('event_date')
        if isinstance(event_date, datetime.datetime):
            st.session_state['edit_event_time'] = event_date.time()
        else:
            st.session_state['edit_event_time'] = datetime.time(9, 0)
    if 'edit_event_location' not in st.session_state:
        st.session_state['edit_event_location'] = event.get('location', '')
    if 'edit_event_doctor' not in st.session_state:
        st.session_state['edit_event_doctor'] = event.get('doctor_name', '')
    if 'edit_event_status' not in st.session_state:
        st.session_state['edit_event_status'] = event.get('status', 'Routine')
    if 'edit_event_notes' not in st.session_state:
        st.session_state['edit_event_notes'] = event.get('notes', '')
    if 'edit_event_successful' not in st.session_state:
        st.session_state['edit_event_successful'] = event.get('success', True)


def _clear_form_state():
    """Clear form-related session state."""
    keys_to_clear = [
        'edit_event_type', 'edit_event_name', 'edit_event_description',
        'edit_event_date', 'edit_event_time', 'edit_event_location',
        'edit_event_doctor', 'edit_event_status', 'edit_event_notes',
        'edit_event_successful'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def _render_event_selection(events, user_id):
    """Render event cards for selection."""
    st.markdown("### 📋 Select a medical event to edit")
    for event in events:
        render_medical_event_card(event, user_id, key_prefix="edit_select_")
        if st.button('✅ Select this event', key=f"select_event_{event['event_id']}", use_container_width=True):
            st.session_state['edit_selected_event'] = event['event_id']
            st.rerun()


def _render_edit_form(selected_event, user_id):
    """Render the edit form for selected event."""
    _initialize_session_defaults(selected_event)
    
    st.markdown(f"### 📝 Editing {selected_event.get('event_name', 'Medical Event')}")
    st.markdown("---")
    
    # Show current event card
    render_medical_event_card(selected_event, user_id, key_prefix="edit_current_")
    
    # Edit form
    st.markdown("### 📋 Update Details")
    
    event_types = ["Procedure", "Hospital Stay", "Appointment", "Test/Lab", "Surgery"]
    event_type = st.selectbox(
        "Event Type",
        event_types,
        index=event_types.index(st.session_state['edit_event_type']) if st.session_state['edit_event_type'] in event_types else 0,
        key='edit_event_type_input'
    )
    st.session_state['edit_event_type'] = event_type
    
    event_name = st.text_input(
        "Event Name",
        value=st.session_state['edit_event_name'],
        key='edit_event_name_input'
    )
    st.session_state['edit_event_name'] = event_name
    
    event_description = st.text_area(
        "Description (Optional)",
        value=st.session_state['edit_event_description'],
        key='edit_event_description_input',
        height=100
    )
    st.session_state['edit_event_description'] = event_description
    
    col1, col2 = st.columns(2)
    with col1:
        event_date = st.date_input(
            "Event Date",
            value=st.session_state['edit_event_date'],
            key='edit_event_date_input'
        )
        st.session_state['edit_event_date'] = event_date
    with col2:
        event_time = st.time_input(
            "Event Time",
            value=st.session_state['edit_event_time'],
            key='edit_event_time_input'
        )
        st.session_state['edit_event_time'] = event_time
    
    location = st.text_input(
        "Location",
        value=st.session_state['edit_event_location'],
        key='edit_event_location_input'
    )
    st.session_state['edit_event_location'] = location
    
    doctor_name = st.text_input(
        "Healthcare Provider",
        value=st.session_state['edit_event_doctor'],
        key='edit_event_doctor_input'
    )
    st.session_state['edit_event_doctor'] = doctor_name
    
    status_options = ["Routine", "Urgent", "Follow-Up", "Completed"]
    status = st.selectbox(
        "Status",
        status_options,
        index=status_options.index(st.session_state['edit_event_status']) if st.session_state['edit_event_status'] in status_options else 0,
        key='edit_event_status_input'
    )
    st.session_state['edit_event_status'] = status
    
    notes = st.text_area(
        "Notes (Optional)",
        value=st.session_state['edit_event_notes'],
        key='edit_event_notes_input',
        height=100
    )
    st.session_state['edit_event_notes'] = notes
    
    successful = st.checkbox(
        "Mark as successful/positive outcome",
        value=st.session_state['edit_event_successful'],
        key='edit_event_successful_input'
    )
    st.session_state['edit_event_successful'] = successful
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.button('✅ Save Changes', type='primary', key='edit_event_save', use_container_width=True):
            _save_changes(selected_event, user_id)
    with col2:
        if st.button('❌ Cancel', key='cancel_edit_event_form', use_container_width=True):
            _clear_form_state()
            _cleanup_edit_session()
            st.rerun()


def _save_changes(selected_event, user_id):
    """Save event changes to database."""
    # Combine date and time
    event_datetime = datetime.datetime.combine(
        st.session_state['edit_event_date'],
        st.session_state['edit_event_time']
    )
    
    success = update_medical_event(
        selected_event['event_id'],
        user_id,
        st.session_state['edit_event_type'],
        st.session_state['edit_event_name'],
        st.session_state['edit_event_description'],
        event_datetime,
        st.session_state['edit_event_location'],
        st.session_state['edit_event_doctor'],
        st.session_state['edit_event_status'],
        st.session_state['edit_event_notes'],
        st.session_state['edit_event_successful']
    )
    
    if success:
        st.success('✅ Medical event updated successfully!')
        st.balloons()
        _clear_form_state()
        _cleanup_edit_session()
        st.rerun()
    else:
        # Error is stored in session state
        st.rerun()


def show_edit_medical_event_overlay(user_id):
    """Show the edit medical event overlay."""
    # Show DB error if present
    if st.session_state.get('db_update_error'):
        st.error("❌ Failed to update event. Please try again.")
        st.session_state['db_update_error'] = None
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 40px; border-radius: 16px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; font-size: 36px;'>✏️ Edit Medical Event</h1>
        <p style='color: rgba(255, 255, 255, 0.9); margin: 8px 0 0 0; font-size: 18px;'>Select an event to update</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Medical History", key="back_from_edit_event"):
        _clear_form_state()
        _cleanup_edit_session()
        st.rerun()
    
    st.markdown("---")
    
    # Get events
    events = get_medical_events(user_id)
    if not events:
        st.info('📊 No medical events found. Add an event first to edit it.')
        return
    
    # Check if event is selected
    selected_id = st.session_state.get('edit_selected_event')
    selected_event = next((evt for evt in events if selected_id == evt['event_id']), None)
    
    if selected_event:
        _render_edit_form(selected_event, user_id)
    else:
        _render_event_selection(events, user_id)

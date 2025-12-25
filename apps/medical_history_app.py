import streamlit as st
from hydralit import HydraHeadApp
from datetime import datetime, timedelta


class MedicalHistoryApp(HydraHeadApp):
    """Medical History Log page for tracking medical events, procedures, and history."""

    def __init__(self, title: str = "Medical History Log", **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        # Check authentication
        if not st.session_state.get('logged_in', False):
            st.warning("Please log in to access your medical history.")
            return

        user_id = st.session_state.get('current_id')
        if not user_id:
            st.warning("Session expired. Please log in again.")
            return
        
        # Show DB errors if present
        if st.session_state.get('db_insert_error'):
            st.error(f"Database Error: {st.session_state['db_insert_error']}")
            st.session_state['db_insert_error'] = None
        
        if st.session_state.get('db_delete_error'):
            st.error(f"Database Error: {st.session_state['db_delete_error']}")
            st.session_state['db_delete_error'] = None
        
        if st.session_state.get('db_update_error'):
            st.error(f"Database Error: {st.session_state['db_update_error']}")
            st.session_state['db_update_error'] = None

        # Handle add event overlay
        from components.add_medical_event_modal import show_add_medical_event_overlay
        if st.session_state.get('show_add_event_form'):
            show_add_medical_event_overlay(user_id)
            return
        
        # Handle edit event overlay
        from components.edit_medical_event import show_edit_medical_event_overlay
        if st.session_state.get('show_edit_event'):
            show_edit_medical_event_overlay(user_id)
            return
        
        # Page header
        st.markdown("## 📋 Medical History Log")
        
        # Import components
        from components.medical_history_header import render_medical_history_header
        from components.medical_timeline import render_medical_timeline
        
        # Render header with summary stats
        render_medical_history_header(user_id)
        
        # View toggle: Timeline or Calendar
        st.write("")
        view_tab1, view_tab2 = st.tabs(["📅 Timeline View", "📆 Calendar View"])
        
        with view_tab1:
            render_medical_timeline(user_id)
        
        with view_tab2:
            from components.medical_calendar import render_medical_calendar
            render_medical_calendar(user_id)

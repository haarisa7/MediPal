import streamlit as st
from hydralit import HydraHeadApp
from datetime import datetime, timedelta


class MedicalHistoryApp(HydraHeadApp):
    """Medical History Log page for tracking medical events, procedures, and history."""

    def __init__(self, title: str = "Medical History Log", **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def _resolve_patient_id(self):
        """Resolve patient ID based on user role."""
        from data.shared.patient_profile import get_user_role
        user_id = st.session_state.get('current_id')
        role = get_user_role(user_id) if user_id else None
        if role == 1:
            # Clinician: use authorized patient's ID
            return st.session_state.get('authorized_patient_id')
        else:
            # Patient: use their own user_id
            return user_id

    def run(self):
        # Check authentication
        if not st.session_state.get('logged_in', False):
            st.warning("Please log in to access your medical history.")
            return

        patient_id = self._resolve_patient_id()
        if not patient_id:
            st.warning("No patient selected. Clinicians must authorize a patient in Home tab.")
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
        from components.medical_history.add_medical_event_modal import show_add_medical_event_overlay
        if st.session_state.get('show_add_event_form'):
            show_add_medical_event_overlay(patient_id)
            return
        
        # Handle edit event overlay
        from components.medical_history.edit_medical_event import show_edit_medical_event_overlay
        if st.session_state.get('show_edit_event'):
            show_edit_medical_event_overlay(patient_id)
            return
        
        # Page header
        st.markdown("## 📋 Medical History Log")
        
        # Import components
        from components.medical_history.medical_history_header import render_medical_history_header
        from components.medical_history.medical_timeline import render_medical_timeline
        
        # Render header with summary stats
        render_medical_history_header(patient_id)
        
        # View toggle: Timeline or Calendar
        st.write("")
        view_tab1, view_tab2 = st.tabs(["📅 Timeline View", "📆 Calendar View"])
        
        with view_tab1:
            render_medical_timeline(patient_id)
        
        with view_tab2:
            from components.medical_history.medical_calendar import render_medical_calendar
            render_medical_calendar(patient_id)

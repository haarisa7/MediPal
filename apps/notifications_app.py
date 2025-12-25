import streamlit as st
from hydralit import HydraHeadApp
from data.medication_requests import get_pending_requests_for_patient, respond_to_medication_request, process_accepted_request, get_all_requests_for_clinician
from data.patient_profile import get_user_role
from components.notification_card import render_notification_card

class NotificationsApp(HydraHeadApp):
    def __init__(self, title: str = 'Notifications', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def _resolve_user_id(self):
        user_id = st.session_state.get('current_id')
        if user_id is None:
            return None
        try:
            return int(user_id)
        except Exception:
            return None

    def run(self):
        # Load global styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass
        
        st.title('🔔 Notifications')
        user_id = self._resolve_user_id()
        if not user_id:
            st.warning('No user logged in.')
            return
        role = get_user_role(user_id)
        
        # Get unread notes BEFORE marking as received (for patient view)
        unread_notes = {}
        if role != 1:  # Patient only
            from data.side_effect_requests import get_all_notes_for_patient_reports
            all_notes = get_all_notes_for_patient_reports(user_id)
            # Filter to only unread notes
            for report_id, notes in all_notes.items():
                unread = [n for n in notes if not n.get('received', False)]
                if unread:
                    unread_notes[report_id] = unread
            
            # Now mark all notes as received
            from data.side_effect_requests import mark_all_notes_as_received
            mark_all_notes_as_received(user_id)
        
        if role == 1:
            # Clinician: show all their requests grouped by status
            st.header('Your Medication Requests')
            requests = get_all_requests_for_clinician(user_id)
            if not requests:
                st.info('No medication requests found.')
                return
            pending = [r for r in requests if not r['responded']]
            accepted = [r for r in requests if r['responded'] and r['approved']]
            rejected = [r for r in requests if r['responded'] and not r['approved']]
            st.subheader('Pending')
            for req in pending:
                render_notification_card(req, 'pending')
            st.subheader('Accepted')
            for req in accepted:
                render_notification_card(req, 'accepted')
            st.subheader('Rejected')
            for req in rejected:
                render_notification_card(req, 'rejected')
            return
        
        # Patient view: show medication requests and side effect notes
        st.header('💊 Medication Requests')
        requests = get_pending_requests_for_patient(user_id)
        if requests:
            for req in requests:
                def accept_callback(req_id=req['request_id']):
                    st.warning('Processing acceptance...')
                    ok = process_accepted_request(req_id)
                    st.warning("ran it")

                    respond_to_medication_request(req_id, True)
                    st.rerun()
                def reject_callback(req_id=req['request_id']):
                    respond_to_medication_request(req_id, False)
                    st.warning('Request rejected.')
                    st.rerun()
                render_notification_card(req, 'pending', accept_callback, reject_callback)
        else:
            st.info('No medication requests pending.')
        
        st.markdown('---')
        st.header('⚕️ Doctor Notes on Side Effects')
        
        if unread_notes:
            from data.patient_side_effect import get_patient_side_effect_report_by_id
            for report_id, notes in unread_notes.items():
                report = get_patient_side_effect_report_by_id(report_id)
                if report:
                    medication_name = (report.get('display_name', 'Unknown Medication') or 'Unknown Medication').title()
                    effect_name = report.get('side_effect_name', 'Side effect')
                    
                    for note in notes:
                        doctor_first = note.get('doctor_first_name', '')
                        doctor_last = note.get('doctor_last_name', '')
                        doctor_name = f"Dr. {doctor_first} {doctor_last}".strip()
                        sent_at = note.get('sent_at', '')
                        
                        st.markdown(f"""
                        <div style='border: 1px solid #e5e7eb; border-left: 4px solid #7c3aed; border-radius: 8px; padding: 12px; margin-bottom: 12px; background: #ffffff;'>
                            <div style='font-weight: 600; font-size: 14px; color: #1f2937; margin-bottom: 4px;'>{medication_name} - {effect_name}</div>
                            <div style='color: #4b5563; font-size: 12px; margin-bottom: 8px;'>{note['doctor_note']}</div>
                            <div style='color: #6b7280; font-size: 11px;'>— {doctor_name} • {sent_at}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info('No doctor notes on side effects.')

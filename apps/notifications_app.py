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
        st.title('🔔 Notifications')
        user_id = self._resolve_user_id()
        if not user_id:
            st.warning('No user logged in.')
            return
        role = get_user_role(user_id)
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
        requests = get_pending_requests_for_patient(user_id)
        if not requests:
            st.info('No medication requests pending.')
            return
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

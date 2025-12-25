import streamlit as st
from hydralit import HydraApp
import apps

st.set_page_config(page_title='MediPal',page_icon="🐙",layout='wide',initial_sidebar_state='auto')

if __name__ == "__main__":

    over_theme = {'txc_inactive': 'black', 'menu_background': '#e8f5e9', 'txc_active': '#10b981'}
    app = HydraApp(
        title='MediPal',
        favicon="🐙",
        hide_streamlit_markers=True,
        use_navbar=True,
        navbar_sticky=True,
        navbar_animation=True,
        navbar_theme=over_theme
    )

    app.add_app("Home", icon="🏠", app=apps.HomeApp(title='Home'),is_home=True)
    app.add_app("Medication Tracker",icon="📈", app=apps.MedicationTracker(title="Medication Tracker"))
    app.add_app("Side Effects", icon="⚠️", app=apps.SideEffects(title="Side Effects"))
    app.add_app("Medical History Log", icon="📋", app=apps.MedicalHistoryApp(title="Medical History Log"))
    app.add_app("Emergency Dashboard", icon="🚨", app=apps.EmergencyDashboard(title="Emergency Dashboard"))
    app.add_app("Login", icon="🔐", app=apps.LoginApp(title="Login"))
    app.add_app("Create Account", icon="📝", app=apps.SignUpApp(title="Create Account"))
    app.add_app("Account", icon="🧑‍💼", app=apps.AccountApp(title="Account"))

    # Notification badge logic
    notification_count = 0
    logged_in = st.session_state.get('logged_in', False)
    if logged_in:
        from data.patient_profile import get_user_role
        user_id = st.session_state.get('current_id')
        role = get_user_role(user_id) if user_id else None
        
        if role == 0:  # Patient
            from data.medication_requests import get_pending_requests_for_patient
            med_request_count = len(get_pending_requests_for_patient(user_id))
            
            # Check for unread doctor notes
            from data.side_effect_requests import get_unread_doctor_notes_for_patient
            unread_notes_count = get_unread_doctor_notes_for_patient(user_id)
            
            # Total notification count includes both medication requests and unread notes
            notification_count = med_request_count + unread_notes_count
            
            last_seen = st.session_state.get('last_seen_notification_count', 0)
            if notification_count > last_seen:
                if med_request_count > 0:
                    st.toast(f"You have {med_request_count} new medication request(s)!", icon="🔔")
                if unread_notes_count > 0:
                    st.toast(f"You have {unread_notes_count} new doctor note(s) on your side effect reports!", icon="💬")
            st.session_state['last_seen_notification_count'] = notification_count
        
        elif role == 1:  # Clinician
            # Check for new side effect reports from authorized patient
            patient_id = st.session_state.get('authorized_patient_id')
            if patient_id:
                from data.patient_side_effect import get_side_effect_reports_count
                side_effect_count = get_side_effect_reports_count(patient_id)
                last_seen_se = st.session_state.get('last_seen_side_effect_count', 0)
                if side_effect_count > last_seen_se:
                    new_count = side_effect_count - last_seen_se
                    st.toast(f"Patient has {new_count} new side effect report(s)!", icon="⚠️")
                st.session_state['last_seen_side_effect_count'] = side_effect_count
    
    # Add Notifications tab with badge
    notifications_key = "Notifications"
    notifications_label = f"Notifications{' [' + str(notification_count) + ']' if notification_count > 0 else ''}"
    app.add_app(notifications_key, icon="🔔", app=apps.NotificationsApp(title=notifications_label))

    if logged_in:
        complex_nav = {
            'Home': ['Home'],
            'Medication Tracker': ['Medication Tracker'],
            'Side Effects': ['Side Effects'],
            'Medical History Log': ['Medical History Log'],
            'Emergency Dashboard': ['Emergency Dashboard'],
            notifications_key: ['Notifications'],
            'Account': ['Account'],
        }
    else:
        # Show only Home, Login, and Create Account when not logged in
        complex_nav = {
            'Home': ['Home'],
            'Login': ['Login'],
            'Create Account': ['Create Account'],
        }

    # and finally just the entire app and all the children.
    try:
        app.run(complex_nav)
    except KeyError as e:
        missing = str(e)
        # Try to list registered app keys for debugging
        registered = None
        try:
            registered = list(getattr(app, '_navbar_pointers', {}).keys())
        except Exception:
            try:
                registered = [a[0] for a in getattr(app, '_apps', [])]
            except Exception:
                registered = None

        st.error(f"Navigation configuration error: missing menu key {missing}.")
        if registered is not None:
            st.write("Registered app keys:")
            st.write(registered)
        st.stop()
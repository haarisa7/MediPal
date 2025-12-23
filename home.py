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
        if role == 0:
            from data.medication_requests import get_pending_requests_for_patient
            notification_count = len(get_pending_requests_for_patient(user_id))
            last_seen = st.session_state.get('last_seen_notification_count', 0)
            if notification_count > last_seen:
                st.toast(f"You have {notification_count} new medication request(s)!", icon="🔔")
            st.session_state['last_seen_notification_count'] = notification_count
    # Add Notifications tab with badge
    notifications_key = "Notifications"
    notifications_label = f"Notifications{' [' + str(notification_count) + ']' if notification_count > 0 else ''}"
    app.add_app(notifications_key, icon="🔔", app=apps.NotificationsApp(title=notifications_label))

    if logged_in:
        complex_nav = {
            'Home': ['Home'],
            'Medication Tracker': ['Medication Tracker'],
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
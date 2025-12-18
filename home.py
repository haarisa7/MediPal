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

    app.enable_guest_access()

    user_access_level, username = app.check_access()

    if user_access_level > 1:
        complex_nav = {
            'Home': ['Home'],
            'Medication Tracker': ['Medication Tracker'],
        }
    elif user_access_level == 1:
        complex_nav = {
            'Home': ['Home'],
            'Medication Tracker': ['Medication Tracker'],

        }
    else:
        complex_nav = {
            'Home': ['Home'],
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
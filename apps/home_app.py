import streamlit as st
from hydralit import HydraHeadApp


class HomeApp(HydraHeadApp):
    """Very small home page for MediPal.

    Provides a `run()` method so it can be used directly or inside a Hydralit
    app as the home screen.
    """

    def __init__(self, title: str = "Home", **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        st.title(self.title)
        logged_in = st.session_state.get('logged_in', False)

        if not logged_in:
            st.write("Welcome to MediPal — a simple medication tracking and health dashboard.")
            st.write("Please log in or create an account to access your medication tracker.")
            st.divider()

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔐 Login"):
                    try:
                        self.do_redirect("Login")
                    except Exception:
                        try:
                            self.do_redirect()
                        except Exception:
                            st.experimental_rerun()
            with col2:
                if st.button("📝 Create Account"):
                    try:
                        self.do_redirect("Create Account")
                    except Exception:
                        try:
                            self.do_redirect()
                        except Exception:
                            st.experimental_rerun()

        else:
            st.write("Welcome back — use the menu to open your Medication Tracker.")
            st.divider()

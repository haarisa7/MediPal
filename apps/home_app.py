import streamlit as st


class HomeApp:
    """Very small home page for MediPal.

    Provides a `run()` method so it can be used directly or inside a Hydralit
    app as the home screen.
    """

    def __init__(self, title: str = "Home"):
        self.title = title

    def run(self):
        st.title(self.title)
        st.write("Welcome to MediPal — a simple medication tracking and health dashboard.")
        st.write("Use the menu to navigate to Medication Tracker, Side Effects, Emergency Dashboard, or Medical History.")
        st.divider()
        st.write("If you don't have an account yet, create one from the 'Create Account' menu.")

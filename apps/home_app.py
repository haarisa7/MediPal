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
        user_id = st.session_state.get('current_id')
        if not logged_in or not user_id:
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
                            st.rerun()
            with col2:
                if st.button("📝 Create Account"):
                    try:
                        self.do_redirect("Create Account")
                    except Exception:
                        try:
                            self.do_redirect()
                        except Exception:
                            st.rerun()
            return

        # Import here to avoid circular import
        from data.patient_profile import get_user_role
        from apps.medication_tracker import MedicationTracker

        role = get_user_role(user_id)
        if role == 1:
            # Clinician view: search for patient, then show tracker for selected patient
            st.subheader("Clinician Dashboard: Search for Patient")
            search_id = st.text_input("Enter Patient User ID")
            search_dob = st.text_input("Enter Patient Date of Birth (YYYY-MM-DD)")
            if st.button("Authorize Patient Access"):
                if search_id and search_dob:
                    from data.patient_profile import get_patient_profile_db
                    patient = get_patient_profile_db(search_id)
                    if patient and str(patient.get('date_of_birth')) == search_dob:
                        st.session_state['authorized_patient_id'] = int(search_id)
                        st.success(f"Authorized patient: {patient.get('first_name', '')} {patient.get('last_name', '')}")
                    else:
                        st.error("No patient found with that ID and DOB.")
                else:
                    st.warning("Please enter both Patient User ID and Date of Birth.")
            st.info("After authorization, use the Medication Tracker tab to view/manage patient medications.")
        else:
            # Patient view: show simple welcome message only
            st.write(f"Welcome back! Use the navigation bar to access your Medication Tracker and Account.")
            st.divider()

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
            st.markdown("## 👨‍⚕️ Clinician Dashboard")
            st.markdown("---")
            
            # Check if there's already an authorized patient
            authorized_patient_id = st.session_state.get('authorized_patient_id')
            
            if authorized_patient_id:
                # Show currently authorized patient info in a container
                from data.patient_profile import get_patient_profile
                current_patient = get_patient_profile(authorized_patient_id)
                
                if current_patient:
                    # Active patient card with prominent styling
                    with st.container():
                        st.markdown("""
                        <div style='padding: 1rem; background-color: #d4edda; border-left: 5px solid #28a745; border-radius: 5px; margin-bottom: 1rem;'>
                            <h3 style='color: #155724; margin: 0 0 0.5rem 0;'>✅ Active Patient</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        with col1:
                            st.metric("Patient Name", f"{current_patient.get('first_name', '')} {current_patient.get('last_name', '')}")
                        with col2:
                            st.metric("User ID", authorized_patient_id)
                        with col3:
                            st.metric("Date of Birth", str(current_patient.get('date_of_birth', 'N/A')))
                        with col4:
                            st.write("")  # Spacer
                            st.write("")  # Spacer
                            if st.button("🔄 Change", use_container_width=True, key="change_patient"):
                                del st.session_state['authorized_patient_id']
                                st.rerun()
                    
                    st.info("💡 **Quick Access:** Use the tabs above to view **Medication Tracker**, **Side Effects**, **Emergency Dashboard**, or **Notifications** for this patient.")
                    st.markdown("---")
                else:
                    # Patient data not found, clear the authorization
                    del st.session_state['authorized_patient_id']
                    st.rerun()
            
            # Show search form with better styling
            with st.container():
                if authorized_patient_id:
                    st.markdown("### 🔍 Authorize Different Patient")
                    st.caption("Search for another patient by entering their credentials below.")
                else:
                    st.markdown("### 🔍 Patient Authorization")
                    st.caption("Enter patient credentials to access their medical information.")
                
                st.write("")  # Spacer
                
                col1, col2 = st.columns(2)
                with col1:
                    search_id = st.text_input(
                        "Patient User ID", 
                        key="patient_search_id",
                        placeholder="e.g., 12345",
                        help="Enter the numeric user ID of the patient"
                    )
                with col2:
                    search_dob = st.text_input(
                        "Date of Birth", 
                        key="patient_search_dob",
                        placeholder="YYYY-MM-DD",
                        help="Enter date in format: YYYY-MM-DD"
                    )
                
                st.write("")  # Spacer
                
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("🔐 Authorize Access", type="primary", use_container_width=True):
                        if search_id and search_dob:
                            from data.patient_profile import get_patient_profile
                            try:
                                patient = get_patient_profile(int(search_id))
                                if patient and str(patient.get('date_of_birth')) == search_dob:
                                    st.session_state['authorized_patient_id'] = int(search_id)
                                    st.rerun()
                                else:
                                    st.error("❌ No patient found with that ID and DOB combination.")
                            except ValueError:
                                st.error("❌ Invalid Patient ID format. Please enter a numeric ID.")
                        else:
                            st.warning("⚠️ Please enter both Patient User ID and Date of Birth.")
        else:
            # Patient view: show simple welcome message only
            st.write(f"Welcome back! Use the navigation bar to access your Medication Tracker and Account.")
            st.divider()

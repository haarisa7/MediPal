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
        logged_in = st.session_state.get('logged_in', False)
        user_id = st.session_state.get('current_id')
        
        # Load global styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass
        
        if not logged_in or not user_id:
            self._render_landing_page()
            return

        # Import here to avoid circular import
        from data.shared.patient_profile import get_user_role

        role = get_user_role(user_id)
        if role == 1:
            self._render_clinician_dashboard()
        else:
            self._render_patient_dashboard()
    
    def _render_landing_page(self):
        """Render the landing page for non-logged-in users."""
        
        # Hero Section
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 40px; border-radius: 20px; margin-bottom: 40px; text-align: center;'>
            <h1 style='font-size: 3.5em; margin-bottom: 10px; font-weight: 800;'>💊 MediPal</h1>
            <p style='font-size: 1.5em; margin-bottom: 10px; opacity: 0.95;'>Your Personal Healthcare Companion</p>
            <p style='font-size: 1.1em; opacity: 0.85; max-width: 700px; margin: 0 auto;'>
                Track medications, monitor side effects, manage medical history, and stay connected with your healthcare team — all in one place.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Action Buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.write("")
        with col2:
            col_login, col_signup = st.columns(2)
            with col_login:
                if st.button("🔐 Login", use_container_width=True, type="primary"):
                    try:
                        self.do_redirect("Login")
                    except Exception:
                        st.rerun()
            with col_signup:
                if st.button("📝 Sign Up", use_container_width=True):
                    try:
                        self.do_redirect("Create Account")
                    except Exception:
                        st.rerun()
        with col3:
            st.write("")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Key Features Section
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='font-size: 2em; color: #1f2937; margin-bottom: 10px;'>✨ Key Features</h2>
            <p style='color: #6b7280; font-size: 1.1em;'>Everything you need to manage your health effectively</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 3em; margin-bottom: 15px;'>📈</div>
                <h3 style='margin-bottom: 10px; font-size: 1.5em;'>Medication Tracker</h3>
                <p style='opacity: 0.9; line-height: 1.6;'>
                    Never miss a dose! Track your medications, set reminders, and monitor adherence rates. 
                    View your daily schedule and medication library at a glance.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 3em; margin-bottom: 15px;'>⚕️</div>
                <h3 style='margin-bottom: 10px; font-size: 1.5em;'>Side Effects Monitor</h3>
                <p style='opacity: 0.9; line-height: 1.6;'>
                    Report and track medication side effects. Get AI-powered insights and communicate 
                    directly with your healthcare provider about any concerns.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 3em; margin-bottom: 15px;'>🔔</div>
                <h3 style='margin-bottom: 10px; font-size: 1.5em;'>Smart Notifications</h3>
                <p style='opacity: 0.9; line-height: 1.6;'>
                    Stay informed with medication requests, doctor notes, and important health updates. 
                    Real-time communication between patients and clinicians.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 3em; margin-bottom: 15px;'>🚨</div>
                <h3 style='margin-bottom: 10px; font-size: 1.5em;'>Emergency Dashboard</h3>
                <p style='opacity: 0.9; line-height: 1.6;'>
                    Quick access to critical health information: current medications, allergies, 
                    medical conditions, and emergency contacts — all in one place.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 3em; margin-bottom: 15px;'>📋</div>
                <h3 style='margin-bottom: 10px; font-size: 1.5em;'>Medical History Log</h3>
                <p style='opacity: 0.9; line-height: 1.6;'>
                    Comprehensive timeline and calendar view of your medical events, procedures, 
                    appointments, and health milestones. Never lose track of your health journey.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 3em; margin-bottom: 15px;'>👨‍⚕️</div>
                <h3 style='margin-bottom: 10px; font-size: 1.5em;'>Clinician Portal</h3>
                <p style='opacity: 0.9; line-height: 1.6;'>
                    Healthcare providers can authorize patients, send medication requests, 
                    monitor adherence, and respond to side effect reports seamlessly.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Why Choose MediPal Section
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 40px; border-radius: 15px; margin-bottom: 30px;'>
            <h2 style='text-align: center; color: #92400e; margin-bottom: 25px; font-size: 2em;'>🌟 Why Choose MediPal?</h2>
            <div style='display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;'>
                <div style='flex: 1; min-width: 200px; text-align: center;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🔒</div>
                    <h4 style='color: #92400e; margin-bottom: 8px;'>Secure & Private</h4>
                    <p style='color: #78350f; font-size: 0.9em;'>Your health data is encrypted and protected</p>
                </div>
                <div style='flex: 1; min-width: 200px; text-align: center;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>📱</div>
                    <h4 style='color: #92400e; margin-bottom: 8px;'>Easy to Use</h4>
                    <p style='color: #78350f; font-size: 0.9em;'>Intuitive interface designed for everyone</p>
                </div>
                <div style='flex: 1; min-width: 200px; text-align: center;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🤖</div>
                    <h4 style='color: #92400e; margin-bottom: 8px;'>AI-Powered</h4>
                    <p style='color: #78350f; font-size: 0.9em;'>Smart insights and recommendations</p>
                </div>
                <div style='flex: 1; min-width: 200px; text-align: center;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🔗</div>
                    <h4 style='color: #92400e; margin-bottom: 8px;'>Connected Care</h4>
                    <p style='color: #78350f; font-size: 0.9em;'>Seamless communication with providers</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Final CTA
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1f2937 0%, #111827 100%); color: white; padding: 50px 40px; border-radius: 15px; text-align: center;'>
            <h2 style='font-size: 2.2em; margin-bottom: 15px;'>Ready to Take Control of Your Health?</h2>
            <p style='font-size: 1.2em; opacity: 0.9; margin-bottom: 30px;'>Join thousands of users managing their health with MediPal</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.write("")
        with col2:
            if st.button("🚀 Get Started Now", use_container_width=True, type="primary", key="final_cta"):
                try:
                    self.do_redirect("Create Account")
                except Exception:
                    st.rerun()
        with col3:
            st.write("")
    
    def _render_patient_dashboard(self):
        """Render the dashboard for logged-in patients."""
        from data.shared.patient_profile import get_patient_profile
        from data.medication_tracker.adherence_stats import get_today_summary_for_user
        from data.medication_tracker.medication_requests import get_pending_requests_for_patient
        from data.side_effect_monitor.patient_side_effect import get_patient_side_effect_analytics
        
        user_id = st.session_state.get('current_id')
        patient = get_patient_profile(user_id)
        
        # Welcome Header
        first_name = patient.get('first_name', 'User') if patient else 'User'
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px;'>
            <h1 style='font-size: 2.5em; margin-bottom: 10px;'>Welcome back, {first_name}! 👋</h1>
            <p style='font-size: 1.2em; opacity: 0.9;'>Here's your health summary for today</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Today's Summary Stats
        today_summary = get_today_summary_for_user(user_id)
        pending_requests = get_pending_requests_for_patient(user_id)
        side_effect_analytics = get_patient_side_effect_analytics(user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <div style='font-size: 3em; margin-bottom: 10px;'>📈</div>
                <div style='font-size: 2.5em; font-weight: 700; margin-bottom: 5px;'>{today_summary['taken']}/{today_summary['total']}</div>
                <div style='font-size: 0.95em; opacity: 0.9;'>Medications Taken</div>
                <div style='font-size: 1.3em; font-weight: 600; margin-top: 10px;'>{today_summary['completion_rate']}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pending_count = len(pending_requests) if pending_requests else 0
            color = '#f59e0b' if pending_count > 0 else '#6b7280'
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <div style='font-size: 3em; margin-bottom: 10px;'>🔔</div>
                <div style='font-size: 2.5em; font-weight: 700; margin-bottom: 5px;'>{pending_count}</div>
                <div style='font-size: 0.95em; opacity: 0.9;'>Pending Requests</div>
                <div style='font-size: 0.85em; margin-top: 10px; opacity: 0.8;'>Needs Your Review</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            active_reports = side_effect_analytics.get('active_reports', 0)
            report_color = '#dc2626' if active_reports > 0 else '#10b981'
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <div style='font-size: 3em; margin-bottom: 10px;'>⚕️</div>
                <div style='font-size: 2.5em; font-weight: 700; margin-bottom: 5px;'>{active_reports}</div>
                <div style='font-size: 0.95em; opacity: 0.9;'>Active Side Effects</div>
                <div style='font-size: 0.85em; margin-top: 10px; opacity: 0.8;'>Being Monitored</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            active_meds = today_summary['active_meds']
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <div style='font-size: 3em; margin-bottom: 10px;'>💊</div>
                <div style='font-size: 2.5em; font-weight: 700; margin-bottom: 5px;'>{active_meds}</div>
                <div style='font-size: 0.95em; opacity: 0.9;'>Active Medications</div>
                <div style='font-size: 0.85em; margin-top: 10px; opacity: 0.8;'>In Your Regimen</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 View Medication Tracker", use_container_width=True, type="primary"):
                try:
                    self.do_redirect("Medication Tracker")
                except Exception:
                    st.rerun()
        
        with col2:
            if st.button("⚕️ Report Side Effect", use_container_width=True):
                try:
                    self.do_redirect("Side Effects")
                except Exception:
                    st.rerun()
        
        with col3:
            if st.button("🔔 Check Notifications", use_container_width=True):
                try:
                    self.do_redirect("Notifications")
                except Exception:
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tips Section
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 30px; border-radius: 12px; margin-top: 20px;'>
            <h3 style='color: #92400e; margin-bottom: 15px;'>💡 Daily Health Tips</h3>
            <ul style='color: #78350f; line-height: 1.8; font-size: 1.05em;'>
                <li><strong>Take medications at consistent times</strong> each day to maintain effectiveness</li>
                <li><strong>Track any side effects</strong> immediately so your doctor can help you</li>
                <li><strong>Keep emergency contacts updated</strong> in your Emergency Dashboard</li>
                <li><strong>Review medication requests</strong> from your healthcare provider promptly</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_clinician_dashboard(self):
        """Render the dashboard for clinicians."""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px;'>
            <h1 style='font-size: 2.5em; margin-bottom: 10px;'>👨‍⚕️ Clinician Dashboard</h1>
            <p style='font-size: 1.2em; opacity: 0.9;'>Manage patient care and medication requests</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if there's already an authorized patient
        authorized_patient_id = st.session_state.get('authorized_patient_id')
        
        if authorized_patient_id:
            # Show currently authorized patient info in a container
            from data.shared.patient_profile import get_patient_profile
            current_patient = get_patient_profile(authorized_patient_id)
            
            if current_patient:
                # Active patient card with prominent styling
                st.markdown("""
                <div style='background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid #28a745;'>
                    <h3 style='color: #155724; margin-bottom: 15px; font-size: 1.5em;'>✅ Currently Authorized Patient</h3>
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
                    if st.button("🔄 Change Patient", use_container_width=True, key="change_patient"):
                        del st.session_state['authorized_patient_id']
                        st.rerun()
                
                st.info("💡 **Quick Access:** Use the tabs above to view **Medication Tracker**, **Side Effects**, **Medical History**, **Emergency Dashboard**, or **Notifications** for this patient.")
                st.markdown("---")
            else:
                # Patient data not found, clear the authorization
                del st.session_state['authorized_patient_id']
                st.rerun()
        
        # Show search form with better styling
        st.markdown("""
        <div style='background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); padding: 30px; border-radius: 12px; margin-top: 20px;'>
            <h3 style='color: #3730a3; margin-bottom: 10px;'>🔍 Patient Authorization</h3>
            <p style='color: #4338ca; font-size: 1.05em;'>Enter patient credentials to access their medical information</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
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
        
        st.write("")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔐 Authorize Access", type="primary", use_container_width=True):
                if search_id and search_dob:
                    from data.shared.patient_profile import get_patient_profile
                    try:
                        patient = get_patient_profile(int(search_id))
                        if patient and str(patient.get('date_of_birth')) == search_dob:
                            st.session_state['authorized_patient_id'] = int(search_id)
                            st.success(f"✅ Successfully authorized patient: {patient.get('first_name', '')} {patient.get('last_name', '')}")
                            st.rerun()
                        else:
                            st.error("❌ No patient found with that ID and DOB combination.")
                    except ValueError:
                        st.error("❌ Invalid Patient ID format. Please enter a numeric ID.")
                else:
                    st.warning("⚠️ Please enter both Patient User ID and Date of Birth.")

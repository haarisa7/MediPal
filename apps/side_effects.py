import streamlit as st
from hydralit import HydraHeadApp
from datetime import datetime

from data.patient_profile import get_patient_profile
from components.side_effect_form import render_side_effect_report_form


class SideEffects(HydraHeadApp):
    def _resolve_user_id(self):
        cur = st.session_state.get('current_id')
        if cur is None:
            return None
        # If it's already an int, return as is
        if isinstance(cur, int):
            return cur
        # If it's a string that looks like an int, convert
        if isinstance(cur, str):
            try:
                return int(cur)
            except Exception:
                return None
        return None

    def _resolve_patient_id(self):
        from data.patient_profile import get_user_role
        user_id = st.session_state.get('current_id')
        role = get_user_role(user_id) if user_id else None
        if role == 1:
            # Clinician: use patient_id from session
            return st.session_state.get('authorized_patient_id')
        else:
            # Patient: use their own user_id
            return user_id

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        from data.patient_profile import get_user_role
        
        user_id = st.session_state.get('current_id')
        role = get_user_role(user_id) if user_id else None
        
        patient_id = self._resolve_patient_id()
        if not patient_id:
            st.title("💊 Side Effects Monitor")
            st.warning("No patient selected. Clinicians must authorize a patient in Home tab.")
            return

        # Check if clinician - show notification view
        if role == 1:
            self._render_clinician_view(patient_id, user_id)
            return
        
        # Patient view
        self._render_patient_view(patient_id)
    
    def _render_patient_view(self, patient_id):
        """Render the patient view with side effect reporting form and monitoring."""
        
        # Initialize session state for side effect form
        if 'show_side_effect_form' not in st.session_state:
            st.session_state.show_side_effect_form = False
        
        # If form is active, show only the form (full screen takeover)
        if st.session_state.show_side_effect_form:
            render_side_effect_report_form(patient_id)
            return

        # Load global styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass

        # Initialize session state for side effects page
        if 'side_effects_expanded' not in st.session_state:
            st.session_state['side_effects_expanded'] = {}

        st.title("⚕️Side Effects Monitor")

        # Get data
        patient = get_patient_profile(patient_id)
        
        # Get real analytics from database
        from data.patient_side_effect import get_patient_side_effect_analytics
        analytics = get_patient_side_effect_analytics(patient_id)
        total_reports = analytics['total_reports']

        # Enhanced header with patient info and statistics
        first_name = patient.get('first_name', '') if patient else ''
        last_name = patient.get('last_name', '') if patient else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='font-size: 24px; font-weight: 700; margin-bottom: 4px;'>Side Effects Monitoring</div>
                    <div style='font-size: 16px; opacity: 0.9;'>{first_name} {last_name} • Medication Safety Profile</div>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 20px; font-weight: 700;'>{total_reports} Total Reports</div>
                    <div style='font-size: 14px; opacity: 0.9;'>{analytics["active_reports"]} Active Issues</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid #7c3aed; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: #7c3aed;'>{total_reports}</div>
                <div style='color: #6b7280; font-size: 14px;'>Total Reports</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            active_reports = analytics.get('active_reports', 0)
            color = '#dc2626' if active_reports > 0 else '#10b981'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{active_reports}</div>
                <div style='color: #6b7280; font-size: 14px;'>Active Issues</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            medications_affected = analytics.get('medications_affected', 0)
            color = '#f59e0b' if medications_affected > 0 else '#6b7280'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{medications_affected}</div>
                <div style='color: #6b7280; font-size: 14px;'>Medications Affected</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            severe_reports = analytics.get('severe_reports', 0)
            color = '#dc2626' if severe_reports > 0 else '#6b7280'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{severe_reports}</div>
                <div style='color: #6b7280; font-size: 14px;'>Severe Reports</div>
            </div>
            """, unsafe_allow_html=True)

        # Main layout: Medications on left, reports/analytics on right
        col_main, col_sidebar = st.columns([2, 1])

        with col_main:
            # Main medication cards with enhanced side effect profiles using real data
            from components.medication_side_effect import render_patient_side_effect_cards
            render_patient_side_effect_cards(patient_id)

        with col_sidebar:
            # Add filter dropdown
            st.subheader("📋 Reports")
            status_filter = st.selectbox(
                "Filter by status:",
                options=['All', 'Active', 'Resolved'],
                index=1,  # Default to 'Active'
                key="patient_side_effect_filter"
            )
            
            # Get filtered reports
            from data.patient_side_effect import (
                get_patient_side_effect_reports,
                get_active_patient_side_effect_reports,
                get_resolved_patient_side_effect_reports,
                resolve_side_effect_report
            )
            
            if status_filter == 'All':
                filtered_reports = get_patient_side_effect_reports(patient_id)
            elif status_filter == 'Active':
                filtered_reports = get_active_patient_side_effect_reports(patient_id)
            else:  # Resolved
                filtered_reports = get_resolved_patient_side_effect_reports(patient_id)
            
            # Display filtered reports
            if filtered_reports:
                for report in filtered_reports:
                    from components.side_effect_report import render_side_effect_report_card
                    render_side_effect_report_card(report, show_doctor_notes=True)
                    
                    # Add resolve button if not resolved
                    resolved = report.get('resolved', False)
                    if not resolved:
                        if st.button("✅ Mark as Resolved", key=f"resolve_{report['report_id']}", use_container_width=True):
                            if resolve_side_effect_report(report['report_id']):
                                st.success("Report marked as resolved!")
                                st.rerun()
                            else:
                                st.error("Failed to resolve report.")
                    st.markdown("---")
            else:
                st.info("No reports found.")
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            if st.button("🚨 Report Emergency Side Effect", type="primary", help="For severe or life-threatening reactions"):
                st.session_state.show_side_effect_form = True
                st.rerun()
            
            if st.button("📞 Contact Healthcare Provider", help="Get in touch with your doctor"):
                st.info("📞 Contact information available in the Emergency Dashboard")
            
            if st.button("📊 View Full Report History", help="See all your side effect reports"):
                st.info("📊 Complete report history available in Medical History")

        # AI Assistant section (enhanced)
        st.divider()
        st.subheader("🤖 AI Side Effects Assistant")
        
        ai_query = st.text_area(
            "Ask about medication side effects:",
            placeholder="Example: I'm experiencing muscle pain after taking Atorvastatin. Is this normal and what should I do?",
            key="side_effects_ai_query",
            height=100
        )
        
        if st.button("Ask AI Assistant", key="side_effects_ai_ask", type="primary"):
            if ai_query.strip():
                st.markdown("""
                <div style='background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 16px; margin-top: 16px;'>
                    <div style='font-weight: 600; color: #0369a1; margin-bottom: 8px;'>🤖 AI Assistant Response:</div>
                    <div style='color: #0369a1; font-size: 14px;'>
                        This is a demonstration feature. In the full version, our AI would provide personalized medical information about your specific side effects, including:
                        <br><br>
                        • <strong>Severity assessment</strong> and urgency level<br>
                        • <strong>Management recommendations</strong> and home remedies<br>
                        • <strong>When to contact</strong> your healthcare provider<br>
                        • <strong>Drug interaction</strong> warnings and precautions<br>
                        • <strong>Alternative medications</strong> to discuss with your doctor
                        <br><br>
                        <em>Always consult your healthcare provider for medical advice and never ignore severe symptoms.</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a question about side effects.")

        return
    
    def _render_clinician_view(self, patient_id, clinician_id):
        """Render the clinician view showing patient's side effect reports as notifications."""
        from components.clinician_side_effect import render_clinician_side_effect_view
        render_clinician_side_effect_view(patient_id, clinician_id)
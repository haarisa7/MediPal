import streamlit as st
from data.patient_profile import get_patient_profile
from data.patient_side_effect import (
    get_patient_side_effect_reports,
    get_active_patient_side_effect_reports,
    get_resolved_patient_side_effect_reports
)
from components.side_effect_report import render_side_effect_report_card


def render_clinician_side_effect_view(patient_id, clinician_id):
    """Render the clinician view showing patient's side effect reports as notifications."""
    
    # Load global styles
    try:
        with open("assets/styles.css", "r", encoding="utf-8") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass
    
    st.title("⚕️ Side Effects Monitor - Clinician View")
    
    # Get patient info
    patient = get_patient_profile(patient_id)
    first_name = patient.get('first_name', '') if patient else ''
    last_name = patient.get('last_name', '') if patient else ''
    
    # Add filter dropdown
    status_filter = st.selectbox(
        "Filter by status:",
        options=['All', 'Active', 'Resolved'],
        index=1,  # Default to 'Active'
        key="clinician_side_effect_filter"
    )
    
    # Get filtered reports from database
    if status_filter == 'All':
        all_reports = get_patient_side_effect_reports(patient_id)
    elif status_filter == 'Active':
        all_reports = get_active_patient_side_effect_reports(patient_id)
    else:  # Resolved
        all_reports = get_resolved_patient_side_effect_reports(patient_id)
    
    total_count = len(all_reports)
    
    # Check for new reports (notifications)
    last_seen_count = st.session_state.get(f'clinician_last_seen_reports_{patient_id}', 0)
    new_reports_count = max(0, total_count - last_seen_count)
    
    if new_reports_count > 0:
        st.toast(f"🚨 {new_reports_count} new side effect report(s) from {first_name} {last_name}!", icon="⚠️")
    
    # Update last seen count
    st.session_state[f'clinician_last_seen_reports_{patient_id}'] = total_count
    
    # Header with patient info
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <div style='font-size: 24px; font-weight: 700; margin-bottom: 4px;'>Patient Side Effect Reports</div>
                <div style='font-size: 16px; opacity: 0.9;'>{first_name} {last_name}</div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 20px; font-weight: 700;'>{total_count} Total Reports</div>
                <div style='font-size: 14px; opacity: 0.9;'>{new_reports_count} New Report(s)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display all reports
    if all_reports:
        st.subheader(f"📋 All Side Effect Reports ({total_count})")
        
        for report in all_reports:
            # Show both patient notes and doctor notes for clinicians
            render_side_effect_report_card(report, show_notes=True, show_doctor_notes=True)
            
            # Add doctor note button
            report_id = report.get('report_id')
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button(f"💬 Add Doctor Note", key=f"add_note_{report_id}"):
                    st.session_state[f'show_note_form_{report_id}'] = True
                    st.rerun()
            
            # Show note form if button was clicked
            if st.session_state.get(f'show_note_form_{report_id}', False):
                with st.form(key=f"doctor_note_form_{report_id}"):
                    st.markdown("**Add Note for Patient:**")
                    doctor_note = st.text_area(
                        "Your note:",
                        placeholder="Enter your medical advice, recommendations, or follow-up instructions...",
                        height=100
                    )
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("📨 Send Note", type="primary")
                    with col_cancel:
                        cancelled = st.form_submit_button("❌ Cancel")
                    
                    if submitted and doctor_note.strip():
                        from data.side_effect_requests import insert_doctor_note
                        request_id = insert_doctor_note(
                            report_id=report_id,
                            clinician_id=clinician_id,
                            patient_id=patient_id,
                            doctor_note=doctor_note.strip()
                        )
                        if request_id:
                            st.success("✅ Note sent to patient!")
                            st.session_state[f'show_note_form_{report_id}'] = False
                            st.rerun()
                        else:
                            st.error("Failed to send note. Please try again.")
                    elif submitted:
                        st.warning("Please enter a note before sending.")
                    
                    if cancelled:
                        st.session_state[f'show_note_form_{report_id}'] = False
                        st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No side effect reports from this patient yet.")

import streamlit as st
from datetime import datetime
import time

from data.patient_side_effect import insert_side_effect_report
from data.patient_medications import get_daily_patient_medications
from data.side_effect import get_all_sideeffects_for_drug, search_all_side_effects, get_side_effect_id_by_name
from data.medications import get_drug_display_name
from components.search_component import render_search_interface, clear_search_selection


def render_side_effect_report_form(patient_id):
    """Render the side effect reporting form that takes over the entire screen."""
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px;'>
        <div style='font-size: 28px; font-weight: 700; margin-bottom: 8px;'>🚨 Report Side Effect</div>
        <div style='font-size: 16px; opacity: 0.9;'>Help us monitor your medication safety</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Important notice
    st.error("⚠️ **For medical emergencies, call 911 immediately!** This form is for reporting and tracking purposes only.")
    
    # Get patient's daily medications
    daily_meds = get_daily_patient_medications(patient_id)
    
    # Form sections
    st.markdown("### 📋 Report Details")
    
    # Medication selection (optional)
    med_options = ["Not sure / Multiple medications"] + [
        f"{get_drug_display_name(med['drug_id'])} - {med['dose']} ({med['timing']})" 
        for med in daily_meds
    ]
    
    selected_med_display = st.selectbox(
        "Which medication do you think caused this? (Optional)",
        med_options,
        help="Select the medication if you know which one caused the side effect"
    )
    
    # Determine patient_medication_id
    patient_medication_id = None
    selected_drug_id = None
    if selected_med_display != "Not sure / Multiple medications":
        # Find the corresponding medication
        med_index = med_options.index(selected_med_display) - 1  # -1 because first option is "Not sure"
        selected_med = daily_meds[med_index]
        patient_medication_id = selected_med['id']
        selected_drug_id = selected_med['drug_id']
    
    # Side effect selection
    st.markdown("### 🤒 What are you experiencing?")
    
    # Use the search component
    side_effect_id, search_query = render_search_interface(
        search_function=search_all_side_effects,
        placeholder_text="e.g., headache, nausea, dizziness, rash...",
        label="Search for a side effect:",
        help_text="Start typing to search for side effects",
        min_chars=2,
        session_key="side_effect_search",
        num_columns=2,
        show_count=True
    )
    
    # If no selection but user has typed something, allow custom text
    if not side_effect_id and search_query and len(search_query) >= 2:
        st.info("💡 No match found? You can still submit with your custom description.")
        side_effect_id = search_query
    
    # Severity rating
    st.markdown("### ⚠️ How severe is it?")
    severity = st.select_slider(
        "Rate the severity:",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: {
            1: "1 - Mild (Minor discomfort)",
            2: "2 - Moderate (Noticeable)",
            3: "3 - Significant (Affecting daily life)",
            4: "4 - Severe (Very concerning)",
            5: "5 - Emergency (Seek immediate help)"
        }[x],
        value=3
    )
    
    # Additional notes
    st.markdown("### 📝 Additional Information")
    notes = st.text_area(
        "Describe your symptoms in detail:",
        placeholder="When did it start? How long has it lasted? Any other relevant information...",
        height=120
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Submit Report", type="primary", use_container_width=True):
            # Validation
            if not side_effect_id:
                st.error("Please select or describe the side effect you're experiencing.")
            else:
                # Convert PT name to meddra_id if it's a string
                if isinstance(side_effect_id, str):
                    meddra_id = get_side_effect_id_by_name(side_effect_id)
                    if not meddra_id:
                        st.error("Could not find the side effect in our database. Please try selecting from the search results.")
                        return
                else:
                    meddra_id = side_effect_id
                
                # Insert the report
                report_id = insert_side_effect_report(
                    user_id=patient_id,
                    side_effect_id=meddra_id,
                    severity=severity,
                    notes=notes,
                    patient_med_id=patient_medication_id
                )
                
                if report_id:
                    st.success("✅ Side effect report submitted successfully!")
                    
                    # Show next steps based on severity
                    if severity >= 4:
                        st.error("⚠️ **High Severity Alert**: Please contact your healthcare provider immediately or seek emergency care.")
                    else:
                        st.info("📋 Your report has been logged. Your healthcare provider will be notified.")
                    
                    # Clear selection from session state
                    clear_search_selection('side_effect_search')
                    
                    # Delay for 1 second then close the form
                    time.sleep(1)
                    st.session_state.show_side_effect_form = False
                    st.rerun()
                else:
                    st.error("Failed to submit report. Please try again.")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_side_effect_form = False
            clear_search_selection('side_effect_search')
            st.rerun()
    
    with col3:
        st.markdown("<div style='padding: 8px;'></div>", unsafe_allow_html=True)
    
    # Emergency contact reminder
    st.markdown("---")
    st.markdown("""
    <div style='background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px; border-radius: 8px;'>
        <div style='font-weight: 700; color: #991b1b; margin-bottom: 8px;'>🚨 Emergency Contacts</div>
        <div style='color: #991b1b; font-size: 14px;'>
            <strong>Emergency Services:</strong> Call 911<br>
            <strong>Poison Control:</strong> 1-800-222-1222 (24/7)<br>
            <strong>Your Doctor:</strong> Contact through your patient portal
        </div>
    </div>
    """, unsafe_allow_html=True)

import streamlit as st
from datetime import date
from data.patient_allergies import get_patient_allergies, insert_patient_allergy


def _get_severity_badge(severity):
    """Get badge styling for allergy severity."""
    styles = {
        'CRITICAL': ('background: #dc2626; color: white;', '🔴'),
        'MODERATE': ('background: #f59e0b; color: white;', '🟡'),
        'MILD': ('background: #10b981; color: white;', '🟢')
    }
    style, icon = styles.get(severity, styles['MODERATE'])
    return f"<span style='{style} padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;'>{icon} {severity}</span>"


def _render_allergy_item(allergy):
    """Render a single allergy card."""
    substance = allergy.get('substance', 'Unknown')
    reaction = allergy.get('reaction', '')
    severity = allergy.get('severity', 'MODERATE')
    
    badge = _get_severity_badge(severity)
    
    st.markdown(f"""
    <div style='background: #fff; border-left: 4px solid #dc2626; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <div style='font-weight: 600; font-size: 15px; color: #1f2937;'>⚠️ {substance}</div>
            {badge}
        </div>
        <div style='color: #6b7280; font-size: 13px;'>{reaction}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_add_form(patient_id):
    """Render add allergy form."""
    st.markdown("### ➕ Add New Allergy")
    
    with st.form("add_allergy_form", clear_on_submit=True):
        substance = st.text_input("Substance/Allergen", placeholder="e.g., Penicillin, Peanuts")
        reaction = st.text_area("Reaction", placeholder="Describe the allergic reaction", height=80)
        severity = st.selectbox("Severity", ['MILD', 'MODERATE', 'CRITICAL'])
        date_discovered = st.date_input("Date Discovered", value=date.today())
        notes = st.text_area("Additional Notes (optional)", height=60)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Add Allergy", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['show_allergy_form'] = False
            st.rerun()
        
        if submit:
            if not substance:
                st.error("Substance is required")
            else:
                if insert_patient_allergy(patient_id, substance, reaction, severity, date_discovered, notes):
                    st.success(f"✅ Allergy '{substance}' added successfully!")
                    st.session_state['show_allergy_form'] = False
                    st.rerun()
                else:
                    st.error("Failed to add allergy. Please try again.")


def render_allergy_cards(patient_id, is_clinician=False):
    """Render allergy cards with add functionality."""
    # Fetch from database
    allergies = get_patient_allergies(patient_id)
    
    if allergies:
        for allergy in allergies:
            _render_allergy_item(allergy)
    else:
        st.info("No allergies recorded")
    
    # Add button - only for patients
    if not is_clinician:
        if st.button("➕ Add Allergy", key="add_allergy_btn", use_container_width=True):
            st.session_state['show_allergy_form'] = True
            st.rerun()
    
    # Show form if triggered - only for patients
    if not is_clinician and st.session_state.get('show_allergy_form'):
        st.markdown("---")
        _render_add_form(patient_id)

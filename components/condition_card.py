import streamlit as st
from data.patient_conditions import get_patient_conditions, insert_patient_condition


def _get_status_badge(status):
    """Get badge styling for condition status."""
    styles = {
        'ACTIVE': ('background: #dc2626; color: white;', '🔴'),
        'MANAGED': ('background: #f59e0b; color: white;', '🟡'),
        'RESOLVED': ('background: #10b981; color: white;', '🟢')
    }
    style, icon = styles.get(status, styles['ACTIVE'])
    return f"<span style='{style} padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;'>{icon} {status}</span>"


def _render_condition_item(condition):
    """Render a single condition card."""
    name = condition.get('name', 'Unknown')
    diagnosed_date = condition.get('diagnosed_date', '')
    status = condition.get('status', 'ACTIVE')
    notes = condition.get('notes', '')
    
    badge = _get_status_badge(status)
    
    st.markdown(f"""
    <div style='background: #fff; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <div style='font-weight: 600; font-size: 15px; color: #1f2937;'>🏥 {name}</div>
            {badge}
        </div>
        <div style='color: #6b7280; font-size: 12px; margin-bottom: 4px;'>Diagnosed: {diagnosed_date}</div>
        {f"<div style='color: #4b5563; font-size: 13px;'>{notes}</div>" if notes else ''}
    </div>
    """, unsafe_allow_html=True)


def _render_add_form(patient_id):
    """Render add condition form."""
    st.markdown("### ➕ Add Medical Condition")
    
    with st.form("add_condition_form", clear_on_submit=True):
        name = st.text_input("Condition Name", placeholder="e.g., Type 2 Diabetes, Hypertension")
        diagnosed_date = st.date_input("Diagnosed Date")
        status = st.selectbox("Status", ['ACTIVE', 'MANAGED', 'RESOLVED'])
        notes = st.text_area("Notes", placeholder="Additional information", height=80)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Add Condition", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['show_condition_form'] = False
            st.rerun()
        
        if submit:
            if not name:
                st.error("Condition name is required")
            else:
                # Severity mapping (1=low, 2=medium, 3=high)
                severity_map = {'ACTIVE': 3, 'MANAGED': 2, 'RESOLVED': 1}
                severity = severity_map.get(status, 2)
                
                if insert_patient_condition(patient_id, name, severity, diagnosed_date, status, notes):
                    st.success(f"✅ Condition '{name}' added successfully!")
                    st.session_state['show_condition_form'] = False
                    st.rerun()
                else:
                    st.error("Failed to add condition. Please try again.")


def render_condition_cards(patient_id, is_clinician=False):
    """Render condition cards with add functionality."""
    # Fetch from database
    conditions = get_patient_conditions(patient_id)
    
    if conditions:
        for condition in conditions:
            _render_condition_item(condition)
    else:
        st.info("No conditions recorded")
    
    # Add button - only for patients
    if not is_clinician:
        if st.button("➕ Add Condition", key="add_condition_btn", use_container_width=True):
            st.session_state['show_condition_form'] = True
            st.rerun()
    
    # Show form if triggered - only for patients
    if not is_clinician and st.session_state.get('show_condition_form'):
        st.markdown("---")
        _render_add_form(patient_id)

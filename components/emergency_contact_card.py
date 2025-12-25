import streamlit as st
from data.emergency_contacts import get_emergency_contacts, insert_emergency_contact


def _get_contact_type_icon(contact_type):
    """Get icon for contact type."""
    icons = {
        'PRIMARY': '👤',
        'SECONDARY': '👥',
        'DOCTOR': '👨‍⚕️',
        'EMERGENCY': '🚨'
    }
    return icons.get(contact_type, '📞')


def _render_contact_item(contact):
    """Render a single emergency contact card."""
    name = contact.get('name', 'Unknown')
    phone = contact.get('phone', '')
    relation = contact.get('relation', '')
    contact_type = contact.get('type', 'PRIMARY')
    email = contact.get('email', '')
    
    icon = _get_contact_type_icon(contact_type)
    
    st.markdown(f"""
    <div style='background: #fff; border-left: 4px solid #2563eb; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
        <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;'>
            <div>
                <div style='font-weight: 600; font-size: 15px; color: #1f2937;'>{icon} {name}</div>
                <div style='color: #6b7280; font-size: 12px;'>{relation} • {contact_type}</div>
            </div>
        </div>
        <div style='color: #2563eb; font-size: 14px; font-weight: 600; margin-bottom: 4px;'>📞 {phone}</div>
        {f"<div style='color: #6b7280; font-size: 12px;'>✉️ {email}</div>" if email else ''}
    </div>
    """, unsafe_allow_html=True)


def _render_add_form(patient_id):
    """Render add emergency contact form."""
    st.markdown("### ➕ Add Emergency Contact")
    
    with st.form("add_contact_form", clear_on_submit=True):
        name = st.text_input("Full Name", placeholder="e.g., Jane Smith")
        phone = st.text_input("Phone Number", placeholder="(555) 123-4567")
        relation = st.text_input("Relationship", placeholder="e.g., Spouse, Parent, Friend")
        contact_type = st.selectbox("Contact Type", ['PRIMARY', 'SECONDARY', 'DOCTOR', 'EMERGENCY'])
        email = st.text_input("Email (optional)", placeholder="email@example.com")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Add Contact", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['show_contact_form'] = False
            st.rerun()
        
        if submit:
            if not name or not phone:
                st.error("Name and phone number are required")
            else:
                if insert_emergency_contact(patient_id, name, relation, phone, contact_type, email):
                    st.success(f"✅ Contact '{name}' added successfully!")
                    st.session_state['show_contact_form'] = False
                    st.rerun()
                else:
                    st.error("Failed to add contact. Please try again.")


def render_emergency_contact_cards(patient_id, is_clinician=False):
    """Render emergency contact cards with add functionality."""
    # Fetch from database
    contacts = get_emergency_contacts(patient_id)
    
    if contacts:
        for contact in contacts:
            _render_contact_item(contact)
    else:
        st.info("No emergency contacts recorded")
    
    # Add button - only for patients
    if not is_clinician:
        if st.button("➕ Add Contact", key="add_contact_btn", use_container_width=True):
            st.session_state['show_contact_form'] = True
            st.rerun()
    
    # Show form if triggered - only for patients
    if not is_clinician and st.session_state.get('show_contact_form'):
        st.markdown("---")
        _render_add_form(patient_id)

"""Helper functions for medication tracking to reduce code duplication."""

import streamlit as st
from data.medications import get_drug_display_name


def build_medication_dict(med):
    """Build a standardized medication dictionary from a patient_medication record."""
    return {
        'drug_name': get_drug_display_name(med['drug_id']),
        'dose': med.get('dose', ''),
        'instructions': med.get('instructions', ''),
        'prescribed_by': med.get('prescribed_by', ''),
        'timing': med.get('timing', ''),
    }


def render_stat_card(value, label, color):
    """Render a statistics card with consistent styling."""
    return f"""
    <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
        <div style='font-size: 24px; font-weight: 700; color: {color};'>{value}</div>
        <div style='color: #6b7280; font-size: 14px;'>{label}</div>
    </div>
    """


def render_page_header(title, subtitle, icon, gradient):
    """Render a consistent page header with gradient background."""
    st.markdown(f"""
    <div style='background: {gradient}; color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px;'>
        <div style='font-size: 28px; font-weight: 700; margin-bottom: 8px;'>{icon} {title}</div>
        <div style='font-size: 16px; opacity: 0.9;'>{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_back_button(label, session_key, additional_cleanup=None):
    """Render a back button that cleans up session state."""
    if st.button(f'← {label}', key=f'{session_key}_back', use_container_width=False):
        st.session_state[session_key] = False
        if additional_cleanup:
            additional_cleanup()
        st.rerun()


def render_info_box(title, items):
    """Render an info box with helpful tips."""
    items_html = ''.join([f"• {item}<br>" for item in items])
    st.markdown(f"""
    <div style='background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px;'>
        <div style='font-weight: 700; color: #1e40af; margin-bottom: 8px;'>💡 {title}</div>
        <div style='color: #1e40af; font-size: 14px;'>
            {items_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_current_role():
    """Get the role of the current user."""
    from data.patient_profile import get_user_role
    return get_user_role(st.session_state.get('current_id'))


def is_clinician():
    """Check if current user is a clinician."""
    return get_current_role() == 1

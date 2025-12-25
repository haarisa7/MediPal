import streamlit as st


def _get_medication_icon(dose):
    """Get medication icon based on dose type."""
    dose_lower = dose.lower() if dose else ''
    if 'tablet' in dose_lower:
        return '💊'
    elif any(x in dose_lower for x in ['ml', ' l ', 'drops', 'drop']):
        return '💉'
    elif any(x in dose_lower for x in ['mg', ' g ', 'mcg']):
        return '⚕️'
    return '💊'


def _build_medication_card_html(medication, adherence_rate, border_style, status_badge, show_timing):
    """Build HTML for medication card with specified styling."""
    drug_name = medication.get('drug_name', 'Medication').title()
    dose = medication.get('dose', '')
    timing = medication.get('timing', '')
    instructions = medication.get('instructions', '')
    prescribed_by = medication.get('prescribed_by', '')
    
    # Adherence badge - position depends on status badge
    adherence_top = '48px' if status_badge else '16px'
    adherence_html = f"<span style='position: absolute; top: {adherence_top}; right: 16px; color: #2563eb; font-size: 13px; background: #e0e7ff; padding: 2px 10px; border-radius: 8px;'>Adherence: {adherence_rate if adherence_rate is not None else '--'}%</span>"
    
    # Instructions with optional timing
    timing_text = f"<b>{timing}</b> • " if (timing and show_timing) else ''
    instructions_text = instructions if instructions else 'Follow package instructions.'
    
    # Get appropriate icon based on dose
    icon = _get_medication_icon(dose)
    
    return f"""
<div style='background: #fff; {border_style}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    {status_badge}{adherence_html}
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <span style='font-size: 24px; margin-right: 12px;'>{icon}</span>
        <div>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{drug_name}</div>
            <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
        </div>
    </div>
    <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
        {timing_text}{instructions_text}
    </div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {prescribed_by}</div>
</div>
    """


def render_medication_card(medication: dict, patient_med_id: int, status=None, context='schedule', adherence_rate=None, active=True):
    """Render a medication card with appropriate styling based on status and context."""
    # Determine border style and status badge
    if context == 'library':
        border_color = '#10b981' if active else '#ef4444'
        border_style = f'border-left: 6px solid {border_color}'
        status_badge = ''
        show_timing = False
    elif context == 'edit':
        border_style = 'border-radius: 12px'
        status_badge = ''
        show_timing = True
    elif status == 'taken':
        border_style = 'border-left: 6px solid #10b981'
        status_badge = "<span style='position: absolute; top: 16px; right: 16px; color: #10b981; font-weight: 700; background: #e0f7ef; padding: 4px 12px; border-radius: 8px;'>✔ Taken</span>"
        show_timing = True
    elif status == 'missed':
        border_style = 'border-left: 6px solid #ef4444'
        status_badge = "<span style='position: absolute; top: 16px; right: 16px; color: #ef4444; font-weight: 700; background: #fee2e2; padding: 4px 12px; border-radius: 8px;'>✖ Missed</span>"
        show_timing = True
    else:  # pending
        border_style = 'border-left: 4px solid #6b7280'
        status_badge = ''
        show_timing = True
    
    # Render card HTML
    card_html = _build_medication_card_html(medication, adherence_rate, border_style, status_badge, show_timing)
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Add action buttons for pending status
    if status is None and context == 'schedule':
        col1, col2, _ = st.columns([1, 1, 2])
        with col1:
            if st.button('✅ Taken', key=f"taken_{patient_med_id}", use_container_width=True):
                from data.medication_log import log_medication_intake
                log_medication_intake(patient_med_id, True)
                st.rerun()
        with col2:
            if st.button('❌ Missed', key=f"missed_{patient_med_id}", use_container_width=True):
                from data.medication_log import log_medication_intake
                log_medication_intake(patient_med_id, False)
                st.rerun()



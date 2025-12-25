import streamlit as st


def _get_rarity_style(rarity):
    """Get styling for rarity badge."""
    styles = {
        'common': {"label": "COMMON", "color": "#10b981"},
        'uncommon': {"label": "UNCOMMON", "color": "#f59e0b"},
        'rare': {"label": "RARE", "color": "#ef4444"},
        'unknown': {"label": "UNKNOWN", "color": "#6b7280"}
    }
    return styles.get(rarity, styles['unknown'])


def _build_doctor_notes_html(report_id, show_notes):
    """Build HTML for doctor notes section."""
    from data.side_effect_requests import get_doctor_notes_for_report
    
    doctor_notes = get_doctor_notes_for_report(report_id)
    
    if not doctor_notes:
        if show_notes:
            return "<div style='border-top: 1px solid #e5e7eb; padding-top: 8px; margin-top: 8px; color: #9ca3af; font-size: 11px; font-style: italic;'>No doctor notes added yet</div>"
        return ""
    
    html = ""
    for note in doctor_notes:
        # Clinician view - always black, Patient view - red for unread
        note_color = '#1f2937' if show_notes else ('#dc2626' if not note.get('received', True) else '#1f2937')
        doctor_name = f"Dr. {note.get('doctor_first_name', '')} {note.get('doctor_last_name', '')}".strip()
        note_text = note.get('doctor_note', '').replace("'", "&#39;").replace('"', '&quot;')
        
        html += f"<div style='border-top: 1px solid #e5e7eb; padding-top: 8px; margin-top: 8px;'><div style='font-weight: 600; font-size: 12px; color: {note_color}; margin-bottom: 4px;'>💬 Doctor's Note</div><div style='color: {note_color}; font-size: 11px; line-height: 1.5; margin-bottom: 4px;'>{note_text}</div><div style='color: #6b7280; font-size: 10px; font-style: italic;'>— {doctor_name}</div></div>"
    
    return html


def render_side_effect_report_card(report, show_notes=False, show_doctor_notes=False):
    """Render a single side effect report as a card."""
    rarity_info = _get_rarity_style(report.get('rarity', 'unknown'))
    
    medication_name = (report.get('display_name', 'Unknown Medication') or 'Unknown Medication').title()
    effect_name = report.get('side_effect_name', 'Side effect')
    reported_date = report.get('reported_at', 'Unknown date')
    frequency = report.get('frequency')
    frequency_display = f"{frequency:.1%}" if frequency is not None else "N/A"
    notes = report.get('notes', '')
    severity = report.get('severity', 0)
    resolved = report.get('resolved', False)
    
    border_color = '#10b981' if resolved else '#ef4444'
    
    # Get doctor notes HTML if needed
    doctor_notes_html = ""
    if show_doctor_notes or show_notes:
        report_id = report.get('report_id')
        if report_id:
            doctor_notes_html = _build_doctor_notes_html(report_id, show_notes)
    
    if show_notes and notes:
        # Clinician view with patient notes
        st.markdown(f"""
        <div style='border: 1px solid #e5e7eb; border-left: 4px solid {border_color}; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: #ffffff; display: flex; gap: 12px;'>
            <div style='flex: 1;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                    <div style='font-weight: 600; font-size: 14px; color: #1f2937;'>{medication_name}</div>
                    <div style='background: {rarity_info["color"]}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 600;'>
                        {rarity_info["label"]}
                    </div>
                </div>
                <div style='color: #4b5563; font-size: 12px; margin-bottom: 4px;'>{effect_name}</div>
                <div style='color: #6b7280; font-size: 11px; margin-bottom: 2px;'>{reported_date}</div>
                <div style='color: #6b7280; font-size: 11px;'>
                    <strong>Frequency:</strong> {frequency_display} • <strong>Severity:</strong> {severity}/5
                </div>
            </div>
            <div style='flex: 1; border-left: 1px solid #e5e7eb; padding-left: 12px;'>
                <div style='font-weight: 600; font-size: 12px; color: #1f2937; margin-bottom: 4px;'>📝 Patient Notes</div>
                <div style='color: #4b5563; font-size: 11px; line-height: 1.5;'>{notes}</div>
                {doctor_notes_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Patient view
        st.markdown(f"""
        <div style='border: 1px solid #e5e7eb; border-left: 4px solid {border_color}; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: #ffffff;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                <div style='font-weight: 600; font-size: 14px; color: #1f2937;'>{medication_name}</div>
                <div style='background: {rarity_info["color"]}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 600;'>
                    {rarity_info["label"]}
                </div>
            </div>
            <div style='color: #4b5563; font-size: 12px; margin-bottom: 4px;'>{effect_name}</div>
            <div style='color: #6b7280; font-size: 11px; margin-bottom: 2px;'>{reported_date}</div>
            <div style='color: #6b7280; font-size: 11px;'>
                <strong>Frequency:</strong> {frequency_display}
            </div>
            {doctor_notes_html}
        </div>
        """, unsafe_allow_html=True)


def render_recent_side_effect_reports(reports, total_count=None, show_doctor_notes=False):
    """
    Render a list of recent side effect reports.
    
    Args:
        reports: List of report dicts
        total_count: Optional total count of all reports (to show if more exist)
        show_doctor_notes: Boolean, if True shows doctor notes on reports (for patient view)
    """
    st.subheader("📋 Recent Reports")
    
    if reports:
        # Display each report as a card
        for report in reports:
            render_side_effect_report_card(report, show_doctor_notes=show_doctor_notes)
        
        # Show info if there are more reports than displayed
        if total_count and total_count > len(reports):
            st.info(f"📊 View all {total_count} reports in Medical History")
    else:
        st.info("No side effects reported yet.")

import streamlit as st
from datetime import datetime
import html


def render_medical_event_card(event, user_id, key_prefix=""):
    """Render a single medical event card with consistent app styling."""
    
    # Determine status badge color and border
    status_config = {
        "Routine": {"color": "#10b981", "bg": "#d1fae5", "border": "#10b981"},
        "Urgent": {"color": "#ef4444", "bg": "#fee2e2", "border": "#ef4444"},
        "Follow-Up": {"color": "#f59e0b", "bg": "#fef3c7", "border": "#f59e0b"},
        "Completed": {"color": "#6b7280", "bg": "#f3f4f6", "border": "#6b7280"}
    }
    
    status = event.get('status', 'Routine')
    config = status_config.get(status, status_config["Routine"])
    
    # Format date
    event_date = event.get('event_date')
    if isinstance(event_date, datetime):
        formatted_date = event_date.strftime("%b %d, %Y")
        formatted_time = event_date.strftime("%I:%M %p")
    else:
        formatted_date = str(event_date)
        formatted_time = ""
    
    # Build event details with default values for missing data and escape HTML
    event_name = html.escape(event.get('event_name', 'Unnamed Event'))
    event_type = html.escape(event.get('event_type', 'Other'))
    description = html.escape(event.get('event_description', '')) if event.get('event_description') else ''
    location = html.escape(event.get('location') or 'Location not specified')
    doctor = html.escape(event.get('doctor_name') or 'No provider specified')
    notes = html.escape(event.get('notes', '')) if event.get('notes') else ''
    icon = event.get('icon', '📝')
    
    # Build event details row
    date_display = formatted_date if formatted_date else 'Unknown date'
    details_line = f"📅 <b>{date_display}</b> {formatted_time} • 📍 {location} • 👨‍⚕️ {doctor}"
    
    # Build description section
    description_html = ""
    if description:
        description_html = f"<div style='color: #4b5563; font-size: 14px; margin-bottom: 12px; font-style: italic;'>{description}</div>"
    
    # Build notes column (right side)
    notes_column = ""
    if notes:
        notes_column = f"""<div style='width: 300px; margin-left: 16px; padding-left: 16px; border-left: 2px solid #e5e7eb;'>
<div style='color: #6b7280; font-size: 12px; font-weight: 700; margin-bottom: 8px;'>📝 NOTES</div>
<div style='color: #4b5563; font-size: 13px; line-height: 1.5;'>{notes}</div>
</div>"""
    
    # Build card HTML with two-column layout
    card_html = f"""<div style='background: #fff; border-left: 6px solid {config["border"]}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
<span style='position: absolute; top: 16px; right: 16px; color: {config["color"]}; font-weight: 700; background: {config["bg"]}; padding: 4px 12px; border-radius: 8px; font-size: 12px;'>{status.upper()}</span>
<div style='display: flex;'>
<div style='flex: 1;'>
<div style='display: flex; align-items: center; margin-bottom: 8px;'>
<span style='font-size: 24px; margin-right: 12px;'>{icon}</span>
<div style='flex: 1; padding-right: 100px;'>
<div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{event_name}</div>
<div style='color: #6b7280; font-size: 13px;'>{event_type}</div>
</div>
</div>
{description_html}
<div style='color: #4b5563; font-size: 13px;'>{details_line}</div>
</div>
{notes_column}
</div>
</div>"""
    
    # Render the card
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("✏️ Edit", key=f"{key_prefix}edit_{event['event_id']}", use_container_width=True):
            st.session_state['show_edit_event'] = True
            st.session_state['edit_selected_event'] = event['event_id']
            st.rerun()
    with col2:
        if st.button("🗑️ Delete", key=f"{key_prefix}delete_{event['event_id']}", use_container_width=True):
            from data.medical_events import delete_medical_event
            if delete_medical_event(event['event_id'], user_id):
                st.success("✅ Event deleted successfully!")
                st.rerun()
            else:
                # Error is stored in session state
                st.rerun()
    
    # Spacing between cards
    st.write("")

import streamlit as st
from datetime import datetime, date, timedelta
from calendar import monthrange
import html


def render_medical_calendar(user_id):
    """Render calendar view of medical events."""
    
    # Get current date
    today = date.today()
    
    # Initialize session state for calendar navigation
    if 'calendar_month' not in st.session_state:
        st.session_state['calendar_month'] = today.month
    if 'calendar_year' not in st.session_state:
        st.session_state['calendar_year'] = today.year
    
    # Month/Year navigation with arrows
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("◀️", key="prev_month", use_container_width=True):
            # Go to previous month
            if st.session_state['calendar_month'] == 1:
                st.session_state['calendar_month'] = 12
                st.session_state['calendar_year'] -= 1
            else:
                st.session_state['calendar_month'] -= 1
            st.rerun()
    
    with col2:
        current_date = date(st.session_state['calendar_year'], st.session_state['calendar_month'], 1)
        st.markdown(f"<h3 style='text-align: center; margin: 0;'>📅 {current_date.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    
    with col3:
        if st.button("▶️", key="next_month", use_container_width=True):
            # Go to next month
            if st.session_state['calendar_month'] == 12:
                st.session_state['calendar_month'] = 1
                st.session_state['calendar_year'] += 1
            else:
                st.session_state['calendar_month'] += 1
            st.rerun()
    
    # Direct month/year selector
    with st.expander("🔍 Jump to specific month"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            jump_month = st.selectbox(
                "Month",
                range(1, 13),
                format_func=lambda x: date(2000, x, 1).strftime("%B"),
                index=st.session_state['calendar_month'] - 1,
                key="jump_month"
            )
        with col2:
            jump_year = st.selectbox(
                "Year",
                range(today.year - 5, today.year + 2),
                index=st.session_state['calendar_year'] - (today.year - 5),
                key="jump_year"
            )
        with col3:
            st.write("")
            if st.button("Go", type="primary", use_container_width=True):
                st.session_state['calendar_month'] = jump_month
                st.session_state['calendar_year'] = jump_year
                st.rerun()
    
    selected_month = st.session_state['calendar_month']
    selected_year = st.session_state['calendar_year']
    
    st.markdown("---")
    
    # Get events from database
    from data.medical_events import get_medical_events
    all_events = get_medical_events(user_id)
    
    # Filter events for selected month
    events_by_date = {}
    for event in all_events:
        event_date = event['event_date']
        if isinstance(event_date, datetime):
            if event_date.year == selected_year and event_date.month == selected_month:
                day = event_date.day
                if day not in events_by_date:
                    events_by_date[day] = []
                events_by_date[day].append(event)
    
    # Days of week header
    st.write("")
    days_header = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    cols = st.columns(7)
    for i, day in enumerate(days_header):
        with cols[i]:
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: #6b7280; padding: 8px;'>{day}</div>", unsafe_allow_html=True)
    
    # Get first day of month and number of days
    first_day, num_days = monthrange(selected_year, selected_month)
    
    # Calculate total cells needed (starting empty cells + days)
    total_cells = first_day + num_days
    rows_needed = (total_cells + 6) // 7  # Round up to nearest week
    
    # Render calendar grid
    current_day = 1
    for week in range(rows_needed):
        cols = st.columns(7)
        for day_of_week in range(7):
            cell_index = week * 7 + day_of_week
            
            with cols[day_of_week]:
                # Empty cell before month starts
                if cell_index < first_day:
                    st.markdown("<div style='height: 100px; border: 1px solid #e5e7eb; border-radius: 8px;'></div>", unsafe_allow_html=True)
                # Days of the month
                elif current_day <= num_days:
                    # Check if today
                    is_today = (current_day == today.day and selected_month == today.month and selected_year == today.year)
                    
                    # Get events for this day
                    day_events = events_by_date.get(current_day, [])
                    
                    # Build event indicators
                    event_dots = ""
                    if day_events:
                        # Show up to 3 colored dots for events
                        status_colors = {
                            "Routine": "#10b981",
                            "Urgent": "#ef4444",
                            "Follow-Up": "#f59e0b",
                            "Completed": "#6b7280"
                        }
                        for i, event in enumerate(day_events[:3]):
                            color = status_colors.get(event.get('status', 'Routine'), "#6b7280")
                            event_dots += f"<span style='width: 6px; height: 6px; background: {color}; border-radius: 50%; display: inline-block; margin: 0 1px;'></span>"
                        if len(day_events) > 3:
                            event_dots += f"<span style='font-size: 10px; color: #6b7280; margin-left: 2px;'>+{len(day_events) - 3}</span>"
                    
                    # Build cell
                    bg_color = "#dbeafe" if is_today else "#fff"
                    border_color = "#3b82f6" if is_today else "#e5e7eb"
                    
                    cell_html = f"""<div style='height: 100px; border: 2px solid {border_color}; border-radius: 8px; padding: 8px; background: {bg_color}; cursor: pointer;'>
<div style='font-weight: {"bold" if is_today else "normal"}; color: {"#1f2937" if day_events else "#9ca3af"}; margin-bottom: 4px;'>{current_day}</div>
<div style='min-height: 12px;'>{event_dots}</div>
</div>"""
                    st.markdown(cell_html, unsafe_allow_html=True)
                    
                    # Show event details below calendar if clicked
                    if day_events:
                        if st.button(f"View {len(day_events)} event(s)", key=f"day_{current_day}", use_container_width=True):
                            st.session_state[f'show_events_day_{current_day}'] = True
                    
                    current_day += 1
                # Empty cells after month ends
                else:
                    st.markdown("<div style='height: 100px; border: 1px solid #e5e7eb; border-radius: 8px;'></div>", unsafe_allow_html=True)
    
    # Show events for selected day
    st.markdown("---")
    selected_day_events = []
    for day, events in events_by_date.items():
        if st.session_state.get(f'show_events_day_{day}', False):
            selected_day_events = events
            st.markdown(f"### 📋 Events on {date(selected_year, selected_month, day).strftime('%B %d, %Y')}")
            
            if st.button("✖ Close", key=f"close_day_{day}"):
                st.session_state[f'show_events_day_{day}'] = False
                st.rerun()
            
            st.write("")
            
            # Render event cards
            from components.medical_event_card import render_medical_event_card
            for event in events:
                render_medical_event_card(event, user_id, key_prefix=f"calendar_day_{day}_")
            
            break
    
    if not selected_day_events and events_by_date:
        st.info(f"💡 Click on days with colored dots to view events. This month has {len(all_events)} total events.")
    elif not events_by_date:
        st.info(f"📭 No medical events in {date(selected_year, selected_month, 1).strftime('%B %Y')}.")
    
    # Add bottom padding
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

import streamlit as st
from datetime import datetime
from collections import defaultdict


def render_medical_timeline(user_id):
    """Render the medical timeline with events grouped by year and month."""
    
    # Header section
    st.markdown("## 📊 Medical Timeline")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Filter by event type:**")
    with col2:
        event_filter = st.selectbox(
            "Filter",
            ["🔍 All Events", "🩺 Procedures", "🏥 Hospital Stays", " Appointments", "🧪 Tests/Labs", "🔪 Surgeries"],
            label_visibility="collapsed"
        )
    
    st.info("💡 Click on any event card below to expand and view detailed information")
    st.markdown("---")
    
    # Get events from database
    from data.medical_events import get_medical_events
    all_events = get_medical_events(user_id)
    
    # Apply filter
    filter_map = {
        "🔍 All Events": None,
        "🩺 Procedures": "Procedure",
        "🏥 Hospital Stays": "Hospital Stay",
        " Appointments": "Appointment",
        "🧪 Tests/Labs": "Test/Lab",
        "🔪 Surgeries": "Surgery"
    }
    
    selected_filter = filter_map.get(event_filter)
    if selected_filter:
        events = [e for e in all_events if e['event_type'] == selected_filter]
    else:
        events = all_events
    
    if not events:
        st.info("📭 No medical events found. Click 'Add New Medical Event' below to create your first entry.")
    else:
        # Group events by year and month
        events_by_year = defaultdict(lambda: defaultdict(list))
        
        for event in events:
            event_date = event['event_date']
            year = event_date.strftime("%Y")
            month = event_date.strftime("%B").upper()
            
            # Add icon based on event type
            icon_map = {
                "Procedure": "🩺",
                "Hospital Stay": "🏥",
                "Appointment": "📋",
                "Test/Lab": "🧪",
                "Surgery": "🔪",
                "Other": "📝"
            }
            event['icon'] = icon_map.get(event['event_type'], "📝")
            
            events_by_year[year][month].append(event)
        
        # Render timeline
        from components.medical_event_card import render_medical_event_card
        
        for year in sorted(events_by_year.keys(), reverse=True):
            # Year header
            st.markdown(f"### 📅 {year}")
            
            months_order = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", 
                           "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
            
            # Get months that have events, in order
            available_months = [m for m in months_order if m in events_by_year[year]]
            
            for month in reversed(available_months):
                # Month header
                st.markdown(f"#### {month}")
                
                # Render each event
                for event in events_by_year[year][month]:
                    render_medical_event_card(event, user_id, key_prefix="timeline_")
                    st.write("")  # Spacing between cards
    
    # Add new event button
    st.markdown("---")
    if st.button("➕ Add New Medical Event", type="primary", use_container_width=True):
        st.session_state['show_add_event_form'] = True
        st.rerun()
    
    # Add bottom padding
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

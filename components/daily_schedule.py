import streamlit as st
from datetime import datetime, time
from data.medications import get_today_schedule, get_medication_by_id
from components.medication_card import render_enhanced_medication_card

def render_daily_schedule():
    """Render today's medication schedule organized by time periods."""
    
    # Get today's doses
    today_doses = get_today_schedule()
    
    # Initialize session state for daily doses tracking
    if 'daily_doses' not in st.session_state:
        st.session_state['daily_doses'] = {}
    
    # Update dose statuses from session state
    for dose in today_doses:
        if dose['id'] in st.session_state['daily_doses']:
            session_dose = st.session_state['daily_doses'][dose['id']]
            dose['status'] = session_dose['status']
            if session_dose.get('actual_time'):
                dose['actual_time'] = datetime.fromisoformat(session_dose['actual_time'])
    
    # Group doses by time periods
    time_periods = {
        'Morning (6 AM - 12 PM)': [],
        'Afternoon (12 PM - 6 PM)': [],
        'Evening (6 PM - 10 PM)': [],
        'Night (10 PM - 6 AM)': []
    }
    
    for dose in today_doses:
        scheduled_time = dose['scheduled_time']
        hour = scheduled_time.hour
        
        if 6 <= hour < 12:
            time_periods['Morning (6 AM - 12 PM)'].append(dose)
        elif 12 <= hour < 18:
            time_periods['Afternoon (12 PM - 6 PM)'].append(dose)
        elif 18 <= hour < 22:
            time_periods['Evening (6 PM - 10 PM)'].append(dose)
        else:
            time_periods['Night (10 PM - 6 AM)'].append(dose)
    
    # Render each time period
    for period_name, doses in time_periods.items():
        if doses:  # Only show periods with medications
            render_time_period(period_name, doses)


def render_time_period(period_name: str, doses: list):
    """Render a time period section with its medications."""
    
    # Get period styling
    period_info = get_period_styling(period_name)
    
    # Period header
    st.markdown(f"""
    <div style='background: {period_info['gradient']}; color: white; padding: 12px 16px; border-radius: 8px; margin: 16px 0 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 20px;'>{period_info['icon']}</span>
                <span style='font-weight: 700; font-size: 16px;'>{period_name}</span>
            </div>
            <div style='font-size: 12px; opacity: 0.9;'>{len(doses)} medication{'s' if len(doses) != 1 else ''}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
        # Render each dose in this period
    for dose in doses:
        medication = get_medication_by_id(dose['medication_id'])
        if medication:
            # Render medication card with inline time info (avoid nested columns)
            render_enhanced_medication_card(medication, dose_info=dose)
            
            # Show time info below the card
            render_dose_time_info(dose)
def render_dose_time_info(dose: dict):
    """Render time information for a specific dose."""
    
    scheduled_time = dose['scheduled_time']
    status = dose['status']
    
    # Time display
    time_str = scheduled_time.strftime('%I:%M %p')
    
    # Status-based styling
    if status == 'taken':
        bg_color = '#dcfce7'
        text_color = '#166534'
        icon = '✅'
    elif status == 'missed':
        bg_color = '#fef2f2'
        text_color = '#991b1b'
        icon = '❌'
    elif status == 'skipped':
        bg_color = '#fef3c7'
        text_color = '#92400e'
        icon = '⏭️'
    else:  # scheduled
        now = datetime.now()
        if scheduled_time > now:
            bg_color = '#f1f5f9'
            text_color = '#475569'
            icon = '⏰'
        else:
            bg_color = '#fef2f2'
            text_color = '#991b1b'
            icon = '⚠️'
    
    st.markdown(f"""
    <div style='background: {bg_color}; color: {text_color}; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px;'>
        <div style='font-size: 16px; margin-bottom: 4px;'>{icon}</div>
        <div style='font-weight: 600; font-size: 14px; margin-bottom: 2px;'>{time_str}</div>
        <div style='font-size: 11px; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.5px;'>{status}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show actual time if taken
    if status == 'taken' and dose.get('actual_time'):
        actual_time_str = dose['actual_time'].strftime('%I:%M %p')
        delay_minutes = int((dose['actual_time'] - scheduled_time).total_seconds() / 60)
        
        if delay_minutes > 0:
            st.markdown(f"""
            <div style='background: #f8fafc; color: #6b7280; padding: 6px; border-radius: 6px; text-align: center; font-size: 10px;'>
                Taken: {actual_time_str}<br>
                ({delay_minutes}m late)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background: #f0fdf4; color: #166534; padding: 6px; border-radius: 6px; text-align: center; font-size: 10px;'>
                Taken: {actual_time_str}<br>
                (On time!)
            </div>
            """, unsafe_allow_html=True)


def get_period_styling(period_name: str):
    """Get visual styling for different time periods."""
    
    if 'Morning' in period_name:
        return {
            'icon': '🌅',
            'gradient': 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
            'color': '#f59e0b'
        }
    elif 'Afternoon' in period_name:
        return {
            'icon': '☀️',
            'gradient': 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
            'color': '#3b82f6'
        }
    elif 'Evening' in period_name:
        return {
            'icon': '🌆',
            'gradient': 'linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%)',
            'color': '#7c3aed'
        }
    else:  # Night
        return {
            'icon': '🌙',
            'gradient': 'linear-gradient(135deg, #6b7280 0%, #374151 100%)',
            'color': '#6b7280'
        }


def get_today_summary():
    """Get summary statistics for today's medication schedule."""
    
    today_doses = get_today_schedule()
    
    # Update from session state
    if 'daily_doses' in st.session_state:
        for dose in today_doses:
            if dose['id'] in st.session_state['daily_doses']:
                dose['status'] = st.session_state['daily_doses'][dose['id']]['status']
    
    total_doses = len(today_doses)
    taken_doses = len([d for d in today_doses if d['status'] == 'taken'])
    missed_doses = len([d for d in today_doses if d['status'] == 'missed'])
    overdue_doses = len([d for d in today_doses if d['status'] == 'scheduled' and d['scheduled_time'] < datetime.now()])
    
    return {
        'total': total_doses,
        'taken': taken_doses,
        'missed': missed_doses,
        'overdue': overdue_doses,
        'remaining': total_doses - taken_doses - missed_doses,
        'completion_rate': round((taken_doses / total_doses * 100) if total_doses > 0 else 0, 1)
    }
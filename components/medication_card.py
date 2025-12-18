import streamlit as st
from datetime import datetime
from data.doctors import get_doctor_name

def render_enhanced_medication_card(medication: dict, dose_info: dict = None, expanded: bool = False):
    """Render enhanced medication card with rich details and actions."""
    
    # Get medication color and icon
    color = medication.get('color', '#6b7280')
    icon = medication.get('icon', '💊')
    
    # Determine status styling
    status_info = get_dose_status_info(dose_info) if dose_info else get_med_status_info(medication)
    status_color = status_info['color']
    status_text = status_info['text']
    status_icon = status_info['icon']
    
    # Doctor info
    doctor_name = get_doctor_name(medication.get('doctor_id'))
    
    # Main medication card
    st.markdown(f"""
    <div style='background: #ffffff; border-left: 4px solid {color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); transition: all 0.2s ease;'>
        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;'>
            <div style='flex: 1;'>
                <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                    <span style='font-size: 24px; margin-right: 12px;'>{icon}</span>
                    <div>
                        <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{medication['name']}</div>
                        <div style='color: #6b7280; font-size: 13px;'>{medication.get('brand_name', '')} • {medication['strength']} {medication['form']}</div>
                    </div>
                </div>
                <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>{medication['frequency']} • {medication.get('time_labels', [''])[0] if medication.get('time_labels') else ''}</div>
                <div style='color: #6b7280; font-size: 13px;'>👨‍⚕️ Dr. {doctor_name} • 🏪 {medication.get('pharmacy', 'N/A')}</div>
            </div>
            <div style='text-align: right;'>
                <div style='background: {status_color}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 8px; display: inline-flex; align-items: center; gap: 4px;'>
                    {status_icon} {status_text}
                </div>
                <div style='color: #6b7280; font-size: 12px;'>Adherence: {medication.get('adherence_rate', 0)}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons for dose tracking (if dose_info provided)
    if dose_info and dose_info['status'] == 'scheduled':
        render_dose_actions(dose_info, medication)
    
    # Expanded details section
    if expanded:
        render_medication_details(medication)


def render_dose_actions(dose_info: dict, medication: dict):
    """Render action buttons for taking/skipping doses."""
    
    # Use horizontal layout without nested columns
    if st.button("✅ Take", key=f"take_{dose_info['id']}", type="primary"):
        mark_dose_taken(dose_info['id'])
        st.success(f"✅ Marked {medication['name']} as taken!")
        st.experimental_rerun()
    
    if st.button("⏭️ Skip", key=f"skip_{dose_info['id']}", type="secondary"):
        mark_dose_skipped(dose_info['id'])
        st.warning(f"⏭️ Skipped {medication['name']}")
        st.experimental_rerun()
    
    # Show overdue warning if applicable
    if dose_info['scheduled_time'] < datetime.now():
        time_diff = datetime.now() - dose_info['scheduled_time']
        minutes_late = int(time_diff.total_seconds() / 60)
        if minutes_late > 0:
            st.markdown(f"<div style='color: #dc2626; font-size: 12px; padding: 8px 0;'>⚠️ {minutes_late} minutes overdue</div>", unsafe_allow_html=True)


def render_medication_details(medication: dict):
    """Render expanded medication details."""
    
    st.markdown(f"""
    <div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;'>
    """, unsafe_allow_html=True)
    
    # Medication information tabs
    tab1, tab2, tab3 = st.tabs(["📋 Details", "⚠️ Side Effects", "📊 Adherence"])
    
    with tab1:
        # Display prescription info without nested columns
        st.markdown("**Prescription Info:**")
        st.markdown(f"• **Prescribed:** {medication.get('prescribed_date', 'N/A')}")
        st.markdown(f"• **Prescription #:** {medication.get('prescription_number', 'N/A')}")
        st.markdown(f"• **Refills Left:** {medication.get('refills_remaining', 0)}")
        st.markdown(f"• **Next Refill:** {medication.get('next_refill_date', 'N/A')}")
        
        st.markdown("**Instructions:**")
        st.markdown(f"• **Frequency:** {medication.get('frequency', 'N/A')}")
        st.markdown(f"• **Duration:** {medication.get('duration', 'N/A')}")
        st.markdown(f"• **Special Instructions:** {medication.get('instructions', 'N/A')}")
        
        if medication.get('notes'):
            st.markdown(f"**Clinical Notes:** {medication['notes']}")
    
    with tab2:
        if medication.get('side_effects_to_watch'):
            st.markdown("**Side Effects to Monitor:**")
            for effect in medication['side_effects_to_watch']:
                st.markdown(f"• {effect.title()}")
        
        if medication.get('interactions'):
            st.markdown("**Drug Interactions & Warnings:**")
            for interaction in medication['interactions']:
                st.markdown(f"• {interaction}")
        
        st.info("💡 Report any side effects using the Side Effects page or contact your healthcare provider.")
    
    with tab3:
        # Adherence statistics without nested columns
        adherence_rate = medication.get('adherence_rate', 0)
        total_doses = medication.get('total_doses', 0)
        missed_doses = medication.get('missed_doses', 0)
        
        # Display stats in a single layout
        st.markdown(f"""
        <div style='display: flex; gap: 8px; margin-bottom: 16px;'>
            <div style='flex: 1; text-align: center; padding: 12px; background: {"#10b981" if adherence_rate >= 80 else "#f59e0b" if adherence_rate >= 60 else "#ef4444"}; color: white; border-radius: 8px;'>
                <div style='font-size: 20px; font-weight: 700;'>{adherence_rate}%</div>
                <div style='font-size: 11px; opacity: 0.9;'>Adherence</div>
            </div>
            <div style='flex: 1; text-align: center; padding: 12px; background: #3b82f6; color: white; border-radius: 8px;'>
                <div style='font-size: 20px; font-weight: 700;'>{total_doses}</div>
                <div style='font-size: 11px; opacity: 0.9;'>Total Doses</div>
            </div>
            <div style='flex: 1; text-align: center; padding: 12px; background: #dc2626; color: white; border-radius: 8px;'>
                <div style='font-size: 20px; font-weight: 700;'>{missed_doses}</div>
                <div style='font-size: 11px; opacity: 0.9;'>Missed</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Adherence progress bar
        st.markdown("**Adherence Trend:**")
        progress = adherence_rate / 100
        st.progress(progress)
        
        if adherence_rate < 80:
            st.warning("⚠️ Consider setting medication reminders to improve adherence.")
        elif adherence_rate >= 95:
            st.success("🎉 Excellent medication adherence! Keep it up!")
    
    st.markdown("</div>", unsafe_allow_html=True)


def get_dose_status_info(dose_info: dict):
    """Get status information for a specific dose."""
    status = dose_info['status']
    
    if status == 'taken':
        return {'color': '#10b981', 'text': 'Taken', 'icon': '✅'}
    elif status == 'missed':
        return {'color': '#ef4444', 'text': 'Missed', 'icon': '❌'}
    elif status == 'skipped':
        return {'color': '#f59e0b', 'text': 'Skipped', 'icon': '⏭️'}
    else:  # scheduled
        now = datetime.now()
        scheduled_time = dose_info['scheduled_time']
        
        if scheduled_time > now:
            return {'color': '#6b7280', 'text': 'Scheduled', 'icon': '⏰'}
        else:
            return {'color': '#dc2626', 'text': 'Overdue', 'icon': '⚠️'}


def get_med_status_info(medication: dict):
    """Get general status information for a medication."""
    status = medication.get('status', 'active')
    
    if status == 'active':
        return {'color': '#10b981', 'text': 'Active', 'icon': '🟢'}
    elif status == 'paused':
        return {'color': '#f59e0b', 'text': 'Paused', 'icon': '⏸️'}
    elif status == 'discontinued':
        return {'color': '#6b7280', 'text': 'Stopped', 'icon': '🛑'}
    else:
        return {'color': '#6b7280', 'text': 'Unknown', 'icon': '❓'}


def mark_dose_taken(dose_id: str):
    """Mark a dose as taken in session state."""
    if 'daily_doses' not in st.session_state:
        st.session_state['daily_doses'] = {}
    
    st.session_state['daily_doses'][dose_id] = {
        'status': 'taken',
        'actual_time': datetime.now().isoformat(),
        'notes': ''
    }


def mark_dose_skipped(dose_id: str):
    """Mark a dose as skipped in session state."""
    if 'daily_doses' not in st.session_state:
        st.session_state['daily_doses'] = {}
    
    st.session_state['daily_doses'][dose_id] = {
        'status': 'skipped',
        'actual_time': datetime.now().isoformat(),
        'notes': 'User skipped'
    }
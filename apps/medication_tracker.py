import streamlit as st
from hydralit import HydraHeadApp
from datetime import date, datetime

from data.medications import get_enhanced_medications, get_adherence_stats
from components.daily_schedule import render_daily_schedule, get_today_summary
from components.medication_card import render_enhanced_medication_card
from data.patient_profile import get_patient_profile

class MedicationTracker(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        # Load global styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass

        st.title("💊 Medication Tracker")
        
        # Initialize session state
        if 'medication_expanded' not in st.session_state:
            st.session_state['medication_expanded'] = {}
        if 'daily_doses' not in st.session_state:
            st.session_state['daily_doses'] = {}

        # Get data
        patient = get_patient_profile()
        medications = get_enhanced_medications()
        adherence_stats = get_adherence_stats()
        today_summary = get_today_summary()

        # Header with patient info and today's summary
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='font-size: 24px; font-weight: 700; margin-bottom: 4px;'>Today's Medications</div>
                    <div style='font-size: 16px; opacity: 0.9;'>{patient['name']} • {datetime.now().strftime('%A, %B %d, %Y')}</div>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 20px; font-weight: 700;'>{today_summary['taken']}/{today_summary['total']} taken</div>
                    <div style='font-size: 14px; opacity: 0.9;'>{today_summary['completion_rate']}% complete</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            remaining = today_summary['remaining']
            color = '#10b981' if remaining == 0 else '#f59e0b' if remaining <= 2 else '#dc2626'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{remaining}</div>
                <div style='color: #6b7280; font-size: 14px;'>Remaining Today</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            overdue = today_summary['overdue']
            color = '#dc2626' if overdue > 0 else '#6b7280'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{overdue}</div>
                <div style='color: #6b7280; font-size: 14px;'>Overdue</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            overall_rate = adherence_stats['overall_rate']
            color = '#10b981' if overall_rate >= 80 else '#f59e0b' if overall_rate >= 60 else '#dc2626'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2p 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{overall_rate}%</div>
                <div style='color: #6b7280; font-size: 14px;'>Overall Adherence</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            active_meds = len([m for m in medications if m['status'] == 'active'])
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: #3b82f6;'>{active_meds}</div>
                <div style='color: #6b7280; font-size: 14px;'>Active Medications</div>
            </div>
            """, unsafe_allow_html=True)

        # Main layout: Daily schedule on left, medication library on right
        col_main, col_sidebar = st.columns([2, 1])

        with col_main:
            st.subheader("📅 Today's Schedule")
            
            if today_summary['total'] == 0:
                st.info("🎉 No medications scheduled for today!")
            else:
                render_daily_schedule()

        with col_sidebar:
            st.subheader("💊 Medication Library")
            
            # Filter options
            status_filter = st.selectbox(
                "Filter by status:",
                options=['All', 'Active', 'Paused', 'Discontinued'],
                index=1  # Default to 'Active'
            )
            
            # Filter medications
            if status_filter == 'All':
                filtered_meds = medications
            else:
                filtered_meds = [m for m in medications if m['status'].lower() == status_filter.lower()]
            
            # Display medications
            for medication in filtered_meds:
                med_id = medication['id']
                expanded = st.session_state['medication_expanded'].get(med_id, False)
                
                # Medication summary card
                render_enhanced_medication_card(medication, expanded=False)
                
                # Expand/collapse button
                if st.button(
                    "📖 Details" if not expanded else "📕 Hide Details",
                    key=f"expand_med_{med_id}",
                    help="View medication details"
                ):
                    st.session_state['medication_expanded'][med_id] = not expanded
                    st.experimental_rerun()
                
                # Show expanded details
                if expanded:
                    render_enhanced_medication_card(medication, expanded=True)

        # Adherence insights section
        if today_summary['total'] > 0:
            st.divider()
            st.subheader("📊 Adherence Insights")
            
            # Today's progress
            progress = today_summary['completion_rate'] / 100
            st.markdown("**Today's Progress:**")
            st.progress(progress)
            st.markdown(f"{today_summary['taken']} of {today_summary['total']} medications taken ({today_summary['completion_rate']}%)")
            
            if today_summary['overdue'] > 0:
                st.warning(f"⚠️ {today_summary['overdue']} medication(s) are overdue")
            elif today_summary['remaining'] == 0:
                st.success("🎉 All medications taken for today!")
            elif today_summary['remaining'] > 0:
                st.info(f"⏰ {today_summary['remaining']} medication(s) remaining today")

            # Overall adherence stats
            st.markdown("**Overall Statistics:**")
            st.markdown(f"• **Total doses prescribed:** {adherence_stats['total_doses']}")
            st.markdown(f"• **Doses taken:** {adherence_stats['taken_doses']}")
            st.markdown(f"• **Doses missed:** {adherence_stats['missed_doses']}")
            st.markdown(f"• **Overall adherence:** {adherence_stats['overall_rate']}%")
            
            if adherence_stats['overall_rate'] >= 95:
                st.success("🏆 Excellent medication adherence!")
            elif adherence_stats['overall_rate'] >= 80:
                st.info("👍 Good medication adherence")
            else:
                st.warning("⚠️ Consider medication reminders to improve adherence")

        return
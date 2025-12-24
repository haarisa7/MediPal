import streamlit as st
from hydralit import HydraHeadApp
from datetime import date, datetime
from data.doctors import get_all_doctors, get_doctor_name
from data.patient_medications import (
    insert_patient_medication,
    get_daily_patient_medications,
    get_all_patient_medications,
    get_active_patient_medications,
    get_inactive_patient_medications
)

from components.medication_card import render_medication_card
from data.patient_profile import get_patient_profile
from data.medication_log import log_missed_intakes_for_day, get_today_intake_status
from data.adherence_stats import (
    get_today_summary_for_user,
    get_total_adherence_for_user,
    get_adherence_for_patient_med_id,
    get_overall_adherence_for_med_id
)
from components.medication_library import show_medication_library
from components.daily_schedule import render_daily_medication_schedule

class MedicationTracker(HydraHeadApp):
    def _resolve_user_id(self):
        cur = st.session_state.get('current_id')
        if cur is None:
            return None
        # If it's already an int, return as is
        if isinstance(cur, int):
            return cur
        # If it's a string that looks like an int, convert
        if isinstance(cur, str):
            try:
                return int(cur)
            except Exception:
                return None
        return None

    def _resolve_patient_id(self):
        from data.patient_profile import get_user_role
        user_id = st.session_state.get('current_id')
        role = get_user_role(user_id) if user_id else None
        if role == 1:
            # Clinician: use patient_id from session
            return st.session_state.get('authorized_patient_id')
        else:
            # Patient: use their own user_id
            return user_id

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        patient_id = self._resolve_patient_id()
        if not patient_id:
            st.title("💊 Medication Tracker")
            st.warning("No patient selected. Clinicians must authorize a patient in Home tab.")
            return

        # Show DB error if present
        if st.session_state.get('db_insert_error'):
            st.error(f"Database Error: {st.session_state['db_insert_error']}")
            st.session_state['db_insert_error'] = None

        # --- Edit medication UI (overlay component) ---
        from components.edit_medication import show_edit_medication_overlay
        if st.session_state.get('show_edit_med'):
            show_edit_medication_overlay(patient_id)
            return

        # Load global styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass

        # --- Add/Edit medication buttons in header ---
        from components.add_medication_modal import show_add_medication_overlay
        
        col_title, col_btn1, col_btn2 = st.columns([2.5, 1, 1])
        with col_title:
            st.title("💊 Medication Tracker")
        with col_btn1:
            if st.button('➕ Add Medication', key='add_med_btn', use_container_width=True):
                st.session_state['show_add_med'] = True
                st.rerun()
        with col_btn2:
            if st.button('✏️ Edit Medication', key='edit_med_btn', use_container_width=True):
                st.session_state['show_edit_med'] = True
                st.rerun()
        
        # Handle overlays
        if st.session_state.get('show_add_med'):
            show_add_medication_overlay(self._resolve_user_id)
            return

        # Initialize session state
        if 'medication_expanded' not in st.session_state:
            st.session_state['medication_expanded'] = {}
        if 'daily_doses' not in st.session_state:
            st.session_state['daily_doses'] = {}

        # Get data
        patient_id = self._resolve_patient_id()
        if not patient_id:
            st.warning("No patient selected. Clinicians must authorize a patient in Home tab.")
            return
        patient = get_patient_profile(patient_id)
        today_summary = get_today_summary_for_user(patient_id)

        # Header with patient info and today's summary
        first_name = patient.get('first_name', '') if patient else ''
        last_name = patient.get('last_name', '') if patient else ''
        today_str = datetime.now().strftime('%A, %B %d, %Y')
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='font-size: 24px; font-weight: 700; margin-bottom: 4px;'>Today's Medications</div>
                    <div style='font-size: 16px; opacity: 0.9;'>{first_name} {last_name} • {today_str}</div>
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
            user_id = self._resolve_user_id()
            total_adherence = get_total_adherence_for_user(user_id)
            color = '#10b981' if (total_adherence or 0) >= 80 else '#f59e0b' if (total_adherence or 0) >= 60 else '#dc2626'
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid {color}; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2p 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: {color};'>{total_adherence if total_adherence is not None else '--'}%</div>
                <div style='color: #6b7280; font-size: 14px;'>Total Patient Adherence</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div style='background: #ffffff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; font-weight: 700; color: #3b82f6;'>{today_summary['active_meds']}</div>
                <div style='color: #6b7280; font-size: 14px;'>Active Medications</div>
            </div>
            """, unsafe_allow_html=True)

        # Main layout: Daily schedule on left, medication library on right
        col_main, col_sidebar = st.columns([2, 1])

        with col_main:
            render_daily_medication_schedule(patient_id)
        with col_sidebar:
            show_medication_library(patient_id)
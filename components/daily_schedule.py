import streamlit as st
from data.patient_medications import (
    get_daily_patient_medications,
)
from data.medications import get_drug_display_name
from data.adherence_stats import (
    get_today_intake_status,
    get_adherence_for_patient_med_id
)
from components.medication_card import render_medication_card 

def render_daily_medication_schedule(user_id):
    st.subheader("📅 Today's Schedule")
    daily_meds = get_daily_patient_medications(user_id)
    periods = [
        ("Morning", "🌅", "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)"),
        ("Afternoon", "☀️", "linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)"),
        ("Evening", "🌆", "linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%)")
    ]
    # Group meds by timing
    meds_by_period = {p[0]: [] for p in periods}
    for med in daily_meds:
        timing = med['timing']
        meds_by_period[timing].append(med)

    for period, icon, gradient in periods:
        meds = meds_by_period[period]
        st.markdown(f"""
        <div style='background: {gradient}; color: white; padding: 12px 16px; border-radius: 8px; margin: 16px 0 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 20px;'>{icon}</span>
                <span style='font-weight: 700; font-size: 16px;'>{period}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if not meds:
            st.info(f"No {period.lower()} medications scheduled!")
        else:
            for med in meds:
                drug_name = get_drug_display_name(med['drug_id'])
                medication = {
                    'drug_name': drug_name,
                    'dose': med.get('dose', ''),
                    'instructions': med.get('instructions', ''),
                    'prescribed_by': med.get('prescribed_by', ''),
                    'timing': med.get('timing', ''),
                }
                status = get_today_intake_status(med['id'])
                adherence_rate = get_adherence_for_patient_med_id(med['id'])
                render_medication_card(medication, med['id'], status=status, context='schedule', adherence_rate=adherence_rate)

import streamlit as st
from data.medication_tracker.patient_medications import (
    get_all_patient_medications,
    get_active_patient_medications,
    get_inactive_patient_medications
)
from data.medication_tracker.adherence_stats import get_adherence_for_drug_and_user
from components.medication_tracker.medication_card import render_medication_card
from utils.medication_helpers import build_medication_dict


def show_medication_library(user_id):
    st.subheader("💊 Medication Library")
    status_filter = st.selectbox(
        "Filter by status:",
        options=['All', 'Active', 'Not Active'],
        index=1  # Default to 'Active'
    )

    # Get medications based on filter
    if status_filter == 'All':
        meds = get_all_patient_medications(user_id)
    elif status_filter == 'Active':
        meds = get_active_patient_medications(user_id)
    else:  # Not Active
        meds = get_inactive_patient_medications(user_id)

    for med in meds:
        medication = build_medication_dict(med)
        adherence_rate = get_adherence_for_drug_and_user(med['drug_id'], user_id)
        active = med.get('status', 'active') == 'active'
        render_medication_card(medication, med['id'], status=None, context='library', adherence_rate=adherence_rate, active=active)

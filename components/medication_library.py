import streamlit as st
from data.medications import get_drug_display_name
from data.patient_medications import (
    get_all_patient_medications,
    get_active_patient_medications,
    get_inactive_patient_medications
)
from data.adherence_stats import get_overall_adherence_for_med_id
from components.medication_card import render_medication_card

def show_medication_library(user_id):
    st.subheader("💊 Medication Library")
    status_filter = st.selectbox(
        "Filter by status:",
        options=['All', 'Active', 'Not Active'],
        index=1  # Default to 'Active'
    )

    if status_filter == 'All':
        meds = get_all_patient_medications(user_id)
    elif status_filter == 'Active':
        meds = get_active_patient_medications(user_id)
    else:  # Not Active
        meds = get_inactive_patient_medications(user_id)

    for med in meds:
        drug_name = get_drug_display_name(med['drug_id'])
        medication = {
            'drug_name': drug_name,
            'dose': med.get('dose', ''),
            'instructions': med.get('instructions', ''),
            'prescribed_by': med.get('prescribed_by', ''),
        }
        adherence_rate = get_overall_adherence_for_med_id(med['drug_id'])
        active = med.get('status', 'active') == 'active'
        render_medication_card(medication, med['id'], status=None, context='library', adherence_rate=adherence_rate, active=active)

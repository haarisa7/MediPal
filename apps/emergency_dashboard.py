import streamlit as st
from hydralit import HydraHeadApp
from data.patient_profile import get_patient_profile, get_user_role


class EmergencyDashboard(HydraHeadApp):
    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
    
    def _resolve_user_id(self):
        cur = st.session_state.get('current_id')
        if cur is None:
            return None
        if isinstance(cur, int):
            return cur
        if isinstance(cur, str):
            try:
                return int(cur)
            except Exception:
                return None
        return None

    def _resolve_patient_id(self):
        user_id = st.session_state.get('current_id')
        role = get_user_role(user_id) if user_id else None
        if role == 1:
            return st.session_state.get('authorized_patient_id')
        return user_id

    def run(self):
        # Load styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass

        user_id = self._resolve_user_id()
        patient_id = self._resolve_patient_id()
        is_clinician = get_user_role(user_id) == 1 if user_id else False
        
        if not patient_id:
            st.warning('No patient selected.')
            return

        # Get patient profile
        profile = get_patient_profile(patient_id)
        if not profile:
            st.error('Patient profile not found.')
            return

        # Emergency header
        from components.emergency_header import render_emergency_header
        info_complete = render_emergency_header(profile, patient_id)
        
        # Only show rest of dashboard if patient info is complete
        if not info_complete:
            if is_clinician:
                st.info("📋 Patient has not completed their medical information form yet.")
            return

        # Layout: 2 columns
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 💊 Current Medications")
            from data.patient_medications import get_active_patient_medications
            from data.medications import get_drug_display_name
            from components.medication_card import _get_medication_icon
            meds = get_active_patient_medications(patient_id)
            if meds:
                for med in meds:
                    drug_id = med.get('drug_id')
                    drug_name = get_drug_display_name(drug_id).title() if drug_id else 'Unknown'
                    dose = med.get('dose', '')
                    timing = med.get('timing', '')
                    prescribed_by = med.get('prescribed_by', '')
                    instructions = med.get('instructions', '')
                    
                    # Get appropriate icon based on dose type
                    icon = _get_medication_icon(dose)
                    
                    dose_time = f"<b>Dose:</b> {dose}" + (f" | <b>Times:</b> {timing}" if timing else "")
                    doctor_info = f"<b>Doctor:</b> {prescribed_by}" if prescribed_by else ""
                    instruction_text = f"<div style='color: #059669; font-size: 12px; margin-top: 4px;'>{instructions}</div>" if instructions else ""
                    
                    st.markdown(f"""
                    <div style='background: #fff; border-left: 4px solid #10b981; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                        <div style='font-weight: 600; font-size: 15px; color: #1f2937; margin-bottom: 6px;'>{icon} {drug_name}</div>
                        <div style='color: #4b5563; font-size: 12px; margin-bottom: 2px;'>{dose_time}</div>
                        {f"<div style='color: #6b7280; font-size: 12px;'>{doctor_info}</div>" if doctor_info else ""}
                        {instruction_text}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active medications")

            st.markdown("---")
            st.markdown("### 🚨 Medical Alerts & Allergies")
            from components.allergy_card import render_allergy_cards
            render_allergy_cards(patient_id, is_clinician)

        with col2:
            st.markdown("### 🏥 Medical Conditions")
            from components.condition_card import render_condition_cards
            render_condition_cards(patient_id, is_clinician)

            st.markdown("---")
            st.markdown("### 📞 Emergency Contacts")
            from components.emergency_contact_card import render_emergency_contact_cards
            render_emergency_contact_cards(patient_id, is_clinician)

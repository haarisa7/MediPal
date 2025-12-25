import streamlit as st
from datetime import datetime
from data.patient_info import get_patient_info, upsert_patient_info
from data.patient_allergies import get_patient_allergies


def _convert_height_to_display(height_cm):
    """Convert height in cm to feet and inches."""
    if not height_cm:
        return ''
    total_inches = float(height_cm) / 2.54
    feet = int(total_inches // 12)
    inches = int(total_inches % 12)
    return f"{feet}'{inches}\""


def _convert_weight_to_display(weight_kg):
    """Convert weight in kg to lbs."""
    if not weight_kg:
        return ''
    lbs = float(weight_kg) * 2.20462
    return f"{int(lbs)} lbs"


def _render_info_form(patient_id):
    """Render form to add/update patient info."""
    st.warning("⚠️ Please update your medical information to enable the Emergency Dashboard")
    
    # Unit selectors outside form for reactivity
    col_unit1, col_unit2 = st.columns(2)
    with col_unit1:
        weight_unit = st.radio("Select Weight Unit", ['kg', 'lbs'], horizontal=True, key="weight_unit_selector")
    with col_unit2:
        height_unit = st.radio("Select Height Unit", ['cm', 'ft/in'], horizontal=True, key="height_unit_selector")
    
    with st.form("patient_info_form", clear_on_submit=False):
        st.markdown("### 📋 Complete Your Medical Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            blood_type = st.selectbox("Blood Type", ['', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
            if weight_unit == 'kg':
                weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=0.1, key="weight_kg_input")
                weight_lbs = 0
            else:
                weight_lbs = st.number_input("Weight (lbs)", min_value=0.0, step=0.1, key="weight_lbs_input")
                weight_kg = 0
        with col2:
            if height_unit == 'cm':
                height_cm = st.number_input("Height (cm)", min_value=0.0, step=0.1, key="height_cm_input")
                feet = 0
                inches = 0
            else:
                height_col1, height_col2 = st.columns(2)
                with height_col1:
                    feet = st.number_input("Feet", min_value=0, max_value=8, step=1, key="height_feet_input")
                with height_col2:
                    inches = st.number_input("Inches", min_value=0, max_value=11, step=1, key="height_inches_input")
                height_cm = 0
        
        notes = st.text_area("Additional Notes (optional)", height=80)
        
        submitted = st.form_submit_button("✅ Save Information", type="primary", use_container_width=True)
        
        if submitted:
            # Calculate final weight in kg based on unit selected
            if weight_unit == 'lbs':
                final_weight_kg = weight_lbs * 0.453592
            else:
                final_weight_kg = weight_kg
            
            # Calculate final height in cm based on unit selected
            if height_unit == 'ft/in':
                total_inches = (feet * 12) + inches
                final_height_cm = total_inches * 2.54
            else:
                final_height_cm = height_cm
            
            if not blood_type or final_weight_kg == 0 or final_height_cm == 0:
                st.error("Blood type, weight, and height are required!")
            else:
                if upsert_patient_info(patient_id, blood_type, final_weight_kg, final_height_cm, notes):
                    st.success("✅ Medical information saved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save information. Please try again.")


def render_emergency_header(profile, patient_id):
    """Render emergency medical information header."""
    first_name = profile.get('first_name', '')
    last_name = profile.get('last_name', '')
    dob = profile.get('date_of_birth', '')
    
    # Calculate age if DOB exists
    age = ''
    if dob:
        try:
            birth_date = datetime.strptime(str(dob), '%Y-%m-%d') if isinstance(dob, str) else dob
            age = f"{(datetime.now() - birth_date).days // 365} years"
        except Exception:
            pass
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(220,38,38,0.2);'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <div style='font-size: 12px; font-weight: 600; letter-spacing: 1px; opacity: 0.9; margin-bottom: 8px;'>🚨 EMERGENCY MEDICAL INFORMATION 🚨</div>
                <div style='font-size: 28px; font-weight: 700; margin-bottom: 4px;'>{first_name} {last_name}</div>
                <div style='font-size: 16px; opacity: 0.9;'>Access critical patient data for emergency responders</div>
            </div>
            <div style='text-align: right; background: rgba(255,255,255,0.15); padding: 16px; border-radius: 8px;'>
                <div style='font-size: 14px; opacity: 0.9; margin-bottom: 4px;'>Date of Birth</div>
                <div style='font-size: 18px; font-weight: 700;'>{dob}</div>
                <div style='font-size: 13px; opacity: 0.9; margin-top: 4px;'>{age}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get patient info from database
    patient_info = get_patient_info(patient_id)
    
    # Check if all required fields exist
    if not patient_info or not patient_info.get('blood_type') or not patient_info.get('weight_kg') or not patient_info.get('height_cm'):
        _render_info_form(patient_id)
        return False
    
    # Display patient info
    blood_type = patient_info.get('blood_type', 'N/A')
    weight_kg = patient_info.get('weight_kg')
    weight_lbs = int(float(weight_kg) * 2.20462) if weight_kg else 0
    height_display = _convert_height_to_display(patient_info.get('height_cm'))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background: #fff; border-left: 4px solid #dc2626; padding: 16px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 12px; color: #6b7280; font-weight: 600; margin-bottom: 4px;'>BLOOD TYPE</div>
            <div style='font-size: 24px; font-weight: 700; color: #dc2626;'>{blood_type}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: #fff; border-left: 4px solid #2563eb; padding: 16px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 12px; color: #6b7280; font-weight: 600; margin-bottom: 4px;'>WEIGHT</div>
            <div style='font-size: 24px; font-weight: 700; color: #2563eb;'>{int(float(weight_kg))} kg</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: #fff; border-left: 4px solid #059669; padding: 16px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 12px; color: #6b7280; font-weight: 600; margin-bottom: 4px;'>HEIGHT</div>
            <div style='font-size: 24px; font-weight: 700; color: #059669;'>{height_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display critical allergies
    allergies = get_patient_allergies(patient_id)
    critical_allergies = [a for a in allergies if a.get('severity') == 'CRITICAL']
    
    if critical_allergies:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        for allergy in critical_allergies:
            substance = allergy.get('substance', 'Unknown')
            st.markdown(f"""
            <div style='background: #fef2f2; border: 2px solid #dc2626; border-radius: 8px; padding: 12px; margin-bottom: 8px;'>
                <div style='display: flex; align-items: center; justify-content: center; gap: 8px;'>
                    <span style='font-size: 18px;'>⚠️</span>
                    <span style='font-weight: 700; color: #991b1b; font-size: 14px;'>ALLERGY: {substance}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    return True

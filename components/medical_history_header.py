import streamlit as st
from datetime import datetime


def render_medical_history_header(user_id):
    """Render the medical history header with patient info and summary statistics."""
    
    # Get patient info
    from data.patient_profile import get_patient_profile
    patient = get_patient_profile(user_id)
    
    if not patient:
        st.error("Unable to load patient information.")
        return
    
    # Get real data from database
    from data.medical_events import get_event_counts, get_date_range
    
    counts = get_event_counts(user_id)
    total_events = counts['total']
    procedures = counts['procedures']
    hospital_stays = counts['hospital_stays']
    successful_events = counts['success']
    
    # Calculate date range
    start_date_obj, end_date_obj = get_date_range(user_id)
    if start_date_obj:
        start_date = start_date_obj.strftime("%Y-%m-%d")
    else:
        start_date = "No events yet"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Header banner with patient name
    full_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 10px; 
                color: white; 
                text-align: center;
                margin-bottom: 2rem;'>
        <h2 style='margin: 0; color: white;'>Medical History Timeline for {full_name}</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Complete medical record from {start_date} to present</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary statistics in 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;'>
            <h1 style='color: #28a745; margin: 0; font-size: 2.5rem;'>{total_events}</h1>
            <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Total Events</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #dc3545;'>
            <h1 style='color: #dc3545; margin: 0; font-size: 2.5rem;'>{procedures}</h1>
            <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Procedures</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #ffc107;'>
            <h1 style='color: #ffc107; margin: 0; font-size: 2.5rem;'>{hospital_stays}</h1>
            <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Hospital Stays</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;'>
            <h1 style='color: #667eea; margin: 0; font-size: 2.5rem;'>{successful_events}</h1>
            <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Successful</p>
        </div>
        """, unsafe_allow_html=True)

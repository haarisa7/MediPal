import streamlit as st
from data.patient_medications import (
    get_active_patient_medications,
)
from data.medications import get_drug_display_name

from data.side_effect import get_sideeffects_by_rarity
from components.medication_card import render_medication_card
from components.side_effect_card import render_side_effect_card 



def render_patient_side_effect_cards(patient_id):
    """Render side effect cards for all active patient medications with real data."""
    st.subheader("💊 Medication Side Effect Profiles")
    st.info("💡 Click on any medication to view comprehensive side effect information, management advice, and report symptoms.")
    
    # Get active medications for patient
    active_medications = get_active_patient_medications(patient_id)
    
    if not active_medications:
        st.info("No active medications found for this patient.")
        return
    
    # Initialize session state for expansion tracking
    if 'side_effects_expanded' not in st.session_state:
        st.session_state['side_effects_expanded'] = {}
    
    for med in active_medications:
        drug_id = med['drug_id']
        drug_name = get_drug_display_name(drug_id)
        
        # Fetch side effects by rarity
        common_effects = get_sideeffects_by_rarity(drug_id, 'common')
        uncommon_effects = get_sideeffects_by_rarity(drug_id, 'uncommon')
        rare_effects = get_sideeffects_by_rarity(drug_id, 'rare')
        
        # Prepare medication data for side effect card
        medication_data = {
            'id': drug_id,
            'name': drug_name,
            'brand_name': '',  # Can be added later if available
            'category': 'Medication',
            'summary': med.get('instructions', 'Follow prescriber instructions'),
            'dose': med.get('dose', ''),
            'instructions': med.get('instructions', ''),
            'prescribed_by': med.get('prescribed_by', ''),
            'common_side_effects': common_effects,
            'uncommon_side_effects': uncommon_effects,
            'rare_effects': rare_effects,
            'icon': '💊',
            'color': '#ef4444',
        }
        
        # Check if this medication is expanded
        expanded = st.session_state['side_effects_expanded'].get(drug_id, False)
        
        # Render the side effect card
        clicked = render_side_effect_card(
            medication_data,
            expanded=expanded,
            button_key=f"medication_{drug_id}"
        )
        
        # Toggle expansion if clicked
        if clicked:
            st.session_state['side_effects_expanded'][drug_id] = not expanded
            st.experimental_rerun()

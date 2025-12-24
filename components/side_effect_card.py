import streamlit as st

from data.doctors import get_all_doctors, get_doctor_name
from data.side_effect import get_all_sideeffects_for_drug


def render_side_effect_card(drug: dict, expanded: bool = False, button_key: str = "card"):
    """Render a medication side effect card with drug name, dose, instructions, and side effect counts."""
    
    # Get medication styling
    color = drug.get('color', '#6b7280')
    icon = drug.get('icon', '💊')
    dose = drug.get('dose', '')
    instructions = drug.get('instructions', '')
    prescribed_by = drug.get('prescribed_by', '')
    
    # Count side effects
    common_count = len(drug.get('common_side_effects', []))
    uncommon_count = len(drug.get('uncommon_side_effects', []))
    rare_count = len(drug.get('rare_effects', []))
    
    # Main medication card
    st.markdown(f"""
    <div style='background: #ffffff; border-left: 4px solid {color}; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);'>
        <div style='display: flex; align-items: center; margin-bottom: 8px;'>
            <span style='font-size: 28px; margin-right: 12px;'>{icon}</span>
            <div>
                <div style='font-weight: 700; font-size: 20px; color: #1f2937;'>{drug['name']}</div>
                <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
            </div>
        </div>
        <div style='color: #4b5563; font-size: 14px; margin-bottom: 12px;'>{instructions}</div>
        <div style='color: #6b7280; font-size: 13px; margin-bottom: 12px;'><strong>Prescribed By:</strong> {prescribed_by}</div>
        <div style='display: flex; gap: 8px; flex-wrap: wrap;'>
            <div style='background: #dbeafe; color: #1e40af; padding: 6px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;'>
                {common_count} Common Effects
            </div>
            <div style='background: #fef3c7; color: #92400e; padding: 6px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;'>
                {uncommon_count} Uncommon Effects
            </div>
            <div style='background: #fef2f2; color: #991b1b; padding: 6px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;'>
                {rare_count} Rare Effects
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # View details button
    clicked = st.button(f"📋 View Side Effect Details", key=button_key, help=f"View comprehensive side effect information for {drug['name']}")

    # Expanded content with side effect details
    if expanded:
        render_enhanced_side_effect_content(drug)

    return clicked


def render_enhanced_side_effect_content(drug: dict):
    """Render comprehensive side effect information with medical context."""
    
    # Action buttons for different sections
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Common", key=f"common_{drug['id']}", use_container_width=True):
            st.session_state[f"side_effect_tab_{drug['id']}"] = "common"
    
    with col2:
        if st.button("⚠️ Uncommon", key=f"uncommon_{drug['id']}", use_container_width=True):
            st.session_state[f"side_effect_tab_{drug['id']}"] = "uncommon"
    
    with col3:
        if st.button("🚨 Rare", key=f"rare_{drug['id']}", use_container_width=True):
            st.session_state[f"side_effect_tab_{drug['id']}"] = "rare"
    
    with col4:
        if st.button("� Search", key=f"report_{drug['id']}", use_container_width=True):
            st.session_state[f"side_effect_tab_{drug['id']}"] = "report"
    
    st.markdown("---")
    
    # Display content based on selected tab
    current_tab = st.session_state.get(f"side_effect_tab_{drug['id']}", "common")
    
    if current_tab == "common":
        render_common_side_effects(drug)
    elif current_tab == "uncommon":
        render_uncommon_side_effects(drug)
    elif current_tab == "rare":
        render_rare_side_effects(drug)
    elif current_tab == "report":
        render_side_effect_search(drug)


def render_common_side_effects(drug: dict):
    """Render common side effects with frequency information."""
    
    common_effects = drug.get('common_side_effects', [])
    
    if not common_effects:
        st.info("No common side effects reported for this medication.")
        return
    
    st.markdown("### Most Frequently Reported Side Effects")
    
    for effect in common_effects:
        # Get pt_name and average_frequency from the database result
        effect_name = effect.get('pt_name', 'Unknown')
        frequency = effect.get('average_frequency', 0)
        frequency_percent = f"{frequency * 100:.1f}%" if frequency else "Unknown"
        
        st.markdown(f"""
        <div style='border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: #ffffff;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='font-weight: 600; font-size: 15px; color: #1f2937;'>{effect_name}</div>
                <div style='background: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;'>
                    {frequency_percent}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_uncommon_side_effects(drug: dict):
    """Render uncommon side effects with frequency information."""
    
    uncommon_effects = drug.get('uncommon_side_effects', [])
    
    if not uncommon_effects:
        st.info("No uncommon side effects reported for this medication.")
        return
    
    st.markdown("### ⚠️ Uncommon Side Effects")
    
    for effect in uncommon_effects:
        effect_name = effect.get('pt_name', 'Unknown')
        frequency = effect.get('average_frequency', 0)
        frequency_percent = f"{frequency * 100:.1f}%" if frequency else "Unknown"
        
        st.markdown(f"""
        <div style='border: 1px solid #f59e0b; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: #fffbeb;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='font-weight: 600; font-size: 15px; color: #92400e;'>{effect_name}</div>
                <div style='background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;'>
                    {frequency_percent}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_rare_side_effects(drug: dict):
    """Render rare side effects with frequency information."""
    
    rare_effects = drug.get('rare_effects', [])
    
    if not rare_effects:
        st.info("No rare side effects documented for this medication.")
        return
    
    st.markdown("### 🚨 Rare Side Effects")
    st.warning("These are rare but potentially serious. Contact your healthcare provider if you experience these symptoms.")
    
    for effect in rare_effects:
        effect_name = effect.get('pt_name', 'Unknown')
        frequency = effect.get('average_frequency', 0)
        frequency_percent = f"{frequency * 100:.1f}%" if frequency else "Unknown"
        
        st.markdown(f"""
        <div style='border: 2px solid #dc2626; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: #fef2f2;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='font-weight: 700; font-size: 15px; color: #991b1b;'>{effect_name}</div>
                <div style='background: #dc2626; color: white; padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;'>
                    {frequency_percent}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Emergency contact info
    st.markdown("### 🚨 Emergency Contacts")
    st.error("**For severe side effects:** Call 911 or go to your nearest emergency room")
    st.info("**For urgent questions:** Contact your healthcare provider")
    st.info("**Poison Control:** 1-800-222-1222 (24/7)")


def render_side_effect_search(drug: dict):
    """Render side effect search functionality for the drug."""
    
    drug_id = drug.get('id')
    drug_name = drug.get('name', 'this medication')
    
    st.markdown("### 🔍 Search Side Effects")
    st.markdown(f"Search for specific side effects associated with **{drug_name}**")
    
    # Get all side effects for this drug
    all_side_effects = get_all_sideeffects_for_drug(drug_id)
    
    if not all_side_effects:
        st.info(f"No side effects data available for {drug_name}")
        return
    
    # Search input
    search_query = st.text_input(
        "Search for a side effect:",
        placeholder="e.g., nausea, headache, dizziness...",
        key=f"search_side_effect_{drug_id}"
    )
    
    # Filter side effects based on search query
    if search_query:
        filtered_effects = [
            effect for effect in all_side_effects
            if search_query.lower() in effect['pt_name'].lower()
        ]
        
        if filtered_effects:
            st.markdown(f"**{len(filtered_effects)} side effect(s) found:**")
            
            # Display as cards matching the style of other tabs
            for effect in filtered_effects:
                effect_name = effect.get('pt_name', 'Unknown')
                frequency = effect.get('average_frequency')
                frequency_percent = f"{frequency * 100:.1f}%" if frequency is not None else "Unknown"
                
                # Determine styling based on frequency
                if frequency is not None and frequency > 0.5:
                    # Common
                    border_color = "#e5e7eb"
                    bg_color = "#ffffff"
                    text_color = "#1f2937"
                    badge_bg = "#dbeafe"
                    badge_color = "#1e40af"
                elif frequency is not None and frequency > 0.2:
                    # Uncommon
                    border_color = "#f59e0b"
                    bg_color = "#fffbeb"
                    text_color = "#92400e"
                    badge_bg = "#fef3c7"
                    badge_color = "#92400e"
                elif frequency is not None:
                    # Rare
                    border_color = "#dc2626"
                    bg_color = "#fef2f2"
                    text_color = "#991b1b"
                    badge_bg = "#dc2626"
                    badge_color = "white"
                else:
                    # Unknown
                    border_color = "#9ca3af"
                    bg_color = "#f9fafb"
                    text_color = "#374151"
                    badge_bg = "#e5e7eb"
                    badge_color = "#374151"
                
                st.markdown(f"""
                <div style='border: 1px solid {border_color}; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: {bg_color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='font-weight: 600; font-size: 15px; color: {text_color};'>{effect_name}</div>
                        <div style='background: {badge_bg}; color: {badge_color}; padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;'>
                            {frequency_percent}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"No side effects found matching '{search_query}'")
    else:
        st.info("Enter a side effect name to search")

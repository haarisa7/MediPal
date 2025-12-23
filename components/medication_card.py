def _render_card_edit(medication, adherence_rate=None, active=True):
    drug_name = medication.get('drug_name', 'Medication')
    dose = medication.get('dose', '')
    timing = medication.get('timing', '')
    instructions = medication.get('instructions', '')
    prescribed_by = medication.get('prescribed_by', '')
    adherence_html = f"<span style='position: absolute; top: 16px; right: 16px; color: #2563eb; font-size: 13px; background: #e0e7ff; padding: 2px 10px; border-radius: 8px;'>Adherence: {adherence_rate if adherence_rate is not None else '--'}%</span>"
    border_color = '#10b981' if active else '#ef4444'
    card_html = f"""
<div style='background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    {adherence_html}
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <span style='font-size: 24px; margin-right: 12px;'>💊</span>
        <div>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{drug_name}</div>
            <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
        </div>
    </div>
    <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
        {f"<b>{timing}</b> • " if timing else ''}{instructions if instructions else 'Follow package instructions.'}
    </div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {prescribed_by}</div>
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def _render_card_taken(medication, adherence_rate=None):
    drug_name = medication.get('drug_name', 'Medication')
    dose = medication.get('dose', '')
    instructions = medication.get('instructions', '')
    prescribed_by = medication.get('prescribed_by', '')
    timing = medication.get('timing', '')
    adherence_html = f"<span style='position: absolute; top: 48px; right: 16px; color: #2563eb; font-size: 13px; background: #e0e7ff; padding: 2px 10px; border-radius: 8px;'>Adherence: {adherence_rate if adherence_rate is not None else '--'}%</span>"
    card_html = f"""
<div style='background: #fff; border-left: 6px solid #10b981; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    <span style='position: absolute; top: 16px; right: 16px; color: #10b981; font-weight: 700; background: #e0f7ef; padding: 4px 12px; border-radius: 8px;'>✔ Taken</span>
    {adherence_html}
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <span style='font-size: 24px; margin-right: 12px;'>💊</span>
        <div>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{drug_name}</div>
            <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
        </div>
    </div>
        <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
            {f"<b>{timing}</b> • " if timing else ''}{instructions if instructions else 'Follow package instructions.'}
        </div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {prescribed_by}</div>
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def _render_card_missed(medication, adherence_rate=None):
    timing = medication.get('timing', '')
    drug_name = medication.get('drug_name', 'Medication')
    dose = medication.get('dose', '')
    instructions = medication.get('instructions', '')
    prescribed_by = medication.get('prescribed_by', '')
    adherence_html = f"<span style='position: absolute; top: 48px; right: 16px; color: #2563eb; font-size: 13px; background: #e0e7ff; padding: 2px 10px; border-radius: 8px;'>Adherence: {adherence_rate if adherence_rate is not None else '--'}%</span>"
    card_html = f"""
<div style='background: #fff; border-left: 6px solid #ef4444; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    <span style='position: absolute; top: 16px; right: 16px; color: #ef4444; font-weight: 700; background: #fee2e2; padding: 4px 12px; border-radius: 8px;'>✖ Missed</span>
    {adherence_html}
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <span style='font-size: 24px; margin-right: 12px;'>💊</span>
        <div>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{drug_name}</div>
            <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
        </div>
    </div>
        <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
            {f"<b>{timing}</b> • " if timing else ''}{instructions if instructions else 'Follow package instructions.'}
        </div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {prescribed_by}</div>
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def _render_card_pending(medication, patient_med_id, adherence_rate=None):
    timing = medication.get('timing', '')
    drug_name = medication.get('drug_name', 'Medication')
    dose = medication.get('dose', '')
    instructions = medication.get('instructions', '')
    prescribed_by = medication.get('prescribed_by', '')
    adherence_html = f"<span style='position: absolute; top: 16px; right: 16px; color: #2563eb; font-size: 13px; background: #e0e7ff; padding: 2px 10px; border-radius: 8px;'>Adherence: {adherence_rate if adherence_rate is not None else '--'}%</span>"
    card_html = f"""
<div style='background: #fff; border-left: 4px solid #6b7280; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    {adherence_html}
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <span style='font-size: 24px; margin-right: 12px;'>💊</span>
        <div>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{drug_name}</div>
            <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
        </div>
    </div>
        <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
            {f"<b>{timing}</b> • " if timing else ''}{instructions if instructions else 'Follow package instructions.'}
        </div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {prescribed_by}</div>
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.button('Taken', key=f"taken_{patient_med_id}"):
            from data.medication_log import log_medication_intake
            log_medication_intake(patient_med_id, True)
            st.rerun()
    with col2:
        if st.button('Missed', key=f"missed_{patient_med_id}"):
            from data.medication_log import log_medication_intake
            log_medication_intake(patient_med_id, False)
            st.rerun()

def _render_card_library(medication, adherence_rate=None, active=True):
    drug_name = medication.get('drug_name', 'Medication')
    dose = medication.get('dose', '')
    instructions = medication.get('instructions', '')
    prescribed_by = medication.get('prescribed_by', '')
    adherence_html = f"<span style='position: absolute; top: 16px; right: 16px; color: #2563eb; font-size: 13px; background: #e0e7ff; padding: 2px 10px; border-radius: 8px;'>Adherence: {adherence_rate if adherence_rate is not None else '--'}%</span>"
    border_color = '#10b981' if active else '#ef4444'
    card_html = f"""
<div style='background: #fff; border-left: 6px solid {border_color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    {adherence_html}
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <span style='font-size: 24px; margin-right: 12px;'>💊</span>
        <div>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{drug_name}</div>
            <div style='color: #6b7280; font-size: 13px;'>{dose}</div>
        </div>
    </div>
        <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
            {instructions if instructions else 'Follow package instructions.'}
        </div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {prescribed_by}</div>
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


import streamlit as st


def render_medication_card(medication: dict, patient_med_id: int, status=None, context='schedule', adherence_rate=None, active=True):
    """Dispatch to the correct card rendering function based on status and context."""
    if context == 'library':
        _render_card_library(medication, adherence_rate=adherence_rate, active=active)
    elif context == 'edit':
        _render_card_edit(medication, adherence_rate=adherence_rate, active=active)
    elif status == 'taken':
        _render_card_taken(medication, adherence_rate=adherence_rate)
    elif status == 'missed':
        _render_card_missed(medication, adherence_rate=adherence_rate)
    else:
        _render_card_pending(medication, patient_med_id, adherence_rate=adherence_rate)



import streamlit as st
from data.medication_requests import compare_medication_entries, get_edit_changes
from data.patient_medications import get_all_patient_medication_entries

def render_add_request_card(request, status, accept_callback=None, reject_callback=None):
    # Card style and icon by status
    if status == 'pending':
        border_color = '#f59e0b'
        icon = '⏳'
    elif status == 'accepted':
        border_color = '#10b981'
        icon = '✅'
    else:
        border_color = '#ef4444'
        icon = '❌'
    patient_name = request['patient_name']
    req_type = 'Add Request'
    card_html = f"""
<div style='background: #fff; border-left: 6px solid {border_color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <div style='display: flex; align-items: center;'>
            <span style='font-size: 22px; margin-right: 8px; margin-top: 2px;'>{icon}</span>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{req_type}</div>
        </div>
    </div>
    <div style='font-size: 15px; color: #222;'><b>Patient:</b> {patient_name}</div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {request['prescribed_by']}</div>
    <div style='color: #6b7280; font-size: 13px;'><b>Drug:</b> {request['drug_name']} &nbsp; <b>Dose:</b> {request['dose']}</div>
    <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
        {f"<b>{request.get('timing','')}</b> • " if request.get('timing') else ''}{request.get('instructions') or 'Follow package instructions.'}
    </div>
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    if status == 'pending' and accept_callback and reject_callback:
        col1, col2, _ = st.columns([1,1,4])
        with col1:
            if st.button("Accept", key=f"accept_{request['request_id']}"):
                accept_callback()
        with col2:
            if st.button("Reject", key=f"reject_{request['request_id']}"):
                reject_callback()

def render_edit_request_card(request, status, accept_callback=None, reject_callback=None):
    # Card style and icon by status
    if status == 'pending':
        border_color = '#f59e0b'
        icon = '⏳'
    elif status == 'accepted':
        border_color = '#10b981'
        icon = '✅'
    else:
        border_color = '#ef4444'
        icon = '❌'
    patient_name = request['patient_name']
    req_type = 'Edit Request'
    changes = get_edit_changes(request)
    def highlight(val, field):
        if field in changes:
            return f"<span style='color:#ef4444;font-weight:600'>{val}</span>"
        return val
    card_html = f"""
<div style='background: #fff; border-left: 6px solid {border_color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); position: relative;'>
    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
        <div style='display: flex; align-items: center;'>
            <span style='font-size: 22px; margin-right: 8px; margin-top: 2px;'>{icon}</span>
            <div style='font-weight: 700; font-size: 18px; color: #1f2937; margin-bottom: 2px;'>{req_type}</div>
        </div>
    </div>
    <div style='font-size: 15px; color: #222;'><b>Patient:</b> {patient_name}</div>
    <div style='font-size: 15px; color: #222;'><b>Prescribed By:</b> {highlight(request['prescribed_by'], 'prescribed_by')}</div>
    <div style='color: #6b7280; font-size: 13px;'><b>Drug:</b> {highlight(request['drug_name'], 'drug_name')} &nbsp; <b>Dose:</b> {highlight(request['dose'], 'dose')}</div>
    <div style='color: #4b5563; font-size: 14px; margin-bottom: 8px;'>
        {f"<b>{highlight(request.get('timing',''), 'timing')}</b> • " if request.get('timing') else ''}{highlight(request.get('instructions') or 'Follow package instructions.', 'instructions')}
    </div>
    {''.join([f"<div style='font-size:13px;color:#ef4444;'><b>Changed:</b> {field.replace('_',' ').title()}: <s>{changes[field][0]}</s> → <b>{changes[field][1]}</b></div>" for field in changes]) if changes else ''}
</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    if status == 'pending' and accept_callback and reject_callback:
        col1, col2, _ = st.columns([1,1,4])
        with col1:
            if st.button("Accept", key=f"accept_{request['request_id']}"):
                accept_callback()
        with col2:
            if st.button("Reject", key=f"reject_{request['request_id']}"):
                reject_callback()

def render_notification_card(request, status, accept_callback=None, reject_callback=None):
    req_type = request.get('request_type', '').lower()
    if req_type == 'edit':
        render_edit_request_card(request, status, accept_callback, reject_callback)
    else:
        render_add_request_card(request, status, accept_callback, reject_callback)

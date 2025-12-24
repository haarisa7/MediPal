import streamlit as st
from hydralit import HydraHeadApp
from auth.auth_service import get_user_by_email, get_user_by_id, update_user_email, update_user_profile, change_user_password
from datetime import datetime, date


class AccountApp(HydraHeadApp):
    def __init__(self, title: str = 'Account', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def _resolve_user_id(self):
        # Only user_id (int) should be stored in session_state['current_id']
        user_id = st.session_state.get('current_id')
        if user_id is None:
            return None
        try:
            return int(user_id)
        except Exception:
            return None

    def run(self) -> None:
        # Load global styles
        try:
            with open("assets/styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass
        
        # Header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px;'>
            <div style='font-size: 28px; font-weight: 700; margin-bottom: 8px;'>🧑‍💼 My Account</div>
            <div style='font-size: 16px; opacity: 0.9;'>Manage your profile and settings</div>
        </div>
        """, unsafe_allow_html=True)

        from data.patient_profile import get_patient_profile
        user_id = self._resolve_user_id()
        current_id_val = st.session_state.get('current_id')
        if not isinstance(current_id_val, int):
            st.warning(f"[DEBUG] session_state['current_id'] is not an int! Value: {current_id_val}")
        if user_id is None:
            st.error("[ERROR] Could not resolve user_id from session_state['current_id']! Account page cannot load user info.")
            return
        
        user = get_patient_profile(user_id) if user_id is not None else {}
        
        # Compute profile defaults before rendering so toggle affects inputs immediately
        first_val = user.get('first_name') or ''
        last_val = user.get('last_name') or ''
        dob_val = user.get('date_of_birth')
        if isinstance(dob_val, str):
            try:
                dob_val = datetime.fromisoformat(dob_val).date()
            except Exception:
                dob_val = None
        if dob_val is None:
            dob_val = date.today()
        email_val = user.get('email', '')

        # Profile Section
        st.markdown('### 👤 Profile Information')
        
        col_main, col_actions = st.columns([3, 1])
        
        with col_actions:
            # Add spacing to align with form fields
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            
            if not st.session_state.get('acct_edit', False):
                if st.button("✏️ Edit Profile", use_container_width=True, type="primary"):
                    st.session_state['acct_edit'] = True
                    st.rerun()
            else:
                if st.button("✅ Save Changes", use_container_width=True, type="primary"):
                    # Attempt to update email and profile
                    new_email = st.session_state.get('acct_email', email_val)
                    new_first = st.session_state.get('acct_first_name', first_val)
                    new_last = st.session_state.get('acct_last_name', last_val)
                    new_dob = st.session_state.get('acct_dob', dob_val)
                    # normalize date
                    if isinstance(new_dob, datetime):
                        new_dob = new_dob.date()

                    ok_email = update_user_email(user_id, new_email)
                    ok_profile = update_user_profile(user_id, new_first, new_last, new_dob)
                    if ok_email and ok_profile:
                        st.success('✅ Profile updated successfully!')
                        st.balloons()
                        # update session current_id (just keep id)
                        st.session_state['current_id'] = user_id
                        st.session_state['acct_edit'] = False
                        st.rerun()
                    else:
                        st.error('❌ Failed to update profile. Please try again.')
                
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state['acct_edit'] = False
                    st.rerun()

        with col_main:
            # Display profile fields
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("👤 First Name", value=first_val, key='acct_first_name', disabled=not st.session_state.get('acct_edit', False))
                st.date_input("📅 Date of Birth", value=dob_val, key='acct_dob', disabled=not st.session_state.get('acct_edit', False))
            
            with col2:
                st.text_input("👤 Last Name", value=last_val, key='acct_last_name', disabled=not st.session_state.get('acct_edit', False))
                st.text_input("📧 Email", value=email_val, key='acct_email', disabled=not st.session_state.get('acct_edit', False))

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Change password section
        st.markdown('### 🔒 Security')
        
        if not st.session_state.get('acct_change_pwd', False):
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔑 Change Password", use_container_width=True):
                    st.session_state['acct_change_pwd'] = True
                    st.rerun()
            with col1:
                st.markdown("""
                <div style='background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px;'>
                    <div style='color: #1e40af; font-size: 14px;'>
                        Keep your account secure by updating your password regularly.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.form(key='chg_pwd_form'):
                st.text_input('🔐 Current Password', type='password', key='cur_pwd_input')
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input('🔑 New Password', type='password', key='new_pwd_input')
                with col2:
                    st.text_input('🔑 Confirm New Password', type='password', key='new_pwd2_input')
                
                col_submit, col_cancel, _ = st.columns([1, 1, 2])
                with col_submit:
                    submitted = st.form_submit_button('✅ Update Password', use_container_width=True, type='primary')
                with col_cancel:
                    cancel = st.form_submit_button('❌ Cancel', use_container_width=True)
                
                if cancel:
                    st.session_state['acct_change_pwd'] = False
                    st.rerun()
                
                if submitted:
                    cur_pwd = st.session_state.get('cur_pwd_input', '')
                    new_pwd = st.session_state.get('new_pwd_input', '')
                    new_pwd2 = st.session_state.get('new_pwd2_input', '')
                    
                    if new_pwd != new_pwd2:
                        st.error('❌ New passwords do not match')
                    else:
                        ok = change_user_password(user_id, cur_pwd, new_pwd)
                        if ok:
                            st.success('✅ Password changed successfully!')
                            st.balloons()
                            st.session_state['acct_change_pwd'] = False
                            st.rerun()
                        else:
                            st.error('❌ Password change failed — check current password and try again')

        # Logout action
        st.markdown("---")
        st.markdown('### 👋 Sign Out')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            <div style='background: #fef2f2; border-left: 4px solid #ef4444; padding: 16px; border-radius: 8px;'>
                <div style='color: #991b1b; font-size: 14px;'>
                    Signing out will end your current session. You'll need to log in again to access your account.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
                st.session_state['logged_in'] = False
                st.session_state['current_id'] = None
                try:
                    self.set_access(0, None)
                except Exception:
                    pass
                try:
                    self.do_redirect("Home")
                except Exception:
                    st.rerun()

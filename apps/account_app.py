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
        st.title("🧑‍💼 Account")
        st.caption("Manage account settings and sign out")
        st.divider()

        from data.patient_profile import get_patient_profile
        user_id = self._resolve_user_id()
        current_id_val = st.session_state.get('current_id')
        if not isinstance(current_id_val, int):
            st.warning(f"[DEBUG] session_state['current_id'] is not an int! Value: {current_id_val}")
        if user_id is None:
            st.error("[ERROR] Could not resolve user_id from session_state['current_id']! Account page cannot load user info.")
        user = get_patient_profile(user_id) if user_id is not None else {}
        # Compute profile defaults before rendering so toggle affects inputs immediately
        st.subheader("Profile")
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

        col1, col2 = st.columns([2, 1])

        # Render controls column first so button toggles take effect for subsequent inputs
        with col2:
            st.info("Edit profile details below.")
            if st.button("Edit Details"):
                st.session_state['acct_edit'] = not st.session_state.get('acct_edit', False)

            # Save changes button (visible when in edit mode)
            if st.session_state.get('acct_edit'):
                if st.button("Save Changes"):
                    # Attempt to update email and profile
                    new_email = st.session_state.get('acct_email', email_val)
                    new_first = st.session_state.get('acct_first_name', first_val)
                    new_last = st.session_state.get('acct_last_name', last_val)
                    new_dob = st.session_state.get('acct_dob', dob_val)
                    # normalize date
                    if isinstance(new_dob, datetime):
                        new_dob = new_dob.date()

                    user_id = self._resolve_user_id()
                    if user_id is None:
                        st.error('Unable to save: user id unknown.')
                    else:
                        ok_email = update_user_email(user_id, new_email)
                        ok_profile = update_user_profile(user_id, new_first, new_last, new_dob)
                        if ok_email and ok_profile:
                            st.success('Profile updated.')
                            # update session current_id (just keep id)
                            st.session_state['current_id'] = user_id
                            st.session_state['acct_edit'] = False
                        else:
                            st.error('Failed to update profile. Please try again.')

        with col1:
            st.markdown("**First name:**")
            st.text_input("First name", value=first_val, key='acct_first_name', disabled=not st.session_state.get('acct_edit', False))

            st.markdown("**Last name:**")
            st.text_input("Last name", value=last_val, key='acct_last_name', disabled=not st.session_state.get('acct_edit', False))

            st.markdown("**Date of birth:**")
            st.date_input("Date of birth", value=dob_val, key='acct_dob', disabled=not st.session_state.get('acct_edit', False))

            st.markdown("**Email:**")
            st.text_input("Email", value=email_val, key='acct_email', disabled=not st.session_state.get('acct_edit', False))

        st.divider()

        # Change password section
        st.subheader("Change password")
        if st.button("Change Password"):
            st.session_state['acct_change_pwd'] = True

        if st.session_state.get('acct_change_pwd'):
            with st.form(key='chg_pwd_form'):
                cur_pwd = st.text_input('Current password', type='password')
                new_pwd = st.text_input('New password', type='password')
                new_pwd2 = st.text_input('Confirm new password', type='password')
                submitted = st.form_submit_button('Submit')
                if submitted:
                    if new_pwd != new_pwd2:
                        st.error('New passwords do not match')
                    else:
                        user_id = self._resolve_user_id()
                        identifier = user_id
                        if identifier is None:
                            st.error('Unable to change password: no user identifier')
                        else:
                            ok = change_user_password(identifier, cur_pwd, new_pwd)
                            if ok:
                                st.success('Password changed successfully')
                                st.session_state['acct_change_pwd'] = False
                            else:
                                st.error('Password change failed — check current password and try again')

        # Logout action
        st.divider()
        if st.button("Log out"):
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

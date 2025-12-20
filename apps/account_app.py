import streamlit as st
from hydralit import HydraHeadApp
from auth.auth_service import get_user_by_email, get_user_by_id, update_user_email, change_user_password


class AccountApp(HydraHeadApp):
    def __init__(self, title: str = 'Account', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def _resolve_user(self):
        cur = st.session_state.get('current_user')
        if cur is None:
            return {}
        # If stored as a dict already
        if hasattr(cur, 'get'):
            return cur
        # If stored as an int id
        if isinstance(cur, int):
            u = get_user_by_id(cur)
            return u or {}
        # If stored as an email string
        if isinstance(cur, str):
            u = get_user_by_email(cur)
            return u or {}
        return {}

    def run(self) -> None:
        st.title("🧑‍💼 Account")
        st.caption("Manage account settings and sign out")
        st.divider()

        user = self._resolve_user()


        # Display basic info
        st.subheader("Profile")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Email:**")
            # Locked until edit
            email_val = user.get('email', '')
            st.text_input("Email", value=email_val, key='acct_email', disabled=not st.session_state.get('acct_edit', False))
            st.markdown("**Display name (not saved):**")
            st.text_input("Name", value=user.get('name', ''), key='acct_name', disabled=not st.session_state.get('acct_edit', False))

        with col2:
            st.info("Edit profile details below.")
            if st.button("Edit Details"):
                st.session_state['acct_edit'] = not st.session_state.get('acct_edit', False)

            # Save changes button (visible when in edit mode)
            if st.session_state.get('acct_edit'):
                if st.button("Save Changes"):
                    # Attempt to update email (only backend-saved field currently)
                    new_email = st.session_state.get('acct_email', email_val)
                    resolved = self._resolve_user()
                    user_id = resolved.get('user_id')
                    if user_id is None:
                        st.error('Unable to save: user id unknown.')
                    else:
                        ok = update_user_email(user_id, new_email)
                        if ok:
                            st.success('Profile updated.')
                            # update session current_user
                            st.session_state['current_user'] = get_user_by_id(user_id)
                            st.session_state['acct_edit'] = False
                        else:
                            st.error('Failed to update profile. Please try again.')

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
                        resolved = self._resolve_user()
                        user_id = resolved.get('user_id')
                        identifier = user_id if user_id is not None else resolved.get('email')
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
            st.session_state['current_user'] = None
            try:
                self.set_access(0, None)
            except Exception:
                pass
            try:
                self.do_redirect("Home")
            except Exception:
                st.experimental_rerun()

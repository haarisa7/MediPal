import streamlit as st
from hydralit import HydraHeadApp
import time
from auth.auth_service import register_user as auth_register_user


class SignUpApp(HydraHeadApp):
    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        st.subheader("Register")
        st.caption(":blue[_create an account_]")
        c1, c2, c3 = st.columns([2, 2, 2])

        form_data = self._create_signup_form(c2)

        if form_data['submitted']:
            self._do_signup(form_data, c2)

    def _create_signup_form(self, parent_container) -> dict:

        login_form = parent_container.form(key="login_form")

        form_state = {}
        form_state['email'] = login_form.text_input('Email', key='reg_email')
        form_state['password'] = login_form.text_input('Password', type="password")
        form_state['password2'] = login_form.text_input('Confirm Password', type="password")
        form_state['user_type'] = login_form.radio('I am a', ['Patient', 'Clinician'], index=0)
        form_state['submitted'] = login_form.form_submit_button('Sign Up')

        return form_state

    def _do_signup(self, form_data, msg_container) -> None:
        if form_data['submitted'] and (form_data['password'] != form_data['password2']):
            msg_container.error('Passwords do not match, please try again.')
        else:
            # Delegate signup and profile creation to the local auth service
            # Map UI role labels to numeric access levels required by the auth service
            role_label = form_data.get('user_type', 'Patient')
            role_map = {'patient': 0, 'clinician': 1}
            role_num = role_map.get(role_label.strip().lower(), 0)

            success = auth_register_user(
                form_data['email'], form_data['password'], role_num
            )
            if success:
                with st.spinner("🤓 now redirecting to login...."):
                    time.sleep(2)

                    # access control uses an int value to allow for levels of permission that can be set for each user
                    self.set_access(0, None)

                    # Redirect explicitly to the Login page so the user can sign in
                    try:
                        self.do_redirect("Login")
                    except Exception:
                        self.do_redirect()
            else:
                msg_container.error('Registration failed — please try again or contact support.')

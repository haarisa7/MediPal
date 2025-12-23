import streamlit as st
from hydralit import HydraHeadApp
import time
from auth.auth_service import register_user as auth_register_user, login_user


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
        form_state['first_name'] = login_form.text_input('First Name', key='reg_first_name')
        form_state['last_name'] = login_form.text_input('Last Name', key='reg_last_name')
        form_state['date_of_birth'] = login_form.date_input('Date of Birth', key='reg_dob')
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
                form_data['email'], form_data['password'], role_num,
                form_data['first_name'], form_data['last_name'], form_data['date_of_birth']
            )
            if success:
                # Automatically log the user in after registration
                user = login_user(form_data['email'], form_data['password'])
                if user:
                    from auth.auth_service import get_user_by_email
                    db_user = get_user_by_email(form_data['email'])
                    user_id = db_user['user_id'] if db_user else user['user_id']
                    try:
                        user_id = int(user_id)
                    except Exception:
                        user_id = None
                    st.session_state.logged_in = True
                    st.session_state.current_id = user_id
                    with st.spinner("🤓 Welcome! Setting up your account...."):
                        time.sleep(1)
                        try:
                            self.set_access(2, form_data['email'])
                        except Exception:
                            pass
                        msg_container.success("✔️ Account created and logged in!")
                        # Redirect to Medication Tracker or Home
                        try:
                            self.do_redirect("Medication Tracker")
                        except TypeError:
                            try:
                                import apps
                                apps.MedicationTracker(title="Medication Tracker").run()
                                st.rerun()
                            except Exception:
                                try:
                                    self.do_redirect()
                                except Exception:
                                    st.rerun()
                else:
                    msg_container.error('Account created but login failed — please try logging in manually.')
            else:
                msg_container.error('Registration failed — please try again or contact support.')

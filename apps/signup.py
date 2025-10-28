import streamlit as st
from hydralit import HydraHeadApp
from supabase import create_client
import toml
import time

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
        form_state['submitted'] = login_form.form_submit_button('Sign Up')

        return form_state

    def _do_signup(self, form_data, msg_container) -> None:
        # Load Supabase URL and API key from secrets.toml file
        secrets = toml.load("secrets.toml")
        supabase_url = secrets["SUPABASE_URL"]
        supabase_key = secrets["SUPABASE_KEY"]
        supabase = create_client(supabase_url, supabase_key)
        if form_data['submitted'] and (form_data['password'] != form_data['password2']):
            msg_container.error('Passwords do not match, please try again.')
        else:
            response = supabase.auth.sign_up(credentials={"email": form_data['email'], "password": form_data['password']})
            if response is not None:
                with st.spinner("🤓 now redirecting to login...."):
                    time.sleep(2)

                    #access control uses an int value to allow for levels of permission that can be set for each user, this can then be checked within each app seperately.
                    self.set_access(0, None)

                    #Do the kick back to the login screen
                    self.do_redirect()


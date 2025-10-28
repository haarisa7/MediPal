import time
from supabase import create_client
import toml
import streamlit as st
from hydralit import HydraHeadApp

class LoginApp(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:

        st.title(":closed_lock_with_key: Login")
        st.caption(":blue[_login to your account_]")
        st.divider()

        with st.container():
            st.markdown("Welcome to the login page. Please enter your credentials to access the Forecaster app.")

        c1, c2, c3, = st.columns([2, 2, 2])

        form_data = self._create_login_form(c2)

        if form_data['submitted']:
            self._do_login(form_data, c2)

    def _create_login_form(self, parent_container) -> dict:

        login_form = parent_container.form(key="login_form")

        form_state = {'email': login_form.text_input('Login Email', key='login_email'),
                      'password': login_form.text_input('Password', type="password", key='login_pass'),
                      'submitted': login_form.form_submit_button('Login')}

        return form_state

    def _do_login(self, form_data, msg_container) -> None:

        # Load Supabase URL and API key from secrets.toml file
        secrets = toml.load("secrets.toml")
        supabase_url = secrets["SUPABASE_URL"]
        supabase_key = secrets["SUPABASE_KEY"]
        supabase = create_client(supabase_url, supabase_key)

        response = supabase.auth.sign_in_with_password(credentials={"email": form_data['email'], "password": form_data['password']})

        if hasattr(response, 'session') and response.session:
            st.session_state.logged_in = True
            self.set_access(2, form_data['email'])
            msg_container.success(f"✔️ Login success")
            with st.spinner("🤓 now redirecting to application...."):
                # Do the kick to the home page
                self.do_redirect()
        else:
            self.session_state.allow_access = 0
            self.session_state.current_user = None
            st.write(response)
            if hasattr(response, 'error') and response.error:
                msg_container.error(f"❌ Login unsuccessful, 😕 please check your username and password and try again.")


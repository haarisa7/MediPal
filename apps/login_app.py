import streamlit as st
from hydralit import HydraHeadApp
from auth.auth_service import login_user

class LoginApp(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:

        st.title(":closed_lock_with_key: Login")
        st.caption(":blue[_login to your account_]")
        st.divider()

        with st.container():
            st.markdown("Welcome to the login page. Please enter your credentials to access the MediPal app.")

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
            # keep previous access pattern
            try:
                self.set_access(2, form_data['email'])
            except Exception:
                pass
            msg_container.success("✔️ Login success")
            with st.spinner("🤓 now redirecting to Home...."):
                try:
                    self.do_redirect("Home")
                except TypeError:
                    try:
                        import apps
                        apps.HomeApp(title="Home").run()
                        st.rerun()
                    except Exception:
                        try:
                            self.do_redirect()
                        except Exception:
                            st.rerun()
        else:
            self.session_state.allow_access = 0
            self.session_state.current_id = None
            msg_container.error("❌ Login unsuccessful, 😕 please check your username and password and try again.")


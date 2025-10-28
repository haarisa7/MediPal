import streamlit as st
from hydralit import HydraApp
import apps

st.set_page_config(page_title='Forecaster',page_icon="🐙",layout='wide',initial_sidebar_state='auto')

if __name__ == "__main__":

    over_theme = {'txc_inactive': 'black', 'menu_background': 'white', 'txc_active': 'red'}
    app = HydraApp(
        title='Forecaster',
        favicon="🐙",
        hide_streamlit_markers=True,
        use_navbar=True,
        navbar_sticky=False,
        navbar_animation=True,
        navbar_theme=over_theme
    )

    app.add_app("Home", icon="🏠", app=apps.HomeApp(title='Home'),is_home=True)
    app.add_app("Correlation Analysis",icon="📈", app=apps.CorrelationAnalysis(title="Correlation Analysis"))
    app.add_app("Historic Graphs", icon="📈", app=apps.HistoricGraphs(title='Historic Graphs'))
    app.add_app("Linear Regression", icon="💹", app=apps.LinearRegressionAnalysis(title='Linear Regression'))
    app.add_app("Neural Network", icon="💹", app=apps.NeuralNetwork(title='Neural Network'))
    app.add_app("Create Account", icon="✨", app=apps.SignUpApp(title='Create Account'), is_unsecure=True)
    app.add_app("Login", icon="🥷", app=apps.LoginApp(title='Login'),is_login=True)

    app.enable_guest_access()

    user_access_level, username = app.check_access()

    if user_access_level > 1:
        complex_nav = {
            'Home': ['Home'],
            'Correlation Analysis': ['Correlation Analysis'],
            'Historic Graphs': ['Historic Graphs'],
            'Linear Regression': ["Linear Regression"],
            'Neural Network': ['Neural Network']
        }
    elif user_access_level == 1:
        complex_nav = {
            'Home': ['Home'],
            'Correlation Analysis': ['Correlation Analysis'],
            'Historic Graphs': ['Historic Graphs'],
            'Sign Up': ['Create Account']
        }
    else:
        complex_nav = {
            'Home': ['Home'],
        }

    # and finally just the entire app and all the children.
    app.run(complex_nav)
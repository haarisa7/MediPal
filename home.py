import streamlit as st
import apps

st.set_page_config(page_title='Forecaster', page_icon="🐙", layout='wide', initial_sidebar_state='auto')


if __name__ == "__main__":
    # Load and show only the simple Home page
    home = apps.HomeApp(title='Home')
    home.run()
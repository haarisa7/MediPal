import plotly.graph_objects as go
import toml
from scipy.stats import spearmanr

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

from data.nn_finance_data import get_stock_data
from data.finance_data import fetch_stock_symbols
from data.finance_data import fetch_timeframes_intervals
from data.nn_data import join_data
from data.nn_weather_data import get_filtered_weather_data
from data.nn_finance_data import get_stock_start_date
from data.nn_data import check_inputs
from hydralit import HydraHeadApp

class CorrelationAnalysis(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def sidebar(self):
        st.sidebar.subheader("Stock")
        stock_symbols_dict = fetch_stock_symbols()
        selected_symbol = st.sidebar.selectbox("Stock:", list(stock_symbols_dict.keys()), index=None,
                                               placeholder="Choose a stock")
        # Initialize symbol as None
        stock = None
        # Check if selected_symbol is not None before accessing the dictionary
        if selected_symbol is not None:
            stock = stock_symbols_dict.get(selected_symbol)
        st.sidebar.divider()
        st.sidebar.subheader("Weather")
        weather_variable = st.sidebar.selectbox("Weather variable:", ["Temperature", "Humidity", "Wind Speed"],
                                                index=None,
                                                placeholder="Choose a weather variable")

        region = st.sidebar.selectbox("Weather region:", ["London", "New York", "Paris"],
                                      index=None,
                                      placeholder="Choose a weather region")

        st.sidebar.divider()
        st.sidebar.subheader("Time")
        timeframes = fetch_timeframes_intervals()
        time_period = st.sidebar.selectbox("Time period", list(timeframes.keys()),
                                           index=None,
                                           placeholder="Choose a time period")

        return {"stock": stock, "variable": weather_variable, "region": region, "period": time_period}


    def join_correlation_data(self, weather_df, stock_df, chosen_variable, chosen_stock, chosen_region, chosen_units):
        stock_symbols_dict = fetch_stock_symbols()
        symbol = list(stock_symbols_dict.keys())[list(stock_symbols_dict.values()).index(chosen_stock)]
        merged_df = join_data(weather_df, stock_df, chosen_variable)

        fig = go.Figure()

        # Add the first subplot for chosen_variable
        fig.add_trace(go.Scatter(x=merged_df["Date"], y=merged_df[chosen_variable], mode='lines', name=chosen_variable,
                                 line=dict(color='#FF0000')))

        # Add the second subplot for chosen_stock
        fig.add_trace(
            go.Scatter(x=merged_df["Date"], y=merged_df['Close'], mode='lines', name=symbol, yaxis='y2',
                       line=dict(color='#0000FF')))

        # Update layout to show subplots
        # if chosen_units == False, then temperature is in Celsius - else it is in Fahrenheit
        # if
        if chosen_variable == "Temperature" and chosen_units == False:
            temperature_label = "Temperature (°C)"
        else:
            temperature_label = chosen_variable
        fig.update_layout(title=f"{symbol} Stock and {chosen_variable} in {chosen_region}",
                          xaxis_title="Date",
                          height=500,
                          yaxis=dict(title=temperature_label, side='left'),
                          yaxis2=dict(title=f"{symbol}", overlaying='y', side='right'))

        # Add subplots
        fig.update_layout()

        st.plotly_chart(fig, use_container_width=True)

        return merged_df


    def calculate_correlation(self, df, chosen_variable, chosen_stock):
        rho, p = spearmanr(df[chosen_variable], df['Close'])
        st.text(f"Spearman's Rank Correlation: {rho}")
        st.text(f"p-value: {p}")


    def send_email(self, subject, message):
        # st.write("in send email method")
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "forecasterbugreporting@gmail.com"

        secrets = toml.load("secrets.toml")  # Load password from toml file
        smtp_password = secrets["SMTP_PASSWORD"]  # Password for the email account

        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = "forecastersystem@gmail.com"  # recipient email address
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)


    def email_action(self):
        message = st.text_area("Type your message here:", "")
        self.send_email("New message from Streamlit app", message)

    def additional_weather_var(self):
        if "weather_var_button" not in st.session_state:
            st.session_state.weather_var_button = False

        if st.button("Add additional weather variable") or st.session_state.weather_var_button:
            st.session_state.weather_var_button = True
            new_var = st.selectbox("Choose a weather variable", ["Temperature", "Humidity", "Precipitation"])
            if new_var and st.button("Enter"):
                return new_var

        return None


    def run(self) -> None:
        # Page setup
        st.title("Correlation Analysis")
        st.caption(":blue[_Correlation Analysis using Spearman's Rank Correlation_]")

        # Initialize session state variables
        if "report_button_clicked" not in st.session_state:
            st.session_state["report_button_clicked"] = False

        # Sidebar and toggle
        user_filters = self.sidebar()

        # Data fetching and processing
        if check_inputs(user_filters):
            new_weather = self.additional_weather_var()
            stock_df = get_stock_data(user_filters["stock"], user_filters["period"])
            start_date = get_stock_start_date(stock_df)
            weather_df = get_filtered_weather_data(
                user_filters["variable"],
                user_filters["region"],
                user_filters["period"],  # Use session state for units
                start_date,
            )
            self.calculate_correlation(
                self.join_correlation_data(
                    weather_df,
                    stock_df,
                    user_filters["variable"],
                    user_filters["stock"],
                    user_filters["region"],
                    False,  # Pass chosen units
                ),
                user_filters["variable"],
                user_filters["stock"],
            )
            # weather button clicked
            if new_weather is not None:
                weather_df = get_filtered_weather_data(new_weather, user_filters["region"],
                                                       user_filters["period"], start_date)
                self.calculate_correlation(
                    self.join_correlation_data(weather_df, stock_df, new_weather, user_filters["stock"], user_filters["region"],
                                          False),
                    new_weather, user_filters["stock"])
                # streamlit refresh logic
                st.button("Remove additional graph")
        else:
            st.warning("Please fill in all required filters in the sidebar.")

        # Report bug feature (nested button)
        if st.button("Report an Issue"):
            st.session_state["report_button_clicked"] = True

        if st.session_state["report_button_clicked"]:
            message = st.text_area("Type the issue here:", "", key="message_area")  # Add key for hiding
            if st.button("Send"):
                # Perform action with the message, such as sending it
                self.send_email("New message: Problem on Correlation Analysis page 😱", message)
                st.session_state["report_button_clicked"] = False  # Reset session state
                st.success("Thank you for your message!")

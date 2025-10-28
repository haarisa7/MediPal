import streamlit as st
import toml

from data.finance_data import fetch_timeframes_intervals
from data.finance_data import go_back
from data.finance_data import plot_historical_data
from data.finance_data import fetch_stock_history
from data.finance_data import fetch_stock_symbols
from data.weather_data import weather_data_intervals
from data.weather_data import extract_relevant_data
from data.weather_data import plot_weather_graph
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hydralit import HydraHeadApp

class HistoricGraphs(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def sidebar(self):
        st.sidebar.subheader("Stock")
        stock_symbols_dict = fetch_stock_symbols()
        selected_symbol = st.sidebar.selectbox("Stock:", list(stock_symbols_dict.keys()), index=None, placeholder="Choose a stock")
        # Initialize symbol as None
        symbol = None
        # Check if selected_symbol is not None before accessing the dictionary
        if selected_symbol is not None:
            symbol = stock_symbols_dict.get(selected_symbol)
        st.sidebar.divider()
        st.sidebar.subheader("Weather")
        weather_variable = st.sidebar.selectbox("Weather variable: ",
                                                ["Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"],
                                                index=None,
                                                placeholder="Choose a weather variable")

        region = st.sidebar.selectbox("Weather region:", ["London", "New York", "Paris"],
                                      index=None,
                                      placeholder="Choose a weather region")
        st.sidebar.divider()
        st.sidebar.subheader("Time")
        timeframes = fetch_timeframes_intervals()
        timeframe = st.sidebar.selectbox("Time period:", list(timeframes.keys()))

        interval = st.sidebar.selectbox("Interval:", timeframes[timeframe], index=None, placeholder="Choose an interval")

        return {"stock": symbol, "variable": weather_variable, "region": region, "period": timeframe,
                "interval": interval}


    def stock_graph(self, user_filters):
        selected_symbol = user_filters[next(iter(user_filters))]
        stock_symbols_dict = fetch_stock_symbols()
        symbol = list(stock_symbols_dict.keys())[list(stock_symbols_dict.values()).index(selected_symbol)]
        st.subheader(f"{symbol} Stock")
        financial_historical_data = fetch_stock_history(user_filters["stock"],
                                                        period=user_filters["period"],
                                                        interval=user_filters["interval"])
        plot_historical_data(financial_historical_data)

    def weather_data(self, user_filters, start_date, end_date, units):
        data = weather_data_intervals(user_filters["region"],
                                           units,
                                           start_date.strftime("%Y/%m/%d/%H/%M"),
                                           end_date.strftime("%Y/%m/%d/%H/%M"))
        if user_filters["period"] == "1y":
            df = extract_relevant_data(data[1:])
        else:
            df = extract_relevant_data(data)
        return df

    def plot_graph(self, user_filters, df):
        plot_weather_graph(df, user_filters["variable"])

    def check_inputs(self, user_filters):
        inputs_given = True
        for key in user_filters:
            if user_filters[key] is None:
                inputs_given = False
        return inputs_given

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

    def run(self) -> None:
        # st.set_page_config(page_title="Historic Graphs", page_icon="📈", layout="wide")
        st.title("Historic Graphs")
        st.caption(":blue[_Historic graphs for stock prices against time and weather variables against time._]")

        if "report_button_clicked" not in st.session_state:
            st.session_state["report_button_clicked"] = False

        user_filters = self.sidebar()
        units = "metric"

        if self.check_inputs(user_filters):
            today = datetime.date.today()
            start_date = (go_back(today, user_filters["period"]))
            end_date = today
            self.stock_graph(user_filters)
            st.subheader(f"{user_filters['variable']} in {user_filters['region']}")
            weather_df = self.weather_data(user_filters, start_date, end_date, units)
            self.plot_graph(user_filters, weather_df)
        else:
            st.warning("Please fill in all required filters in the sidebar.")

        # Report bug feature (nested button)
        if st.button("Report an Issue"):
            st.session_state["report_button_clicked"] = True

        if st.session_state["report_button_clicked"]:
            message = st.text_area("Type the issue here:", "", key="message_area")  # Add key for hiding
            if st.button("Send"):
                # Perform action with the message, such as sending it
                self.send_email("New message: Problem on Historic Graphs page 😱", message)
                st.session_state["report_button_clicked"] = False  # Reset session state
                st.success("Thank you for your message!")

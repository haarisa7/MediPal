import streamlit as st
import toml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from data.finance_data import fetch_stock_symbols
from data.finance_data import fetch_timeframes_intervals
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from data.nn_finance_data import get_forecast_weather_df
from data.nn_finance_data import get_stock_data
from data.nn_finance_data import get_stock_start_date
from data.nn_data import join_data
from data.nn_data import check_inputs
from data.nn_weather_data import get_forecast_weather_data
from data.nn_weather_data import weather_data
from datetime import date
from hydralit import HydraHeadApp

class LinearRegressionAnalysis(HydraHeadApp):

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
        weather_variable = st.sidebar.selectbox("Weather variable:", ["Temperature", "Humidity", "Wind Speed"], index=None,
                                                placeholder="Choose a weather variable")

        region = st.sidebar.selectbox("Weather region:", ["London", "New York", "Paris"], index=None,
                                      placeholder="Choose a weather region")
        st.sidebar.divider()
        st.sidebar.subheader("Time")
        timeframes = fetch_timeframes_intervals()
        time_period = st.sidebar.selectbox("Time period", list(timeframes.keys()), index=None,
                                           placeholder="Choose a time period")

        return {"stock": stock, "variable": weather_variable, "region": region, "period": time_period}


    def display_predicted_graphs(self, merged_weather_and_stock_df, merged_df, chosen_variable, chosen_stock, region):
        variable_to_column = {"Temperature": 1, "Wind Speed": 2, "Precipitation": 3, "Humidity": 4, "Pressure": 5}
        selected_column = variable_to_column[chosen_variable]
        stock_symbols_dict = fetch_stock_symbols()
        symbol = list(stock_symbols_dict.keys())[list(stock_symbols_dict.values()).index(chosen_stock)]

        fig = go.Figure()
        # actual data
        fig.add_trace(
            go.Scatter(x=merged_weather_and_stock_df["Date"], y=merged_weather_and_stock_df[chosen_variable], mode='lines',
                       name=chosen_variable,
                       line=dict(color='#FF0000')))
        fig.add_trace(
            go.Scatter(x=merged_weather_and_stock_df["Date"], y=merged_weather_and_stock_df['Close'], mode='lines',
                       name=symbol, yaxis='y2',
                       line=dict(color='#0000FF')))
        # forecasted data
        fig.add_trace(
            go.Scatter(x=merged_df[0], y=merged_df[selected_column], mode='lines', name=chosen_variable + " Prediction",
                       line=dict(color='#FF0000', dash='dash')))
        fig.add_trace(
            go.Scatter(x=merged_df[0], y=merged_df['Close'], mode='lines', name=symbol + " Prediction", yaxis='y2',
                       line=dict(color='#0000FF', dash='dash')))

        # add a dashed trace that goes from the last point of the original data to the first point of the forecasted data
        fig.add_trace(go.Scatter(x=[merged_weather_and_stock_df["Date"].iloc[-1], merged_df[0].iloc[0]],
                                 y=[merged_weather_and_stock_df['Close'].iloc[-1], merged_df['Close'].iloc[0]],
                                 mode='lines', name=symbol, showlegend=False, yaxis='y2',
                                 line=dict(color='#0000FF', dash='dash')))
        fig.add_trace(go.Scatter(x=[merged_weather_and_stock_df["Date"].iloc[-1], merged_df[0].iloc[0]],
                                 y=[merged_weather_and_stock_df[chosen_variable].iloc[-1],
                                    merged_df[selected_column].iloc[0]], mode='lines', name=chosen_variable,
                                 showlegend=False, line=dict(color='#FF0000', dash='dash')))

        # allowing temp to have C on it
        chosen_variable1 = chosen_variable
        chosen_variable2 = chosen_variable

        if chosen_variable2 == "Temperature":
            chosen_variable2 = "Temperature (°C)"

        fig.update_layout(title=f"{symbol} Stock against Predicted {chosen_variable1} in {region}",
                          xaxis_title="Date",
                          height=500,
                          yaxis=dict(title=chosen_variable2, side='left'),
                          yaxis2=dict(title=symbol, overlaying='y', side='right'))
        fig.update_layout()
        st.plotly_chart(fig, use_container_width=True)


    def calculate_linear_model(self, merged_df, chosen_variable, chosen_stock, region):
        stock_symbols_dict = fetch_stock_symbols()
        symbol = list(stock_symbols_dict.keys())[list(stock_symbols_dict.values()).index(chosen_stock)]
        # Plotting stock data against weather data each day as a scatter graph
        fig = go.Figure()

        # allowing temp to have C on it
        chosen_variable1 = chosen_variable
        chosen_variable2 = chosen_variable

        if chosen_variable2 == "Temperature":
            chosen_variable2 = "Temperature (°C)"

        fig.add_trace(go.Scatter(x=merged_df[chosen_variable1], y=merged_df['Close'], mode='markers'))
        fig.update_layout(title=f"{symbol} Stock against {chosen_variable1} in {region}",
                          xaxis_title=chosen_variable2,
                          yaxis_title="Stock Price",
                          height=500, showlegend=False)
        # Drawing a straight line through this scatter graph and calculating a linear regression model
        model = LinearRegression()
        # split the data into training data and test data
        x_train, x_test, y_train, y_test = train_test_split(merged_df[[chosen_variable]], merged_df['Close'], test_size=0.2,
                                                            random_state=0)
        # fit the model to the training data
        model.fit(x_train, y_train)
        m = model.coef_[0]
        c = model.intercept_
        # Plot this on the scatter graph
        x = np.linspace(merged_df[chosen_variable].min(), merged_df[chosen_variable].max(), 100)
        y = m * x + c
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='red'), showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"The linear model is: y = {m:.2f}x + {c:.2f}")

        return model


    def calculate_forecast_stock_data(self, predicted_weather_df, model, chosen_variable):
        variable_to_column = {"Temperature": 1, "Wind Speed": 2, "Precipitation": 3, "Humidity": 4, "Pressure": 5}
        selected_column = variable_to_column[chosen_variable]
        x = np.array(predicted_weather_df[selected_column]).reshape(-1, 1)
        y = model.predict(x)
        predicted_weather_df["Close"] = y
        return predicted_weather_df


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
        st.title("Linear Regression Analysis")
        st.caption(":blue[_Linear Regression Model to predict stock prices against time using weather variables._]")

        if "report_button_clicked" not in st.session_state:
            st.session_state["report_button_clicked"] = False

        user_filters = self.sidebar()
        units = "metric"

        if check_inputs(user_filters):
            # 15 days of forecast weather data
            all_weather_data = get_forecast_weather_data(user_filters["region"], "68d1484b8e59a8cbd7100ef5de8a2b51", units)
            forecast_weather_df = get_forecast_weather_df(all_weather_data).iloc()[1:]

            # prediction - 1y

            stock_df_prediction = get_stock_data(user_filters["stock"], "1y")
            start_date_prediction = get_stock_start_date(stock_df_prediction)
            today = date.today()
            weather_df_prediction = weather_data(user_filters, start_date_prediction, today, units, is1y=True)

            # display

            stock_df_display = get_stock_data(user_filters["stock"], user_filters["period"])
            start_date_display = get_stock_start_date(stock_df_display)
            if user_filters["period"] == "1y":
                weather_df_display = weather_data(user_filters, start_date_display, today, units, is1y=True)
            else:
                weather_df_display = weather_data(user_filters, start_date_display, today, units)
            weather_df_display.columns = ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]
            merged_df_time_period = join_data(weather_df_display, stock_df_display, user_filters["variable"])
            weather_df_prediction.columns = ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]
            merged_df_1y = join_data(weather_df_prediction, stock_df_prediction, user_filters["variable"])
            model = self.calculate_linear_model(merged_df_1y, user_filters["variable"], user_filters["stock"],
                                                user_filters["region"])
            merged_df = self.calculate_forecast_stock_data(forecast_weather_df, model, user_filters["variable"])
            self.display_predicted_graphs(merged_df_time_period, merged_df, user_filters["variable"], user_filters["stock"],
                                          user_filters["region"])

        else:
            st.warning("Please fill in all required filters in the sidebar.")

        # Report bug feature (nested button)
        if st.button("Report an Issue"):
            st.session_state["report_button_clicked"] = True

        if st.session_state["report_button_clicked"]:
            message = st.text_area("Type the issue here:", "", key="message_area")  # Add key for hiding
            if st.button("Send"):
                # Perform action with the message, such as sending it
                self.send_email("New message: Problem on Linear Regression page 😱", message)
                st.session_state["report_button_clicked"] = False  # Reset session state
                st.success("Thank you for your message!")
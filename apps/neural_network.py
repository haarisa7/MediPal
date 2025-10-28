import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import numpy as np
import pandas as pd
import tensorflow as tf
import toml
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.src.layers import Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from data.finance_data import fetch_stock_symbols, fetch_timeframes_intervals
from data.nn_finance_data import get_forecast_weather_df, get_stock_data, get_stock_start_date
from data.nn_data import join_data, check_inputs
from data.nn_weather_data import get_forecast_weather_data, get_weather_data_one_year, weather_data
from sklearn.model_selection import train_test_split
from hydralit import HydraHeadApp
class NeuralNetwork(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def sidebar(self):
        st.sidebar.subheader("Stock")
        stock_symbols_dict = fetch_stock_symbols()
        selected_symbol = st.sidebar.selectbox("Stock:", list(stock_symbols_dict.keys()), index=None,
                                               placeholder="Choose a stock")
        stock = None
        if selected_symbol is not None:
            stock = stock_symbols_dict.get(selected_symbol)

        st.sidebar.divider()
        st.sidebar.subheader("Weather")
        weather_variable = st.sidebar.selectbox("Weather variable:", ["Temperature", "Humidity", "Wind Speed"], index=0,
                                                placeholder="Choose a weather variable")

        region = st.sidebar.selectbox("Weather region:", ["London", "New York", "Paris"], index=0,
                                      placeholder="Choose a weather region")
        st.sidebar.divider()
        st.sidebar.subheader("Time")
        time_period = st.sidebar.selectbox("Time period", list(fetch_timeframes_intervals().keys()), index=0,
                                           placeholder="Choose a time period")

        return {"stock": stock, "variable": weather_variable, "region": region, "period": time_period}

    # functions used for model training
    def preprocess_data(self, df, chosen_weather_variable):
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values(by='Date', inplace=True)

        # x_train and y_train are taken from 'features'
        features = df[['Close', chosen_weather_variable]].values.reshape(-1, 2)

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_features = scaler.fit_transform(features)

        n_steps = 15
        x_train, y_train = [], []
        for i in range(n_steps, len(scaled_features)):
            x_train.append(scaled_features[i - n_steps:i, :])
            y_train.append(scaled_features[i,
                           :])  # y_train includes the 15th day stock close as well as weather attribute to feed back into model when predicting

        x_train, y_train = np.array(x_train), np.array(y_train)

        # Ensuring the correct shape for x_train
        x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 2)
        return x_train, y_train, scaler

    def train_lstm_model(self, x_train, y_train):
        # Building the LSTM model
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 2)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=2)  # Adjusted to predict 2 outputs
        ])
        # Compile model
        model.compile(optimizer='adam', loss='mse')

        # Train model
        model.fit(x_train, y_train, epochs=100, batch_size=32)
        model.save('model2.keras')

        return model

    def evaluate_model(self, model, X_test, y_test):
        # Evaluate model
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        print("Mean Absolute Error:", mae)
        return mae

    def create_model(self, merged_df, chosen_weather_variable):
        # Preprocess the data with the selected weather variable
        scalar = MinMaxScaler(feature_range=(0, 1))

        x_train, y_train, scaler = self.preprocess_data(merged_df, chosen_weather_variable)

        # Split the data into training and test sets
        x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

        # Train the LSTM model
        model = self.train_lstm_model(x_train, y_train)

        return model, scaler

    def predict_future_stock_prices(self, model, scaler, merged_df_1y, forecast_weather_data, chosen_variable, time_period,
                                    n_steps=15):
        forecast_weather_data['Close'] = merged_df_1y['Close'].iloc[-1]
        forecast_weather_data = forecast_weather_data[['Date', 'Close', chosen_variable]]
        n_steps = 15  # Assuming this is the number of past days you want to use for each prediction
        input_features = merged_df_1y[['Close', chosen_variable]].values[-n_steps:].reshape(-1, 2)

        scaled_features = scaler.fit_transform(input_features)

        predictions = []
        current_sequence = scaled_features
        forecast_weather_data_arr = forecast_weather_data[chosen_variable].to_numpy()
        print(forecast_weather_data_arr)
        # predict the next x days
        for i in range(15):
            prediction_scaled = model.predict(current_sequence.reshape(1, n_steps, 2))

            prediction = scaler.inverse_transform(prediction_scaled)[0]  # Assuming prediction_scaled shape is (1, 2)

            print(prediction[1])
            prediction[1] = forecast_weather_data_arr[i]

            predictions.append(prediction)

            new_day_scaled = scaler.transform([prediction])
            current_sequence = np.vstack((current_sequence[1:], new_day_scaled))

        stock_prices = [pred[0] for pred in predictions]
        stockPrices = np.array(stock_prices)
        forecast_weather_data['Close'] = stockPrices[0:15]
        return forecast_weather_data

    def display_predicted_graphs(self, predicted_df, historical_merged_df , forecast_weather_df, chosen_variable, chosen_stock, region):
        stock_symbols_dict = fetch_stock_symbols()
        symbol = list(stock_symbols_dict.keys())[list(stock_symbols_dict.values()).index(chosen_stock)]

        fig = go.Figure()
        # past stock data:
        fig.add_trace(
            go.Scatter(x=historical_merged_df["Date"], y=historical_merged_df[chosen_variable],
                       mode='lines',
                       name=chosen_variable,
                       line=dict(color='#FF0000')))
        fig.add_trace(
            go.Scatter(x=historical_merged_df["Date"], y=historical_merged_df['Close'], mode='lines',
                       name=symbol, yaxis='y2',
                       line=dict(color='#0000FF')))

        # past weather attribute
        fig.add_trace(
            go.Scatter(x=forecast_weather_df['Date'], y=forecast_weather_df[chosen_variable], mode='lines', name=chosen_variable + " Prediction",
                       line=dict(color='#FF0000', dash='dash')))

        fig.add_trace(
            go.Scatter(x=forecast_weather_df['Date'], y=predicted_df['Close'], mode='lines',
                       name=symbol + " Prediction",yaxis='y2',
                       line=dict(color='#0000FF', dash='dash')))

        # add a dashed trace that goes from the last point of the original data to the first point of the forecasted data
        fig.add_trace(go.Scatter(x=[historical_merged_df['Date'].iloc[-1], forecast_weather_df['Date'].iloc[0]],
                                 y=[historical_merged_df['Close'].iloc[-1], predicted_df['Close'].iloc[0]],
                                 mode='lines', name=symbol, showlegend=False, yaxis='y2',
                                 line=dict(color='#0000FF', dash='dash')))

        fig.add_trace(go.Scatter(x=[historical_merged_df["Date"].iloc[-1], forecast_weather_df['Date'].iloc[0]],
                                 y=[historical_merged_df[chosen_variable].iloc[-1],
                                    forecast_weather_df[chosen_variable].iloc[0]], mode='lines', name=chosen_variable,
                                 showlegend=False, line=dict(color='#FF0000', dash='dash')))

        # allowing temp to have C on it
        chosen_variable1 = chosen_variable

        if chosen_variable1 == "Temperature":
            chosen_variable1 = "Temperature (°C)"

        fig.update_layout(title=f"{symbol} Stock against Predicted {chosen_variable} in {region}",
                          xaxis_title="Date",
                          height=500,
                          yaxis=dict(title=chosen_variable1, side='left'),
                          yaxis2=dict(title=symbol, overlaying='y', side='right'))
        fig.update_layout()
        st.plotly_chart(fig, use_container_width=True)

    def resolve_period_to_days(self, period):
        if period == "5d":
            return 5
        elif period == "1mo":
            return 30
        elif period == "3mo":
            return 90
        elif period == "6mo":
            return 180
        elif period == "1y":
            return 365
        else:
            return None

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
        st.title("LSTM Neural Network")
        st.caption(":blue[_LSTM Neural Network Model to predict stock prices using merged data._]")

        if "report_button_clicked" not in st.session_state:
            st.session_state["report_button_clicked"] = False

        user_filters = self.sidebar()
        units = "metric"

        end_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        all_forecast_weather_data = get_forecast_weather_data(user_filters["region"],
                                                              "68d1484b8e59a8cbd7100ef5de8a2b51",
                                                              units)
        forecast_weather_df = get_forecast_weather_df(all_forecast_weather_data, call_flag="neuralNetworks").iloc()[1:]

        print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
        print("Physical devices:", tf.config.list_physical_devices())
        if tf.test.gpu_device_name():
            print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))
        else:
            print("Please install GPU version of TF")

        if check_inputs(user_filters):
            # 1yr merged df to train the model
            all_weather_data = get_weather_data_one_year(user_filters['region'], "metric", end_date)
            all_stock_data = get_stock_data(user_filters["stock"], "1y")
            merged_df_1y = join_data(all_weather_data, all_stock_data, user_filters['variable'])

            # Check if model and scaler are already in session state
            if "model" not in st.session_state:
                model, scaler = self.create_model(merged_df_1y, user_filters['variable'])
                st.session_state["model"] = model
                st.session_state["scaler"] = scaler
            else:
                model = st.session_state["model"]
                scaler = st.session_state["scaler"]

            # model, _ = self.create_model(merged_df_1y, user_filters['variable'])
            # # If needed we can load pre-trained model (for demo):
            # # model = models.load_model('model.keras')
            #
            # scaler = MinMaxScaler(feature_range=(0, 1))

            predict_prices_df = self.predict_future_stock_prices(model, scaler, merged_df_1y, forecast_weather_df,
                                                            user_filters['variable'],
                                                            self.resolve_period_to_days(user_filters["period"]))

            # past stock and weather data for graph
            stock_df_display = get_stock_data(user_filters["stock"], user_filters["period"])
            start_date_display = get_stock_start_date(stock_df_display)
            weather_df_display = weather_data(user_filters, start_date_display, (date.today()), units,  True if user_filters["period"] == "1y" else False)
            weather_df_display.columns = ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]
            historical_merged_df = join_data(weather_df_display, stock_df_display, user_filters['variable'])

            self.display_predicted_graphs(predict_prices_df, historical_merged_df, forecast_weather_df, user_filters['variable'], user_filters["stock"], user_filters["region"])

        else:
            st.warning("Please fill in all required filters in the sidebar.")

        # Report bug feature (nested button)
        if st.button("Report an Issue"):
            st.session_state["report_button_clicked"] = True

        if st.session_state["report_button_clicked"]:
            message = st.text_area("Type the issue here:", "", key="message_area")  # Add key for hiding
            if st.button("Send"):
                # Perform action with the message, such as sending it
                self.send_email("New message: Problem on LSTM Neural Network page 😱", message)
                st.session_state["report_button_clicked"] = False  # Reset session state
                st.success("Thank you for your message!")
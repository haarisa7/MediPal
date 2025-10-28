from data.finance_data import fetch_stock_history
import pandas as pd
from collections import defaultdict
from datetime import datetime


def get_forecast_weather_df(all_weather_data, call_flag=None):
    # Extract information for selected variable information
    data = defaultdict(lambda: {'temp': [], 'wind_speed': [], 'precipitation': [], 'humidity': [], 'pressure': []})
    for entry in all_weather_data['list']:
        date = datetime.fromtimestamp(entry['dt']).date()
        data[date]['temp'].append(entry['temp']['day'])
        data[date]['wind_speed'].append(entry['speed'])
        for weather_condition in entry['weather']:
            if weather_condition['main'] == 'Rain':
                data[date]['precipitation'].append(entry['rain'])
            elif weather_condition['main'] == 'Snow':
                data[date]['precipitation'].append(entry['snow'])

        data[date]['humidity'].append(entry['humidity'])
        data[date]['pressure'].append(entry['pressure'])

    # Calculate weather values for each day
    daily_data = []
    for date, values in data.items():
        temperature = sum(values['temp']) / len(values['temp'])
        wind_speed = sum(values['wind_speed']) / len(values['wind_speed'])
        precipitation = sum(values['precipitation'])  # Total precipitation instead of average
        humidity = sum(values['humidity']) / len(values['humidity'])
        pressure = sum(values['pressure']) / len(values['pressure'])
        daily_data.append((date, temperature, wind_speed, precipitation, humidity, pressure))
    if call_flag != None:
        column_names = ['Date', 'Temperature', 'Wind Speed', 'Precipitation', 'Humidity', 'Pressure']
        forecast_weather_df = pd.DataFrame(daily_data, columns=column_names)
        return forecast_weather_df
    else:
        forecast_weather_df = pd.DataFrame(daily_data)
        return forecast_weather_df


def get_stock_data(stock, time_period):
    stock_data = fetch_stock_history(stock, time_period, "1d")
    return stock_data["Close"]


def get_stock_start_date(df):
    """
    Stock data may have earlier start date due to lack of stock data on weekends and bank holidays.
    Function gets the start date that should be used to gather weather data
    """
    start_date = df.index.values[0]
    start_date = pd.to_datetime(start_date).date()
    return start_date
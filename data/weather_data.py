import requests
import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

def extract_relevant_data(all_weather_data: list[dict]):
    data = defaultdict(lambda: {'temp': [], 'wind_speed': [], 'precipitation': [], 'humidity': [], 'pressure': []})
    for weather_data in all_weather_data:
        for entry in weather_data['list']:
            date = datetime.fromtimestamp(entry['dt']).date()
            data[date]['temp'].append(entry['main']['temp'])
            data[date]['wind_speed'].append(entry['wind']['speed'])
            for weather_condition in entry['weather']:
                if weather_condition['main'] == 'Rain':
                    data[date]['precipitation'].append(entry.get('rain', {}).get('1h', 0))
                elif weather_condition['main'] == 'Snow':
                    data[date]['precipitation'].append(entry.get('snow', {}).get('1h', 0))
                else:
                    data[date]['precipitation'].append(0)

            data[date]['humidity'].append(entry['main']['humidity'])
            data[date]['pressure'].append(entry['main']['pressure'])

    daily_data = []
    for date, values in data.items():
        temperature = sum(values['temp']) / len(values['temp'])
        wind_speed = sum(values['wind_speed']) / len(values['wind_speed'])
        precipitation = sum(values['precipitation'])  # Total precipitation instead of average
        humidity = sum(values['humidity']) / len(values['humidity'])
        pressure = sum(values['pressure']) / len(values['pressure'])
        daily_data.append((date, temperature, wind_speed, precipitation, humidity, pressure))
    df = pd.DataFrame(daily_data)
    return df

def plot_weather_graph(df, weather_variable):

    df.columns = ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df[weather_variable], mode='lines', name=weather_variable))
    if weather_variable == "Temperature":
        weather_variable = weather_variable + " (°C)"
    fig.update_layout(xaxis_title="Date", yaxis_title=weather_variable)
    st.plotly_chart(fig, use_container_width=True)

@st.cache_resource
def get_weather_data(_api_key, city_name, units, start, end) -> dict:
    start_date = int(datetime.strptime(start.strftime("%Y/%m/%d/%H/%M"), "%Y/%m/%d/%H/%M").timestamp())
    end_date = int(datetime.strptime(end.strftime("%Y/%m/%d/%H/%M"), "%Y/%m/%d/%H/%M").timestamp())

    base_url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        "q": city_name,
        'type': 'day',
        "start": start_date,
        "end": end_date,
        "appid": _api_key,
        "units": units
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

def weather_data_intervals(region, units, start, end):
    all_weather_data = []

    interval_duration = 8

    start_date_object = datetime.strptime(start, "%Y/%m/%d/%H/%M")
    end_date_object = datetime.strptime(end, "%Y/%m/%d/%H/%M")

    total_days = (end_date_object - start_date_object).days + 1
    num_intervals = total_days // interval_duration
    remaining_days = total_days % interval_duration
    for i in range(num_intervals):
        interval_start_date = start_date_object + relativedelta(days=i * interval_duration)
        interval_end_date = interval_start_date + relativedelta(days=interval_duration - 1)
        weather_data = get_weather_data('68d1484b8e59a8cbd7100ef5de8a2b51', region, units, interval_start_date,
                                        interval_end_date)
        all_weather_data.append(weather_data)
    if remaining_days > 0:
        final_interval_start_date = start_date_object + relativedelta(days=num_intervals * interval_duration)
        final_interval_end_date = end_date_object

        weather_data = get_weather_data('68d1484b8e59a8cbd7100ef5de8a2b51', region, units,
                                        final_interval_start_date,
                                        final_interval_end_date)
        all_weather_data.append(weather_data)
    return all_weather_data
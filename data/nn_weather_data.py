from datetime import date
from data.weather_data import weather_data_intervals, extract_relevant_data
import requests
import pandas as pd
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

def weather_data(user_filters, start_date, end_date, units, is1y=False):
    data = weather_data_intervals(user_filters["region"],
                                  units,
                                  start_date.strftime("%Y/%m/%d/%H/%M"),
                                  end_date.strftime("%Y/%m/%d/%H/%M"))
    if is1y==True:
        df = extract_relevant_data(data[1:])
    else:
        df = extract_relevant_data(data)
    return df


def get_forecast_weather_data(city_name, _api_key, units):
    base_url = "http://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "q": city_name,
        'type': 'day',
        "appid": _api_key,
        "units": units,
        "cnt": 16
    }
    response = requests.get(base_url, params=params)
    all_weather_data = response.json()
    return all_weather_data


def get_filtered_weather_data(weather_variable, region, period, start_date):
    end_date = date.today()
    data = weather_data_intervals(region, "metric", start_date.strftime("%Y/%m/%d/%H/%M"),
                                  end_date.strftime("%Y/%m/%d/%H/%M"))
    if period == "1y":
        df = extract_relevant_data(data[1:])
    else:
        df = extract_relevant_data(data)
    df.columns = ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]

    filtered_df = df.reindex(columns=["Date", weather_variable])
    return filtered_df

def extract_relevant_data_neural_network(all_weather_data: list[dict]):
    data = defaultdict(lambda: {'temp': [], 'wind_speed': [], 'precipitation': [], 'humidity': [], 'pressure': []})
    for weather_data in all_weather_data:
        if 'list' in weather_data:
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
    column_names = ['Date', 'Temperature', 'Wind Speed', 'Precipitation', 'Humidity', 'Pressure']
    df = pd.DataFrame(daily_data, columns=column_names)
    return df
def get_weather_data_one_year(region, units, end_date):
    # Calculate start and end dates
    start_date = end_date - timedelta(days=400)
    # Get weather data intervals
    all_weather_data = weather_data_intervals(region, units, start_date.strftime("%Y/%m/%d/%H/%M"),
                                              end_date.strftime("%Y/%m/%d/%H/%M"))

    # Extract relevant data
    weather_df = extract_relevant_data_neural_network(all_weather_data)

    return weather_df
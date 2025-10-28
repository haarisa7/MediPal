from datetime import datetime
import pandas as pd
from data.nn_weather_data import weather_data, get_filtered_weather_data
from data.nn_weather_data import get_forecast_weather_data, get_weather_data_one_year, extract_relevant_data_neural_network
import pytest
from data.weather_data import weather_data_intervals
from datetime import timedelta

def test_weather_data():
    # Define user filters
    user_filters = {
        "region": "London",
        "period": "5d"
    }

    # Define start and end dates
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 2, 1)

    # Define units
    units = "metric"

    # Call the function with the test data
    result_df = weather_data(user_filters, start_date, end_date, units)

    # Assert that the result is a DataFrame
    assert isinstance(result_df, pd.DataFrame), "Output should be a pandas DataFrame"

    # Assert that the DataFrame is not empty
    assert not result_df.empty, "Output DataFrame should not be empty"

    # Assert that the DataFrame has the correct columns
    expected_columns = [0, 1, 2, 3, 4, 5]
    assert list(result_df.columns) == expected_columns, "Output DataFrame should have the correct columns"

    # test if 1y is True
    result_df_1y = weather_data(user_filters, start_date, end_date, units, is1y=True)
    assert isinstance(result_df_1y, pd.DataFrame), "Output should be a pandas DataFrame"

def test_get_filtered_weather_data():
    # Define user filters
    region = "London"
    start_date = datetime(2024, 1, 1)

    # Call the function with the test data
    result_df = get_filtered_weather_data("Temperature", region, "1mo", start_date)

    # Assert that the result is a DataFrame
    assert isinstance(result_df, pd.DataFrame), "Output should be a pandas DataFrame"

    # Assert that the DataFrame is not empty
    assert not result_df.empty, "Output DataFrame should not be empty"

    # Assert that the DataFrame has the correct columns
    expected_columns = ["Date", "Temperature"]
    assert list(result_df.columns) == expected_columns, "Output DataFrame should have the correct columns"

    ## check if period is 1y

    result_df_1y = get_filtered_weather_data("Temperature", region, "1y", start_date)
    assert isinstance(result_df_1y, pd.DataFrame), "Output should be a pandas DataFrame"

def test_get_weather_data_one_year():

    end_date = datetime(2024, 1, 1)
    expected_df = get_weather_data_one_year("London", "metric", end_date)
    assert len(expected_df) == 272

def test_extract_relevant_data_neural_network():
    end_date = datetime(2024, 3, 28)
    start_date = datetime(2024, 3, 23)
    all_weather_data = weather_data_intervals("London", "metric", start_date.strftime("%Y/%m/%d/%H/%M"), end_date.strftime("%Y/%m/%d/%H/%M"))
    actual_df = extract_relevant_data_neural_network(all_weather_data)
    assert len(actual_df) == 6

def test_get_forecast_weather_data():

    expected_weather_data = get_forecast_weather_data("London", "68d1484b8e59a8cbd7100ef5de8a2b51", "metric")
    dates = []
    for entry in expected_weather_data['list']:
        dates.append(entry['dt'])
    assert len(dates) == 16


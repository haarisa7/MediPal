from datetime import datetime
import pandas as pd
from data.nn_finance_data import get_stock_data
from data.nn_finance_data import get_forecast_weather_df, get_stock_start_date
import pytest

def test_get_forecast_weather_df():
    # Test data
    all_weather_data = {
        'list': [
            {
                'dt': 1640995200,  # 2022-01-01
                'temp': {'day': 10},
                'speed': 5,
                'weather': [{'main': 'Rain'}],
                'rain': 3,
                'humidity': 80,
                'pressure': 1000
            },
            {
                'dt': 1641081600,  # 2022-01-02
                'temp': {'day': 15},
                'speed': 10,
                'weather': [{'main': 'Snow'}],
                'snow': 2,
                'humidity': 70,
                'pressure': 1005
            }
        ]
    }

    # Expected result
    expected_df = pd.DataFrame([
        (datetime(2022, 1, 1).date(), 10.0, 5.0, 3, 80.0, 1000.0),
        (datetime(2022, 1, 2).date(), 15.0, 10.0, 2, 70.0, 1005.0)
    ], columns=[0, 1, 2, 3, 4, 5])

    # Call the function with the test data
    result_df = get_forecast_weather_df(all_weather_data)

    # Assert that the result is as expected
    pd.testing.assert_frame_equal(result_df, expected_df)

    expected_df_call_flag = pd.DataFrame([
        (datetime(2022, 1, 1).date(), 10.0, 5.0, 3, 80.0, 1000.0),
        (datetime(2022, 1, 2).date(), 15.0, 10.0, 2, 70.0, 1005.0)
    ], columns=['Date', 'Temperature', 'Wind Speed', 'Precipitation', 'Humidity', 'Pressure'])

    # testing if call_flag is for Neural Network
    result_df = get_forecast_weather_df(all_weather_data, "neuralNetworks")

    # Assert that the result is as expected
    pd.testing.assert_frame_equal(result_df, expected_df_call_flag)


def test_get_stock_data():
    # Test for a known stock over a known time period
    stock_data = get_stock_data('AAPL', '1mo')
    assert isinstance(stock_data, pd.Series), "Output should be a pandas Series"
    assert not stock_data.empty, "Output series should not be empty"
def test_get_stock_start_date():
    # Test data
    df = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104]
    }, index=pd.date_range(start='2022-01-01', periods=5, freq='D'))

    # Expected result
    expected_start_date = datetime(2022, 1, 1).date()

    # Call the function with the test data
    result_start_date = get_stock_start_date(df)

    # Assert that the result is as expected
    assert result_start_date == expected_start_date, "Start date should match the first date in the DataFrame"

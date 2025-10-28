from datetime import datetime
import pandas as pd
from data.nn_finance_data import get_stock_data
from data.nn_data import check_inputs, join_data
from data.nn_weather_data import get_filtered_weather_data


def test_check_inputs():
    # Test for all inputs given
    assert check_inputs({"stock": "AAPL", "variable": "Temperature", "region": "London", "period": "1d"}) == True

    # Test for no inputs given
    assert check_inputs({"stock": None, "variable": None, "region": None, "period": None}) == False

    # Test for some inputs given
    assert check_inputs({"stock": None, "variable": "Temperature", "region": None, "period": "1d"}) == False

    # Test for some inputs given
    assert check_inputs({"stock": "AAPL", "variable": None, "region": None, "period": None}) == False


def test_join_data():
    weather_df = get_filtered_weather_data("Temperature", "London", "5d", datetime(2024, 1, 1))
    stock_df = get_stock_data("^FTSE", "5d")
    assert join_data(weather_df, stock_df, "Temperature").shape == (5, 3)

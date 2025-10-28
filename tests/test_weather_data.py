import pandas as pd
from datetime import datetime
from data.weather_data import extract_relevant_data, get_weather_data, weather_data_intervals, plot_weather_graph


def test_extract_relevant_data():
    end_date = datetime(2024, 3, 28)
    start_date = datetime(2024, 3, 23)
    all_weather_data = weather_data_intervals("London",
                                  "metrics",
                                  start_date.strftime("%Y/%m/%d/%H/%M"),
                                  end_date.strftime("%Y/%m/%d/%H/%M"))
    actual_df = extract_relevant_data(all_weather_data)
    assert len(actual_df) == 6

def test_weather_data_intervals():
    # Test for a known city over a known time period
    all_weather_data = weather_data_intervals('London', 'metric', '2022/01/01/00/00', '2022/01/31/00/00')
    assert isinstance(all_weather_data, list), "Output should be a list"
    assert all(
        isinstance(item, dict) for item in all_weather_data), "All items in the output list should be dictionaries"

def  test_get_weather_data():
    end_date = datetime(2024, 3, 29)
    start_date = datetime(2024, 3, 24)
    expected_weather_data = get_weather_data("68d1484b8e59a8cbd7100ef5de8a2b51", "London", "metric", start_date, end_date)
    # assert amount of data
    dates = []
    for entry in expected_weather_data['list']:
        dates.append(entry['dt'])
    assert len(dates) == 121

def test_plot_weather_graph():
    df = pd.DataFrame([
            (datetime(2022, 1, 1).date(), 10.0, 5.0, 3, 80.0, 1000.0),
            (datetime(2022, 1, 2).date(), 15.0, 10.0, 2, 70.0, 1005.0)
        ], columns=[0, 1, 2, 3, 4, 5])
    weather_variable = "Temperature"
    df.columns = ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]
    plot_weather_graph(df, weather_variable)
    assert df.columns.tolist() == ["Date", "Temperature", "Wind Speed", "Precipitation", "Humidity", "Pressure"]
    # assert x axis title
    assert df.columns[0] == "Date"
    # assert y axis title
    assert df.columns[1] == ("Temperature")

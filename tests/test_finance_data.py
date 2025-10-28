from datetime import datetime

from data.finance_data import go_back
from data.finance_data import fetch_stock_symbols
from data.finance_data import fetch_timeframes_intervals
from data.finance_data import fetch_stock_history
from data.finance_data import plot_historical_data

def test_fetch_stock_symbols():
    # Test for the stock symbols
    assert fetch_stock_symbols() == {
        "FTSE": "^FTSE",
        "GSPC": "^GSPC",
        "DJI": "^DJI",
        "IXIC": "^IXIC",
        "N225": "^N225",
        "APPL": "APPL",
        "GOOG": "GOOG",
        "IBM": "IBM",
        "AMZN": "AMZN",
        "META": "META",
        "NFLX": "NFLX",
        "TSLA": "TSLA",
    }


def test_fetch_timeframes_intervals():
    # Test for the timeframes and intervals
    assert fetch_timeframes_intervals() == {
        "5d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "1mo": ["30m", "60m", "90m", "1d"],
        "3mo": ["1d", "5d", "1wk", "1mo"],
        "6mo": ["1d", "5d", "1wk", "1mo"],
        "1y": ["1d", "5d", "1wk", "1mo"],
    }


def test_go_back():
    # Test for days
    assert go_back(datetime(2022, 12, 31), '5d') == datetime(2022, 12, 26)
    assert go_back(datetime(2022, 12, 31), '10d') == datetime(2022, 12, 21)

    # Test for months
    assert go_back(datetime(2022, 12, 31), '1mo') == datetime(2022, 11, 30)
    assert go_back(datetime(2022, 12, 31), '6mo') == datetime(2022, 6, 30)

    # Test for years
    assert go_back(datetime(2022, 12, 31), '1y') == datetime(2021, 12, 31)
    assert go_back(datetime(2022, 12, 31), '2y') == datetime(2020, 12, 31)


def test_fetch_stock_history():
    assert fetch_stock_history("^FTSE", "1mo", "1d").shape == (22,5)
    csv = fetch_stock_history("^FTSE", "1mo", "1d").to_csv()
    assert fetch_stock_history("^FTSE", "1mo", "1d").to_csv() == csv


def test_plot_historical_data():
    data = fetch_stock_history("^FTSE", "1mo", "1d")
    plot_historical_data(data)
    # assert x axis title
    assert data.columns[0] == "Open"
    assert data.columns[1] == "High"
    assert data.columns[2] == "Low"
    assert data.columns[3] == "Close"
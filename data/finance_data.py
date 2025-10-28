import pandas as pd
import yfinance as yf
import streamlit as st
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go


def plot_historical_data(historical_data):
    # Create a plot for the historical data
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=historical_data.index,
                open=historical_data["Open"],
                high=historical_data["High"],
                low=historical_data["Low"],
                close=historical_data["Close"],
            )
        ]
    )

    # add labels to the axes
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Prices"
    )

    # Customize the historical data graph
    fig.update_layout(xaxis_rangeslider_visible=False)

    # Use the native streamlit theme
    st.plotly_chart(fig, use_container_width=True)

def fetch_timeframes_intervals():
    # Create dictionary for timeframes and intervals
    timeframes = {
        "5d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "1mo": ["30m", "60m", "90m", "1d"],
        "3mo": ["1d", "5d", "1wk", "1mo"],
        "6mo": ["1d", "5d", "1wk", "1mo"],
        "1y": ["1d", "5d", "1wk", "1mo"]
    }

    # Return the dictionary
    return timeframes


def fetch_stock_symbols():
    stock_symbols = ["^FTSE", "^GSPC", "^DJI", "^IXIC", "^N225", "APPL", "GOOG", "IBM", "AMZN", "META", "NFLX", "TSLA"]
    symbol_mapping = {symbol.lstrip('^'): symbol for symbol in stock_symbols}
    return symbol_mapping

@st.cache_data
def fetch_stock_history(symbol, period, interval):
    # Pull the data for the stock index chosen
    stock_data = yf.Ticker(symbol)

    # Clean the data to only extract the columns we want
    stock_data_history = stock_data.history(period=period, interval=interval)[
        ["Open", "High", "Low", "Close", "Volume"]
    ]

    # Return the stock data
    return stock_data_history


def go_back(end_date, interval):
    unit = interval[-1]
    m_unit = interval[-2:]

    # converts the string 'timeframe' into days and subtracts from today's date
    if unit == 'd':
        quantity = int(interval[:-1])
        rd = relativedelta(days=quantity)
        return end_date - rd
    elif m_unit == 'mo':
        quantity = int(interval[:-2])
        rd = relativedelta(months=quantity)
        return end_date - rd
    elif unit == 'y':
        quantity = int(interval[:-1])
        rd = relativedelta(years=quantity)
        return end_date - rd

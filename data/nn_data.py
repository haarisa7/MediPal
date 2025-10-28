import pandas as pd


def check_inputs(user_filters):
    inputs_given = True
    for key in user_filters:
        if user_filters[key] is None:
            inputs_given = False
    return inputs_given


def join_data(weather_df, stock_df, chosen_variable):
    # Merge the stock data and weather data on the date column

    indexed_stock_data_history = pd.DataFrame(stock_df)
    indexed_stock_data_history.reset_index(inplace=True)
    indexed_stock_data_history.columns = ['Date', 'Close']
    indexed_stock_data_history["Date"] = indexed_stock_data_history["Date"].dt.date

    # Merge DataFrames
    merged_df = pd.merge(indexed_stock_data_history, weather_df, on='Date')

    # Forward fill missing values
    merged_df[chosen_variable] = merged_df[chosen_variable].ffill()
    merged_df['Close'] = merged_df['Close'].ffill()

    return merged_df

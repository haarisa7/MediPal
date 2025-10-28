import streamlit as st
from hydralit import HydraHeadApp

class HomeApp(HydraHeadApp):

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):

        st.title(":chart_with_upwards_trend: Forecaster")
        st.caption(":blue[_enhancing financial decisions_]")

        with st.container():
            st.markdown("Welcome to Forecaster, your extensive tool for analysing the intricate relationship between "
                        "financial stocks and weather data. With Forecaster, you are able to select a stock, a weather variable"
                        " and a region to analyse; with this you can investigate the historical trends, linear regression "
                        "and correlation between the stock and weather variable, and prediction for the stock using an ML "
                        "model.")

        st.divider()
        st.subheader("👼 Getting Started")
        st.markdown("To get started follow these simple steps:")
        st.markdown("1. Sign Up / Login: If you haven't already, sign up for an account or log in to your existing account.")
        st.markdown("2. If you do not wish to sign up, you can enjoy the free tier features available to you - Historic Graphs and Correlation Analysis")
        st.markdown("3. By creating an account you gain access to our premium tier features - Linear Regression and Neural Network prediction tools.")

        st.divider()
        st.subheader("🕊️ Free Tier Features Overview")
        st.markdown("There are 2 main features available in the free tier")
        with st.container():
            text, img1, img2 = st.columns(3)
            with text:
                st.caption(":blue[_Historic Graphs_]")
                st.markdown(
                    "**Description**: Use this feature to view historic weather and stock data for your selected time period.")
                st.markdown("**Steps:**")
                st.markdown("1. Select \"Historical Graphs\" from the navbar")
                st.markdown("2. Fill in the filters in the sidebar")
                st.markdown("3. The graphs will begin loading once all filters are filled.")
            with img1:
                st.image('resources/hitoric_graphs.jpg', use_column_width=True)
            with img2:
                st.image('resources/hitoric_graphs_2.jpg', use_column_width=True)

        with st.container():
            st.caption(":blue[_Correlation Analysis_]")
            text, img1, img2 = st.columns(3)
            with text:
                st.markdown(
                    "**Description**: Use this feature to create visualizations illustrating the relationship between a chosen weather variable and a stock index, and calcualate a Spearman Rank Correlation Coefficient")
                st.markdown("**Steps:**")
                st.markdown("1. Select \"Correlation Analysis\" from the navbar")
                st.markdown("2. Fill in the filters in the sidebar")
                st.markdown("3. The graphs will begin loading once all filters are filled.")
                st.markdown("4. Select multiple weather variables to get a side-by-side comparison.")
            with img1:
                st.image('resources/correlation_analysis.jpg', use_column_width=True)
            with img2:
                st.image('resources/correlation_analysis_2.jpg', use_column_width=True)

        st.divider()
        st.subheader("🐯 Premium Tier Features Overview")
        st.markdown("There are 2 main features available in the premium tier, which you can access when logged in")
        with st.container():
            st.caption(":blue[_Linear Regression_]")
            text, img1, img2 = st.columns(3)
            with text:
                st.markdown(
                    "**Description**: Use this feature to predict stock prices using weather data and a linear regression model.")
                st.markdown("**Steps:**")
                st.markdown("1. Select \"Linear Regression\" from the navbar")
                st.markdown("2. Fill in the filters in the sidebar")
                st.markdown("3. The first graph is a model that shows the linear relationship between weather and stock data.")
                st.markdown("4. The second graph is a forecast of stock prices using weather data on the created model.")
            with img1:
                st.image('resources/linear_regression.jpg', use_column_width=True)
            with img2:
                st.image('resources/linear_regression_2.jpg', use_column_width=True)

        st.markdown("")

        with st.container():
            text, img = st.columns([2, 1])
            with text:
                st.caption(":blue[_Neural Network_]")
                st.markdown(
                    "**Description**: Use this feature to predict stock prices using weather data and our LSTM neural network model.")
                st.markdown("**Steps:**")
                st.markdown("1. Select \"Neural Network\" from the navbar")
                st.markdown("2. Fill in the filters in the sidebar")
                st.markdown("3. The graph will begin loading once all filters are filled and show predicted stock prices.")
            with img:
                st.image('resources/neural_networl.jpg', use_column_width=True)

        st.divider()
        st.subheader(":bulb: Support and Feedback")
        st.markdown("If you encounter any issues or have suggestions for improvement, please don't hesitate to reach out to our support team. We value your feedback and are here to assist you in making the most of our platform.")
        st.markdown("If you encounter any bugs or issues while using our platform, please let us know by clicking on the \"Report an Issue\" button located on any page.")
        st.markdown("")
        st.markdown("")
        st.markdown("")
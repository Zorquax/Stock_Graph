import datetime as dt 
import pandas_datareader as pdr 
import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st
import numpy as np

#pd.options.plotting.backend = "plotly"
yf.pdr_override()
def getStock():
    while True: 
        try:
            start = input("Enter start date in YYYY/MM/DD format \n")
            if start == "exit":
                break
            start = list(map(int,start.split("/")))
            print(start)
            start = dt.datetime(start[0], start[1], start[2])
            print(start)
            break
        except:
            print("Not a valid start date or format - try again \n")
    while True: 
        try:
            end = input("Enter end date in YYYY/MM/DD format \n")
            if end == "exit":
                break
            end = list(map(int,end.split("/")))
            end = dt.datetime(end[0], end[1], end[2])
            break
        except:
            print("Not a valid end date or format - try again \n")
    while True:
        try:
            stock = input("Enter acronym of stock \n")
            if stock == "exit":
                break
            data = pdr.data.get_data_yahoo(stock, start, end)
            return data
        except Exception as error:
            print(type(error).__name__)
            print("Not a valid stock acronym - try again \n")

data1 = getStock()
#data2 = getStock()
#data1 = pdr.get_data_yahoo('AAPL', start = '2018-01-01',
#                           end = '2018-02-02')

q1 = st.selectbox('What stock would you like', ['AAPL', 'NVDA'])
chart_type = st.selectbox('Choose a chart type', ['Line', 'Bar'])
 
## Create the chart
if chart_type == 'Bar':
    fig = px.bar(data1)
elif chart_type == 'Line':
    fig = px.line(data1)
 
## Display the chart
st.plotly_chart(fig, use_container_width=True)
#st.plotly_chart(fig)

#fig1 = data1.plot()
#fig1.show()
#fig2 = data2.plot()
#fig2.show()
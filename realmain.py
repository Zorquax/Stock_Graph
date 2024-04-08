import datetime as dt 
import pandas_datareader as pdr 
import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st

yf.pdr_override()

#Run with "streamlit realmain.py" where file is located, in terminal 

class StockStuff:
	
	invalid = []

	@classmethod
	def getStock(cls, stock, start, end):
			try:
				start = str(start)
				end = str(end)
				temp = stock
				stock = cls.convertDuplicateStock(stock)
				data = pdr.data.get_data_yahoo(stock, start = str(start), end = str(end))
				data["Stock Name"] = [stock] * data.shape[0] if temp == stock else [temp] * data.shape[0]
				#data.insert(0, 'Stock Name', stock)
				start_open = data.iloc[0]['Close']
				start_date = data.index[0]
				e = list(map(lambda x: (x-start_date).days , data.index))
				data['Date'] = data.index.date
				data.index = e
				data.index.name = 'Days Since Start'
				data['Price Difference from Start'] = data['Close'] - start_open
				data['Percentage Difference'] = ((data['Price Difference from Start'] / start_open) * 100)
				data['Percentage Format'] = data['Percentage Difference'].map('{:.2f}%'.format)
				return data
			except Exception as error:
				print(error)
				print("Not a valid stock acronym - try again \n")
	
	@classmethod
	def convertDuplicateStock(cls, stock):
		i = len(stock)-1
		while stock[i].isdigit():
			i -= 1
		return stock[0:i+1]

	@classmethod
	def checkValidStock(cls, stock):
		if stock[-1].isdigit():
			stock = cls.convertDuplicateStock(stock)
		try:
			info = yf.Ticker(stock).history(
				period='1mo',
				interval='1d',
			)
			if len(info) > 0:
				return True
			else:
				return False
		except:
			return False

	@classmethod
	def createFullData(cls, stock_with_data):
		res = []
		for stock, start, end in stock_with_data:
			if stock not in cls.invalid:
				res.append(cls.getStock(stock, start, end))
		final = pd.concat(res)
		return final
	
stuck = st.text_input("List of stocks, separated by commas", key = "stock", value = "AAPL",
					placeholder= "Ticker of stock - E.G AAPL for Apple",
					help ="For example, if you wanted to see Apple, Nvidia, and Tesla, enter: AAPL, NVDA, TSLA")
stocklist = list(map(str.strip, stuck.split(",")))
for stoc in stocklist:
	if StockStuff.checkValidStock(stoc) == False:
		StockStuff.invalid.append(stoc)
if len(StockStuff.invalid) > 0:
	st.write(f'Invalid stocks listed: {StockStuff.invalid}')
stock_with_data = []
for stock in stocklist:
	if stock in StockStuff.invalid:
		continue
	start = st.date_input(f'What would you like the start date for {stock} to be?', 
						dt.datetime.now() - dt.timedelta(days=30), min_value=dt.datetime(1981,1,1))
	end = st.date_input(f'What would you like the end date for {stock} to be?', 
						dt.datetime.now(), min_value=start, max_value = dt.datetime.now()) + dt.timedelta(1)
	stock_with_data.append([stock, start, end])

if st.button("Generate stock data"):
	data2 = StockStuff.createFullData(stock_with_data)

	data1 = data2[["Close", "Stock Name", "Price Difference from Start", "Percentage Difference", "Percentage Format", "Date"]]

	data1['Stock Price'] = data1['Close'].apply(lambda x: f"${x:.2f}")

	fig = px.line(data1, color = 'Stock Name', markers = True, hover_name = "Stock Price", hover_data = {
		"Stock Name" : True, "Date": True, "Price Difference from Start" : ":.2f", "value": False, "variable" : False,
		"Percentage Difference" : ":.2f", "Percentage Format" : False}, 
		title = "Stock Values")
	min_percent = data1["Percentage Difference"].min()
	max_percent = data1["Percentage Difference"].max()
	fig2 = px.line(data1, y = "Percentage Difference", color = 'Stock Name', markers = True, hover_name = "Percentage Format", hover_data = {
		"Date": True,"Percentage Difference" : ":.2f", "Stock Name" : True, "Stock Price" : True, "Price Difference from Start" : ":.2f"}, 
		title = "Percentage Gain", range_y = (min_percent-1,max_percent+1))

	st.plotly_chart(fig2, use_container_width=True)
	st.plotly_chart(fig, use_container_width=True)

	# Table

	change_in_price = data1.groupby('Stock Name')['Price Difference from Start'].agg(lambda x: f"${x.iloc[-1]:.2f}")
	last_percentage_difference = data1.groupby('Stock Name')['Percentage Format'].last()

	result = pd.DataFrame({'Change in price from start to end': change_in_price,
						'Percentage Difference from start to end': last_percentage_difference})
	st.table(result)

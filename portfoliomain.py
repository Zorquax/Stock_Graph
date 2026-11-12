import datetime as dt 
import pandas_datareader as pdr 
import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

yf.pdr_override()

class StockStuff:
	
	invalid = []
	d = {}
	p = {}
	initial_money = 0

	@classmethod
	def fillMissing(cls, df, working_days):
		# Reindex to include all dates in 'working_days'
		full_df = df.reindex(working_days)

		# Forward fill missing data
		full_df.ffill(inplace=True)

		# Replace any initial NaN values with 0 instead of backward filling
		full_df.fillna(0, inplace=True)

		# Return the filled DataFrame
		return full_df

	
	@classmethod
	def getStock(cls, stock, start, end):
		try:
			temp = stock
			stock = cls.convertDuplicateStock(stock)
			print(stock)

			# Fetch the stock data from Yahoo Finance
			data = pdr.data.get_data_yahoo(stock, start=str(start), end=str(end))

			data["Stock Name"] = [stock] * data.shape[0] if temp == stock else [temp] * data.shape[0]
			data["Stock Range"] = data["Stock Name"] + f" ({start.strftime('%m/%d/%Y')} TO {end.strftime('%m/%d/%Y')})"

			start_open = data.iloc[0]['Close']
			start_date = data.index[0]
			data['Date'] = data.index

			# Use 'Date' as the index
			data.index.name = 'Date'

			# Add necessary columns
			data['Price Difference from Start'] = data['Close'] - start_open
			data['Percentage Difference'] = ((data['Price Difference from Start'] / start_open) * 100)
			data['Percentage Format'] = data['Percentage Difference'].map('{:.2f}%'.format)
			data["Hover"] = data["Stock Name"] + ", " + data["Percentage Format"] + ", " + data.index.astype(str)
			data["Temp Price"] = data["Price Difference from Start"].apply(lambda x: f"${x:.2f}")
			data["Hover Stock"] = data["Stock Name"] + ", " + data["Temp Price"] + ", " + data.index.astype(str)
			data["Investing"] = StockStuff.d[stock] * (data['Percentage Difference'] / 100)

			# Calculate Daily Gain Percentage
			data['Daily Gain'] = ((data['Close'] - data['Close'].shift(1)) / data['Close'].shift(1)).fillna(0) * 100

			# Calculate ITD Gain Percentage
			data['ITD Gain'] = ((data['Close'] - start_open) / start_open) * 100

			# Generate the full range of working days
			working_days = pd.date_range(start, end - dt.timedelta(1), freq='B')

			# Fill missing data if necessary
			if data.shape[0] != len(working_days):
				print("Ruh roh")
				data = cls.fillMissing(data, working_days)
				data["Stock Name"] = [stock] * len(working_days)
				data["Stock Range"] = data["Stock Name"] + f" ({start.strftime('%m/%d/%Y')} TO {end.strftime('%m/%d/%Y')})"
			
			print(data)

			# After filling, convert 'Date' index to 'Days Since Start'
			data['Days Since Start'] = (data.index - working_days[0]).days

			# Reset the index to get 'Date' as a column
			data.reset_index(drop=False, inplace=True)  # Convert 'Date' index to a column

			# Replace the 'Date' column with the values from 'working_days'
			data['Date'] = working_days

			# Set 'Days Since Start' as the new index
			data.set_index('Days Since Start', inplace=True)
			data.index.name = 'Days Since Start'

			return data
		except Exception as error:
			print(error)
			print("Not a valid stock acronym - try again \n")


	
	@classmethod
	def calculateInvestmentTotals(cls, stock_df):
		# Ensure that the DataFrame index is correctly set to 'Days Since Start'
		
		# Group by 'Days Since Start' and sum up the 'Investing' values
		grouped_totals = stock_df.groupby('Days Since Start')['Investing'].sum().reset_index()
		
		# Rename columns for clarity
		grouped_totals.columns = ['Days Since Start', 'Investment Totals']
		
		# Set 'Days Since Start' as the index
		grouped_totals.set_index('Days Since Start', inplace=True)
		
		return grouped_totals
	
	@classmethod
	def createPortfolio(cls, stock_df):
		try:
			# Ensure 'Days Since Start' is the index
			if stock_df.index.name != 'Days Since Start':
				raise ValueError("'Days Since Start' must be the index.")

			# Retrieve the allocation percentages from the p dictionary
			allocation_percentages = cls.p

			# Calculate Daily Gain for the Portfolio
			daily_gain_components = []
			for stock, percentage in allocation_percentages.items():
				stock_data = stock_df[stock_df['Stock Name'] == stock]
				# Use the already calculated 'Daily Gain' column
				daily_gain_components.append(stock_data['Daily Gain'] * percentage)
				
			# Aggregate the Daily Gain
			grouped_df = stock_df.groupby(level='Days Since Start').agg({
				'Investing': 'sum'
			})
			grouped_df['Daily Gain'] = sum(daily_gain_components)
			grouped_df['Daily Gain'] = grouped_df['Daily Gain'].apply(lambda x: (x - 1) * 100)  # Convert to percentage


			# Calculate ITD Gain as per the formula
			itd_gain_components = []
			for stock, percentage in allocation_percentages.items():
				stock_data = stock_df[stock_df['Stock Name'] == stock]
				itd_gain_components.append(stock_data['Percentage Difference'] * percentage)

			grouped_df['ITD Gain'] = sum(itd_gain_components)
			grouped_df['ITD Gain'] = grouped_df['ITD Gain'].apply(lambda x: (x - 1) * 100)  # Convert to percentage

			# Add 100% to ITD Gain
			grouped_df['ITD Gain'] += 100
			grouped_df['Daily Gain'] += 100
			
			# Retrieve the trade dates from the first stock
			first_stock_name = stock_df['Stock Name'].unique()[0]
			first_stock_df = stock_df[stock_df['Stock Name'] == first_stock_name]
			trade_dates = first_stock_df[['Date']]

			# Join trade dates with the grouped DataFrame
			portfolio_df = grouped_df.join(trade_dates, how='left')

			# Print or process the portfolio DataFrame
			print(portfolio_df)

			# Return the portfolio DataFrame with only the required columns
			return portfolio_df[['Daily Gain', 'ITD Gain', 'Investing', 'Date']]

		except Exception as error:
			print(error)
			print("Something went wrong when attempting to create the portfolio.")


	@classmethod
	def convertDuplicateStock(cls, stock):
		i = len(stock) - 1
		while stock[i].isdigit():
			i -= 1
		return stock[0:i + 1]

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
		port = cls.createPortfolio(final)
		return (final, port)
	
stuck = st.text_input("List of stocks, separated by commas", key="stock", value="AAPL",
					  placeholder="Ticker of stock - E.G AAPL for Apple",
					  help="For example, if you wanted to see Apple, Nvidia, and Tesla, enter: AAPL, NVDA, TSLA")
stocklist = list(map(str.strip, stuck.split(",")))
for stoc in stocklist:
	if StockStuff.checkValidStock(stoc) == False:
		StockStuff.invalid.append(stoc)
if len(StockStuff.invalid) > 0:
	st.write(f'Invalid stocks listed: {StockStuff.invalid}')

stock_with_data = []
start = st.text_input(f'What would you like the start date for the stocks to be?', value=(dt.datetime.now() - dt.timedelta(days=30)).strftime("%m/%d/%Y"))
end = st.text_input(f'What would you like the end date for the stocks to be?', value=dt.datetime.now().strftime("%m/%d/%Y"))

real_start = dt.datetime.strptime(start, "%m/%d/%Y").date()
real_end = dt.datetime.strptime(end, "%m/%d/%Y").date()

for stock in stocklist:
	if stock in StockStuff.invalid:
		continue
	stock_with_data.append([stock, real_start, real_end])

money = st.number_input("How much money would you like to track over the interval?", 
						placeholder="Enter a number in $ amount", step=100) 
StockStuff.initial_money = money

for stock in stocklist: 
	if stock in StockStuff.invalid:
		continue
	value = st.number_input(f'What % of the money would you like to have for {stock}') / 100
	StockStuff.d[stock] = value * money 
	StockStuff.p[stock] = value / 100

st.write(StockStuff.d)
st.write(StockStuff.initial_money)

if st.button("Generate stock data"):
	data2, portfolio_data = StockStuff.createFullData(stock_with_data)

	# Prepare the data
	data1 = data2[["Close", "Stock Name", "Stock Range", "Hover", "Hover Stock", "Price Difference from Start", "Percentage Difference", "Percentage Format", "Date", "Investing", "Daily Gain", "ITD Gain"]]
	data1['Stock Price'] = data1['Close'].apply(lambda x: f"${x:.2f}")

	min_percent = data1["Percentage Difference"].min()
	max_percent = data1["Percentage Difference"].max()

	portfolio_data['Stock Range'] = 'Portfolio'
	portfolio_data['Hover'] = portfolio_data['Date'].astype(str) + ", ITD Gain: " + portfolio_data['ITD Gain'].map('{:.2f}%'.format)

	min_portfolio_itd = portfolio_data['ITD Gain'].min()
	max_portfolio_itd = portfolio_data['ITD Gain'].max()

	if min_portfolio_itd < min_percent:
		min_percent = min_portfolio_itd
	if max_portfolio_itd > max_percent:
		max_percent = max_portfolio_itd

	combined_data = pd.concat([data1, portfolio_data])

	# Create a figure using Plotly Graph Objects
	fig = go.Figure()

	# Add traces for each stock
	for stock in data1['Stock Name'].unique():
		stock_data = data1[data1['Stock Name'] == stock]
		fig.add_trace(go.Scatter(
			x=stock_data.index,
			y=stock_data['ITD Gain'],
			mode='lines',
			name=stock,
			hovertemplate=
			'<i>Days Since Start</i>: %{x}' +  # Display the index
			'<br><i>Stock Name</i>: %{customdata[0]}' +
			'<br><i>Stock Price</i>: %{customdata[1]}' +
			'<br><i>Price Difference from Start</i>: $%{customdata[2]:.2f}' +
			'<br><i>Percentage Gain</i>: %{customdata[3]:.2f}%' +  # Display Percentage Gain instead of ITD Gain
			'<br><i>Daily Gain</i>: %{customdata[4]:.2f}%' +
			'<br><i>Investment</i>: $%{customdata[5]:.2f}' +  # Display the investment component rounded to the nearest cent
			'<br><i>Date</i>: %{customdata[6]}' +  # Display the Date as the last hover data
			'<extra></extra>',
			customdata=stock_data[['Stock Name', 'Stock Price', 'Price Difference from Start', 'Percentage Difference', 'Daily Gain', 'Investing', 'Date']].values
		))


	# Add trace for the portfolio
	fig.add_trace(go.Scatter(
		x=portfolio_data.index,
		y=portfolio_data['ITD Gain'],
		mode='lines',
		name='Portfolio',
		hovertemplate=
		'<i>Date</i>: %{customdata[2]}' +
		'<br><i>Daily Gain</i>: %{customdata[0]:.2f}%' +
		'<br><i>ITD Gain</i>: %{y:.2f}%' +
		'<br><i>Portfolio</i>: $%{customdata[1]:.2f}' +
		'<extra></extra>',
		customdata=portfolio_data[['Daily Gain', 'Investing', 'Date']].values
	))

	fig.update_layout(
		title=f"ITD Gain - {stocklist}",
		yaxis_title='ITD Gain (%)',
		xaxis_title='Days Since Start',
		hoverlabel_align='right',
		yaxis=dict(
			range=[min_percent - 1, max_percent + 1]  # Correctly set the y-axis range
		)
	)

	st.plotly_chart(fig, use_container_width=True)

	# Table
	change_in_price = data1.groupby('Stock Name')['Price Difference from Start'].agg(lambda x: f"${x.iloc[-1]:.2f}")
	last_percentage_difference = data1.groupby('Stock Name')['Percentage Format'].last()

	result = pd.DataFrame({'Change in price from start to end': change_in_price,
						   'Percentage Difference from start to end': last_percentage_difference})
	
	st.table(result)
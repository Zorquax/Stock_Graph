Stock quick visualization.

Uses streamlit for visual interface + buttons to choose options
Uses plotly for the graphs plotted within streamlit - interactive
Uses pandas dataframe as input for plotly to plot
Uses yahoo finance to retrieve stock data, via pandas datareader
Uses mySQL to store and keep data(?)

First, enter the stock(s) tickers you would like to input, with a comma as the delimiter
<img width="711" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/57c731f7-54e2-46ae-b380-d6ef1abebaf5">

If you wanted more, it would look something like this: 
<img width="726" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/a8c62ee4-c7c6-4345-9b66-6c6702cb09e0">

Make sure you are pressing the Enter key after inputting desired stock tickers.

For each stock, enter the start and end date that you would like to see. The default is a range of 30 days prior to current day.
<img width="720" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/3fb3d51b-1fdb-4da3-b3b4-9107ee357fed">

As an added feature, this project is also able to display comparisons between the same stock at different price points. Let's say you wanted to compare the dates of AAPL from two different dates. Simply repeat the process above, but include a unique number for each different date you wish to display.
<img width="717" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/09661d7e-56f0-46a4-9b29-e6d815d34954">

Note - using numerical order is not required, but is recommended for simplicity.

After inputting dates of your choice - using either the calendar upon click or manual input in the form of "YYYY/MM/DD" - click the "Generate Stock Data" button to display results. Example input:
<img width="730" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/46984444-d4c9-4716-aec6-58a4f46422e6">

This graph displays the percentage gain for each day since the start. Hovering over the data points gives the percentage, bolded, and other relevant data.
<img width="751" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/f8f46857-1781-4b1d-859c-d3505baf0ae9">

This graph simply displays the stock price for each day, with similar info upon hover.
<img width="760" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/a2b120c6-0c2f-4a33-a9e0-625f70a7487d">

Lastly, a table displays the change in percent difference and price difference from the start date and end date of each stock.
<img width="734" alt="image" src="https://github.com/Zorquax/Stock_Graph/assets/55953710/5840f225-9027-4edc-8687-6309e7747e3b">

Enjoy!

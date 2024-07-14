import yfinance as yf
import pandas as pd

########## Constants ##########
PERIOD = "max"
LOW_PERIOD = 30

########## Screens ##########

def get_all_stocks():
    """
    This function retrieves all ASX stocks from a CSV file.
    Returns:
        list: A list of ASX stock tickers.
    """
    data = pd.read_csv("data/ASX_Listed_Companies.csv")
    tickers = data["ASX code"].tolist()
    return tickers


def run_screen(stock):
    """
    This function checks if a stock meets certain criteria:
    - The highest Close price is at least double the lowest Close price.
    - The lowest Close price occurred in the last LOW_PERIOD days.

    Args:
        stock (yfinance.Ticker): The stock to screen.

    Returns:
        int: 1 if the stock meets the criteria, otherwise 0.
    """
    hist = stock.history(period=PERIOD)
    high = hist["Close"].max()
    low = hist["Close"].min()
    low_period_low = hist["Close"].nlargest(LOW_PERIOD).min()
    print('Stock:', stock.ticker, 'High:', high, 'Low Period Low:', low_period_low)
    if high >= low * 2 and hist["Close"].idxmin() > hist.index[-LOW_PERIOD]:
        return 1
    return 0


########## Main ##########

# Get all the stocks
stocks = get_all_stocks()

# Append .AX to the stock names to comply with Yahoo Finance
stocks = [stock + ".AX" for stock in stocks]

# Filter stocks based on the screening criteria
buys = []
for stock_symbol in stocks:
    stock = yf.Ticker(stock_symbol)
    if run_screen(stock) == 1:
        buys.append(stock)
        
# Format the list of buys
buys = ['ASX:' + stock.ticker.replace('.AX', '') for stock in buys]

# Convert the list to a single string with comma separation
buys_string = ','.join(buys)

# Save the string to a text file
with open('output/watchlist.txt', 'w') as file:
    file.write(buys_string)

print(buys_string)
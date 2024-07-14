import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

########## Constants ##########
PERIOD = "max" # The period to consider for the historical data
LOW_PERIOD = 30 # Number of days to consider for the lowest Close price

MAX_WORKERS = 30 # Number of threads to run in parallel

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


def run_screen(stock_symbol):
    """
    This function checks if a stock meets certain criteria:
    - The highest Close price is at least double the lowest Close price.
    - The lowest Close price occurred in the last LOW_PERIOD days.

    Args:
        stock_symbol (str): The stock symbol to screen.

    Returns:
        str: The stock symbol if it meets the criteria, otherwise None.
    """
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period=PERIOD)
    if hist.empty:
        return None

    high = hist["Close"].max()
    low = hist["Close"].min()
    low_period_low = hist["Close"].nlargest(LOW_PERIOD).min()

    if high >= low * 2 and hist["Close"].idxmin() > hist.index[-LOW_PERIOD]:
        return stock_symbol
    return None


########## Main ##########

# Get all the stocks
stocks = get_all_stocks()

# Append .AX to the stock names to comply with Yahoo Finance
stocks = [stock + ".AX" for stock in stocks]

print(f"Total stocks to process: {len(stocks)}")

# Use ThreadPoolExecutor to run the screen in parallel
buys = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_stock = {executor.submit(run_screen, stock): stock for stock in stocks}
    for i, future in enumerate(as_completed(future_to_stock), 1):
        result = future.result()
        if result is not None:
            buys.append(result)
        print(f"Processed {i}/{len(stocks)} stocks")

# Format the list of buys
buys = ['ASX:' + stock.replace('.AX', '') for stock in buys]

# Convert the list to a single string with comma separation
buys_string = ','.join(buys)

# Save the string to a text file
with open('output/watchlist.txt', 'w') as file:
    file.write(buys_string)

print(f"Buy list: {buys_string}")
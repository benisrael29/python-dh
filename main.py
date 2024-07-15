import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from tqdm import tqdm

########## Constants ##########

PERIOD = input("Enter the period to consider for the historical data must be one of ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'): ")
LOW_PERIOD = int(input("Enter the number of days to consider for the lowest Close price: "))

####### Immutable ###########
MAX_WORKERS = 30  # Number of threads to run in parallel

########## Screens ##########

def get_all_stocks():
    """
    This function retrieves all ASX stocks from a CSV file.
    Returns:
        list: A list of ASX stock tickers.
    """
    # Get list of files in the data directory
    files = os.listdir("data")
    csv_files = [file for file in files if file.endswith(".csv")]

    # Check if there is exactly one CSV file
    if len(csv_files) != 1:
        print('There must be exactly one CSV file in the data directory. Please check the data directory and try again.')
        raise FileNotFoundError("There must be exactly one CSV file in the 'data' directory.")
    
    # Read the CSV file
    file_path = os.path.join("data", csv_files[0])
    data = pd.read_csv(file_path)
    
    # Check if the CSV file contains the 'ASX code' column
    if 'ASX code' not in data.columns:
        print('The CSV file does not contain the required "ASX code" column. Please check the CSV file and try again.')
        raise ValueError("The CSV file does not contain the required 'ASX code' column.")
    
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
    time_of_low = hist["Close"].idxmin()

    if high >= low * 2 and time_of_low >= hist.index[-LOW_PERIOD]:
        return stock_symbol
    return None

########## Main ##########
try:
    # Get all the stocks
    stocks = get_all_stocks()

    # Append .AX to the stock names to comply with Yahoo Finance
    stocks = [stock + ".AX" for stock in stocks]

    print(f"Total stocks to process: {len(stocks)}")

    # Use ThreadPoolExecutor to run the screen in parallel
    buys = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_stock = {executor.submit(run_screen, stock): stock for stock in stocks}
        with tqdm(total=len(stocks), desc="Processing stocks", unit="stock") as pbar:
            for future in as_completed(future_to_stock):
                result = future.result()
                if result is not None:
                    buys.append(result)
                pbar.update(1)

    # Format the list of buys
    buys = ['ASX:' + stock.replace('.AX', '') for stock in buys]

    # Convert the list to a single string with comma separation
    buys_string = ','.join(buys)

    # Save the string to a text file
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'watchlist.txt'), 'w') as file:
        file.write(buys_string)

    print(f"Buy list: {buys_string}")
except Exception as e:
    print(f"An unexpected error occurred. Please contact Ben: {e}")
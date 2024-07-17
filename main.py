import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, sys
from tqdm import tqdm
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


####### Immutable ###########
MAX_WORKERS = 30  # Number of threads to run in parallel
LISTED_COMPANIES_FILE_URL = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"

########## Screens ##########

def get_application_path():
    """Return the directory of the executable."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # For onefile mode, sys.executable points to the executable file path
        return os.path.dirname(sys.executable)
    # For unfrozen or one-folder mode, just use the script's directory
    return os.path.dirname(os.path.abspath(__file__))


def inputs_and_validations():
    while True:
        PERIOD_in = input(
            "Enter the period to consider for the historical data must be one of ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'): "
        )
        if PERIOD_in in (
            "1d",
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
            "10y",
            "ytd",
            "max",
        ):
            break
        else:
            print("Invalid period. Please enter a valid period.")
    while True:
        LOW_PERIOD_out = input(
            "Enter the number of days to consider for the lowest Close price: "
        )
        try:
            LOW_PERIOD_out = int(LOW_PERIOD_out)
            if LOW_PERIOD_out > 0:
                break
            else:
                print(
                    "Invalid number of days. Please enter a valid number of days as an integer"
                )
        except ValueError:
            print(
                "Invalid number of days. Please enter a valid number of days as an integer"
            )

    return PERIOD_in, LOW_PERIOD_out


def get_all_stocks():
    """
    This function retrieves all ASX stocks from a CSV file.
    Returns:
        list: A list of ASX stock tickers.
    """
    data = pd.read_csv(LISTED_COMPANIES_FILE_URL, skiprows=2)
    # data = pd.read_csv(file_path)

    # Check if the CSV file contains the 'ASX code' column
    if "ASX code" not in data.columns:
        print(
            'The CSV of listed companies does not contain the required "ASX code" column. Please check the CSV file and try again.'
        )
        raise ValueError(
            "The CSV file does not contain the required 'ASX code' column."
        )

    tickers = data["ASX code"].tolist()

    def list_to_string(lst):
        return ", ".join(lst)

    print(
        f"Total stocks in the ASX: {len(data)}:\n {list_to_string(tickers[:3])} ... {list_to_string(tickers[-3:])}"
    )
    return tickers


########## INPUTS ##########
TICKERS = get_all_stocks()
PERIOD, LOW_PERIOD = inputs_and_validations()


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
    hist = stock.history(period=PERIOD, repair=True)
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

    # Append .AX to the stock names to comply with Yahoo Finance
    TICKERS = [stock + ".AX" for stock in TICKERS]

    print(f"Total stocks to process: {len(TICKERS)}")

    # Use ThreadPoolExecutor to run the screen in parallel
    buys = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        try:
            future_to_stock = {
                executor.submit(run_screen, stock): stock for stock in TICKERS
            }
            with tqdm(
                total=len(TICKERS), desc="Processing stocks", unit="stock"
            ) as pbar:
                for future in as_completed(future_to_stock):
                    result = future.result()
                    if result is not None:
                        buys.append(result)
                    pbar.update(1)
        except KeyboardInterrupt as e:
            print("Interrupted by user. Cancelling tasks...")
            # Cancel all pending futures
            for future in future_to_stock.keys():
                future.cancel()
            # Ensure executor is properly shut down
            executor.shutdown(wait=False)
            print("Cancelled.")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e
    # Format the list of buys
    buys = ["ASX:" + stock.replace(".AX", "") for stock in buys]

    # Convert the list to a single string with comma separation
    buys_string = ",".join(buys)

    # Save the string to a text file
    output_dir = get_application_path()
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "watchlist.txt"), "w") as file:
        file.write(buys_string)
    print(output_dir)
    time.sleep(10)

    print(f"Buy list: {buys_string}")
except Exception as e:
    print(f"An unexpected error occurred. If it persists please contact Ben: {e}")

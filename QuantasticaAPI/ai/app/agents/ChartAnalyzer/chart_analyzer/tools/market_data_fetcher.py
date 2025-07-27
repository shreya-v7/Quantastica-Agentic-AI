import pandas as pd
import numpy as np
from nsepython import equity_history
from datetime import datetime, timedelta


# ==============================================================================
# --- Agent Tool Functions (Using Simple Types) ---
# ==============================================================================

def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> list:
    """
    Fetches historical stock data and returns it as a list of dictionaries.
    This format is agent-friendly and uses simple data types.

    Args:
        symbol (str): The stock symbol (e.g., "INFY", "RELIANCE").
        start_date (str): The start date in "dd-mm-yyyy" format.
        end_date (str): The end date in "dd-mm-yyyy" format.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row of data.
              Returns an empty list if no data is found.
    """
    print(f"Fetching data for {symbol} from {start_date} to {end_date}...")
    try:
        df = equity_history(
            symbol=symbol,
            series="EQ",
            start_date=start_date,
            end_date=end_date
        )
        if df.empty:
            print(f"No data for {symbol}")
            return []

        # Map and rename columns
        df['Date'] = pd.to_datetime(df['CH_TIMESTAMP']).dt.strftime('%m-%d-%Y')
        df = df.rename(columns={
            'CH_OPENING_PRICE': 'Open',
            'CH_TRADE_HIGH_PRICE': 'High',
            'CH_TRADE_LOW_PRICE': 'Low',
            'CH_CLOSING_PRICE': 'Close',
            'CH_TOT_TRADED_QTY': 'Volume'
        })

        # Select and format the required columns
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        df_final = df[required_cols]

        # Convert DataFrame to a list of dictionaries for agent compatibility
        return df_final.to_dict(orient="records")

    except Exception as e:
        print(f"An error occurred while fetching data for {symbol}: {e}")
        return []


def calculate_indicators_and_risk(stock_records: list) -> dict:
    """
    Calculates technical indicators and risk from a list of stock data records.
    This function takes a simple list as input and returns a dictionary.

    Args:
        stock_records (list): List of dicts with stock data.

    Returns:
        dict: Contains 'indicators_df' (list of dicts) and 'risk_parameters' (dict).
    """
    if not stock_records:
        print("Input data is empty. Cannot perform calculations.")
        return {}

    print("Calculating technical indicators and risk parameters...")
    df = pd.DataFrame(stock_records)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=True)

    # === Technical Indicators ===
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    mid = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = mid + 2 * std
    df['BB_Lower'] = mid - 2 * std

    # === Risk Parameters ===
    df['daily_return'] = df['Close'].pct_change()
    df.dropna(inplace=True)

    volatility = df['daily_return'].std() * np.sqrt(252) * 100
    var_95 = df['daily_return'].quantile(0.05) * 100
    if not df.empty and 'Close' in df.columns and len(df['Close']) > 1:
        cumulative_return = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
    else:
        cumulative_return = 0
    sharpe_ratio = (df['daily_return'].mean() / df['daily_return'].std()) * np.sqrt(252) if df['daily_return'].std() != 0 else 0
    cumulative = (1 + df['daily_return']).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    risk_params = {
        "volatility_annualized_pct": f"{volatility:.2f}",
        "sharpe_ratio": f"{sharpe_ratio:.2f}",
        "cumulative_return_pct": f"{cumulative_return * 100:.2f}",
        "max_drawdown_pct": f"{max_drawdown:.2f}",
        "value_at_risk_95_daily_pct": f"{var_95:.2f}"
    }

    # Reset index to convert the 'Date' index back to a column
    df.reset_index(inplace=True)
    last_month = datetime.now() - timedelta(days=30)
    df = df[df['Date'] >= last_month]
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return {
        "indicators_df": df.to_dict(orient="records"),
        "risk_parameters": risk_params
    }


# ==============================================================================
# --- Example Usage ---
# ==============================================================================
if __name__ == "__main__":
    SYMBOL = "INFY"
    # Set a fixed date range for consistent testing
    start_date_str = "15-07-2024"
    end_date_str = "15-07-2025"

    # 1. Fetch the data by calling the first function
    stock_records = fetch_stock_data(SYMBOL, start_date_str, end_date_str)

    # 2. Check if data fetching was successful before proceeding
    if stock_records:
        # 3. Perform analysis by passing the fetched data to the second function
        analysis_results = calculate_indicators_and_risk(stock_records)
        print(analysis_results)
        # 4. Check if analysis was successful and print the results
        if analysis_results:
            print("\n=== Risk Parameters ===")
            for key, value in analysis_results['risk_parameters'].items():
                print(f"{key}: {value}")

            # Convert the list of dicts back to a DataFrame for easy viewing
            indicators_dataframe = pd.DataFrame(analysis_results['indicators_df'])

            print("\n=== Sample Data with Indicators (last 5 days) ===")
            # Set the 'Date' column as the index for better readability
            if 'Date' in indicators_dataframe.columns:
                indicators_dataframe['Date'] = pd.to_datetime(indicators_dataframe['Date'])
                indicators_dataframe.set_index('Date', inplace=True)

            print(indicators_dataframe.tail())
    else:
        print(f"Could not perform analysis because no data was fetched for {SYMBOL}.")

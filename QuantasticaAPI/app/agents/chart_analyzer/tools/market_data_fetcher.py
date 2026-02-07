import pandas as pd
import numpy as np
from nsepython import equity_history
from datetime import datetime, timedelta


def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> list:
    """
    Fetches historical stock data and returns it as a list of dictionaries.

    Args:
        symbol: The stock symbol (e.g., "INFY", "RELIANCE").
        start_date: The start date in "dd-mm-yyyy" format.
        end_date: The end date in "dd-mm-yyyy" format.

    Returns:
        A list of dictionaries, each representing a row of OHLCV data.
        Returns an empty list if no data is found.
    """
    print(f"Fetching data for {symbol} from {start_date} to {end_date}...")
    try:
        df = equity_history(
            symbol=symbol,
            series="EQ",
            start_date=start_date,
            end_date=end_date,
        )
        if df.empty:
            print(f"No data found for {symbol}")
            return []

        df['Date'] = pd.to_datetime(df['CH_TIMESTAMP']).dt.strftime('%m-%d-%Y')
        df = df.rename(columns={
            'CH_OPENING_PRICE': 'Open',
            'CH_TRADE_HIGH_PRICE': 'High',
            'CH_TRADE_LOW_PRICE': 'Low',
            'CH_CLOSING_PRICE': 'Close',
            'CH_TOT_TRADED_QTY': 'Volume',
        })

        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        return df[required_cols].to_dict(orient="records")

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return []


def calculate_indicators_and_risk(stock_records: list) -> dict:
    """
    Calculates technical indicators and risk parameters from stock data records.

    Args:
        stock_records: List of dicts with OHLCV data.

    Returns:
        Dict containing 'indicators_df' (list of dicts) and 'risk_parameters' (dict).
    """
    if not stock_records:
        print("Input data is empty. Cannot perform calculations.")
        return {}

    print("Calculating technical indicators and risk parameters...")
    df = pd.DataFrame(stock_records)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=True)

    # Technical Indicators
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

    # Risk Parameters
    df['daily_return'] = df['Close'].pct_change()
    df.dropna(inplace=True)

    volatility = df['daily_return'].std() * np.sqrt(252) * 100
    var_95 = df['daily_return'].quantile(0.05) * 100

    if not df.empty and len(df['Close']) > 1:
        cumulative_return = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
    else:
        cumulative_return = 0

    sharpe_ratio = (
        (df['daily_return'].mean() / df['daily_return'].std()) * np.sqrt(252)
        if df['daily_return'].std() != 0
        else 0
    )

    cumulative = (1 + df['daily_return']).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    risk_params = {
        "volatility_annualized_pct": f"{volatility:.2f}",
        "sharpe_ratio": f"{sharpe_ratio:.2f}",
        "cumulative_return_pct": f"{cumulative_return * 100:.2f}",
        "max_drawdown_pct": f"{max_drawdown:.2f}",
        "value_at_risk_95_daily_pct": f"{var_95:.2f}",
    }

    df.reset_index(inplace=True)
    last_month = datetime.now() - timedelta(days=30)
    df = df[df['Date'] >= last_month]
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    return {
        "indicators_df": df.to_dict(orient="records"),
        "risk_parameters": risk_params,
    }

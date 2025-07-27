# from typing import Dict, List
# from datetime import datetime, timedelta
# import requests
#
#
# def filter_last_n_days(indicator_data: Dict[str, Dict[str, str]], n: int = 7) -> Dict[str, Dict[str, str]]:
#     """
#     Filters the indicator data to only include the last n days, based on string dates in YYYY-MM-DD format.
#     """
#     if not indicator_data:
#         return {}
#
#     # Convert string dates to datetime objects and sort
#     date_objs = sorted(
#         [(datetime.strptime(date, "%Y-%m-%d"), date) for date in indicator_data.keys()],
#         reverse=True
#     )
#     # Find the max date
#     max_date_obj = date_objs[0][0]
#     min_date_obj = max_date_obj - timedelta(days=n - 1)
#
#     # Filter to only dates within the last n days (including max_date)
#     filtered = {
#         date: indicator_data[date]
#         for date_obj, date in date_objs
#         if min_date_obj <= date_obj <= max_date_obj
#     }
#     return filtered
#
#
# def get_signal_rsi_last_n_days(rsi_data: Dict[str, Dict[str, str]], n: int = 7) -> Dict[str, str]:
#     """
#     Uses only values from the last n days to generate a signal.
#     Signal is determined by the average RSI over the last n days:
#         - If average RSI < 30: Bullish (oversold)
#         - If average RSI > 70: Bearish (overbought)
#         - Else: Neutral
#     """
#     filtered = filter_last_n_days(rsi_data, n=n)
#     if not filtered:
#         return {"signal": "Neutral", "rationale": f"No RSI data in last {n} days."}
#
#     rsi_values = [float(val['RSI']) for val in filtered.values() if 'RSI' in val]
#     if not rsi_values:
#         return {"signal": "Neutral", "rationale": f"No valid RSI values in last {n} days."}
#
#     avg_rsi = sum(rsi_values) / len(rsi_values)
#     if avg_rsi < 30:
#         return {"signal": "Bullish", "rationale": f"Avg RSI over last {n} days is {avg_rsi:.2f} (oversold)."}
#     elif avg_rsi > 70:
#         return {"signal": "Bearish", "rationale": f"Avg RSI over last {n} days is {avg_rsi:.2f} (overbought)."}
#     else:
#         return {"signal": "Neutral", "rationale": f"Avg RSI over last {n} days is {avg_rsi:.2f} (normal range)."}
#
#
# class AlphaVantageTechnicalAgent:
#     BASE_URL = "https://www.alphavantage.co/query"
#
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#
#     def _get(self, params: dict):
#         params['apikey'] = self.api_key
#         response = requests.get(self.BASE_URL, params=params)
#         response.raise_for_status()
#         return response.json()
#
#     def get_sma(self, symbol: str, interval: str = "daily", time_period: int = 20, series_type: str = "close"):
#         params = {
#             "function": "SMA",
#             "symbol": symbol,
#             "interval": interval,
#             "time_period": time_period,
#             "series_type": series_type,
#             "outputsize": "compact"
#         }
#         return self._get(params)
#
#     def get_ema(self, symbol: str, interval: str = "daily", time_period: int = 20, series_type: str = "close"):
#         params = {
#             "function": "EMA",
#             "symbol": symbol,
#             "interval": interval,
#             "time_period": time_period,
#             "series_type": series_type,
#             "outputsize": "compact"
#         }
#         return self._get(params)
#
#     def get_rsi(self, symbol: str, interval: str = "daily", time_period: int = 14, series_type: str = "close"):
#         params = {
#             "function": "RSI",
#             "symbol": symbol,
#             "interval": interval,
#             "time_period": time_period,
#             "series_type": series_type,
#             "outputsize": "compact"
#         }
#         return self._get(params)
#
#     def get_macd(self, symbol: str, interval: str = "daily", series_type: str = "close", fastperiod: int = 12,
#                  slowperiod: int = 26, signalperiod: int = 9):
#         params = {
#             "function": "MACD",
#             "symbol": symbol,
#             "interval": interval,
#             "series_type": series_type,
#             "fastperiod": fastperiod,
#             "slowperiod": slowperiod,
#             "signalperiod": signalperiod,
#             "outputsize": "compact"
#         }
#         return self._get(params)
#
#     def get_bbands(self, symbol: str, interval: str = "daily", time_period: int = 20, series_type: str = "close",
#                    nbdevup: int = 2, nbdevdn: int = 2, matype: int = 0):
#         params = {
#             "function": "BBANDS",
#             "symbol": symbol,
#             "interval": interval,
#             "time_period": time_period,
#             "series_type": series_type,
#             "nbdevup": nbdevup,
#             "nbdevdn": nbdevdn,
#             "matype": matype,
#             "outputsize": "compact"
#         }
#         return self._get(params)
#
#     def get_willr(self, symbol: str, interval: str = "daily", time_period: int = 14):
#         params = {
#             "function": "WILLR",
#             "symbol": symbol,
#             "interval": interval,
#             "time_period": time_period,
#             "outputsize": "compact"
#         }
#         return self._get(params)
#
#
# # Example usage:
# if __name__ == "__main__":
#     # # For demonstration, using example RSI data dictionary
#     # rsi_data = {
#     #     '2025-07-26': {'RSI': '28.5'},
#     #     '2025-07-25': {'RSI': '32.2'},
#     #     '2025-07-24': {'RSI': '30.1'},
#     #     '2025-07-23': {'RSI': '29.2'},
#     #     '2025-07-22': {'RSI': '35.4'},
#     #     '2025-07-21': {'RSI': '31.6'},
#     #     '2025-07-20': {'RSI': '34.1'},
#     #     '2025-07-19': {'RSI': '29.8'},
#     #     '2025-07-18': {'RSI': '36.2'},
#     # }
#     # filtered = filter_last_n_days(rsi_data, n=7)
#     # print("Filtered RSI data (last 7 days):", filtered)
#     # print(get_signal_rsi_last_n_days(rsi_data, n=7))
#
#     #AlphaVantage agent example usage (requires real API key for live data)
#     api_key = "XL79PE4NU9QEJZK9"
#     agent = AlphaVantageTechnicalAgent(api_key=api_key)
#
#     # print("SMA Example:")
#     # sma_response = agent.get_sma(symbol="IBM")
#     # filtered_sma = filter_last_n_days(sma_response.get("Technical Analysis: SMA", {}), n=7)
#     # print(filtered_sma)
#
#     print("\nEMA Example:")
#     ema_response = agent.get_ema(symbol="IBM")
#     print(ema_response)
#     filtered_ema = filter_last_n_days(ema_response.get("Technical Analysis: EMA", {}), n=7)
#     print(filtered_ema)
#
#     # print("\nRSI Example:")
#     # rsi_response = agent.get_rsi(symbol="IBM")
#     # # To use get_signal_rsi_last_n_days with live data, extract the RSI "Technical Analysis: RSI" dict:
#     # rsi_live_data = rsi_response.get("Technical Analysis: RSI", {})
#     # print(get_signal_rsi_last_n_days(rsi_live_data, n=7))
#     #
#     # print("\nMACD Example:")
#     # macd_response = agent.get_macd(symbol="IBM")
#     # filtered_macd = filter_last_n_days(macd_response.get("Technical Analysis: MACD", {}), n=7)
#     # print(filtered_macd)
#     #
#     # print("\nBollinger Bands Example:")
#     # bbands_response = agent.get_bbands(symbol="IBM")
#     # filtered_bbands = filter_last_n_days(bbands_response.get("Technical Analysis: BBANDS", {}), n=7)
#     # print(filtered_bbands)

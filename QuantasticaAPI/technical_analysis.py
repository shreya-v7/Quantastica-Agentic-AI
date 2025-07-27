# import requests
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
#     def get_macd(self, symbol: str, interval: str = "daily", series_type: str = "close", fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9):
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
#     def get_bbands(self, symbol: str, interval: str = "daily", time_period: int = 20, series_type: str = "close", nbdevup: int = 2, nbdevdn: int = 2, matype: int = 0):
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
#     api_key = "1JSQUPZU7U1RUZ1W"  # Replace with your real API key!
#     agent = AlphaVantageTechnicalAgent(api_key=api_key)
#
#     print("SMA Example:")
#     print(agent.get_sma(symbol="IBM"))
#
#     print("\nEMA Example:")
#     print(agent.get_ema(symbol="IBM"))
#
#     print("\nRSI Example:")
#     print(agent.get_rsi(symbol="IBM"))
#
#     print("\nMACD Example:")
#     print(agent.get_macd(symbol="IBM"))
#
#     print("\nBollinger Bands Example:")
#     print(agent.get_bbands(symbol="IBM"))
#
#     print("\nWilliams %R Example:")
#     print(agent.get_willr(symbol="IBM"))
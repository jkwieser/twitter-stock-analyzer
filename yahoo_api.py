# Yahoo! Finance-Module reference: https://github.com/ranaroussi/yfinance


import datetime
import pandas as pd
import requestor
import yfinance as yf


class Utils():
    
    @staticmethod
    def get_date() -> str:
        return datetime.datetime.now().strftime('%Y-%m-%d')
    
    
    @staticmethod
    def get_date_add(days: int) -> str:
        date_minus_days = datetime.datetime.now() + datetime.timedelta(days = days)
        return date_minus_days.strftime("%Y-%m-%d")




class YahooFinanceAPI(requestor.Requestor):
    
    _stock: yf.ticker.Ticker = None
    _last_datetime: str = None
    

    def __init__(self, stock: str):
        self._stock = yf.Ticker(stock)
        
        
    def request_new(self) -> [{}]:
        date_now = Utils.get_date()
        date_tomorrow = Utils.get_date_add(1)
        history = self._stock.history(start = date_now, end = date_tomorrow, interval = '1m')
        history_dict = self._stock_to_dict(history.iloc[-1])
        if history_dict['stock_timestamp'] == self._last_datetime:
            return None
        self._last_datetime = history_dict['stock_timestamp']
        return [history_dict]
    
    
    def _stock_to_dict(self, stock: pd.core.series.Series) -> {}:
        return {
            'timestamp': self.get_time(),
            'value': stock['Open'],
            'stock_timestamp': str(stock.name)
        }
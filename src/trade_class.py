# -*- encoding: utf-8 -*-
'''
@File    :   trade_class.py
@Time    :   2023/01/27 18:49:35
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''



"""Trade template class"""

import time

class TradeClass:
    def __init__(self, currrent_exchange):
        self.init_ts = time.time()
        self.exchange = currrent_exchange
        self._name = self.exchange.GetName()
        self._pairs = self.exchange.GetCurrency()
    
    def get_account(self):
        """Get account info"""
        try:
            self.Account = self.exchange.GetAccount()

            self.Balance =  self.Account['Balance']
            self.Amount = self.Account['Stocks']
            self.FrozenBalance =  self.Account['FrozenBalance']
            self.FrozenStocks = self.Account['FrozenStocks']
            return True
        except:
            return False

    def get_ticker(self):
        """Get market ticker info"""
        try:
            self.ticker = self.exchange.GetTicker()
        
            self.high = self.ticker['High']
            self.low = self.ticker['Low']
            self.sell =  self.ticker['Sell']
            self.buy =  self.ticker['Buy']
            self.last =  self.ticker['Last']
            self.Volume = self.ticker['Volume']
            return True
        except:
            return False

    def get_depth(self):
        """Get market depth info"""
        try:
            self.depth = self.exchange.GetDepth()

            self.asks = self.depth['Asks']
            self.bids = self.depth ['Bids']
            return True
        except:
            return False

    def get_kline(self, period=60):
        """Get market kline info"""
        self.kline = self.exchange.GetRecords(period)

    def create_order(self, order_type, price, amount):
        """Post limit order"""
        if order_type == "buy":
            try: 
                order_id = self.exchange.Buy(price, amount)
            except:
                raise TypeError("Unknown buy order info")
        elif order_type == "sell":
            try: 
                order_id = self.exchange.Sell(price, amount)
            except:
                raise TypeError("Unknown sell order info")
        return order_id

    def cancel_order(self, order_id):
        """Revoke limit order"""
        return self.exchange.CancelOrder(order_id)
    
    def update_data(self):
        """Update infomation"""
        if not self.get_account():
            return 'false_get_account'
        if not self.get_ticker():
            return 'false_get_ticker'
        if not self.get_depth():
            return 'false_get_depth'
        try:
            self.get_kline()
        except:
            return 'false_get_K_line_info'
        
        return 'update_data_finish!'

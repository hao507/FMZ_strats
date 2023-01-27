# -*- encoding: utf-8 -*-
'''
@File    :   dynamic_balance.py
@Time    :   2023/01/27 18:55:23
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''


import time

def logger(*args, **kwargs):
    Log(*args, **kwargs)

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

class DynamicBalance:
    def __init__(self, trade_class):
        self.platform = trade_class
        self.last_time = time.time()
        self.last_trade_price = self.platform.last
        self.buy_count = 0
        self.sell_count = 0
    
    def NeedAccountInfo(self):
        self.platform.update_data()
        # Current account info
        self.stock = float(self.platform.Amount)
        self.balance = float(self.platform.Balance)
        latest_price = float(self.platform.last)
        
        self.total_balance = self.stock * latest_price + self.balance
        self.half_balance = self.total_balance / 2
        self.need_buy_amount = (self.half_balance - self.stock * latest_price) / latest_price
        self.need_sell_amount = (self.half_balance - self.balance) / latest_price
    
    def do_balance_trade(self, diff):
        if self.need_buy_amount > diff:
            self.platform.create_order("buy", self.platform.low, self.need_buy_amount)
            self.buy_count += 1
        elif self.need_sell_amount > diff:
            self.platform.create_order("sell", self.platform.high, self.need_sell_amount)
            self.sell_count += 1
        
        logger("Buy_Times: ", self.buy_count, "Sell_Times: ", self.sell_count)
    
    def if_need_trade(self, condition, time_diff, price_diff, spread):
        if condition == "time":
            if time.time() - self.last_time > time_diff:
                self.do_balance_trade(spread)
                self.last_time = time.time()
        elif condition == "price":
            if abs((self.platform.last -  self.last_trade_price)/self.last_trade_price)  > price_diff:
                self.do_balance_trade(spread)
                self.last_trade_price = self.platform.last



def main():
    test = TradeClass(exchange)
    logger(test.update_data())
    test_trade = DynamicBalance(test)

    while True:
        Sleep(1000)
        test_trade.NeedAccountInfo()
        test_trade.if_need_trade("price", 0, 0.05, 0.002)

# -*- encoding: utf-8 -*-
'''
@File    :   pure_mkt_making.py
@Time    :   2023/01/28 22:21:43
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''


import random
import time
from tools import *


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
    
    def get_unfilled_orders(self):
        self.undo_orders = self.exchange.GetOrders()
        return self.undo_orders
    
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


class PureMM(TradeClass):
    """
    Pure Market Making Strategy
    """
    def __init__(self, platform, bid_spread, ask_spread, minimum_spread,
                order_refresh_time, max_order_age, order_refresh_tolerance_pct,
                order_amount, price_ceiling, price_floor, moving_price_band_enabled, price_ceiling_pct, price_floor_pct, price_band_refresh_time,
                order_levels, order_level_amount, order_level_spread,
                inventory_skew_enabled, inventory_target_pct, inventory_price,
                ask_order_optimization_depth, bid_order_optimization_depth):
        self.platform = platform
        self.bid_spread = bid_spread
        self.ask_spread = ask_spread
        self.minimum_spread = minimum_spread
        self.order_refresh_time = order_refresh_time
        self.max_order_age = max_order_age
        self.order_refresh_tolerance_pct = order_refresh_tolerance_pct
        self.order_amount = order_amount
        self.price_ceiling = price_ceiling
        self.price_floor = price_floor
        self.moving_price_band_enabled = moving_price_band_enabled
        self.price_ceiling_pct = price_ceiling_pct
        self.price_floor_pct = price_floor_pct
        self.price_band_refresh_time = price_band_refresh_time
        self.order_levels = order_levels
        self.order_level_amount = order_level_amount
        self.order_level_spread = order_level_spread
        self.inventory_skew_enabled = inventory_skew_enabled
        self.inventory_target_pct = inventory_target_pct
        self.inventory_price = inventory_price
        self.ask_order_optimization_depth = ask_order_optimization_depth
        self.bid_order_optimization_depth = bid_order_optimization_depth

    def update_account_data(self):
        """Update account information data"""
        self.platform.update_data()
        self.stock = self.platform.Amount
        self.balance = self.platform.Balance
        self.available_buy_stock = self.balance / self.platform.buy

    # 
    # Check proceed conditions
    # 
    def check_if_proceed(self, interval_time=1000):
        """Check whether it should proceed to update order price and adjust order placements
        
        :return: bool"""
        order_state = []
        if order_state:
            return True
        else:
            Sleep(interval_time)
            return False
    
    # 
    # Recalculate indicators
    # 
    def get_weighted_price(self):
        """Get weighted average price based on orderbook"""
        pass




    # 
    # Merge and execute proposals
    # 

    def TradeDict(self):
        pass



def main():

    platform = TradeClass(exchange)
    param = {
        "platform": platform,
        "bid_spread": 10,
        "ask_spread": 20,
        "minimum_spread": 30,
        "order_refresh_time": 1000,
        "max_order_age": None,
        "order_refresh_tolerance_pct": None,
        "order_amount": None,
        "price_ceiling" : None,
        "price_floor": None,
        "moving_price_band_enabled": None,
        "price_ceiling_pct" : None,
        "price_floor_pct" : None,
        "price_band_refresh_time" : None,
        "order_levels" : None,
        "order_level_amount": None,
        "order_level_spread" : None,
        "inventory_skew_enabled" : None,
        "inventory_target_pct": None,
        "inventory_price": None,
        "ask_order_optimization_depth": None,
        "bid_order_optimization_depth": None
    }
    
    
    bot = PureMM(**param)
    bot.platform.get_depth()
    
    Log(bot.platform.asks)
    Log(bot.platform.bids)
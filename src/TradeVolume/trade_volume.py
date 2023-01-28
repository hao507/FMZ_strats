# -*- encoding: utf-8 -*-
'''
@File    :   trade_volume.py
@Time    :   2023/01/27 22:05:44
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


class TradeVol:
    """
    TradeVolume: Trade when price equal
    TradeSpread: Trade when limit order feed
    """
    def __init__(self, trade_class, amount_N, price_N, post_times):
        self.platform = trade_class
        self.traded_amount = {'spread': 0, 'volume': 0}
        self.init_time = time.time()
        self.last_time = time.time()
        self.wait_time = 60
        self.amount_N = amount_N
        self.price_N = price_N

        self.traded_pair = {'spread': [], 'volume': []}
        self.undo_state = []
        self.posted_times = {}
        for i in range(post_times):
            self.posted_times[i] = 0

    def update_data(self):
        """Loop update data"""
        self.platform.update_data()
        self.stock = self.platform.Amount
        self.balance = self.platform.Balance
        self.available_buy_stock = self.balance / self.platform.buy
        self.mid_price = (self.platform.buy + self.platform.sell) / 2
        return
    
    def deal_frozen(self):
        undo_orders = self.platform.get_unfilled_orders()
        if len(undo_orders) > 0:
            for i in undo_orders:
                self.platform.cancel_order(i['Id'])
    
    #
    # Define Trade Dicts
    # 

    def TradeDict(self, trade_dicts):
        for td in trade_dicts:
            if td['do_trade']:
                buy_id = self.platform.create_order('buy', td['buy_price'], td['amount'])
                sell_id = self.platform.create_order('sell', td['sell_price'], td['amount'])

                if td['buy_price'] == td['sell_price']:
                    self.traded_amount['volume'] += td['amount']
                    self.traded_pair['volume'].append({'buy_id': buy_id, 'sell_id': sell_id, 
                                                        'init_time': time.time(), 'amount': td['amount'],
                                                        'post_times_num': td['post_times_num']})
                else:
                    self.traded_pair['spread'].append({'buy_id': buy_id, 'sell_id': sell_id, 
                                                        'init_time': time.time(), 'amount': td['amount'],
                                                        'post_times_num': td['post_times_num']})
                self.last_time = time.time()
    
    def TradeVolDict(self, set_amount, each_amount):
        """To achieve trade set volume"""
        trade_price = self.mid_price
        trade_price = round(trade_price, self.price_N)

        if trade_price > self.platform.Buy and trade_price < self.platform.Sell:
            do_trade = self.stock > each_amount # ensure sell action
            do_trade = do_trade and self.available_buy_stock > each_amount # ensure buy action
            trade_dict = {
                'do_trade': do_trade,
                'buy_price': trade_price,
                'sell_price': trade_price,
                'amount': each_amount,
                'post_times_num': 0
            }
            return [trade_dict]

    def TradeSpreadDict(self, price_range, min_price_len, each_amount):
        trade_dicts = []
        mid_price = self.mid_price
        price_alphas = {}

        for i in self.posted_times:
            price_alphas[i] = price_range - self.posted_times[i] * min_price_len * random.randint(0, 5)
            if price_alphas[i] < 0:
                price_alphas[i] = 0
                self.posted_times[i] = 0
        
        for post_times_num in price_alphas:
            price_alphas = price_alphas[post_times_num]

            buy_price = mid_price - price_alphas
            buy_price = round(buy_price, self.price_N)
            available_buy_stock = self.balance / buy_price

            sell_price = mid_price + price_alphas
            sell_price = round(sell_price, self.price_N)

            do_trade = (self.balance > each_amount) and (available_buy_stock > each_amount)

            trade_dict = {
                'do_trade': do_trade,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'amount': each_amount,
                'post_times_num': post_times_num
            }
            trade_dicts.append(trade_dict)

            return trade_dicts
    
    # 
    # Check Trade Conditions
    # 

    def check_trade_conditions(self, now_times):
        """Check if trade"""
        for traded_id in self.traded_pair['spread']:
            # Check buy order status
            try:
                buy_state = self.platform.GetOrder(traded_id['buy_id'])
            except:
                self.platform.cancel_order(traded_id['sell_id'])
                self.traded_pair['spread'].remove(traded_id)
                if traded_id in self.traded_pair['spread']:
                    self.traded_pair['spread'].remove(traded_id)
            # Check sell order status
            try:
                sell_state = self.platform.GetOrder(traded_id['sell_id'])
            except:
                self.platform.cancel_order(traded_id['buy_id'])
                if traded_id in self.traded_pair['spread']:
                    self.traded_pair['spread'].remove(traded_id)

            if traded_id in self.traded_pair['spread']:
                if {sell_state['Status'], buy_state['Status']} == {0, 0}:
                    if now_times % 50 == 0:
                        Log(sell_state['Status'], buy_state['Status'], now_times%50)
                        self.platform.cancel_order(traded_id['buy_id'])
                        self.platform.cancel_order(traded_id['sell_id'])
                        self.posted_times[traded_id['post_times_num']] += random.randint(1, 3)
                        self.traded_pair['spread'].remove(traded_id)

                elif {sell_state['Status'], buy_state['Status']} == {1, 0} or {sell_state['Status'], buy_state['Status']} == {0, 1}:
                    if now_times % 50 == 0:
                        Log(sell_state['Status'], buy_state['Status'], now_times%50)
                        if buy_state['Status'] == 0:
                            self.platform.cancel_order(traded_id['buy_id'])
                            self.undo_state.append(['buy', buy_state['Status']])
                            self.traded_pair['spread'].remove(traded_id)
                        elif sell_state['Status'] == 0:
                            self.platform.cancel_order(traded_id['sell_id'])
                            self.undo_state.append(['sell', sell_state['Status']])
                            self.traded_pair['spread'].remove(traded_id)

                elif {sell_state['Status'], buy_state['Status']} == {1, 1}:
                    Log(sell_state['Status'], buy_state['Status'], traded_id['amount'])
                    self.traded_amount['spread'] += traded_id['amount']
                    self.traded_amount['spread'].remove(traded_id)

                else:
                    Log(sell_state, buy_state)
                    Log("Order status check: ", sell_state['Status'], buy_state['Status'])
                    Log(traded_id)

    def dynamic_balance(self, condition_ratio=1):
        # Dynamic Balance Action
        self.half_stock = (self.available_buy_stock + self.stock) * 0.5
        condition_balance_amount = (condition_ratio/100) * 2 * self.half_stock

        need_sell_amount = self.stock - self.half_stock
        need_buy_amount = self.available_buy_stock - self.half_stock

        if need_buy_amount > condition_balance_amount:
            self.platform.create_order('buy', self.platform.buy, need_buy_amount)
        elif need_sell_amount > condition_balance_amount:
            self.platform.create_order('sell', self.platform.sell, need_sell_amount)
    


def main():

    times = 0

    Set_amount_N = 4
    Set_price_N = 4
    set_amount = 10
    post_N = 5

    price_range = 50
    min_price_len = 1
    each_amount = 0.01
    condition_ratio = 2

    bot = TradeClass(exchange)
    Log(bot.update_data())
    bot = TradeVol(bot, Set_amount_N, Set_price_N, post_N)

    while(bot.traded_amount['spread'] < set_amount):

        bot.check_trade_conditions(times)
        Sleep(1000)
        bot.update_data()

        if times % 100 == 1:
            bot.dynamic_balance(condition_ratio)
        else:
            if len(bot.traded_pair['spread']) < post_N:
                trade_dicts = bot.TradeSpreadDict(price_range, min_price_len, each_amount)
                bot.TradeDict(trade_dicts)
                Log(bot.traded_amount['spread'])
        
        times += 1
    
    Log("Stock and Available_buy_stock: ", bot.stock, bot.available_buy_stock)

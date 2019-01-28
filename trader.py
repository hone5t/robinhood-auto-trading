#!/usr/bin/env python
import yaml
from Robinhood import Robinhood
import pdb
import time

class Trader:
    def __init__(self):
        cfg = self.get_config()
        self.user_name = cfg.get('robinhood').get('user')
        self.password = cfg.get('robinhood').get('password')
        self.client = Robinhood()
        self.client.login(username=self.user_name, password = self.password)
        self.stock_list = self.get_stock_list(cfg.get('stock'))
        self.stock_owned()

    def get_stock_list(self, stock_dict):
        stock_list = []
        for stock in stock_dict:
            instrument = self.client.instrument(stock)[0].get('url')
            instrument_id = self.client.instrument(stock)[0].get('id')
            stock_details = stock_dict.get(stock)
            stock_details['instrument'] = instrument
            stock_details['instrument_id'] = instrument_id
            stock_details['symobl'] = stock
            stock_list.append(stock_details)
        return stock_list

    def stock_owned(self):
        stocks = self.client.securities_owned()
        for stock in stocks.get('results'):
            for s in self.stock_list:
                if s.get('instrument') == stock.get('instrument'):
                    s['amount_owned'] = float(stock.get('quantity'))
                    s['purchase_price'] = float(stock.get('pending_average_buy_price'))
                    s['sell_price'] = float(s['purchase_price']) + float(s.get('target-profit'))
                    break
                else :
                    s['amount_owned'] = 0
                    s['purchase_price'] = 0

                if not stock.get('purchase_price'):
                    s['sell_price'] = float(s.get('median-price')) + float(s.get('target-profit'))
                    s['purchase_price'] = float(s.get('median-price')) + float(s.get('price-target'))


    def create_buy_order(self, stock):
        qty = stock.get('position')  - stock.get('amount_owned')
        if qty > 0:
            stock['order'] = self.client.place_limit_buy_order(
                              None,
                              stock.get('symobl'),
                              'GFD',
                              stock.get('purchase_price'),
                              qty
                            ).json()

    def create_sell_order(self, stock):
        qty = stock.get('amount_owned')
        if stock.get('can_sell_today'):
            self.client.place_limit_sell_order(
                  None,
                  stock.get('symobl'),
                  'GFD',
                  stock.get('sell_price'),
                  qty
            ).json()
        else:
            print("this might trigger day trading sorry no order created")

    def should_i_stop_trading(self):
        for stock in self.stock_list:
            if stock.get('can_sell_today'):
                print(stock)
                return False
        return True

    def create_market_position(self):
        for stock in self.stock_list:
            if stock.get('amount_owned') == 0 :
                #prevent day tradding
                stock['can_sell_today'] = False
                self.create_buy_order(stock)
                stock['amount_owned'] = stock.get('position')
            else:
                self.create_sell_order(stock)


    def check_if_sell_order_confirmed(self):
        for stock in self.stock_list:
            order = stock.get('order')
            if order and  order.get('side') == 'sell':
                order_state = self.client.order_history(order.get('id')).get('state')
                if order_state == "filled":
                    stock['amount_owned'] = 0
                    self.create_market_position()


    def get_config(self):
        with open("config.yaml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        return cfg

if __name__ == '__main__':
    trader = Trader()
    trader.create_market_position()
    while not trader.should_i_stop_trading():
        trader.check_if_sell_order_confirmed()
        time.sleep(5)

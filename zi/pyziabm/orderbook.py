import bisect
import numpy as np
import pandas as pd
from collections import OrderedDict

class Orderbook(object):
    '''
    Orderbook tracks, processes and matches orders.
    
    Orderbook is a set of linked lists and dictionaries containing trades, bids and asks.
    One dictionary contains a history of all orders;
    two other dictionaries contain priced bid and ask orders with linked lists for access;
    one dictionary contains trades matched with orders on the book.
    Orderbook also provides methods for storing and retrieving orders and maintaining a 
    history of the book.
    Public attributes: order_history, confirm_modify_collector, confirm_trade_collector,
    trade_book and traded.
    Public methods: add_order_to_book(), process_order(), order_history_to_h5(), trade_book_to_h5(),
    sip_to_h5() and report_top_of_book()
    '''
    
    def __init__(self, window):
        '''
        Initialize the Orderbook with a set of empty lists and dicts and other defaults
        
        order_history is a list of all incoming orders (dicts) in the order received
        _bid_book_prices and _ask_book_prices are linked (sorted) lists of bid and ask prices
        which serve as pointers to:
        _bid_book and _ask_book: dicts of current order book state and OrderedDicts of orders
        the OrderedDicts maintain time priority for each order at a given price.
        confirm_modify_collector and confirm_trade_collector are lists that carry information (dicts) from the
        order processor and/or matching engine to the traders
        trade_book is a list if trades in sequence
        _order_index identifies the sequence of orders in event time
        '''
        self.order_history = []
        self._bid_book = {}
        self._bid_book_prices = []
        self._ask_book = {}
        self._ask_book_prices = []
        self.confirm_modify_collector = []
        self.confirm_trade_collector = []
        self._sip_collector = []
        self.trade_book = []
        self._order_index = 0
        self._window = window
        self._spreads = [0]
        self.traded = False

    def _add_order_to_history(self, order):
        '''Add an order (dict) to order_history'''
        hist_order = {'order_id': order['order_id'], 'timestamp': order['timestamp'], 'type': order['type'], 
                      'quantity': order['quantity'], 'side': order['side'], 'price': order['price']}
        self._order_index += 1
        hist_order['exid'] = self._order_index
        self.order_history.append(hist_order)
    
    def add_order_to_book(self, order):
        '''
        Use insort to maintain on ordered list of prices which serve as pointers
        to the orders - for random price grid, check "not in" list, for more realistic
        books, check "in" list (TODO).
        '''
        book_order = {'order_id': order['order_id'], 'timestamp': order['timestamp'], 'type': order['type'], 
                      'quantity': order['quantity'], 'side': order['side'], 'price': order['price']}
        if order['side'] == 'buy':
            book_prices = self._bid_book_prices
            book = self._bid_book
        else:
            book_prices = self._ask_book_prices
            book = self._ask_book 
        if order['price'] not in book_prices:
            bisect.insort(book_prices, order['price'])
            book[order['price']] = {'num_orders': 1, 'size': order['quantity'], 'order_ids': [order['order_id']],
                                     'orders': OrderedDict([(order['order_id'],  book_order)])}
        else:
            book[order['price']]['num_orders'] += 1
            book[order['price']]['size'] += order['quantity']
            book[order['price']]['order_ids'].append(order['order_id'])
            book[order['price']]['orders'][order['order_id']] =  book_order
            
    def _remove_order(self, order_side, order_price, order_id):
        '''Pop the order_id; if  order_id exists, updates the book.'''
        if order_side == 'buy':
            book_prices = self._bid_book_prices
            book = self._bid_book
        else:
            book_prices = self._ask_book_prices
            book = self._ask_book
        is_order = book[order_price]['orders'].pop(order_id, None)
        if is_order:
            book[order_price]['num_orders'] -= 1
            book[order_price]['size'] -= is_order['quantity']
            book[order_price]['order_ids'].remove(is_order['order_id'])
            if book[order_price]['num_orders'] == 0:
                book_prices.remove(order_price)
                    
    def _modify_order(self, order_side, order_quantity, order_id, order_price):
        '''Modify order quantity; if quantity is 0, removes the order.'''
        book = self._bid_book if order_side == 'buy' else self._ask_book        
        if order_quantity < book[order_price]['orders'][order_id]['quantity']:
            book[order_price]['size'] -= order_quantity
            book[order_price]['orders'][order_id]['quantity'] -= order_quantity
        else:
            self._remove_order(order_side, order_price, order_id)
            
    def _add_trade_to_book(self, resting_order_id, resting_timestamp, incoming_order_id, timestamp, price, quantity, side):
        '''Add trades (dicts) to the trade_book list.'''
        self.trade_book.append({'resting_order_id': resting_order_id, 'resting_timestamp': resting_timestamp, 
                                'incoming_order_id': incoming_order_id, 'timestamp': timestamp, 'price': price,
                                'quantity': quantity, 'side': side})

    def _confirm_trade(self, timestamp, order_side, order_quantity, order_id, order_price):
        '''Add trade confirmation to confirm_trade_collector list.'''
        trader = order_id.partition('_')[0]
        self.confirm_trade_collector.append({'timestamp': timestamp, 'trader': trader, 'order_id': order_id, 
                                             'quantity': order_quantity, 'side': order_side, 'price': order_price})
    
    def _confirm_modify(self, timestamp, order_side, order_quantity, order_id):
        '''Add modify confirmation to confirm_modify_collector list.'''
        trader = order_id.partition('_')[0]
        self.confirm_modify_collector.append({'timestamp': timestamp, 'trader': trader, 'order_id': order_id, 
                                              'quantity': order_quantity, 'side': order_side})
                  
    def process_order(self, order):
        '''Check for a trade (match); if so call _match_trade, otherwise modify book(s).'''
        self.confirm_modify_collector.clear()
        self.traded = False
        self._add_order_to_history(order)
        if order['type'] == 'add':
            if order['side'] == 'buy':
                if order['price'] >= self._ask_book_prices[0]:
                    self._match_trade(order)
                else:
                    self.add_order_to_book(order)
            else: #order['side'] == 'sell'
                if order['price'] <= self._bid_book_prices[-1]:
                    self._match_trade(order)
                else:
                    self.add_order_to_book(order)
        else:
            book_prices = self._bid_book_prices if order['side'] == 'buy' else self._ask_book_prices
            if order['price'] in book_prices:
                book = self._bid_book if order['side'] == 'buy' else self._ask_book
                if order['order_id'] in book[order['price']]['orders']:
                    self._confirm_modify(order['timestamp'], order['side'], order['quantity'], order['order_id'])
                    if order['type'] == 'cancel':
                        self._remove_order(order['side'], order['price'], order['order_id'])
                    else: #order['type'] == 'modify'
                        self._modify_order(order['side'], order['quantity'], order['order_id'], order['price'])
    
    def _match_trade(self, order):
        '''Match orders to generate trades, update books.'''
        self.traded = True
        self.confirm_trade_collector.clear()
        if order['side'] == 'buy':
            book_prices = self._ask_book_prices
            book = self._ask_book
            remainder = order['quantity']
            while remainder > 0:
                if book_prices:
                    price = book_prices[0]
                    if order['price'] >= price:
                        book_order_id = book[price]['order_ids'][0]
                        book_order = book[price]['orders'][book_order_id]
                        if remainder >= book_order['quantity']:
                            self._confirm_trade(order['timestamp'], book_order['side'], book_order['quantity'], book_order['order_id'], book_order['price'])
                            self._add_trade_to_book(book_order['order_id'], book_order['timestamp'], order['order_id'], order['timestamp'], book_order['price'], 
                                                   book_order['quantity'], order['side'])
                            self._remove_order(book_order['side'], book_order['price'], book_order['order_id'])
                            remainder -= book_order['quantity']
                        else:
                            self._confirm_trade(order['timestamp'], book_order['side'], remainder, book_order['order_id'], book_order['price'])
                            self._add_trade_to_book(book_order['order_id'], book_order['timestamp'], order['order_id'], order['timestamp'], book_order['price'],
                                                   remainder, order['side'])
                            self._modify_order(book_order['side'], remainder, book_order['order_id'], book_order['price'])
                            break
                    else:
                        order['quantity'] = remainder
                        self.add_order_to_book(order)
                        break
                else:
                    print('Ask Market Collapse with order {0}'.format(order))
                    break
        else: #order['side'] =='sell'
            book_prices = self._bid_book_prices
            book = self._bid_book
            remainder = order['quantity']
            while remainder > 0:
                if book_prices:
                    price = book_prices[-1]
                    if order['price'] <= price:
                        book_order_id = book[price]['order_ids'][0]
                        book_order = book[price]['orders'][book_order_id] 
                        if remainder >= book_order['quantity']:
                            self._confirm_trade(order['timestamp'], book_order['side'], book_order['quantity'], book_order['order_id'], book_order['price'])
                            self._add_trade_to_book(book_order['order_id'], book_order['timestamp'], order['order_id'], order['timestamp'], book_order['price'],
                                                   book_order['quantity'], order['side'])
                            self._remove_order(book_order['side'], book_order['price'], book_order['order_id'])
                            remainder -= book_order['quantity']
                        else:
                            self._confirm_trade(order['timestamp'], book_order['side'], remainder, book_order['order_id'], book_order['price'])
                            self._add_trade_to_book(book_order['order_id'], book_order['timestamp'], order['order_id'], order['timestamp'], book_order['price'],
                                                   remainder, order['side'])
                            self._modify_order(book_order['side'], remainder, book_order['order_id'], book_order['price'])
                            break
                    else:
                        order['quantity'] = remainder
                        self.add_order_to_book(order)
                        break
                else:
                    print('Bid Market Collapse with order {0}'.format(order))
                    break

    def order_history_to_df(self):
        temp_df = pd.DataFrame(self.order_history)
        return temp_df

    def trade_book_to_df(self):
        temp_df = pd.DataFrame(self.trade_book)
        return temp_df

    def sip_to_df(self):
        temp_df = pd.DataFrame(self._sip_collector)
        return temp_df
    
    def report_top_of_book(self, now_time):
        '''Update the top-of-book prices and sizes'''
        lagged_mean_spread = np.mean(self._spreads[-self._window:])
        best_bid_price = self._bid_book_prices[-1]
        best_bid_size = self._bid_book[best_bid_price]['size']   
        best_ask_price = self._ask_book_prices[0]
        best_ask_size = self._ask_book[best_ask_price]['size']
        self._spreads.append(best_ask_price - best_bid_price)
        tob = {'timestamp': now_time, 'best_bid': best_bid_price, 'best_ask': best_ask_price, 'bid_size': best_bid_size, 'ask_size': best_ask_size,
               'lag_spread': lagged_mean_spread}
        self._sip_collector.append(tob)
        return tob
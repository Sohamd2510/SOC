from src.backtester import Order, OrderBook
from typing import List
import pandas as pd
import numpy as np
import statistics
import math

# Base Class
class BaseClass:
    def __init__(self, product_name, max_position):
        self.product_name = product_name
        self.max_position = max_position
    
    def get_orders(self, state, orderbook, position):
        """Override this method in product-specific strategies"""
        return []

class SpreadTracker:
    def __init__(self, beta=7.79, lookback=100):
        self.beta = beta
        self.lookback = lookback
        self.spread_history = []

    def update(self, misty_price, luxray_price):
        spread = misty_price - self.beta * luxray_price
        self.spread_history.append(spread)
        if len(self.spread_history) > self.lookback:
            self.spread_history.pop(0)
        return spread

    def get_stats(self):
        if len(self.spread_history) < self.lookback:
            return None, None
        mean = sum(self.spread_history) / len(self.spread_history)
        std = (sum((x - mean) ** 2 for x in self.spread_history) / len(self.spread_history)) ** 0.5
        return mean, std

class MistyStrategy(BaseClass):
    def __init__(self, spread_tracker):
        super().__init__("MISTY", 50)
        self.spread_tracker = spread_tracker
        self.trade_active = False

    def get_orders(self, state, orderbook, position):
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders)
        best_ask = min(orderbook.sell_orders)
        mid_price = (best_bid + best_ask) / 2

        # Get Luxray mid price
        luxray_book = state.order_depth.get("LUXRAY")
        if not luxray_book or not luxray_book.buy_orders or not luxray_book.sell_orders:
            return orders
        luxray_mid = (max(luxray_book.buy_orders) + min(luxray_book.sell_orders)) / 2

        spread = self.spread_tracker.update(mid_price, luxray_mid)
        mean, std = self.spread_tracker.get_stats()
        if mean is None or std == 0:
            return orders

        z = (spread - mean) / std

        # Dynamic size
        size = 0
        if abs(z) >= 2.5:
            size = 20
        elif abs(z) >= 2.0:
            size = 15
        elif abs(z) >= 1.5:
            size = 10
        elif abs(z) >= 1.2:
            size = 5

        # Entry
        if position == 0 and size > 0:
            if z > 1.2:
                orders.append(Order(self.product_name, best_bid, -size))  # Short MISTY
                self.trade_active = True
            elif z < -1.2:
                orders.append(Order(self.product_name, best_ask, size))   # Long MISTY
                self.trade_active = True

        # Exit
        elif self.trade_active and abs(z) < 0.5:
            exit_price = best_ask if position > 0 else best_bid
            orders.append(Order(self.product_name, exit_price, -position))
            self.trade_active = False

        return orders
class LuxrayStrategy(BaseClass):
    def __init__(self, spread_tracker):
        super().__init__("LUXRAY", 50)
        self.spread_tracker = spread_tracker
        self.trade_active = False

    def get_orders(self, state, orderbook, position):
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders)
        best_ask = min(orderbook.sell_orders)
        mid_price = (best_bid + best_ask) / 2

        # Get MISTY mid price
        misty_book = state.order_depth.get("MISTY")
        if not misty_book or not misty_book.buy_orders or not misty_book.sell_orders:
            return orders
        misty_mid = (max(misty_book.buy_orders) + min(misty_book.sell_orders)) / 2

        spread = self.spread_tracker.update(misty_mid, mid_price)
        mean, std = self.spread_tracker.get_stats()
        if mean is None or std == 0:
            return orders

        z = (spread - mean) / std

        # Dynamic size
        size = 0
        if abs(z) >= 2.5:
            size = 20
        elif abs(z) >= 2.0:
            size = 15
        elif abs(z) >= 1.5:
            size = 10
        elif abs(z) >= 1.2:
            size = 5

        # Entry
        if position == 0 and size > 0:
            if z > 1.2:
                orders.append(Order(self.product_name, best_bid, size))   # Long LUXRAY
                self.trade_active = True
            elif z < -1.2:
                orders.append(Order(self.product_name, best_ask, -size))  # Short LUXRAY
                self.trade_active = True

        # Exit
        elif self.trade_active and abs(z) < 0.5:
            exit_price = best_bid if position > 0 else best_ask
            orders.append(Order(self.product_name, exit_price, -position))
            self.trade_active = False

        return orders


class AbraStrategy(BaseClass):
    def __init__(self):
        super().__init__("ABRA", 50)
        self.lookback = 200
        self.z_threshold = 2.0
        self.z_mm_threshold = 0.3
        self.skew_factor = 0.1
        self.prices = []

    def get_orders(self, state, orderbook, position):
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders.keys())
        best_ask = min(orderbook.sell_orders.keys())
        mid_price = (best_ask + best_bid) // 2
        self.prices.append(mid_price)

        if len(self.prices) > self.lookback:
            mean_price = statistics.mean(self.prices[-self.lookback:])
            stddev_price = statistics.stdev(self.prices[-self.lookback:])
            z_score = (mid_price - mean_price) / stddev_price

            if z_score > self.z_threshold:
                orders.append(Order(self.product_name, best_bid, -10))
            elif z_score < -self.z_threshold:
                orders.append(Order(self.product_name, best_ask, 10))
            elif abs(z_score) < self.z_mm_threshold:
                return self.market_make(mid_price, position)
        else:
            return self.market_make(mid_price, position)

        return orders

    def market_make(self, mid_price, position):
        skewed_price = mid_price + self.skew_factor * position
        return [
            Order(self.product_name, int(skewed_price - 1), 8),
            Order(self.product_name, int(skewed_price + 1), -8)
        ]
    
class DrowzeeStrategy(BaseClass):
    def __init__(self):
        super().__init__("DROWZEE", 50)
        self.lookback = 50
        self.z_threshold = 3.75
        self.prices = []

    def get_orders(self, state, orderbook, position):
        orders = []
        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders.keys())
        best_ask = min(orderbook.sell_orders.keys())
        mid_price = (best_ask + best_bid) // 2
        self.prices.append(mid_price)

        if len(self.prices) > self.lookback:
            mean_price = statistics.mean(self.prices[-self.lookback:])
            stddev_price = statistics.stdev(self.prices[-self.lookback:])
            z_score = (mid_price - mean_price) / stddev_price

            size = 30 if abs(z_score) > self.z_threshold + 1 else 20

            if z_score > self.z_threshold:
                orders.append(Order(self.product_name, best_bid, -size))
            elif z_score < -self.z_threshold:
                orders.append(Order(self.product_name, best_ask, size))
            else:
                return self.market_make(mid_price)
        else:
            return self.market_make(mid_price)

        return orders

    def market_make(self, price):
        return [
            Order(self.product_name, price - 0.5, 15),
            Order(self.product_name, price + 0.5, -15)
        ]

class Trader:
    MAX_LIMIT = 0
     # for single product mode only, don't remove
    def __init__(self):
        misty_luxray_tracker = SpreadTracker(beta=7.79)
        self.strategies = {
            "DROWZEE": DrowzeeStrategy(), 
            "ABRA": AbraStrategy(),
            "MISTY": MistyStrategy(misty_luxray_tracker),
            "LUXRAY": LuxrayStrategy(misty_luxray_tracker),
        }
    
    def run(self, state):
        result = {}
        positions = getattr(state, 'positions', {})
        if len(self.strategies) == 1: self.MAX_LIMIT= self.strategies["PRODUCT"].max_position # for single product mode only, don't remove

        for product, orderbook in state.order_depth.items():
            current_position = positions.get(product, 0)
            product_orders = self.strategies[product].get_orders(state, orderbook, current_position)
            result[product] = product_orders
        
        return result, self.MAX_LIMIT

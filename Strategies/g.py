#here tried to use stoploss for drowzee but something was issue no trades
class DrowzeeStrategy(BaseClass):
    def __init__(self):
        super().__init__("DROWZEE", 50)
        self.lookback = 50
        self.z_threshold = 3.75
        self.prices = []
        self.active_trade = None
        self.take_profit = 10  # price units
        self.stop_loss = 6     # price units
        self.trade_size = 15

    def get_orders(self, state, orderbook, position=None):
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        # Get market data
        best_bid = max(orderbook.buy_orders.keys())
        best_ask = min(orderbook.sell_orders.keys())
        mid_price = (best_ask + best_bid) / 2

        self.prices.append(mid_price)
        if len(self.prices) > self.lookback:
            self.prices.pop(0)

        # === If we are in a trade, monitor SL/TP ===
        if self.active_trade:
            entry_price = self.active_trade["entry_price"]
            side = self.active_trade["side"]

            if side == "long":
                if mid_price >= entry_price + self.take_profit:
                    # Take Profit
                    orders.append(Order(self.product_name, best_bid, -self.trade_size))
                    self.active_trade = None
                    return orders
                elif mid_price <= entry_price - self.stop_loss:
                    # Stop Loss
                    orders.append(Order(self.product_name, best_bid, -self.trade_size))
                    self.active_trade = None
                    return orders

            elif side == "short":
                if mid_price <= entry_price - self.take_profit:
                    # Take Profit
                    orders.append(Order(self.product_name, best_ask, self.trade_size))
                    self.active_trade = None
                    return orders
                elif mid_price >= entry_price + self.stop_loss:
                    # Stop Loss
                    orders.append(Order(self.product_name, best_ask, self.trade_size))
                    self.active_trade = None
                    return orders

            # If in trade but TP/SL not hit — do nothing else
            return orders

        # === No active trade: evaluate z-score strategy ===
        if len(self.prices) < self.lookback:
            return self.market_make(mid_price)

        mean_price = statistics.mean(self.prices)
        stddev_price = statistics.stdev(self.prices)

        if stddev_price == 0:
            return self.market_make(mid_price)

        z_score = (mid_price - mean_price) / stddev_price

        if z_score > self.z_threshold:
            # Price is too high → Sell
            orders.append(Order(self.product_name, best_bid, -self.trade_size))
            self.active_trade = {
                "entry_price": best_bid,
                "side": "short"
            }

        elif z_score < -self.z_threshold:
            # Price is too low → Buy
            orders.append(Order(self.product_name, best_ask, self.trade_size))
            self.active_trade = {
                "entry_price": best_ask,
                "side": "long"
            }

        else:
            # Neutral → Market make
            return self.market_make(mid_price)

        return orders

    def market_make(self, price):
        return [
            Order(self.product_name, price - 1, 10),
            Order(self.product_name, price + 1, -10)
        ]

#tried to change values for drowzee a bit to make it trade more, pnl=7k
class DrowzeeStrategy(BaseClass):
    def __init__(self):
        super().__init__("DROWZEE", 50)
        self.lookback = 30             # More responsive
        self.z_threshold = 2.0         # Trade more often
        self.prices = []

    def get_orders(self, state, orderbook, position=None):
        orders = []
        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_ask = min(orderbook.sell_orders.keys())
        best_bid = max(orderbook.buy_orders.keys())
        mid_price = (best_bid + best_ask) / 2
        self.prices.append(mid_price)

        if len(self.prices) > self.lookback:
            self.prices.pop(0)

        if len(self.prices) < self.lookback:
            return self.market_make(best_bid, best_ask)

        mean_price = statistics.mean(self.prices)
        stddev_price = statistics.stdev(self.prices)
        if stddev_price == 0:
            return self.market_make(best_bid, best_ask)

        z_score = (mid_price - mean_price) / stddev_price

        if z_score > self.z_threshold:
            orders.append(Order(self.product_name, best_bid, -15))
        elif z_score < -self.z_threshold:
            orders.append(Order(self.product_name, best_ask, 15))
        else:
            return self.market_make(best_bid, best_ask)

        return orders

    def market_make(self, best_bid, best_ask):
        orders = []
        spread = best_ask - best_bid

        if spread >= 2:
            orders.append(Order(self.product_name, best_bid + 1, 10))
            orders.append(Order(self.product_name, best_ask - 1, -10))
        return orders

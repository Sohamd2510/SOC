#tried something with momentum for drowzee, pnl 5.5k
class DrowzeeStrategy(BaseClass):
    def __init__(self):
        super().__init__("DROWZEE", 50)
        self.price_history = []
        self.window = 5
        self.min_trend_strength = 3  # number of consistent moves required
        self.trade_size = 15

    def get_orders(self, state, orderbook, position=None):
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders.keys())
        best_ask = min(orderbook.sell_orders.keys())
        mid_price = (best_bid + best_ask) / 2

        self.price_history.append(mid_price)
        if len(self.price_history) > self.window:
            self.price_history.pop(0)

        if len(self.price_history) < self.window:
            return self.market_make(best_bid, best_ask)

        trend = 0
        for i in range(1, len(self.price_history)):
            if self.price_history[i] > self.price_history[i-1]:
                trend += 1
            elif self.price_history[i] < self.price_history[i-1]:
                trend -= 1

        if trend >= self.min_trend_strength:
            # Strong upward trend → BUY aggressively
            orders.append(Order(self.product_name, best_ask + 1, self.trade_size))
        elif trend <= -self.min_trend_strength:
            # Strong downward trend → SELL aggressively
            orders.append(Order(self.product_name, best_bid - 1, -self.trade_size))
        else:
            # No strong momentum → fallback to MM
            return self.market_make(best_bid, best_ask)

        return orders

    def market_make(self, best_bid, best_ask):
        orders = []
        spread = best_ask - best_bid
        if spread >= 2:
            orders.append(Order(self.product_name, best_bid + 1, 10))
            orders.append(Order(self.product_name, best_ask - 1, -10))
        return orders

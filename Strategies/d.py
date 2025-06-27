#Tried to incorporate mean reversion type thingy while using fair price of 10000, failed got 11k profit
class SudowoodoStrategy(BaseClass): 
    def __init__(self):
        super().__init__("SUDOWOODO", 50)
        self.fair_value = 10000
        self.mid_prices = []
        self.lookback = 30
        self.z_threshold = 2.5

    def get_orders(self, state, orderbook, position=None):
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders.keys())
        best_ask = min(orderbook.sell_orders.keys())
        mid_price = (best_bid + best_ask) / 2

        self.mid_prices.append(mid_price)
        if len(self.mid_prices) > self.lookback:
            self.mid_prices.pop(0)

        if len(self.mid_prices) >= self.lookback:
            mean_price = statistics.mean(self.mid_prices)
            std_dev = statistics.stdev(self.mid_prices)

            if std_dev > 0:
                z_score = (mid_price - mean_price) / std_dev

                if z_score > self.z_threshold:
                    orders.append(Order(self.product_name, best_bid, -10))
                    return orders
                elif z_score < -self.z_threshold:
                    orders.append(Order(self.product_name, best_ask, 10))
                    return orders
                  
        buy_price = min(best_ask - 1, self.fair_value - 1)
        sell_price = max(best_bid + 1, self.fair_value + 1)

        if buy_price < sell_price:
            orders.append(Order(self.product_name, buy_price, 10))
            orders.append(Order(self.product_name, sell_price, -10))

        return orders

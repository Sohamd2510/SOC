# trying some values only
#got 21k pnl (just a bit below the practice code)
def get_orders(self, state, orderbook, position=None):
    orders = []

    if not orderbook.buy_orders or not orderbook.sell_orders:
        return orders

    best_bid = max(orderbook.buy_orders.keys())
    best_ask = min(orderbook.sell_orders.keys())
    spread = best_ask - best_bid
  
    buy_prices = [self.fair_value - 2, self.fair_value - 1]
    sell_prices = [self.fair_value + 1, self.fair_value + 2]

    if spread >= 4:
        buy_prices = [self.fair_value - 3, self.fair_value - 2]
        sell_prices = [self.fair_value + 2, self.fair_value + 3]

    for price in buy_prices:
        orders.append(Order(self.product_name, price, 5))

    for price in sell_prices:
        orders.append(Order(self.product_name, price, -5))

    return orders

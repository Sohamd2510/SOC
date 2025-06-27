#Tried to use the fair_value as avg for market making around it with spread of 2
#pnl 7.5k

class SudowoodoStrategy(BaseClass): 
    def _init_(self):
        super()._init_("SUDOWOODO", 50)

    def get_orders(self, state, orderbook, position=None):  # position unused
        orders = []

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return orders

        best_bid = max(orderbook.buy_orders.keys())
        best_ask = min(orderbook.sell_orders.keys())

        fair_value = (best_bid + best_ask) / 2

        buy_price = int(fair_value - 1)
        sell_price = int(fair_value + 1)

        orders.append(Order(self.product_name, buy_price, 10))   # Buy low
        orders.append(Order(self.product_name, sell_price, -10)) # Sell high

        return orders


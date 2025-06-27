#Tried to use the position to decide the spread
#pnl 8.2k

def get_orders(self, state, orderbook, position):
    orders = []
    
    if not orderbook.buy_orders or not orderbook.sell_orders:
        return orders

    best_bid = max(orderbook.buy_orders.keys())
    best_ask = min(orderbook.sell_orders.keys())
    
    fair_value = (best_bid + best_ask) / 2
    
    skew = -0.1 * position
    adjusted_fv = fair_value + skew

    buy_price = int(adjusted_fv - 1)
    sell_price = int(adjusted_fv + 1)
    
    size = max(1, 10 - abs(position)//5)
    
    # Add orders
    orders.append(Order(self.product_name, buy_price, size))
    orders.append(Order(self.product_name, sell_price, -size))
    
    return orders

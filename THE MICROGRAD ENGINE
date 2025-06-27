
#THIS IS THE MICROGRAD ENGINE
import math
from graphviz import Digraph

class Value:
    """Stores a scalar value and its gradient with autograd support."""

    def __init__(self, data, _children=(), _op='', label=''):
        self.data = data
        self.grad = 0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.label = label  # NEW: helpful for graph visualization

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), '+')

        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward

        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), '*')

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward

        return out

    def __pow__(self, other):
        assert isinstance(other, (int, float)), "only supporting int/float powers for now"
        out = Value(self.data**other, (self,), f'**{other}')

        def _backward():
            self.grad += (other * self.data**(other-1)) * out.grad
        out._backward = _backward

        return out

    def relu(self):
        out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')

        def _backward():
            self.grad += (out.data > 0) * out.grad
        out._backward = _backward

        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), 'tanh')

        def _backward():
            self.grad += (1 - t**2) * out.grad
        out._backward = _backward

        return out

    def backward(self):
        topo = []
        visited = set()

        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        self.grad = 1
        for v in reversed(topo):
            v._backward()

    def __neg__(self): return self * -1
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return other + (-self)
    def __rmul__(self, other): return self * other
    def __truediv__(self, other): return self * other**-1
    def __rtruediv__(self, other): return other * self**-1

    def __repr__(self):
        return f"Value(data={self.data}, grad={self.grad})"

    # Optional: For better string printing
    def __str__(self):
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f}, label='{self.label}')"

    # NEW: Graph Visualization
    def draw_dot(self):
        def trace(root):
            nodes, edges = set(), set()

            def build(v):
                if v not in nodes:
                    nodes.add(v)
                    for child in v._prev:
                        edges.add((child, v))
                        build(child)

            build(root)
            return nodes, edges

        dot = Digraph(format='png', graph_attr={'rankdir': 'LR'})
        nodes, edges = trace(self)

        for n in nodes:
            uid = str(id(n))
            label = f"{n.label} | data={n.data:.4f} | grad={n.grad:.4f}"
            dot.node(uid, label=label, shape='record')
            if n._op:
                dot.node(uid + n._op, label=n._op)
                dot.edge(uid + n._op, uid)

        for src, dst in edges:
            dot.edge(str(id(src)), str(id(dst)) + dst._op)

        return dot

from yaupon.traversal.aggregate_visitor import AggregateVisitor

class X(object):
    dependencies = []
    name = 'X'
    
    def __init__(self, x): pass

class Y(object):
    dependencies = [X]
    name = 'Y'

    def __init__(self, x): pass

class Z(object):
    dependencies = [X]
    name = 'Z'

    def __init__(self, x): pass

class W(object):
    dependencies = [Y,X]
    name = 'W'

    def __init__(self, x): pass

def test_dependency_order_1():
    v = AggregateVisitor(visitors={})
    v.add_visitor(W, None)
    v.add_visitor(X, None)
    v.add_visitor(Y, None)
    v.add_visitor(W, None)
    v.add_visitor(Y, None)
    v.add_visitor(W, None)
    v.add_visitor(Z, None)
    v.compile_visit_order()

    order = [x.name for x in v.visit_order]
    assert len(order) == 4
    assert order.index('X') < order.index('Y')
    assert order.index('X') < order.index('Z')
    assert order.index('X') < order.index('W')
    assert order.index('Y') < order.index('W')

def test_dependency_order_simple():
    v = AggregateVisitor(visitors={})
    v.add_visitor(X, None)
    v.add_visitor(Y, None)
    v.add_visitor(Z, None)
    v.add_visitor(W, None)
    v.compile_visit_order()

    order = [x.name for x in v.visit_order]
    assert len(order) == 4
    assert order.index('X') < order.index('Y')
    assert order.index('X') < order.index('Z')
    assert order.index('X') < order.index('W')
    assert order.index('Y') < order.index('W')

def test_dependency_order_implicit():
    v = AggregateVisitor(visitors={})
    v.add_visitor(W, None)
    v.compile_visit_order()

    order = [x.name for x in v.visit_order]
    assert len(order) == 3
    assert order.index('X') < order.index('Y')
    assert order.index('X') < order.index('W')
    assert order.index('Y') < order.index('W')

def test_dependency_order_2():
    v = AggregateVisitor(visitors={})
    v.add_visitor(Z, None)
    v.add_visitor(W, None)
    v.add_visitor(X, None)
    v.add_visitor(W, None)
    v.add_visitor(X, None)
    v.add_visitor(Y, None)
    v.add_visitor(Y, None)
    v.add_visitor(W, None)
    v.compile_visit_order()

    order = [x.name for x in v.visit_order]
    assert len(order) == 4
    assert order.index('X') < order.index('Y')
    assert order.index('X') < order.index('Z')
    assert order.index('X') < order.index('W')
    assert order.index('Y') < order.index('W')



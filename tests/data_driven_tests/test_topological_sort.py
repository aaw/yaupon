from yaupon.tests.testutils import graph_database_iteration
from yaupon.traversal import depth_first_generator
from yaupon.algorithm.exceptions import NoIndegreeZeroVertices, CycleExists
import yaupon.algorithm.topological_sort as topological_sort

def pytest_generate_tests(metafunc):
    graph_database_iteration(metafunc)

def test_topological_ordering(graph):
    g = graph()
    
    # Does the input graph have a cycle?
    has_cycle = False
    s = depth_first_generator(g)
    for v in g.vertices():
        s.bootstrap(v)
    for e in s.events():
        if e['type'] == 'EDGE' and e['target_state'] == 'DISCOVERED':
            has_cycle = True
            break

    # Does the input graph have any vertices of indegree 0?
    has_indegree_zero_vertices = False
    for v in g.vertices():
        try:
            g.edges(target=v).next()
        except StopIteration:
            has_indegree_zero_vertices = True

    # Run the topological sort, exit if the graph doesn't have
    # indegree zero vertices or has a cycle and either is detected
    # correctly
    try:
        order_generator = topological_sort.compile(g)
    except NoIndegreeZeroVertices:
        assert not has_indegree_zero_vertices
        return
    except CycleExists:
        assert has_cycle
        return

    # Otherwise, the topological ordering returned should respect
    # all of the individual edge orderings.
    order = [x for x in order_generator()]
    for e in g.edges():
        assert order.index(e[0]) < order.index(e[1])

    
        

    

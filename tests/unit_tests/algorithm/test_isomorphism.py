import py.test
import yaupon.algorithm.isomorphism as isomorphism
from yaupon.algorithm.exceptions import NoIsomorphismExists
from yaupon.tests.testutils import pytest_generate_tests

def test_two_cycles_against_one_cycle(graph_type):
    """
    Two cycles of length n have the same degree sequence
    as one cycle of length 2n, so can fool isomorphism
    detection that relies on degree sequences
    """
    def cycle_edges(start_vertex, length):
        edges = [(x,x+1) for x in xrange(start_vertex,length)]
        edges.append((start_vertex + length - 1, start_vertex))
        return edges
    
    for cycle_length in [3,4,5,10,20]:
        g1 = graph_type(edges = cycle_edges(0, cycle_length) +  
                                cycle_edges(cycle_length, cycle_length))
        g2 = graph_type(edges = cycle_edges(0, 2*cycle_length))
        py.test.raises(NoIsomorphismExists, 'isomorphism.compile(g1,g2)')

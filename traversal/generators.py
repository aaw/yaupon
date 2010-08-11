from yaupon.data_structures import ydeque, ydict, yheap
from yaupon.util.shortcuts import other_vertex
from yaupon.traversal.traversal_exception import SuccessfulTraversal

UNDISCOVERED = 'UNDISCOVERED'
DISCOVERED = 'DISCOVERED'
FINISHED = 'FINISHED'

class base_generator(object):
    def __init__(self, graph):
        self.__vertex_state = ydict(backend=graph)
        self.graph = graph

    def bootstrap(self, v):
        if self.__get_state(v) != UNDISCOVERED:
            return False
        self.__put_next_discovered(v)
        return True

    def __get_state(self, v):
        return self.__vertex_state.get(v, UNDISCOVERED)

    def __put_next_discovered(self, v):
        self.__vertex_state[v] = DISCOVERED
        self.put({'type':'VERTEX', 'state':FINISHED, 'vertex':v})
        for e in self.graph.edges(source=v):
            self.put({'type':'EDGE', 'edge':e})

    def events(self):
        while self.has_more():
            record = self.get()
            if record['type'] == 'EDGE':
                source, target = record['edge']
                record['source_state'] = self.__get_state(source)
                record['target_state'] = self.__get_state(target)
                if record['target_state'] == UNDISCOVERED:
                    self.__put_next_discovered(record['edge'][1])
            else:
                self.__vertex_state[record['vertex']] = record['state']
            yield record

class depth_first_generator(base_generator):
    def __init__(self, graph):
        base_generator.__init__(self, graph)
        self.__deque = ydeque(backend=graph)

    def put(self, item):
        self.__deque.append(item)

    def get(self):
        return self.__deque.pop()

    def has_more(self):
        return bool(self.__deque)

class breadth_first_generator(base_generator):
    def __init__(self, graph):
        base_generator.__init__(self, graph)
        self.__deque = ydeque(backend=graph)

    def put(self, item):
        self.__deque.append(item)

    def get(self):
        return self.__deque.popleft()
       
    def has_more(self):
        return bool(self.__deque)
 

class uniform_cost_generator(object):
    def __init__(self, graph, edge_weight):
        self.__graph = graph
        self.__edge_weight = edge_weight
        self.__priority_queue = yheap(backend=graph)
        self.__vertex_state = ydict(backend=graph)

    def bootstrap(self, vertex):
        if self.__get_state(vertex) != UNDISCOVERED:
            return False
        self.__put_next_discovered(vertex, 0)
        return True

    def __get_state(self, v):
        return self.__vertex_state.get(v, UNDISCOVERED)

    def __put_next_discovered(self, v, cost):
        self.__vertex_state[v] = DISCOVERED
        for e in self.__graph.edges(source=v):
            edge_cost = cost + self.__edge_weight[e]
            self.__priority_queue.insert(item=e, key=edge_cost)

    def events(self):
        while self.__priority_queue:
            cost = self.__priority_queue.findminkey()
            edge = self.__priority_queue.deletemin()
            vertex = edge[1]
            target_state = self.__get_state(vertex)
            if target_state == UNDISCOVERED:
                self.__put_next_discovered(vertex, cost)
            yield {'type':'EDGE', 
                   'edge':edge, 
                   'cost':cost, 
                   'target_state':target_state}



class best_first_generator(object):
    def __init__(self, graph, vertex_heuristic):
        self.__graph = graph
        self.__h = vertex_heuristic
        self.__priority_queue = yheap(backend=graph)
        self.__vertex_state = ydict(backend=graph)

    def bootstrap(self, vertex):
        if self.__get_state(vertex) != UNDISCOVERED:
            return False
        self.__put_next_discovered(vertex)
        return True

    def __get_state(self, v):
        return self.__vertex_state.get(v, UNDISCOVERED)

    def __put_next_discovered(self, v):
        self.__vertex_state[v] = DISCOVERED
        for e in self.__graph.edges(source=v):
            self.__priority_queue.insert(item=e, key=self.__h[e[1]])

    def events(self):
        while self.__priority_queue:
            cost = self.__priority_queue.findminkey()
            edge = self.__priority_queue.deletemin()
            vertex = edge[1]
            target_state = self.__get_state(vertex)
            if target_state == UNDISCOVERED:
                self.__put_next_discovered(vertex)
            yield {'type':'EDGE', 
                   'edge':edge, 
                   'cost':cost, 
                   'target_state':target_state}
            if cost == 0:
                return

# a*, uniform_cost, and best_first can all be merged into one class,
# since this is basically cut and paste for now until everything is
# tested
class a_star_generator(object):
    def __init__(self, graph, edge_weight, vertex_heuristic):
        self.__graph = graph
        self.__edge_weight = edge_weight
        self.__h = vertex_heuristic
        self.__priority_queue = yheap(backend=graph)
        self.__vertex_state = ydict(backend=graph)

    def bootstrap(self, vertex):
        if self.__get_state(vertex) != UNDISCOVERED:
            return False
        self.__put_next_discovered(vertex, self.__h[vertex])
        return True

    def __get_state(self, v):
        return self.__vertex_state.get(v, UNDISCOVERED)

    def __put_next_discovered(self, v, cost):
        #print 'next discovered = %s' % v
        self.__vertex_state[v] = DISCOVERED
        for e in self.__graph.edges(source=v):
            edge_cost = self.__edge_weight[e] + self.__h[e[1]]
            cost_estimate = cost - self.__h[e[0]] + edge_cost \
                            if edge_cost >= 0 \
                            else cost
            #print 'Cost estimate of %s is %s + %s + %s - %s = %s' % \
            #       (e, cost, self.__edge_weight[e], self.__h[e[1]], 
            #        self.__h[e[0]], cost_estimate)
            self.__priority_queue.insert(item=e, key=cost_estimate)

    def events(self):
        while self.__priority_queue:
            cost = self.__priority_queue.findminkey()
            edge = self.__priority_queue.deletemin()
            vertex = edge[1]
            h_value = self.__h[vertex]
            target_state = self.__get_state(vertex)
            if target_state == UNDISCOVERED:
                self.__put_next_discovered(vertex, cost)
            #TODO: rekey discovered edges?
            yield {'type':'EDGE', 
                   'edge':edge, 
                   'cost':cost - h_value,
                   'distance': h_value,
                   'target_state':target_state}


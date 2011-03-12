from yaupon.traversal import *
from yaupon.adapters.undirected_graph import UndirectedGraph
from yaupon.util.shortcuts import other_vertex

from itertools import chain
from functools import partial
from operator import getitem

DEBUG_LEVEL = 0 # greater value == less output

def PRINT(s, level = None):
    if level is None or level > DEBUG_LEVEL:
        print(s)

class face_iterator(object):
    def __init__(self, lead, follow, face_handles):
        self.lead = lead
        self.follow = follow
        self.face_handles = face_handles

    def __iter__(self):
        return self

    def next(self):
        old_lead = self.lead
        face_handle = self.face_handles[self.lead]
        if not face_handle.handle_list:
            raise StopIteration

        first_endpoint = face_handle.first_endpoint()
        second_endpoint = face_handle.second_endpoint()
        if first_endpoint == self.follow:
            self.lead = second_endpoint
        elif second_endpoint == self.follow:
            self.lead = first_endpoint
        elif first_endpoint == second_endpoint: # one-edge bicomp
            self.lead = first_endpoint
        else:
            raise StopIteration

        self.follow = old_lead
        return self.lead


class face_handle(object):
    def __init__(self, vertex, handle_list):
        self.vertex = vertex
        self.handle_list = handle_list

    def first_endpoint(self):
        u,v = self.handle_list[0]
        return u if v == self.vertex else v

    def second_endpoint(self):
        u,v = self.handle_list[-1]
        return u if v == self.vertex else v

    def __str__(self):
        return '%s: %s' % (self.vertex, self.handle_list)

    def __repr__(self):
        return str(self)







class boyer_myrvold(object):

    def __init__(self, g):
        self.g = UndirectedGraph(g)

        v = {LowPoint:None, LeastAncestor:None, Parent:None, ParentEdge:None}
        self.vis = AggregateVisitor(backend=self.g, visitors=v)
        traverse(self.g.vertices(), self.vis, depth_first_generator(self.g))

        self.vertices_by_lowpoint = \
            sorted(self.g.vertices(), 
                   key=partial(getitem, self.vis.LowPoint))

        self.vertices_by_dfs_num = \
            sorted(self.g.vertices(), 
                   key=partial(getitem, self.vis.DiscoverTime))

        self.face_handle = {}
        self.df_face_handle = {}
        self.canonical_df_child = dict((v,v) for v in self.g.vertices())
        self.pertinent_roots = dict((v,[]) for v in self.g.vertices())
        self.separated_df_child_list = dict((v,[]) for v in self.g.vertices())
        self.self_loops = []
        self.backedges = dict((v,[]) for v in self.g.vertices())
        self.backedge_flag = dict((v,-1) for v in self.g.vertices())
        self.visited = dict((v,-1) for v in self.g.vertices())

        for v in self.g.vertices():
            parent = self.vis.Parent.get(v)
            parent_edge = self.vis.ParentEdge.get(v)
            handle_list = [] if parent is None else [parent_edge]
            self.face_handle[v] = face_handle(v, handle_list[:])
            self.df_face_handle[v] = face_handle(parent, handle_list[:])

        PRINT('Parent: %s' % self.vis.Parent, 1)

        for v in self.g.vertices():
            PRINT('ParentEdge %s: %s' % (v, self.vis.ParentEdge.get(v)), 1)

        for v in self.g.vertices():
            PRINT('DiscoverTime %s: %s' % (v, self.vis.DiscoverTime.get(v)), 1)

        for v in self.g.vertices():
            PRINT('LowPoint %s: %s' % (v, self.vis.LowPoint.get(v)), 1)

        PRINT('Vertices by dfs num: %s' % self.vertices_by_dfs_num)
            

    def planar_embedding(self):

        for v in reversed(self.vertices_by_dfs_num):
            self.store_old_face_handles()
            self.walkup(v)
            if not self.walkdown(v):
                 return False

        self.clean_up_embedding()
        return True

    def walkup(self, v):
        
        PRINT('--- Starting walkup from %s ---' % v, 1)
        PRINT('--- edges to consider: %s ---' % \
                  [e for e in self.g.edges(source=v)])
        for e in self.g.edges(source = v):
            w = other_vertex(e, v)
            PRINT('Looking at (v,w) = (%s,%s)' % (v,w), 4)
            if v == w:
                self.self_loops.append(e)
                continue
            
            if self.vis.DiscoverTime[w] < self.vis.DiscoverTime[v] or \
               e == self.vis.ParentEdge[w]:
                continue

            self.backedges[w].append(e)
            timestamp = self.vis.DiscoverTime[v]
            self.backedge_flag[w] = timestamp

            for face_itr in chain((w,),self.first_face_iter(w)):
                PRINT('Traveler: %s' % face_itr)
                if face_itr == v or self.visited[face_itr] == timestamp:
                    break
                elif self.is_bicomp_root(face_itr):
                    PRINT('Setting visited/pertinent roots for %s' % face_itr)
                    dfs_child = self.canonical_df_child[face_itr]
                    parent = self.vis.Parent.get(dfs_child, dfs_child)
                    handle = self.df_face_handle[dfs_child]
                    PRINT('Handle: %s' % handle)
                    if handle.vertex is not None:
                        self.visited[handle.first_endpoint()] = timestamp
                        self.visited[handle.second_endpoint()] = timestamp

                    v_df_number = self.vis.DiscoverTime[v]
                    if self.vis.LowPoint[dfs_child] < v_df_number or \
                       self.vis.LeastAncestor[dfs_child] < v_df_number:
                        PRINT('Appending %s to %s''s prs' % (handle, parent))
                        self.pertinent_roots[parent].append(handle)
                    else:
                        PRINT("Prepending %s to %s's prs" % (handle, parent))
                        self.pertinent_roots[parent].insert(0,handle)
                self.visited[face_itr] = timestamp

        PRINT('--- Done with walkup from %s ---' % v, 1)    
        PRINT('Visited: %s' % self.visited, 1)
            


    def walkdown(self, v):
        
        PRINT('--- Starting walkdown from %s ---' % v, 1)
        PRINT('pertinent roots: %s' % self.pertinent_roots[v], 1)
        merge_stack = []
        while self.pertinent_roots[v]:
            root_handle = self.pertinent_roots[v].pop(0)
            curr_handle = root_handle
            PRINT('Traversing from handle %s' % curr_handle)

            endpoints = []
            PRINT('Traversal endpoints are %s and %s' % \
                (curr_handle.first_endpoint(), curr_handle.second_endpoint()))
            first_endpoint = curr_handle.first_endpoint()
            second_endpoint = curr_handle.second_endpoint()
            if first_endpoint == second_endpoint:
                endpoints.append((curr_handle.vertex, first_endpoint))
            else:
                for endpoint in (first_endpoint, second_endpoint):
                    tail = curr_handle.vertex
                    for face_v in face_iterator(curr_handle.vertex, 
                                                endpoint,
                                                self.face_handle):
                        if self.pertinent(face_v, v) or \
                           self.externally_active(face_v, v):
                            endpoints.append((tail, face_v))
                            break
                    tail = face_v
            PRINT('Endpoints: %s' % endpoints)

            first_tail, first_side_vertex = endpoints[0]
            second_tail, second_side_vertex = endpoints[-1]
            if self.internally_active(first_side_vertex, v):
                chosen, chose_first_upper_path = first_side_vertex, True
            elif self.internally_active(second_side_vertex, v):
                chosen, chose_first_upper_path = second_side_vertex, False
            elif self.pertinent(first_side_vertex, v):
                chosen, chose_first_upper_path = first_side_vertex, True
            elif self.pertinent(second_side_vertex, v):
                chosen, chose_first_upper_path = second_side_vertex, False
            else:
                PRINT('NOT PLANAR!')
                return False

            PRINT('Chosen: %s, Chose first: %s' % \
                  (chosen, chose_first_upper_path))


        PRINT('--- Done with walkdown from %s ---' % v, 1)
        return True


    def store_old_face_handles(self):
        pass

    def clean_up_embedding(self):
        pass

    def first_face_iter(self, v):
        return face_iterator(v, self.face_handle[v].first_endpoint(), 
                             self.face_handle)

    def second_face_iter(self, v):
        return face_iterator(v, self.face_handle[v].second_endpoint(), 
                             self.face_handle)

    def pertinent(self, w, v):
        return self.backedge_flag[w] == self.vis.DiscoverTime[v] or \
               self.pertinent_roots[w]

    def externally_active(self, w, v):
        v_num = self.vis.DiscoverTime[v]
        return self.vis.LeastAncestor[w] < v_num or \
               (self.separated_df_child_list[w] and \
                self.vis.LowPoint[self.separated_df_child_list[w][0]] < v_num)

    def internally_active(self, w, v):
        return self.pertinent(w,v) and not self.externally_active(w,v)

    def is_bicomp_root(self, v):
        handle = self.face_handle[v]
        if not handle.handle_list:
            return True
        first_endpoint = handle.first_endpoint()
        second_endpoint = handle.second_endpoint()
        if first_endpoint == second_endpoint:
            return True # one-edge bicomp
        if face_handle[first_endpoint].first_endpoint() != v and \
           face_handle[first_endpoint].second_endpoint() != v:
            return True
        return False
            

if __name__ == '__main__':
    import yaupon
    g = yaupon.Graph()

    if False:

        for v_num in xrange(1,10):
            g.add_vertex(v_num)

        g.add_edge(1,2)
        g.add_edge(2,9)
        g.add_edge(2,3)
        g.add_edge(3,8)
        g.add_edge(3,4)
        g.add_edge(4,5)
        g.add_edge(5,6)
        g.add_edge(5,7)
        g.add_edge(1,9)
        g.add_edge(2,8)
        g.add_edge(4,6)
        g.add_edge(4,7)

    elif True:

        for i in xrange(5):
            for j in xrange(i):
                PRINT('Adding (%s,%s)' % (i,j))
                g.add_edge(i,j)

    else:

        for i in xrange(5):
            g.add_edge(i, i+1)

    print 'Graph is: %s' % [e for e in g.edges()]
    import time
    start = time.time()
    bm = boyer_myrvold(g)
    res = bm.planar_embedding()
    print 'Result is: %s' % res
    PRINT(time.time() - start)

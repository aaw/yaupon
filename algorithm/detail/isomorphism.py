from itertools import izip
from functools import partial

from yaupon.data_structures import ydict, ydeque, ysorted
from yaupon.algorithm import connected_components

def reachability_signature(g, reach):
    sig = ydict(backend=g)
    for v in g.vertices():
        sig[v] = ydeque(sig, [1])
    for i in range(reach):
        for u in g.vertices():
            val = sum(sig[v][i] for x,v in g.edges(source=u))
            sig[u].append(val)
    return ydict(g, ((k,v[-1]) for k,v in sig.iteritems()))


def connected_component_signature(g):
    components = connected_components.compile(g)
    component_size = ydict(g)
    for v in g.vertices():
        c = components(v)
        component_size[c] = component_size.setdefault(c,0) + 1
    return ydict(g, ((v, component_size[components(v)]) for v in g.vertices()))


def canonical_form(g, test_funcs):
    result_dicts = [func(g) for func in test_funcs]
    return ydict(g, ((v,tuple(d[v] for d in result_dicts)) 
                     for v in g.vertices()))


def function_inverse(f, backend):
    inverse = ydict(backend=backend)
    for key, value in f.iteritems():
        inverse.setdefault(value,ydeque(backend=inverse)).append(key)
    return inverse


def is_a_partial_isomorphism(g1, g2, iso):
    """
    Precondition: len(g1.vertices()) == len(g2.vertices()) and
                  len(g1.edges()) == len(g2.edges())
    """
    g2_edges_mapped = ydict(backend=g1)
    for u,v in g1.edges():
        is_a_partial_iso = False
        try:
            u_image, v_image = iso[u], iso[v]
        except KeyError:
            continue
        chosen_edge = None
        for edge in g2.edges(source=u_image, target=v_image):
            if g2_edges_mapped.get(edge) is None:
                g2_edges_mapped[edge] = True
                chosen_edge = edge
                break
        if chosen_edge is None:
            return False
    return True


def isomorphism(g1, g2):
    if sum(1 for v in g1.vertices()) != sum(1 for v in g2.vertices()) or \
       sum(1 for e in g1.edges()) != sum(1 for e in g2.edges()):
        return None

    test_funcs = [partial(reachability_signature, reach=1),
                  partial(reachability_signature, reach=2),
                  partial(reachability_signature, reach=4)]
    g1cf = canonical_form(g1, test_funcs)
    g2cf = canonical_form(g2, test_funcs)

    sorted_g1cf = ysorted(g1, g1cf.itervalues())
    sorted_g2cf = ysorted(g2, g2cf.itervalues())

    for x,y in izip(sorted_g1cf, sorted_g2cf):
        if x != y:
            return None

    g2_cform_inv = function_inverse(g2cf, g2)

    iso = ydict(backend=g1)

    contexts = ydeque(backend=g1)
    for v in g1.vertices():
        g2_inv_image = ydeque(backend=contexts)
        for image_element in g2_cform_inv[g1cf[v]]:
            g2_inv_image.append(image_element)
        contexts.append((v, g2_inv_image))
    index = 0

    while index >= 0 and index < len(contexts):
        vertex = contexts[index][0]
        if contexts[index][1]:
            v_prime = contexts[index][1].popleft()
            iso[vertex] = v_prime
            if is_a_partial_isomorphism(g1, g2, iso):
                index += 1
        else:
            if vertex in iso:
                del iso[vertex]
            g2_inv_image = ydeque(backend=contexts)
            for image_element in g2_cform_inv[g1cf[vertex]]:
                g2_inv_image.append(image_element)
                (index, vertex, str([x for x in g2_inv_image]))
            contexts[index] = (vertex, g2_inv_image)
            index -= 1

    if index < 0:
        return None
    else:
        return iso


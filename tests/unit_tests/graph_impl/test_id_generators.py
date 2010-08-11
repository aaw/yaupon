import inspect
import yaupon.graph_impl.id_generators as generators

def test_generators():
    """
    We'll assume every class definition in id_generators is an
    id generator, and try to generate 10,000 ids with it. As long
    as all of those are unique, we'll assume that it's a good generator
    """
    id_gens = [x for x in dir(generators) \
                 if inspect.isclass(getattr(generators,x))]
    for id_generator in id_gens:
        generator = getattr(generators, id_generator)()
        ids = set()
        for i in xrange(10000):
            id = generator()
            assert id not in ids
            ids.add(id)

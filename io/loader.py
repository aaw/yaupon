import os

import yaupon
import yaupon.io.ygp as ygp

def load(path, GraphType = None):
     print 'Path is %s' % path
     if GraphType is None:
         GraphType = yaupon.Graph
     for file in os.listdir(path):
         fullname = os.path.join(path, file)
         if os.path.isfile(fullname) and file.endswith('.ygp'):
             g = GraphType()
             ygp.load(open(fullname, 'rb'), g)
             yield g
         elif os.path.isdir(fullname):
             load(fullname, GraphType)

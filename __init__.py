VERSION = 0.01

import config

Graph = config.dispatch_graph
Forest = config.dispatch_forest

from yaupon.data_structures import ydeque, ydict, ysorted, yheap, yunion_find

from yaupon.backend import BackendCore, BackendSQLite
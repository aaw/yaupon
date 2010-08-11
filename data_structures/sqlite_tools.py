import cPickle as pickle
import sqlite3

def to_db(value, pickle_protocol = 2):
    return sqlite3.Binary(pickle.dumps(value, pickle_protocol))

def from_db(value):
    return pickle.loads(str(value))

#backend_cache: backend_id -> backend
backend_cache = {}

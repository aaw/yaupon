import uuid

class UUIDGenerator(object):
    def __call__(self):
        return str(uuid.uuid4())

class IntGenerator(object):
    def __init__(self, start = None):
        if start is None:
            start = -1
        self.next_id = start

    def __call__(self):
        self.next_id += 1
        return self.next_id

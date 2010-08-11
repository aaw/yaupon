
class TraversalException:
    def __init__(self, info = None):
        self.info = info
        
class SuccessfulTraversal(TraversalException): pass
class UnsuccessfulTraversal(TraversalException): pass

class UnknownPoolException(Exception):
    
    def __init__(self, message):
        self._message = message
        super().__init__(self._message)
    
class PoolAlreadyExistsException(Exception):

    def __init__(self, message):
        self._message = message
        super().__init__(self._message)

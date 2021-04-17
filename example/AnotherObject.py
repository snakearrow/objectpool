from objectpool import GenericObject

class AnotherObject(GenericObject):
    
    def __init__(self, _cnt: int = 0):
        super().__init__()
        self._cnt = _cnt
        self._huge = 100*["test"]
        
    def set_cnt(self, cnt: int):
        self._cnt = cnt
        
    def get_cnt(self):
        return self._cnt
        
    def __str__(self):
        return f"AnotherObject(cnt={self._cnt})"

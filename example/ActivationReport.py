from GenericObject import *

class ActivationReport(GenericObject):

    _cnt = 0
    
    def __init__(self, _cnt: int = None):
        super().__init__()
        self._cnt = _cnt
        
    def set_cnt(self, cnt: int):
        self._cnt = cnt
        
    def get_cnt(self):
        return self._cnt
        
    def __str__(self):
        return f"ActivationReport(cnt={self._cnt})"

from abc import ABC, abstractmethod
import pyhash

class GenericObject(ABC):

    _hasher = pyhash.super_fast_hash()
    
    def _get_name(self):
        return self.__class__.__name__
        
    def _get_id(self):
        return self._hasher(self._get_name())
        
    def __str__(self):
        return "GenericObject"

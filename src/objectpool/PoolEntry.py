from .GenericObject import GenericObject
from datetime import datetime


class PoolEntry:

    def __init__(self, obj: GenericObject):
        self._obj = obj
        self._ts = datetime.now()
        
    def get_object(self):
        return self._obj
        
    def get_object_id(self):
        return self._obj._get_id()
        
    def get_object_name(self):
        return self._obj._get_name()
        
    def get_age(self):
        return datetime.now() - self._ts
        
    def get_timestamp(self):
        return self._ts
        
    def get_timestamp_str(self):
        return self._ts.strftime("%Y-%m-%d, %H:%M:%S.%f")
        
    def __eq__(self, obj):
        if self.get_object_id() != obj.get_object_id():
            return False
        if self.get_timestamp() != obj.get_timestamp():
            return False
        return True
        
    def __str__(self):
        return f"PoolEntry for Object {self.get_object_name()}"

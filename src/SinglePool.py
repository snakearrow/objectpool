from GenericObject import GenericObject
from PoolEntry import PoolEntry
from collections import deque
import threading
import sys


class Subscription:    
    """
        A subscription contains a function to call when a certain object is put
        into the queue.
    """
        
    def __init__(self, obj_id: int, fnct, args: list, filter_func, filter_func_args):
        self._obj_id = obj_id
        self._function = fnct
        self._args = args
        self._filter_func = filter_func
        self._filter_func_args = filter_func_args
        self._pool_name = None
        
    def set_pool_name(self, pool_name):
        self._pool_name = pool_name
        
    def get_pool_name(self):
        return self._pool_name
            
    def is_for(self, o: GenericObject):
        return o._get_id() == self._obj_id
            
    def call(self, obj):
        process = True
        if self._filter_func:
            if self._filter_func_args:
                process = self._filter_func(obj, self._filter_func_args)
            else:
                process = self._filter_func(obj)
                
        if not process:
            return
        
        if self._args:
            t = threading.Thread(target=self._function, args=(obj, self._args,))
        else:
            t = threading.Thread(target=self._function, args=(obj,))
        t.start()



class SinglePool:

    def __init__(self, name: str, max_size: int = None):
        self._name = name
        self._max_size = max_size
        self._cur_size = 0
        self._queue = {}  # format: queue[obj_id] = [list, of, pool_entries]
        self._subscriptions = []
        
    def purge(self):
        max_len = 0
        max_len_obj_id = None
        for obj_id, lst in self._queue.items():
            if len(lst) >= max_len:
                max_len = len(lst)
                max_len_obj_id = obj_id
        if max_len_obj_id:
            self._queue[max_len_obj_id].popleft()
            self._cur_size -= 1
        
    def put(self, obj: GenericObject):
        entry = PoolEntry(obj)
        obj_id = obj._get_id()
        if obj_id not in self._queue:
            self._queue[obj_id] = deque()
        
        self._queue[obj_id].append(entry)
        
        self._cur_size += 1
        if self._max_size:
            if self._cur_size > self._max_size:
                self.purge()
                
        # check if we have to notify any subscribers
        for s in self._subscriptions:
            if s.is_for(obj):
                s.call(obj)
    
    def get_queue(self):
        return self._queue
        
    def get_name(self):
        return self._name
        
    def length(self):
        return self._cur_size
        
    def get_max_size(self):
        return self._max_size
        
    def is_empty(self):
        return self._cur_size <= 0
        
    def n_subscriptions(self):
        return len(self._subscriptions)
        
    def subscribe(self, obj, fnct, args: list, filter_func, filter_func_args):
        self._subscriptions.append(Subscription(obj._get_id(), fnct, args, filter_func, filter_func_args))
        
    def subscribe_with_obj(self, subscription: Subscription):
        self._subscriptions.append(subscription)


from .SinglePool import SinglePool, Subscription
from .GenericObject import GenericObject
from .PoolEntry import PoolEntry
from .Exceptions import UnknownPoolException, PoolAlreadyExistsException
from .UI import UI
from dearpygui import core, simple
import threading
import psutil
import os
import time


class ObjectPool:

    def __init__(self, name: str = None):
        self._name = name
        self._pools = {}
        self._lock = threading.Lock()
        self._pending_subscriptions = []
        self._ui = UI(name, self._pools)
        self._quit = False
        
    def register_pool(self, name: str, max_size: int = None, fail_if_already_registered=True):
        with self._lock:
            if name in self._pools:
                if fail_if_already_registered:
                    raise PoolAlreadyExistsException(f"Failed to register pool: Pool with name '{name}' already exists")
                return
            
            pool = SinglePool(name, max_size=max_size)
            self._pools[name] = pool
            self._ui.mark_dirty()
            
            # check if there are any pending subscriptions
            for subscription in list(self._pending_subscriptions):
                if subscription.get_pool_name() == name:
                    self._pools[name].subscribe_with_obj(subscription)
                    self._pending_subscriptions.remove(subscription)
                    print(f"Successfully subscribed pending subscription to pool {name}")
                    
    def deregister_pool(self, name, fail_if_already_deregistered=True):
        with self._lock:
            if name in self._pools:
                del self._pools[name]
                self._ui.mark_dirty()
            elif fail_if_already_deregistered:
                raise UnknownPoolException(f"Failed to deregister pool '{name}'")
                
    def is_registered(self, name):
        return name in self._pools
        
    def put(self, pool_name: str, obj: GenericObject):
        if pool_name in self._pools:
            with self._lock:
                self._pools[pool_name].put(obj)
        else:
            raise UnknownPoolException(f"Failed to put object into pool: Pool '{pool_name}' does not exist")

    def size(self, pool_name: str):
        if pool_name in self._pools:
            return self._pools[pool_name].size()
        return None
        
    def get_all(self, pool_name: str):
        if pool_name in self._pools:
            return self._pools[pool_name].get_queue()
        return None
        
    def subscribe(self, pool_name: str, obj, fnct, args: list = None, filter_func = None, filter_func_args = None):
        with self._lock:
            inst = obj()
            if pool_name in self._pools:
                self._pools[pool_name].subscribe(inst, fnct, args, filter_func, filter_func_args)
            else:
                print(f"Cannot subscribe to pool {pool_name} yet, will do if pool is created")
                subscription = Subscription(inst._get_id(), fnct, args, filter_func, filter_func_args)
                subscription.set_pool_name(pool_name)
                self._pending_subscriptions.append(subscription)
        
    def _update_ui_thread(self):
        while not self._quit:
            self._ui.update(self._pools)
            time.sleep(0.25)
        
    def show_ui(self):
        t = threading.Thread(target=self._update_ui_thread)
        self._ui.show()
        t.start()
        
    def quit(self):
        self._quit = True
        self._ui.destroy()
        
    def __str__(self):
        return f"ObjectPool {self._name}"


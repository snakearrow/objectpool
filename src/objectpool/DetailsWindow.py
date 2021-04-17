from .PoolEntry import PoolEntry
from dearpygui import core, simple
from typing import Callable
import threading
from time import sleep
from timeit import default_timer as timer


class DetailsWindow:

    def __init__(self, entry: PoolEntry, pool_name: str, destroy_func: Callable):
        self._entry = entry
        self._pool_name = pool_name
        self._win_name = f"Details_{self._pool_name}_{self._entry.get_object_name()}"
        self._destroy_func = destroy_func
        self._frequency_cnt = 0
        self._frequency = 0.0
        self._freq_thread = threading.Thread(target=self._calc_frequency_thread)
        self._active = True
        
    def _calc_frequency_thread(self):
        ts_start = timer()
        while self._active:
            ts_stop = timer()
            diff = ts_stop - ts_start
            
            if diff >= 2.123:
                if self._frequency_cnt > 0:
                    self._frequency = 1.0 / (diff / self._frequency_cnt)
                    self._frequency_cnt = 0
                    ts_start = timer()
                
            sleep(0.1)
        
    def show(self) -> None:
        if core.does_item_exist(self._win_name):
            self.destroy(self._win_name)
            
        obj_name = self._entry.get_object_name()
        
        with simple.window(self._win_name, label=f"{obj_name}", on_close=self.destroy, width=400):
            ts = self._entry.get_timestamp_str()
            age = self._entry.get_age()
            
            core.add_label_text(self._win_name+"ts", label=f"Timestamp", default_value=f"{ts}")
            core.add_label_text(self._win_name+"age", label=f"Age", default_value=f"{age}")
            core.add_label_text(self._win_name+"freq", label=f"Frequency", default_value=f"0.0 Hz")
            core.add_text("")
            core.add_label_text(self._win_name+"content", default_value=str(self._entry.get_object()), label="")
            
        self._freq_thread.start()
            
    def update(self, entry: PoolEntry):
        if entry == self._entry:
            return
        
        core.set_value(self._win_name+"ts", entry.get_timestamp_str())
        core.set_value(self._win_name+"content", str(entry.get_object()))
        core.set_value(self._win_name+"freq", "{:.2f} Hz".format(self._frequency))
        
        self._entry = entry
        self._frequency_cnt += 1
        
    def update_static(self):
        # updates values like age (which do not require a new entry)
        age = self._entry.get_age()
        core.set_value(self._win_name+"age", str(age))
    
    def destroy(self, sender):
        self._destroy_func(sender)
        self._active = False
        self._freq_thread.join()
        
    def get_name(self):
        return self._win_name
        
    def get_pool_name(self):
        return self._pool_name
        
    def get_obj_id(self):
        return self._entry.get_object_id()

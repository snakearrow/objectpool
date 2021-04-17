## Summary
objectpool is a Python implementation for object pools. The library let's you
- create object pools
- put arbitrary objects into pools
- subscribe for new objects

## Installation
Currently there is no official release yet. You can build a python wheel by using\
`python3 -m build`\
This will create a wheel which can be installed by using pip.

### Example
---
```Python
from objectpool import ObjectPool
from MyObject import MyObject
from AnotherObject import AnotherObject

def handle_my_obj(obj):
  print(obj)

if __name__ == "__main__":
  pool = ObjectPool("My Pool")
  pool.register_pool("P1")
  pool.subscribe("P1", MyObject, handle_my_obj)
  pool.put("P1", AnotherObject())
```

### API
---
#### Create new pools
```Python
pool = ObjectPool("Main Pool Name")
pool.register_pool("Pool Name 1")
pool.register_pool("Pool Name 2", max_size=100)
pool.register_pool("Pool Name 1", fail_if_already_registered=False)
```

#### Put objects into pool
---
Objects which can be put into a pool have to inherit from `GenericObject`:
```Python
from objectpool import GenericObject

class MyObject(GenericObject):

    _cnt = 0
    
    def __init__(self, _cnt: int = None):
        super().__init__()
        self._cnt = _cnt
        
    def set_cnt(self, cnt: int):
        self._cnt = cnt
        
    def get_cnt(self):
        return self._cnt
        
    def __str__(self):
        return f"MyObject(cnt={self._cnt})"
```

```Python
for i in range(100):
  obj = MyObject(i)
  pool.put("P1", obj)
```



#### Subscribe for new objects
---
You can subscribe for any new object which is put into a pool:
```Python
def handle_myobject(obj: MyObject):
  print("Object MyObject was put into pool")
  
pool.subscribe("P1", MyObject, handle_myobject)
```

Subscriptions support arguments and filter functions:
```Python
def handle_myobject(obj: MyObject, args):
  print("Object MyObject was put into pool")
  print(f"Args = {args})
  
def filter_myobject(obj: MyObject, min_size: int):
  return obj.get_cnt() >= min_size
  
pool.subscribe("P1", MyObject, handle_myobject, args=["argument 1", 4321], filter_func=filter_myobject, filter_func_args=50)
```

If a filter function is provided, the function is called on every reception of the specified object. If (and only if) the filter function returns true, the handle function is called.

### Miscellaneous
---
Deregister pool:
```Python
pool.deregister_pool("P1")
pool.deregister_pool("P2", fail_if_already_deregistered=False)
```

Get number of objects in pool:
```Python
pool.size("P1")
```

Get a list of all objects in pool:
```Python
# returns a map of {obj_id = deque of entries}
all_objs = pool.get_all("P1")
```
Check if pool is registered:
```Python
pool.is_registered("P3")
```

Show debug UI:
```Python
pool = ObjectPool("My Pool")
pool.show_ui()
```

### Dependencies
- [psutil](https://github.com/giampaolo/psutil)
- [dearpygui](https://github.com/hoffstadt/DearPyGui)
- [pyhash](https://github.com/flier/pyfasthash)

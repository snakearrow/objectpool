from MyObject import MyObject
from AnotherObject import AnotherObject
from ProgressionReport import ProgressionReport
from ActivationReport import ActivationReport
from objectpool import ObjectPool
import threading
from random import randrange
import signal
import sys
from time import sleep


abort = False

class Worker1(threading.Thread):
    
    _pool = None
    _sleep_time = 1.123
    _registered_pool3 = False

    def __init__(self, pool, *args, **kwargs):
        super(Worker1, self).__init__(*args, **kwargs)
        self._pool = pool
        
    def handle_another_obj(self, obj):
        self._sleep_time = min(2.5, obj._cnt / 10.0)
        if self._sleep_time >= 1.0 and not self._registered_pool3:
            self._pool.register_pool("Pool W3")
            self._registered_pool3 = True
        elif self._registered_pool3 and self._sleep_time >= 1.6:
            self._pool.deregister_pool("Pool W3", fail_if_already_deregistered=False)

    def run(self):
        global abort
        print(f'running worker 1 with {self._pool}')
        
        pool = self._pool
        pool.register_pool("Pool W1", max_size=20, fail_if_already_registered=False)
        pool.subscribe("Pool W1", AnotherObject, self.handle_another_obj)
        
        i = 0
        while not abort:
            m = MyObject(i)
            i += 2
            self._pool.put("Pool W1", m)
            sleep(self._sleep_time)
            self._pool.put("Pool W2", ActivationReport())
            
class Worker2(threading.Thread):
    
    _pool = None

    def __init__(self, pool, *args, **kwargs):
        super(Worker2, self).__init__(*args, **kwargs)
        self._pool = pool
        
    def handle_progression_report(self, obj, args):
        self._pool.put("Pool W1", obj)
        print("handle progression report, cnt = {}".format(obj.get_cnt()))
        
    @staticmethod
    def filter_progression_report(obj, which):
        if obj.get_cnt() % which == 0:
            return True
        return False

    def run(self):
        global abort
        print(f'running worker 2 with {self._pool}')
        
        pool = self._pool
        pool.register_pool("Pool W1", max_size=20, fail_if_already_registered=False)
        pool.register_pool("Pool W2", fail_if_already_registered=True)
        pool.subscribe("Pool W4", ProgressionReport, self.handle_progression_report, args=["arg1", "arg2"], filter_func=self.filter_progression_report, filter_func_args=3)
        
        i = 1
        while not abort:
            m = MyObject(i)
            i += 2
            self._pool.put("Pool W1", m)
            self._pool.put("Pool W2", m)
            m = AnotherObject(i)
            self._pool.put("Pool W1", m)
            sleep(1)
            
            if i >= 10:
                if not pool.is_registered("Pool W4"):
                    pool.register_pool("Pool W4")
                pool.put("Pool W4", ProgressionReport(i))

def high_speed_worker(pool, sleep_time):
    global abort
    
    cnt = 0
    while not abort:
        rnd = randrange(4)
        if rnd % 3 == 0:
            pool.put("Pool W4", ProgressionReport(cnt))
            cnt += 1
        elif rnd % 3 == 1:
            pool.put("Pool W4", ActivationReport())
        else:
            pool.put("Pool W4", AnotherObject())
            
        sleep(sleep_time)
            
def signal_handler(sig, frame):
    global abort
    print('Exiting...')
    abort = True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    pool = ObjectPool("My Pool")
    pool.show_ui()
    
    worker1 = Worker1(pool)
    worker1.start()
    worker2 = Worker2(pool)
    worker2.start()
    
    
    # main loop
    while not abort:
        inp = input()
        t = threading.Thread(target=high_speed_worker, args=(pool, 0.01))
        t.start()

    worker1.join()
    worker2.join()
    
    pool.quit()
    

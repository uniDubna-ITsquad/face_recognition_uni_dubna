from face_recognition_uni_dubna.MLogs import MLogs
from threading import Thread, Event, Semaphore, BoundedSemaphore
from queue import Queue
import time
import sys


log_info = lambda message : MLogs.info('Threading', message)
log_error = lambda message : MLogs.error('Threading', message)

def run_fun(*, target, args = None, kwargs = None):
    if args == None and kwargs == None:
        target()
    elif args == None and kwargs != None:
        target(**kwargs)
    elif args != None and kwargs == None:
        target(*args)
    elif args != None and kwargs != None:
        target(*args, **kwargs)


class ThreadControllerLimitedElapsed():
        MAX_ELAPSED = 1
        LOOP_IN_SECOND = 10

        class _Thread(Thread):
            def __init__(self, stop_event, daemon = True, *args, **kwargs):
                super(ThreadControllerLimitedElapsed._Thread, self).__init__(*args, **kwargs)
                self.stop_event = stop_event
                self.elapsed = {}

            def run(self):
                log_info('Start Limited Thread')
                while not self.stop_event.is_set():
                    for fun in list(self.elapsed.values()):
                        fun()
                    time.sleep(1 / ThreadControllerLimitedElapsed.LOOP_IN_SECOND)
                log_info('Stop Limited Thread')

        def __init__(self):
            self._elapsed = {}
            self._threads = {}
                    
        def add_elapsed(self, key, event_handler):
            if not(key in self._elapsed):
                thread = self._get_available_thread()
                self._elapsed[key] = thread
                thread.elapsed[key] = event_handler
            else:
                raise Exception('already have handler')

        def remove_elapsed(self, key):
            if (key in self._elapsed):
                thread = self._elapsed[key]
                del thread.elapsed[key]
                if len(thread.elapsed) == 0:
                    log_info('Destroy thread ThreadControllerLimitedElapsed')
                    self._threads[thread].set()
                    del self._threads[thread]
            else:
                raise Exception("no handler exists")

        def _get_available_thread(self):
            for thread in self._threads.keys():
                if len(thread.elapsed) < self.MAX_ELAPSED:
                    return thread
            return self._get_new_thread()
        
        def _get_new_thread(self):
            log_info('Start new thread ThreadControllerLimitedElapsed')
            n_stop_event = Event()
            n_thread = self._Thread(n_stop_event, )
            self._threads[n_thread] = n_stop_event
            n_thread.start()
            return n_thread

        def __len__(self):
            return len(self._elapsed)
     
class ThreadSemaphore:
    def __init__(self, lim_handlers):
        self.bounded_semaphore = BoundedSemaphore(lim_handlers)

    def add_to_queue(self,* , fun, args=None, kwargs=None):
        self.bounded_semaphore.acquire()
        Thread(target=self._run, args=(fun, args, kwargs)).start()

    def _run(self, fun, args=None, kwargs=None):
        try:
            run_fun(
                target = fun, 
                args = args, 
                kwargs = kwargs
            )
        finally:
            self.bounded_semaphore.release()

class StoppableLoopedThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, target, sleep_time, *args, **kwargs):
        super(StoppableLoopedThread, self).__init__(*args, **kwargs)
        self._stop_event = Event()
        self.target = target
        self.sleep_time = sleep_time

    def run(self):
        log_info('Start Looped Thread')
        while not self._stop_event.is_set():
            self.target()
            time.sleep(self.sleep_time)
        log_info('Stop Looped Thread')
        

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class MultipleQueueThread:
    def __init__(self, *, target, max_thread4queue):
        self._max_thread4queue = max_thread4queue
        self._semaphore = BoundedSemaphore(max_thread4queue)
        self._queue = Queue()
        self._stop_event = Event()
        self._target = target
        for i in range(max_thread4queue):
            self._semaphore.acquire()
            Thread(target = self._run).start()
        log_info('Start MultipleQueueThread')

    def _run(self):
        while not self._stop_event.is_set():
            try:
                args, kwargs = self._queue.get()
                run_fun(
                    target = self._target,
                    args = args,
                    kwargs = kwargs
                )
            except TypeError:
                pass
        self._semaphore.release()

    def stop(self, *, force = False):
        if not force:
            while not self._queue.empty():
                pass
        
        self._stop_event.set()
        for i in range(self._max_thread4queue):
            self._queue.put(None)
        while self._semaphore._value != 0:
            pass
        log_info('Stop MultipleQueueThread')

    def put(self, *, args = None, kwargs = None):
        if self._stop_event.is_set():
            raise Exception('Already stopped')
        # tt = time.time()
        self._queue.put((args, kwargs, ))
        # log_info(f'Put tume: {time.time() - tt}')
        
    def is_stopped(self):
        return self._stop_event.is_set()

import multiprocessing as mp
import time
import sys
import os


log_info = lambda message : MLogs.info('Processing', message)
log_error = lambda message : MLogs.error('Processing', message)


def run_fun(*, target, args = None, kwargs = None):
    if args == None and kwargs == None:
        target()
    elif args == None and kwargs != None:
        target(**kwargs)
    elif args != None and kwargs == None:
        target(*args)
    elif args != None and kwargs != None:
        target(*args, **kwargs)


class MultipleQueueProc:
    def __init__(self, *, target, max_thread4queue):
        self._max_thread4queue = max_thread4queue
        self._queue = mp.Queue()
        self._stop_event = mp.Event()
        self._target = target
        for i in range(max_thread4queue):
            mp.Process(
                target = self._run
                # deamon = True
            ).start()
        # log_info('Start MultipleQueueProc')

    def _run(self):
        while not self._queue.empty() or not self._stop_event.is_set():
            try:
                args, kwargs = self._queue.get()
                # print(os.getpid())
                run_fun(
                    target = self._target,
                    args = args,
                    kwargs = kwargs
                )
            except TypeError:
                break

    def stop(self, *, force = False):
        if not force:
            while not self._queue.empty():
                pass
        
        self._stop_event.set()
        for i in range(self._max_thread4queue):
            self._queue.put(None)
        # log_info('Stop MultipleQueueThread')

    def put(self, *, args = None, kwargs = None):
        if self._stop_event.is_set():
            raise Exception('Already stopped')
        # tt = time.time()
        # print(f'Put {args}, {kwargs}')
        self._queue.put((args, kwargs, ))
        # log_info(f'Put tume: {time.time() - tt}')
        
    def is_stopped(self):
        return self._stop_event.is_set()

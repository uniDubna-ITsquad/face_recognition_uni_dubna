from threading import Thread, Event
import time
import sys

class ThreadControllerLimitedElapsed():
        MAX_ELAPSED = 2
        class _Thread(Thread):
            def __init__(self, stop_event):
                Thread.__init__(self)
                self.stop_event = stop_event
                self.elapsed = {}

            def run(self):
                while not self.stop_event.is_set():
                    for fun in list(self.elapsed.values()):
                        fun()

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
                    print('Destroy thread')
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
            print('Start new thread')
            n_stop_event = Event()
            n_thread = self._Thread(n_stop_event)
            self._threads[n_thread] = n_stop_event
            n_thread.start()
            return n_thread

        def __len__(self):
            return len(self._elapsed)
     
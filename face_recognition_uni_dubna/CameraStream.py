from threading import Thread, Event
import time
import os

class CameraStream:

    class _Timer(Thread):
        def __init__(self, event):
            Thread.__init__(self)
            self.stopped = event
            self._elapsed = {}

        def run(self):
            while not self.stopped.wait(.01):
                for key, fun in self._elapsed.items():
                    fun()
                    
        def add_elapsed(self, key, event_handler):
            if not(key in self._elapsed):
                self._elapsed[key] = event_handler
            else:
                raise Exception('already have handler')

        def remove_elapsed(self, key):
            if (key in self._elapsed):
                del self._elapsed[key]
            else:
                raise Exception("no handler exists")

        def __len__(self):
            return len(self._elapsed)
        
    _timer = None
    @property
    def _timer(self):
        return type(self)._timer
    @_timer.setter
    def _timer(self, value):
        type(self)._timer = value

    _timer_stop_ev = None
    @property
    def _timer_stop_ev(self):
        return type(self)._timer_stop_ev
    @_timer_stop_ev.setter
    def _timer_stop_ev(self, value):
        type(self)._timer_stop_ev = value

    def __init__(self, *, cam_ip, save_dir=None, auth_login='admin', auth_password='admin'):
        self.cam_ip = cam_ip
        self.auth_login = auth_login
        self.auth_password = auth_password
        self.save_dir = save_dir

    def open(self, *, save_interval):
        # self.cam_cap = cv2.VideoCapture(
        #     f"rtsp://{self.auth_login}:{self.auth_password}@{self.cap_ip}"
        #     ),

        print(f"start {self.cam_ip}")
        self._add2timer(save_interval)

    def close(self):
        print(f"close {self.cam_ip}")
        self._remove_from_timer()


    def _add2timer(self, save_interval):
        if type(self._timer) != CameraStream._Timer \
           or len(self._timer) == 0:
            print('in here')
            self._timer_stop_ev = Event()
            self._timer = self._Timer(
                self._timer_stop_ev
            )
            self._timer.start()
        
        self._timer.add_elapsed(
            self,
            self._get_save_handler(save_interval))

    def _remove_from_timer(self):
        self._timer.remove_elapsed(self)
        if len(self._timer) == 0:
            self._timer_stop_ev.set()

    def _get_save_handler(self, interval):
        start_time = [int(round(time.time() * 1000))]
        def _try_save_screen():
            cur_time = int(round(time.time() * 1000))
            diff_time = cur_time - start_time[0]
            if diff_time >  interval:
                self._save_screen()
                start_time[0] = cur_time

        return _try_save_screen
    
    def _save_screen(self):
        print(self._get_save_path())

    def _get_save_path(self):
        cur_time_str = time.strftime(
            "%y_%m_%d-%H_%M_%S",
            time.localtime()
        )
        if self.__dict__['save_dir']:
            return os.path.join(
                self.save_dir, cur_time_str + '.jpg'
            )
        else:
            return os.path.join(
                'media', self.cam_ip, cur_time_str + '.jpg'
            )

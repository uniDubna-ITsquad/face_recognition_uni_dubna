from threading import Thread, Event
import time
import os
import cv2

class CameraStream:

    class _Timer(Thread):
        def __init__(self, event):
            Thread.__init__(self)
            self.stopped = event
            self._elapsed = {}

        def run(self):
            # while not self.stopped.wait(.01):
            while True:
                for fun in list(self._elapsed.values()):
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
        self.cam_cap = cv2.VideoCapture(
            f"rtsp://{self.auth_login}:{self.auth_password}@{self.cam_ip}"
        )

        print(f"start {self.cam_ip}")
        self._add2timer(save_interval)

    def close(self):
        self._remove_from_timer()
        self.cam_cap.release()
        print(f"closed {self.cam_ip}")


    def _add2timer(self, save_interval):
        if type(self._timer) != CameraStream._Timer \
           or len(self._timer) == 0:
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
            ret, frame = self.cam_cap.read()
            if diff_time >  interval:
                self._save_screen(frame)
                start_time[0] = cur_time

        return _try_save_screen
    
    def _save_screen(self, frame):
        _path = self._get_save_path()
        print(_path)
        cv2.imwrite(_path , frame)

    def _get_save_file_path(self):
        cur_time_str = time.strftime(
            "%y_%m_%d-%H_%M_%S",
            time.localtime()
        )
        res_floder_path = None
        if self.__dict__['save_dir']:
            res_floder_path = os.path.join(
                self.save_dir, self.cam_ip
            )
        else:
            res_floder_path = os.path.join(
                'media', self.cam_ip
            )

        self._check_folder_path(res_floder_path)

        return os.path.join(res_floder_path, cur_time_str + '.jpg')

    def _check_folder_path(folder_path):
        pass
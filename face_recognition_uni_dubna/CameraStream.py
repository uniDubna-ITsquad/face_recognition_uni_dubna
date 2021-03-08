from threading import Thread, Event
import time
import os
import cv2
import sys

class CameraStream:
    
    class _ThreadController():
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
        
    _thread_controller = None
    @property
    def _thread_controller(self):
        return type(self)._thread_controller
    @_thread_controller.setter
    def _thread_controller(self, value):
        type(self)._thread_controller = value

    def __init__(self, *, cam_ip, handler_of_taked_frames,
                # save_dir=None,
                auth_login='admin', auth_password='admin', debug=False):
        self.cam_ip = cam_ip
        self.auth_login = auth_login
        self.auth_password = auth_password
        # self.save_dir = save_dir
        self.is_debug = debug
        self.handler_of_taked_frames = handler_of_taked_frames
        self._is_tread_alive = False
        self._test_open()

    def open(self, *, save_interval):
        if not self.is_debug:
            self._open_rtsp()
        self._add2thread(save_interval)
        self._is_tread_alive = True
        print(f"start {self.cam_ip}")

    def close(self):
        if not self._is_tread_alive:
            raise Exception("cannot close a stream that was not open")
        self._remove_from_timer()
        if not self.is_debug:
            self._close_rtsp()
        print(f"close {self.cam_ip}")

    def _test_open(self):
        if not self.is_debug:
            self._open_rtsp()
            self._close_rtsp()

    def _open_rtsp(self):
        print('open')
        self.cam_cap = cv2.VideoCapture(
            f"rtsp://{self.auth_login}:{self.auth_password}@{self.cam_ip}"
        )
        self.cam_cap.set(cv2.CAP_PROP_POS_AVI_RATIO,1)

    def _close_rtsp(self):
        self.cam_cap.release()
        del self.cam_cap

    def _add2thread(self, save_interval):
        if type(self._thread_controller) != CameraStream._ThreadController \
           or len(self._thread_controller) == 0:
            self._thread_controller = self._ThreadController()
        
        self._thread_controller.add_elapsed(
            self,
            self._get_save_handler(save_interval))

    def _remove_from_timer(self):
        self._thread_controller.remove_elapsed(self)
        if len(self._thread_controller) == 0:
            print('destroyed')
            self._thread_controller = None

    def _get_save_handler(self, interval):
        start_time = [int(round(time.time() * 1000))]
        # start_time = [0]
        def _try_save_screen():
            cur_time = int(round(time.time() * 1000))
            diff_time = cur_time - start_time[0]
            # cur_time = self._get_duration_of_capture()
            # diff_time = cur_time - start_time[0]
            frame = None
            if not self.is_debug:
                ret, frame = self.cam_cap.read()
            # if diff_time > interval / 1000:
            if diff_time > interval:
                if not self.is_debug and not ret and frame == None:
                    print("Here ----------------------------------------------\n" * 4)
                    print(ret, frame)
                    print("Here ----------------------------------------------\n" * 4)
                    # return _try_save_screen()
                    return None
                # self._save_screen(frame)
                self.handler_of_taked_frames(frame)
                start_time[0] += interval

        return _try_save_screen
    
    def _save_screen(self, frame):
        _path = self._get_save_file_path()
        print(_path)
        if not self.is_debug:
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

    def _check_folder_path(self, folder_path):
        if os.path.exists(folder_path): 
            return
        dirs = os.path.split(folder_path)
        for i in range(1, len(dirs) + 1):
            cur_folder_path = os.path.join(*dirs[:i])
            if not os.path.exists(cur_folder_path):
                os.mkdir(cur_folder_path)

    def _get_duration_of_capture(self):
        return int(self.cam_cap.get(cv2.CAP_PROP_POS_FRAMES)) \
             / int(self.cam_cap.get(cv2.CAP_PROP_FPS))

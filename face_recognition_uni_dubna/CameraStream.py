from face_recognition_uni_dubna.MThreading import ThreadControllerLimitedElapsed
from face_recognition_uni_dubna.MLogs import MLogs
from datetime import datetime
import time
import os
import cv2
import sys


log_info = lambda message : MLogs.info('CameraStream', message)
log_error = lambda message : MLogs.error('CameraStream', message)

class CameraStream:
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

    def is_openable_rtsp(self):
        res = False
        try:
            if not self.is_debug:
                self._open_rtsp()
            res = True
        except Exception as e:
            pass
        if res:
            passself._close_rtsp()
        return res


    def open(self, *, save_interval):
        log_info(f'Open rtsp for {self.cam_ip}')
        if not self.is_debug:
            self._open_rtsp()
        self._add2thread(save_interval)
        self._is_tread_alive = True

    def close(self):
        if not self._is_tread_alive:
            raise Exception("cannot close a stream that was not open")
        # print(f"close {self.cam_ip}")
        self._remove_from_timer()
        if not self.is_debug:
            self._close_rtsp()
        log_info(f'Close rtsp for {self.cam_ip}')

        self._is_tread_alive = False

    def _open_rtsp(self):
        # print('open')
        self.cam_cap = cv2.VideoCapture(
            f"rtsp://{self.auth_login}:{self.auth_password}@{self.cam_ip}"
        )
        # self.cam_cap.set(cv2.CAP_PROP_POS_AVI_RATIO,1)

    def _close_rtsp(self):
        self.cam_cap.release()
        del self.cam_cap

    def _add2thread(self, save_interval):
        if type(self._thread_controller) != ThreadControllerLimitedElapsed \
           or len(self._thread_controller) == 0:
            self._thread_controller = ThreadControllerLimitedElapsed()
        
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
        # Count of frame before invoke handler
        frame_counter = [0]
        # start_time = [0]
        def _try_save_screen():
            # In seconds
            cur_time = time.time()
            diff_time = int(round(cur_time * 1000)) - start_time[0]
            # cur_time = self._get_duration_of_capture()
            # diff_time = cur_time - start_time[0]
            frame = None
            if not self.is_debug:
                ret, frame = self.cam_cap.read()
            if type(frame) != type(None):
                frame_counter[0] += 1
            # if diff_time > interval / 1000:
            if diff_time > interval:
                if not self.is_debug and not ret and frame == None:
                    print("Here ----------------------------------------------\n" * 4)
                    print(ret, frame)
                    print("Here ----------------------------------------------\n" * 4)
                    # return _try_save_screen()
                    return None
                # self._save_screen(frame)

                log_info(f'Start send for {self.cam_ip}\n\t' +\
                    f'Unsend frame count is {frame_counter[0]} for {self.cam_ip}'
                )
                frame_counter[0] = 0
                start_time[0] += interval
                cur_date = datetime.now()
                self.handler_of_taked_frames(frame, self.cam_ip, cur_date)
                # log_info(f'End of camera while')

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

    @staticmethod         
    def is_connectable_cam_params(*, cam_ip, auth_login='admin', auth_password='admin'):
        cam_cap = None
        try:
            cam_cap = cv2.VideoCapture(
                f"rtsp://{auth_login}:{auth_password}@{cam_ip}"
            )
        except Exception as err:
            print(err)
            return False

        ret, frame = cam_cap.read()
        
        cam_cap.release()

        return ret

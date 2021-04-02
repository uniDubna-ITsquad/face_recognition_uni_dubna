from face_recognition_uni_dubna.MThreading import ThreadControllerLimitedElapsed
from face_recognition_uni_dubna.MLogs import MLogs
from face_recognition_uni_dubna.TimeGenerator import TimeGenerator
from datetime import datetime, timedelta
import multiprocessing as mp
import time
import os
import cv2
import sys


log_info = lambda message : MLogs.info('CameraStream', message)
log_error = lambda message : MLogs.error('CameraStream', message)



class DroppedRtspProc():
    def __init__(self,rtsp_url):        
        #load pipe for data transmittion to the process
        self.parent_conn, child_conn = mp.Pipe()
        self.get_event = mp.Event()
        self.stop_event = mp.Event()

        self.p = mp.Process(
            target=self.update, 
            args=(child_conn, self.get_event, self.stop_event, rtsp_url)
        )        

        self.is_wait4get_frame = False

        self.p.daemon = False
        self.p.start()

    def update(self, conn, get_ev, stop_ev, rtsp_url):
        cap = cv2.VideoCapture(rtsp_url,cv2.CAP_FFMPEG)   
        
        while True:
            ret,frame = cap.read()
            
            if get_ev.is_set():
                rec_dat = conn.send(frame)

            elif stop_ev.is_set():
                cap.release()
                break

        conn.close()

    def get_frame(self,resize=None):
        self.get_event.set()
        frame = self.parent_conn.recv()
        self.get_event.clear()

        return frame

    def stop(self):
        self.stop_event.set()


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
                auth_login = 'admin', auth_password = 'admin',
                cam_fps = None, debug = False):
        self.cam_ip = cam_ip
        self.auth_login = auth_login
        self.auth_password = auth_password
        self.is_debug = debug
        self.handler_of_taked_frames = handler_of_taked_frames
        self._is_tread_alive = False
        self.cap_cur_fps = None

    # def is_openable_rtsp(self):
    #     res = False
    #     try:
    #         if not self.is_debug:
    #             self._open_rtsp()
    #         res = True
    #     except Exception as e:
    #         pass
    #     if res:
    #         passself._close_rtsp()
    #     return res


    def open(self, *, save_interval):
        log_info(f'Open rtsp for {self.cam_ip}')
        self._open_rtsp()
        self._add2thread(save_interval)
        self._is_tread_alive = True

    def close(self):
        if not self._is_tread_alive:
            raise Exception("cannot close a stream that was not open")
        self._remove_from_timer()
        self._close_rtsp()
        log_info(f'Close rtsp for {self.cam_ip}')
        self._is_tread_alive = False

    def _open_rtsp(self):
        rtsp_url = \
            f"rtsp://{self.auth_login}:{self.auth_password}@{self.cam_ip}"
        self.rtsp = DroppedRtspProc(rtsp_url)

    def _close_rtsp(self):
        self.rtsp.stop()
        del self.rtsp

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
            self._thread_controller = None

    def _get_save_handler(self, interval):
        interval /= 1000
        SKIP_FIRST_TIME = 6
        start_time = time.time() + SKIP_FIRST_TIME
        count = [0]

        def _try_save_screen():
            if time.time() > start_time + interval * count[0]:
                frame = self.rtsp.get_frame()
                frame_time = datetime.now()
                self.handler_of_taked_frames(frame, self.cam_ip, frame_time)
                count[0] += 1

        return _try_save_screen

    @staticmethod
    def check_cam_fps(*, cam_ip, auth_login='admin', auth_password='admin'):
        TIME4TEST = 68
        FIRST_PASS = 8
        frame_count_by_sec = [0]

        cam_cap = cv2.VideoCapture(
            f"rtsp://{auth_login}:{auth_password}@{cam_ip}"
        )
        log_info(f'Check fps for: {cam_ip}')

        start_time = time.time()
        while start_time + TIME4TEST > time.time():
            ret, frame = cam_cap.read()
            if not ret:
                continue
            if start_time + len(frame_count_by_sec) < time.time():
                frame_count_by_sec.append(0)
            frame_count_by_sec[len(frame_count_by_sec) - 1] += 1

        cam_cap.release()
        slice4res = frame_count_by_sec[FIRST_PASS:-2]
        res_fps = sum(slice4res) / len(slice4res)
        return res_fps

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

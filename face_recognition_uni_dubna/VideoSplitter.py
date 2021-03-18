from face_recognition_uni_dubna.MLogs import MLogs
from threading import Thread
import cv2
import os

log_info = lambda message : MLogs.info('VideoSplitter', message)
log_error = lambda message : MLogs.error('VideoSplitter', message)

class VideoSplitter:
    #def __init__(save_path)
    def __init__(self, *, video_location, interval_ms, handler_of_taked_frames):
        self.video_location = video_location
        self.interval_ms = interval_ms
        self.handler_of_taked_frames = handler_of_taked_frames
        self.sended = 0


    def start(self):
        Thread(target = self._start).start()
        # self._start()
        
    def _start(self):
        cap = cv2.VideoCapture(self.video_location)
        cap_framerate = cap.get(cv2.CAP_PROP_FPS)
        ret = True
        count = 0
        while ret:
            ret, frame = cap.read()
            count += 1
            if (cap_framerate * self.interval_ms / 1000) <= count:
                self.handler_of_taked_frames(frame)
                self.sended += 1
                log_info(f'Total get {self.sended}')
                count = 0

# rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen03.stream

from face_recognition_uni_dubna.MDispatcher import MDispatcher
from face_recognition_uni_dubna.MThreading import ThreadSemaphore
from face_recognition_uni_dubna.VideoSplitter import VideoSplitter
import os
from tabulate import tabulate
from time import sleep

media_dir = os.path.join('media', 'test002')

def run_fun(*, target, args = None, kwargs = None):
    if args == None and kwargs == None:
        target()
    elif args == None and kwargs != None:
        target(**kwargs)
    elif args != None and kwargs == None:
        target(*args)
    elif args != None and kwargs != None:
        target(*args, **kwargs)

def fun(name, *, slp):
    print('start', name)
    sleep(slp)
    print('close', name)


def print_cameras_list(cam_list):
    table_cameras = tabulate(
        cam_list,
        headers=['id', 'ip', 'is_alive']
    )
    print(table_cameras)

# tt = ThreadSemaphore(2)

def try_pass(*, fun, args = None, kwargs = None):
    try:
        run_fun(
            target = fun,
            args = args,
            kwargs = kwargs
        )
    except:
        pass

while (True):
    cmd = input('Command:\n')
    # try:
    if cmd == 'q':
        MDispatcher.close_all_cameras()
        try_pass(fun = MDispatcher.stop_screens_faces_handler)
        try_pass(fun = MDispatcher.stop_commiter4taked_screens)
        break
    elif cmd == 'global init' or cmd == 'gi':
        MDispatcher.connect2db()
        MDispatcher.start_commiter4taked_screens()
        MDispatcher.start_screens_faces_handler()
    elif cmd == 'db init':
        db_user = input('DB user:\n')
        db_password = input('DB password:\n')
        db_name = input('DB name:\n')
        MDispatcher.db_init(db_user, db_password, db_name)
    elif cmd == 'db connect':
        MDispatcher.connect2db()
    elif cmd == 'camera create':
        cam_ip = input('Camera ip:\n')
        cam_auth_login = input('Camera auth login:\n')
        cam_auth_password = input('Camera auth password:\n')
        MDispatcher.add_cam_in_conf(cam_ip, cam_auth_login, cam_auth_password)
    elif cmd == 'camera remove':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        cam_choice = input('Which one to remove?:\n')
        MDispatcher.del_cam_from_config(cam_choice)
    elif cmd == 'camera list' or cmd == 'cl':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
    elif cmd == 'camera start' or cmd == 'cs':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        cam_choice = input('Which one to start?:\n')
        interval = input('What interval?:\n')
        if interval.isdigit():
            interval = int(interval)
        else:
            print('E: Interval is not digit!')
        MDispatcher.start_cam_with_interval(cam_choice, interval, media_dir)
    elif cmd == 'camera start all' or cmd == 'csa':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        interval = input('What interval?:\n')
        if interval.isdigit():
            interval = int(interval)
        else:
            print('E: Interval is not digit!')
        MDispatcher.start_all_cam_with_interval(interval, media_dir)
    elif cmd == 'camera close' or cmd == 'cc':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        cam_choice = input('Which one to close?:\n')
        MDispatcher.close_cam(cam_choice)
    elif cmd == 'camera close all' or cmd == 'cca':
        MDispatcher.close_all_cameras()
    elif cmd == 'dispatcher screen_commiter start':
        MDispatcher.start_commiter4taked_screens()
    elif cmd == 'dispatcher screen_commiter stop':
        MDispatcher.stop_commiter4taked_screens()
    elif cmd == 'dispatcher face_handler start':
        MDispatcher.start_screens_faces_handler()
    elif cmd == 'dispatcher face_handler stop':
        MDispatcher.stop_screens_faces_handler()
    elif cmd == 'students load':
        stud_path = os.path.join('media', 'it_squad')
        MDispatcher.load_student_features_from_dir(stud_path)
    elif cmd == 'test_video' or cmd == 'tv':
        video_location = os.path.join('media', 'test_video', 'test.mp4')
        video_out_path = os.path.join('media', 'test_video', 'out')
        interval_ms = 1000 / 3
        MDispatcher.start_video(video_location, video_out_path, interval_ms)
    elif cmd == 'get screens':
        out_file = os.path.join("media", "res.json")
        MDispatcher.get_and_save_screens_by_cam_ip('test', out_file)

        
##### XD #####
    elif cmd == 'test':
        MDispatcher.test()
        # MDispatcher.connect2db()
        # for cam_ip in cam_ips:
        #     MDispatcher.add_cam_in_conf(cam_ip, '***')

    #     tt.add_to_queue(fun = fun, args = ('test0', ), kwargs = {'slp' : 1})
    #     tt.add_to_queue(fun = fun, args = ('test1', ), kwargs = {'slp' : 2})
    #     tt.add_to_queue(fun = fun, args = ('test2', ), kwargs = {'slp' : 3})
    #     tt.add_to_queue(fun = fun, args = ('test3', ), kwargs = {'slp' : 4})
        

print('bb')
# rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen03.stream

from face_recognition_uni_dubna.MDispatcher import MDispatcher
from face_recognition_uni_dubna.MThreading import ThreadSemaphore
import os
from tabulate import tabulate
from time import sleep
# from datetime import datetime


#im4fr = face_recognition.load_image_file("test.jpg")
#face_locations = face_recognition.face_locations(im4fr)

#print(face_recognition.face_encodings(im4fr))


# im4pil = Image.open("test.jpg")
# for i, [y0, x1, y1, x0] in enumerate(face_locations):
#     im4pil.crop((x0, y0, x1, y1)).save(str(i) + '.jpg')



## -- Norm cod -- ##

media_dir = os.path.join('media', 'test002')
# streams = []

# for cam_ip in cam_ips:
#     streams.append(
#         CameraStream(
#             cam_ip=cam_ip,
#             auth_login='admin',
#             auth_password='admin',
#             save_dir=media_dir,
#             # without rtps and saving screens
#             debug=True
#         )
#     )

# for stream in streams:
#     stream.open(
#         save_interval=1000
#     )

# # time.sleep(4)

# while True:
#     if input() == 'q':
#         for stream in streams:
#             stream.close()
#         break

## -- Norm cod \ - ##

# MDispatcher.connect2db()

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

while (True):
    cmd = input('Command:\n')
    # try:
    if cmd == 'q':
        MDispatcher.close_all_cameras()
        try:
            MDispatcher.stop_new_screens_faces_handler()
        except Exception:
            pass
        break
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
    elif cmd == 'camera list':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
    elif cmd == 'camera start':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        cam_choice = input('Which one to start?:\n')
        interval = input('What interval?:\n')
        if interval.isdigit():
            interval = int(interval)
        else:
            print('E: Interval is not digit!')
        MDispatcher.start_cam_with_interval(cam_choice, interval, media_dir)
    elif cmd == 'camera start all':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        interval = input('What interval?:\n')
        if interval.isdigit():
            interval = int(interval)
        else:
            print('E: Interval is not digit!')
        MDispatcher.start_all_cam_with_interval(interval, media_dir)
    elif cmd == 'camera close':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        cam_choice = input('Which one to close?:\n')
        MDispatcher.close_cam(cam_choice)
    elif cmd == 'camera close all':
        MDispatcher.close_all_cameras()
    elif cmd == 'dispatcher start new screens faces handler':
        MDispatcher.start_new_screens_faces_handler()

        
##### XD #####
    elif cmd == 'test':
        pass
        # MDispatcher.connect2db()
        # for cam_ip in cam_ips:
        #     MDispatcher.add_cam_in_conf(cam_ip, '***')

    #     tt.add_to_queue(fun = fun, args = ('test0', ), kwargs = {'slp' : 1})
    #     tt.add_to_queue(fun = fun, args = ('test1', ), kwargs = {'slp' : 2})
    #     tt.add_to_queue(fun = fun, args = ('test2', ), kwargs = {'slp' : 3})
    #     tt.add_to_queue(fun = fun, args = ('test3', ), kwargs = {'slp' : 4})
        

    # except:
    #     print(e)
    #     MDispatcher.close_all_cameras()
    #     break



        

print('bb')


# cameras_connector = MDispatcher.get_cameras_connector(media_dir)

# cameras_connector(cam_ip=cam_ips[0], debug=True).open(1500)


# Command.load_student_features_from_dir(os.path.join('media', 'us'))
# Command.load_screens_from_dir(os.path.join('media', 'test_screens'))
# Command.test()



# time.sleep(2)
# streams[0].close()

# time.sleep(30)

# for stream in streams:
#     stream.close()

# cap1.Close

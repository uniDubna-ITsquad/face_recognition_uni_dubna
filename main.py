# rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen03.stream

from face_recognition_uni_dubna.MDispatcher import MDispatcher
import os
from tabulate import tabulate
# from datetime import datetime


#im4fr = face_recognition.load_image_file("test.jpg")
#face_locations = face_recognition.face_locations(im4fr)

#print(face_recognition.face_encodings(im4fr))


# im4pil = Image.open("test.jpg")
# for i, [y0, x1, y1, x0] in enumerate(face_locations):
#     im4pil.crop((x0, y0, x1, y1)).save(str(i) + '.jpg')



## -- Norm cod -- ##

media_dir = os.path.join('media', 'test000')
# cam_ips = [
#     '10.210.6.152',
#     '10.210.52.7',
#     '10.210.52.8',
#     '10.210.52.6',
#     '10.210.1.6',

# ]

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

def print_cameras_list(cam_list):
    table_cameras = tabulate(
        cam_list,
        headers=['id', 'ip', 'is_alive']
    )
    print(table_cameras)


while (True):
    cmd = input('Command:\n')
    if cmd == 'q':
        MDispatcher.close_all_cameras()
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
        cam_choise = input('Which one to delete?:\n')
        MDispatcher.del_cam_from_config(cam_choise)
    elif cmd == 'camera list':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
    elif cmd == 'camera start':
        cameras_list = MDispatcher.get_cameras_list()
        print_cameras_list(cameras_list)
        cam_choise = input('Which one to delete?:\n')
        interval = input('What interval?:\n')
        if interval.isdigit():
            interval = int(interval)
        else:
            print('E: Interval is not digit!')
        MDispatcher.start_cam_with_interval(cam_choise, interval, media_dir)
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
        cam_choise = input('Which one to close?:\n')
        MDispatcher.close_cam(cam_choise)
    elif cmd == 'camera close all':
        MDispatcher.close_all_cameras()


        

print('bb')

# MDispatcher.add_cam_in_conf('10.210.52.7', 'admin', 'admin')

# media_dir = os.path.join('media', 'test000')
# cam_ips = [
#     '10.210.6.152',
#     '10.210.52.7',
#     '10.210.52.8',
#     '10.210.52.6',
#     '10.210.1.6',
# ]

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

# while(True):
#     t = time.localtime()
#     current_time = time.strftime("%y_%m_%d-%H_%M_%S", t)
#     print(current_time)
#     for dict_cap in capts:
#         [cap_ip, cap] = (dict_cap['ip'], dict_cap['cap'])

#         # print(cap.isOpened())

#         ret, frame = cap.read()
#         # if(not frame):
#         #     continue

#         im = Image.fromarray(frame)

#         im_file_name = current_time + '.jpg'
#         save_path = os.path.join(media_dir, cap_ip, im_file_name)


#         # cv2.imshow('frame', frame)

#         # try:
#         #     im.save(os.path.join(media_dir, cap_ip, im_file_name))
#         # except OSError as e:
#         #     os.mkdir(os.path.join(media_dir, cap_ip))
#         #     im.save(os.path.join(media_dir, cap_ip, im_file_name))
#         try:
#             cv2.imwrite(save_path, frame)   
#         except OSError as e:
#             os.mkdir(os.path.join(media_dir, cap_ip))
#             cv2.imwrite(save_path, frame)   
#         print(save_path)

#     if cv2.waitKey(1000) & 0xFF == ord('q'):
#         break
#     # time.sleep(15)

#     # cv2.imshow('frame', frame)
#     # if cv2.waitKey(20) & 0xFF == ord('q'):
#     #     break


# start_time = int(round(time.time()))
# cap = capts[0]['cap']
# while(cap.isOpened()):
#     ret, frame = cap.read()
#     # cv2.imshow('frame', frame)
#     cur_time_in_sec = int(round(time.time()))
#     print(cur_time_in_sec - start_time)
#     print(capts[0]['last_time'] + 5)
#     if cur_time_in_sec - start_time > capts[0]['last_time'] + 5:
#         t = time.localtime()
#         current_time = time.strftime("%y_%m_%d-%H_%M_%S", t)
#         save_path = os.path.join(
#             media_dir, capts[0]['ip'], current_time + '.jpg'
#         )
#         cv2.imwrite(save_path, frame)
#         capts[0]['last_time'] = cur_time_in_sec - start_time

# # view
# # cap = capts[4]['cap']
# # while(cap.isOpened()):
# #     ret, frame = cap.read()
# #     cv2.imshow('frame', frame)
# #     if cv2.waitKey(20) & 0xFF == ord('q'):
# #         break

# for dict_cap in capts:
#     dict_cap['cap'].release()
# cv2.destroyAllWindows()
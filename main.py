# rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen03.stream

import face_recognition
from PIL import Image
import cv2
import time
import os
import sys
from face_recognition_uni_dubna.CameraStream import CameraStream
from face_recognition_uni_dubna.Command import Command
# from datetime import datetime


#im4fr = face_recognition.load_image_file("test.jpg")
#face_locations = face_recognition.face_locations(im4fr)

#print(face_recognition.face_encodings(im4fr))


# im4pil = Image.open("test.jpg")
# for i, [y0, x1, y1, x0] in enumerate(face_locations):
#     im4pil.crop((x0, y0, x1, y1)).save(str(i) + '.jpg')



## -- Norm cod -- ##

# media_dir = os.path.join('media', 'test000')
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

Command.connect2db()

media_dir = os.path.join('media', 'test000')
cam_ips = [
    '10.210.6.152',
    '10.210.52.7',
    '10.210.52.8',
    '10.210.52.6',
    '10.210.1.6',
]

cameras_connector = Command.get_cameras_connector(media_dir)

cameras_connector(cam_ip=cam_ips[0], debug=True).open(1500)


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
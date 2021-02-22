# rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen03.stream

import face_recognition
from PIL import Image
import cv2
import time
import os
from face_recognition_uni_dubna.CameraStream import CameraStream
# from datetime import datetime


#im4fr = face_recognition.load_image_file("test.jpg")
#face_locations = face_recognition.face_locations(im4fr)

#print(face_recognition.face_encodings(im4fr))


# im4pil = Image.open("test.jpg")
# for i, [y0, x1, y1, x0] in enumerate(face_locations):
#     im4pil.crop((x0, y0, x1, y1)).save(str(i) + '.jpg')

# не робит
#
# тест

media_dir = os.path.join('media', 'test')

cap = CameraStream(
    cam_ip='10.210.6.152',
    auth_login='admin',
    auth_password='admin'
)

cap1 = CameraStream(
    cam_ip='10.210.52.7',
    auth_login='admin',
    auth_password='admin'
)

cap.open(
    save_interval=2000
)
time.sleep(3)
cap.close()
time.sleep(4)
cap.open(
    save_interval=500
)
time.sleep(1)
cap1.open(
    save_interval=1333
)
time.sleep(1)
cap.close()
time.sleep(2)
cap1.close()

# cap1.Close

# capts = [
#     # {
#     # 'ip': '10.210.6.152',
#     # 'cap': cv2.VideoCapture("rtsp://admin:admin@10.210.6.152"),
#     # },
#     # {
#     # 'ip': '10.210.52.7',
#     # 'cap': cv2.VideoCapture("rtsp://admin:admin@10.210.52.7"),
#     # },
#     # {
#     # 'ip': '10.210.52.8',
#     # 'cap': cv2.VideoCapture("rtsp://admin:admin@10.210.52.8"),
#     # },
#     # {
#     # 'ip': '10.210.52.6',
#     # 'cap': cv2.VideoCapture("rtsp://admin:admin@10.210.52.6"),
#     # },
#     {
#     'ip': '10.210.1.6',
#     'cap': cv2.VideoCapture("rtsp://admin:admin@10.210.1.6"),
#     },
# ]


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
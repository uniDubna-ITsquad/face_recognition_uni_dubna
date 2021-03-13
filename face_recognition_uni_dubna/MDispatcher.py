from face_recognition_uni_dubna.MDBQuery import MDBQuery
from face_recognition_uni_dubna.MFaceRecognition import MFaceRecognition
from face_recognition_uni_dubna.CameraStream import CameraStream
from face_recognition_uni_dubna.MConfig import MConfig
from face_recognition_uni_dubna.MThreading import StoppableLoopedThread
import os
import cv2
import imghdr
from time import time, mktime, localtime, strftime
from datetime import datetime
from threading import Thread, Event

class Object(object):
    pass

def log(*args):
    print(*args)

class MDispatcher:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def test():
        pass

##### DB #####

    @staticmethod
    def connect2db():
        conf_db = MConfig.get_by_name('DATABASE')
        MDBQuery.connect2db(
            dbname=conf_db['database'],
            user=conf_db['user'],
            password=conf_db['password'],
            host=conf_db['host']
        )

        n_db_version = MDBQuery.check_version(float(conf_db['version']))
        if n_db_version != float(conf_db['version']):
            MConfig.set_db_version(n_db_version)
    
    @staticmethod
    def db_init(db_user, db_password, db_name):
        MConfig.init_config_db(
            user=db_user, 
            password=db_password, 
            db_name=db_name
        )

##### Face Recognition #####

    handler_new_screens = None

    @staticmethod
    def load_student_features_from_dir(folder_path):
        corrects_images_pathes = MDispatcher._get_correct_pictures_from_dir(folder_path)
        for im_path in corrects_images_pathes:
            face_features_im_list = MFaceRecognition.get_faces_features_of_image(im_path)
            if len(face_features_im_list) != 1:
                print(f'Failed for {im_path}')
                continue
            feature_im = face_features_im_list[0]
            student_name = os.path.basename(os.path.splitext(im_path)[0])
            MDBQuery.insert_student_with_feature(
                student_name, im_path, feature_im
            )

    @staticmethod
    def load_screens_from_dir(folder_path):
        corrects_screen_pathes = MDispatcher._get_correct_pictures_from_dir(folder_path)
        for screen_path in corrects_screen_pathes:
            frame_face_parameters = MFaceRecognition.get_faces_parameters_of_image(screen_path)
            MDBQuery.commit_screen(
                screen_path = screen_path, 
                frame_face_parameters = frame_face_parameters
            )


    @staticmethod
    def handle_unprocessed_screens_faces():
        students_data = MDBQuery.get_students_id_and_features()
        screens_faces_data = MDBQuery.get_unprocessed_screens_faces()
        
        MFaceRecognition.set_student_data(students_data)

        zip_screens_faces = zip(
            screens_faces_data['ids'],
            screens_faces_data['features']
        )

        for screen_face_id, screen_face_feature in zip_screens_faces:
            student_id = MFaceRecognition.recognize_face(screen_face_feature)
            
            MDBQuery.update_screens_face4match_student(screen_face_id, student_id)
       # MFaceRecognition.compare()


    @staticmethod
    def _get_correct_pictures_from_dir(folder_path):
        dir_files_pathes = os.listdir(folder_path)
        for file_name in os.listdir(folder_path):
            full_file_name = os.path.join(folder_path, file_name)
            if imghdr.what(full_file_name) != None:
                yield full_file_name

    @staticmethod
    def start_new_screens_faces_handler():
        if MDispatcher.handler_new_screens != None:
            raise Exception('Screens faces handler is already running')


        students_data = MDBQuery.get_students_id_and_features()
        MFaceRecognition.set_student_data(students_data)

        MDispatcher.handler_new_screens = StoppableLoopedThread(
            target = MDispatcher._handler_for_unprocessed_faces,
            sleep_time = 2
        )
        MDispatcher.handler_new_screens.start()

    @staticmethod
    def stop_new_screens_faces_handler():
        if MDispatcher.handler_new_screens == None:
            raise Exception('Screens faces handler is not alive')

        MDispatcher.handler_new_screens.stop()
        MDispatcher.handler_new_screens = None
        MFaceRecognition.set_student_data(None)
        
    @staticmethod
    def _handler_for_unprocessed_faces():
        screens_faces_data = MDBQuery.get_unprocessed_screens_faces()
        
        zip_screens_faces = zip(
            screens_faces_data['ids'],
            screens_faces_data['features']
        )
        for screen_face_id, screen_face_feature in zip_screens_faces:
            student_id = MFaceRecognition.recognize_face(screen_face_feature)
            
            MDBQuery.update_screens_face4match_student(screen_face_id, student_id)

##### Camera Commands #####
    cameras_streams = {}

    @staticmethod
    def start_cam_with_interval(cam_choice, interval, save_dir):
        cam_conf = MDispatcher._get_camera_from_conf(cam_choice)
        MDispatcher._start_cam(cam_conf, interval, save_dir)

    @staticmethod
    def start_all_cam_with_interval(interval, save_dir):
        cameras_conf = MConfig.get_all_cameras()
        for cam_conf in cameras_conf:
            if not cam_conf['cam_ip'] in MDispatcher.cameras_streams.keys():
                MDispatcher._start_cam(cam_conf, interval, save_dir)

    @staticmethod
    def close_cam(cam_choice):
        cam_conf = MDispatcher._get_camera_from_conf(cam_choice)
        cam_ip = cam_conf['cam_ip']

        if cam_ip in MDispatcher.cameras_streams.keys():
            MDispatcher.cameras_streams[cam_ip].close()
            del MDispatcher.cameras_streams[cam_ip]
        else:
            raise Exception('Camera is not alive')

    @staticmethod
    def close_all_cameras():
        for cam in MDispatcher.cameras_streams.values():
            cam.close()

        MDispatcher.cameras_streams.clear()

    @staticmethod
    def _start_cam(cam_conf, interval, save_dir, debug=False):
        handler = lambda frame, cam_ip: \
            MDispatcher._new_thread_of_handler_of_taked_frames(
                frame, cam_ip, save_dir
            )
        cam = CameraStream(
            **cam_conf, debug=debug,
            handler_of_taked_frames=handler)

        cam.open(save_interval=interval)
        MDispatcher.cameras_streams[cam_conf['cam_ip']] = cam

    @staticmethod
    def _new_thread_of_handler_of_taked_frames(frame, cam_ip, save_dir):
        n_thread = Thread(
            target=MDispatcher._handler_of_taked_frames,
            args=(frame, cam_ip, save_dir,)
        )
        n_thread.start()

    @staticmethod
    def _handler_of_taked_frames(frame, cam_ip, save_dir):
        ##### !!!!!!!!!!!!!!!!!! #####
        ##### !!!!!!!!!!!!!!!!!! #####
        ##### !!!!!!!!!!!!!!!!!! #####
        if type(frame) == type(None):
            raise Exception("Frame is None")

        n_frame_path, time = MDispatcher._get_save_file_path_by_cur_time()
        n_frame_path = os.path.join(save_dir, cam_ip, n_frame_path)
        MDispatcher._check_folder_path(os.path.split(n_frame_path)[0])

        # if frame != None:
        cv2.imwrite(n_frame_path, frame)

        frame_face_parameters = MFaceRecognition.get_faces_parameters_of_image(n_frame_path)
        correct_time = MDispatcher._correct_time_for_db(time)
        MDBQuery.commit_screen(
            cam_ip = cam_ip,
            frame_face_parameters = frame_face_parameters,
            screen_path = n_frame_path, 
            time = correct_time
        )

    @staticmethod
    def _correct_time_for_db(time):
        return datetime.fromtimestamp(mktime(time))

    @staticmethod
    def _check_folder_path(folder_path):
        if os.path.exists(folder_path): 
            return
        dirs = folder_path.split(os.sep)
        for i in range(1, len(dirs) + 1):
            cur_folder_path = os.path.join(*dirs[:i])
            if not os.path.exists(cur_folder_path):
                os.mkdir(cur_folder_path)

    @staticmethod
    def _get_save_file_path_by_cur_time():
        cur_time = localtime()
        cur_time_str = strftime(
            "%y_%m_%d-%H_%M_%S",
            cur_time
        )

        [file_dir, file_name] = cur_time_str.split('-')
        
        res_path = os.path.join(
            *file_dir.split('_'),
            file_name + '.jpg'
        )

        return (res_path, cur_time)

##### MConfig #####
    @staticmethod
    def del_cam_from_config(choice):
        if choice.isdigit():
            MConfig.del_camera_by_id(int(choice))
        else:
            MConfig.del_camera_by_ip(choice)
        
        
    @staticmethod
    def add_cam_in_conf(cam_ip, cam_auth_login, cam_auth_password):

        is_connectable = CameraStream.is_connectable_cam_params(
            cam_ip = cam_ip,
            auth_login = cam_auth_login,
            auth_password = cam_auth_password
        )

        if is_connectable:
            MConfig.add_camera(cam_ip, cam_auth_login, cam_auth_password)
        else:
            print()


    @staticmethod
    def get_cameras_list():
        res = []
        for i, cam_ip in enumerate(MConfig.get_cameras_ip_list()):
            res.append(
                [i, cam_ip, cam_ip in MDispatcher.cameras_streams.keys()]
            )
        return res

    @staticmethod
    def _get_camera_from_conf(choice):
        if type(choice) is int or choice.isdigit():
            return MConfig.get_camera_by_id(int(choice))
        else:
            return MConfig.get_camera_by_ip(choice)


    # @staticmethod
    # def _get_cameras_connector(save_dir):
    #     def connector(*args, **kwargs):
    #         handler = lambda frame: \
    #             MDispatcher._handler_of_taked_frames(frame, save_dir)
    #         cam = CameraStream(
    #             *args, **kwargs,
    #             handler_of_taked_frames=handler)
    #         obj = Object()
    #         setattr(
    #             obj, 'open',
    #             lambda interval: \
    #                 cam.open(save_interval=interval)
    #         )
    #         setattr(
    #             obj, 'close',
    #             lambda interval: cam.close()
    #         )
    #         return obj

    #     return connector
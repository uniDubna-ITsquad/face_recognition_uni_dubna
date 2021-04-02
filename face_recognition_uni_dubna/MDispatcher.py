from face_recognition_uni_dubna.MDBQuery import MDBQuery
from face_recognition_uni_dubna.MFaceRecognition import MFaceRecognition
from face_recognition_uni_dubna.CameraStream import CameraStream
from face_recognition_uni_dubna.VideoSplitter import VideoSplitter
from face_recognition_uni_dubna.MConfig import MConfig
from face_recognition_uni_dubna.MThreading \
    import StoppableLoopedThread, MultipleQueueThread
from face_recognition_uni_dubna.MProcessing \
    import MultipleQueueProc
from face_recognition_uni_dubna.MLogs import MLogs
from face_recognition_uni_dubna.TimeGenerator import TimeGenerator
import os
import cv2
import imghdr
import json
from time import time, mktime, localtime, strftime, sleep
from datetime import datetime, timedelta, date
from threading import Thread, Event


log_info = lambda message : MLogs.info('Dispatcher', message)
log_error = lambda message : MLogs.error('Dispatcher', message)

class Object(object):
    pass

def log(*args):
    print(*args)

class MDispatcher:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def test():
        MDBQuery.get_processed_screens_by_cam_ip('test')


######################################
######################################
################# DB #################
######################################
######################################

    @staticmethod
    def connect2db():
        conf_db = MConfig.get_by_name('DATABASE')
        try:
            MDBQuery.connect2db(
                dbname=conf_db['database'],
                user=conf_db['user'],
                password=conf_db['password'],
                host=conf_db['host']
            )
        except Exception as e:
            print(e)
            log_error('Failde to connect to database')
            return

        log_info('Successfy connection to dabadase')


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

######################################
######################################
########## Face Recognition ##########
######################################
######################################

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
            log_info(f'Load student path: {screen_path}')
            log_info(f'\tTotal faces: {len(frame_face_parameters["locations"])}')
            MDBQuery.commit_screen(
                screen_path = screen_path, 
                frame_face_parameters = frame_face_parameters
            )

    @staticmethod
    def get_and_save_screens_by_cam_ip(cam_ip, out_file):
        data = MDBQuery.get_processed_screens_by_cam_ip(cam_ip)
        with open(out_file, 'w') as json_file:
            json.dump(data, json_file)


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
            student_ids = MFaceRecognition.recognize_face(screen_face_feature)
            
            MDBQuery.update_screens_face4match_student(screen_face_id, student_ids)
       # MFaceRecognition.compare()


    @staticmethod
    def _get_correct_pictures_from_dir(folder_path):
        dir_files_pathes = os.listdir(folder_path)
        for file_name in os.listdir(folder_path):
            full_file_name = os.path.join(folder_path, file_name)
            if imghdr.what(full_file_name) != None:
                yield full_file_name

    @staticmethod
    def start_screens_faces_handler():
        if MDispatcher.handler_new_screens != None:
            raise Exception('Screens faces handler is already running')


        students_data = MDBQuery.get_students_id_and_features()
        MFaceRecognition.set_student_data(students_data)

        MDispatcher.handler_new_screens = StoppableLoopedThread(
            target = MDispatcher._handler_for_unprocessed_faces,
            sleep_time = 2
        )
        MDispatcher.handler_new_screens.start()
        log_info('Start handler of new screen faces')

    @staticmethod
    def stop_screens_faces_handler():
        if MDispatcher.handler_new_screens == None:
            raise Exception('Screens faces handler is not alive')

        MDispatcher.handler_new_screens.stop()
        MDispatcher.handler_new_screens = None
        MFaceRecognition.set_student_data(None)
        log_info('Stop handler of new screen faces')
        
    @staticmethod
    def _handler_for_unprocessed_faces():
        screens_faces_data = MDBQuery.get_unprocessed_screens_faces()
        
        zip_screens_faces = zip(
            screens_faces_data['ids'],
            screens_faces_data['features']
        )
        for screen_face_id, screen_face_feature in zip_screens_faces:
            student_ids = MFaceRecognition.recognize_face(screen_face_feature)
            
            MDBQuery.update_screens_face4match_student(screen_face_id, student_ids)


######################################
######################################
########### Camera Commands ##########
######################################
######################################

    cameras_streams = {}
    commiter4taked_screens = None

    @staticmethod
    def start_commiter4taked_screens():
        if MDispatcher.commiter4taked_screens != None and\
            not MDispatcher.commiter4taked_screens.is_stopped():
           raise Exception('Commiter already running')
        MDispatcher.commiter4taked_screens = MultipleQueueProc(
            target = MDispatcher._handler_of_taked_frames,
            max_thread4queue = 15
        )
        log_info('Start commiter for taked screen')

    def stop_commiter4taked_screens():
        if MDispatcher.commiter4taked_screens == None or\
            MDispatcher.commiter4taked_screens.is_stopped():
           raise Exception('Commiter already stopped or uninitialization')
        
        MDispatcher.commiter4taked_screens.stop()
        log_info('Stop commiter for taked screen')

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
    def _start_cam(cam_conf, interval, save_dir, debug=False):
        if not 'cam_fps' in cam_conf:
            cam_fps = CameraStream.check_cam_fps(**cam_conf)
            cam_conf = MConfig.edit_camera_by_ip(
                cam_conf['cam_ip'], {
                    'cam_fps': cam_fps,
            })
        handler = lambda frame, cam_ip, send_time: \
            MDispatcher._new_thread_of_handler_of_taked_frames(
                frame, cam_ip, save_dir, send_time
            )
        cam = CameraStream(
            **cam_conf, debug=debug,
            handler_of_taked_frames=handler)

        cam.open(save_interval=interval)
        MDispatcher.cameras_streams[cam_conf['cam_ip']] = cam


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
    def _new_thread_of_handler_of_taked_frames(frame, cam_ip, save_dir, send_time):
        # log_info('Start Dispatcher New thread')
        # log_info(f'Send from {cam_ip}')
        tt = time()
        MDispatcher.commiter4taked_screens.put(
            args = (frame, cam_ip, save_dir, send_time,)
        )
        # log_info(f'Put time: {time() - tt}')
        # log_info('End Dispatcher New thread')

    @staticmethod
    def _handler_of_taked_frames(frame, cam_ip, save_dir, send_time):
        if type(frame) == type(None):
            raise Exception("Frame is None")

        # log_info(f'Start screen handler')
        n_frame_path = MDispatcher._get_save_file_path_by_time(send_time)
        n_frame_path = os.path.join(save_dir, cam_ip, n_frame_path)
        MDispatcher._check_folder_path(os.path.split(n_frame_path)[0])

        # if frame != None:
        cv2.imwrite(n_frame_path, frame)

        frame_face_parameters = MFaceRecognition.get_faces_parameters_of_image(n_frame_path)
        correct_time = MDispatcher._correct_time_for_db(send_time)
        faces_count = len(frame_face_parameters['locations'])
        MDBQuery.commit_screen(
            cam_ip = cam_ip,
            frame_face_parameters = frame_face_parameters,
            screen_path = n_frame_path, 
            time = correct_time
        )
        log_info(f'End send for: {cam_ip}  faces count: {faces_count}\n\tby path: {n_frame_path}')

    @staticmethod
    def _correct_time_for_db(time):
        return time
        # return datetime.fromtimestamp(mktime(time))

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
    def _get_save_file_path_by_time(send_time):
        # log_info(f'\ttest {send_time}')
        cur_time_str = send_time.strftime(
            "%y_%m_%d-%H_%M_%S_%f"
        )

        # log_info(f'\t{cur_time_str}')
        # log_info('\ttest0')
        [file_dir, file_name] = cur_time_str.split('-')
        # log_info('\ttest1')
        
        res_path = os.path.join(
            *file_dir.split('_'),
            file_name + '.jpg'
        )
        # log_info('\ttest2')

        return res_path

######################################
######################################
################ Video ###############
######################################
######################################
   

# frame, cam_ip, save_dir, send_time
    @staticmethod
    def start_video(video_location, save_dir, interval_ms):
        time_gen = TimeGenerator(interval_ms)

        handler_of_taked_frames = lambda frame: \
            MDispatcher._new_thread_of_handler_of_taked_frames(
                frame, 'test', save_dir, time_gen.next()
            )

        video = VideoSplitter(
            video_location = video_location,
            interval_ms = interval_ms,
            handler_of_taked_frames = handler_of_taked_frames
        )

        video.start()
    
    @staticmethod
    def get_video_from_frame(image_folder):
        VideoSplitter.get_video_from_frame(image_folder)
        


######################################
######################################
############### MConfig ##############
######################################
######################################

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
            MDBQuery.insert_camera(cam_ip)
            MConfig.add_camera(cam_ip, cam_auth_login, cam_auth_password)

        else:
            log('Camera is not connectable')


    @staticmethod
    def get_cameras_list():
        res = []
        for i, cam_ip in enumerate(MConfig.get_cameras_ip_list()):
            res.append(
                [i, cam_ip, cam_ip in MDispatcher.cameras_streams.keys()]
            )
        return res


    @staticmethod
    def get_database_conf():
        return MConfig.get_by_name('DATABASE')

    @staticmethod
    def _get_camera_from_conf(choice):
        if type(choice) is int or choice.isdigit():
            return MConfig.get_camera_by_id(int(choice))
        else:
            return MConfig.get_camera_by_ip(choice)

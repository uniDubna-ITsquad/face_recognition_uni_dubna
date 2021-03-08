import configparser
import os
import time
from face_recognition_uni_dubna.MDBQuery import MDBQuery
from face_recognition_uni_dubna.MFaceRecognition import MFaceRecognition
from face_recognition_uni_dubna.CameraStream import CameraStream
import cv2
import imghdr

class Object(object):
    pass

class Command:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def connect2db():
        conf_db = Config.get_by_name('DATABASE')
        MDBQuery.connect2db(
            dbname=conf_db['Database'],
            user=conf_db['User'],
            password=conf_db['Password'],
            host=conf_db['Host']
        )

        n_db_version = MDBQuery.check_version(float(conf_db['Version']))
        if n_db_version != float(conf_db['Version']):
            Config.set_db_version(n_db_version)

    @staticmethod
    def load_student_features_from_dir(folder_path):
        corrects_images_pathes = Command._get_correct_pictures_from_dir(folder_path)
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
        corrects_screen_pathes = Command._get_correct_pictures_from_dir(folder_path)
        for screen_path in corrects_screen_pathes:
            face_parameters_im = MFaceRecognition.get_faces_parameters_of_image(screen_path)
            MDBQuery.commit_screen(screen_path, face_parameters_im)


    @staticmethod
    def test():
        students_data = MDBQuery.get_students_id_and_features()
        screens_faces_data = MDBQuery.get_unprocessed_screens_faces()
        
        MFaceRecognition.set_student_data(students_data)

        zip_screens_faces = zip(
            screens_faces_data['ids'],
            screens_faces_data['features']
        )

        for screen_face_id, screen_face_feature in zip_screens_faces:
            student_id = MFaceRecognition.test(screen_face_feature)
            
            MDBQuery.update_screens_face4match_student(screen_face_id, student_id)
       # MFaceRecognition.compare()


    @staticmethod
    def _get_correct_pictures_from_dir(folder_path):
        dir_files_pathes = os.listdir(folder_path)
        for file_name in os.listdir(folder_path):
            full_file_name = os.path.join(folder_path, file_name)
            if imghdr.what(full_file_name) != None:
                yield full_file_name

##### Camera Commands #####

    @staticmethod
    def get_cameras_connector(save_dir):
        def connector(*args, **kwargs):
            handler = lambda frame: \
                Command._handler_of_taked_frames(frame, save_dir)
            cam = CameraStream(
                *args, **kwargs,
                handler_of_taked_frames=handler)
            obj = Object()
            setattr(
                obj, 'open',
                lambda interval: \
                    cam.open(save_interval=interval)
            )
            setattr(
                obj, 'close',
                lambda interval: cam.close()
            )
            return obj

        return connector

    @staticmethod
    def _handler_of_taked_frames(frame, save_dir):
        n_frame_path, time = Command._get_save_file_path_by_cur_time()
        n_frame_path = os.path.join(save_dir, n_frame_path)
        Command._check_folder_path(os.path.split(n_frame_path)[0])
        # cv2.imwrite(n_frame_path, frame)


        # print(a)

    @staticmethod
    def _check_folder_path(folder_path):
        print(folder_path)
        return
        if os.path.exists(folder_path): 
            return
        dirs = os.path.split(folder_path)
        for i in range(1, len(dirs) + 1):
            cur_folder_path = os.path.join(*dirs[:i])
            if not os.path.exists(cur_folder_path):
                os.mkdir(cur_folder_path)

    @staticmethod
    def _get_save_file_path_by_cur_time():
        cur_time = time.localtime()
        cur_time_str = time.strftime(
            "%y_%m_%d-%H_%M_%S",
            cur_time
        )

        [file_dir, file_name] = cur_time_str.split('-')
        
        res_path = os.path.join(
            *file_dir.split('_'),
            file_name + '.jpg'
        )

        return (res_path, cur_time)

_config_file_name = 'config.cfg'

class Config:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def init_config_db(*, user, password, db_name, host='127.0.0.1', port='5432'):
        Command._try_create_conf_file()
        config = configparser.ConfigParser()
        config.read(_config_file_name)
        if 'DATABASE' in config:
            raise Exception('DATABASE aready in config')
        config['DATABASE'] = {
            'Version': '0',
            'User': user,
            'Password': password,
            'Host': host,
            'Port': port,
            'Database': db_name,
        }
        with open(_config_file_name, 'w') as configfile:
            config.write(configfile)
    
    @staticmethod
    def _try_create_conf_file():
        if not os.path.exists(_config_file_name):
            open(_config_file_name, 'w').close()
        return config[name]
            
    @staticmethod
    def get_by_name(name):
        config = configparser.ConfigParser()
        config.read(_config_file_name)
        return config[name]

    @staticmethod
    def set_db_version(version):
        try:
            float(version)
        except TypeError as e:
            raise Exception('Database version must be a number')
        config = configparser.ConfigParser()
        config.read(_config_file_name)

        config.set('DATABASE', 'Version', str(version))

        with open(_config_file_name, 'w') as configfile:
            config.write(configfile)
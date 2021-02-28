import configparser
import os
from face_recognition_uni_dubna.MDBQuery import MDBQuery
from face_recognition_uni_dubna.MFaceRecognition import MFaceRecognition
import imghdr
from progress.bar import Bar


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
        corrects_images_pathes = Command._get_correct_images_from_dir(folder_path)
        for im_path in corrects_images_pathes:
            feature_im_list = MFaceRecognition.get_features_of_image(im_path)
            if len(feature_im_list) != 1:
                print(f'Failed for {im_path}')
                continue
            feature_im = feature_im_list[0]
            student_name = os.path.basename(os.path.splitext(im_path)[0])
            MDBQuery.insert_student_with_feature(
                student_name, im_path, feature_im
            )


    @staticmethod
    def _get_correct_images_from_dir(folder_path):
        dir_files_pathes = os.listdir(folder_path)
        progress_bar = Bar('Getting_correct_images_from_dir', max=len(dir_files_pathes))
        for file_name in os.listdir(folder_path):
            progress_bar.next()
            full_file_name = os.path.join(folder_path, file_name)
            if imghdr.what(full_file_name) != None:
                yield full_file_name

        

_config_file_name = 'config.cfg'

class Config:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def init_config_db(*, user, password, host='127.0.0.1', port='5432', db_name):
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

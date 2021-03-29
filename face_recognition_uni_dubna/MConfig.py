import configparser
import os
import time
import json


_config_file_name = os.path.join(
    *('/home;camera;FRUD'.split(';')), 'config.json'
)

# _config_file_name = 'config.cfg'

class MConfig:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def init_config_db(*, user, password, db_name, host='127.0.0.1', port='5432'):
        config = MConfig._get_conf_dict()
        if 'version' in config['DATABASE']:
            raise Exception('DATABASE aready in config')
        config['DATABASE'] = {
            'version': '0',
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'database': db_name,
        }

        MConfig._save_config(config)

    @staticmethod
    def set_db_version(version):
        try:
            float(version)
        except TypeError as e:
            raise Exception('Database version must be a number')
        config = MConfig._get_conf_dict()

        config['DATABASE']['version'] = str(version)

        MConfig._save_config(config)

    @staticmethod
    def check_for_existence_cam(cam_ip, cam_auth_login, cam_auth_password):
        pass

    @staticmethod
    def add_camera(cam_ip, cam_auth_login, cam_auth_password):
        config = MConfig._get_conf_dict()

        finded_cam_conf = MConfig._check_camera_by_ip_is_empty(cam_ip)
        if not finded_cam_conf:
            raise Exception('Camera already created')

        config['CAMERAS'].append({
            'cam_ip': cam_ip,
            'auth_login': cam_auth_login,
            'auth_password': cam_auth_password
        })

        MConfig._save_config(config)
    

    @staticmethod
    def del_camera_by_ip(cam_ip):
        config = MConfig._get_conf_dict()

        ind_of_camera = None
        for i, cam in enumerate(config['CAMERAS']):
            if cam_ip == cam['cam_ip']:
                ind_of_camera = i
                break
                
        if ind_of_camera == None:
            raise Exception('camera ip not found')
            
        del config['CAMERAS'][ind_of_camera]
        
        MConfig._save_config(config)
    
    @staticmethod
    def del_camera_by_id(cam_id):
        config = MConfig._get_conf_dict()

        if len(config['CAMERAS']) <= cam_id:
            raise Exception('camera id out of range')


        del config['CAMERAS'][cam_id]
        
        MConfig._save_config(config)


    @staticmethod
    def get_cameras_ip_list():
        cameras_list = MConfig.get_by_name('CAMERAS')
        return [cam['cam_ip'] for cam in cameras_list]

    @staticmethod
    def get_all_cameras():
        config = MConfig._get_conf_dict()

        return config['CAMERAS']

    @staticmethod
    def get_camera_by_ip(cam_ip):
        config = MConfig._get_conf_dict()

        for conf_cam in config['CAMERAS']:
            if cam_ip == conf_cam['cam_ip']:
                return conf_cam
        raise Exception('Camera is not found')
        
    @staticmethod
    def get_camera_by_id(cam_id):
        config = MConfig._get_conf_dict()

        if len(config['CAMERAS']) <= cam_id:
            raise Exception('Camera id out of range')

        return config['CAMERAS'][cam_id]

    @staticmethod
    def edit_camera_by_ip(cam_ip, dict2edit):
        config = MConfig._get_conf_dict()
        for cam in config['CAMERAS']:
            if cam['cam_ip'] == cam_ip:
                for key, val in dict2edit.items():
                    cam[key] = val
        MConfig._save_config(config)

    @staticmethod
    def _check_camera_by_ip_is_empty(cam_ip):
        config = MConfig._get_conf_dict()


        for conf_cam in config['CAMERAS']:
            if cam_ip == conf_cam['cam_ip']:
                return False
        return True

    @staticmethod
    def get_by_name(name):
        return MConfig._get_conf_dict()[name]

    @staticmethod
    def _get_or_create_by_name(name):
        config = MConfig._get_conf_dict()

        if not name in config:
            config[name] = {}

    
    @staticmethod
    def _try_create_conf_file():
        if not os.path.exists(_config_file_name):
            config = {
                "DATABASE": {},
                "CAMERAS": []
            }
            with open(_config_file_name, 'w') as json_file:
                json.dump(config, json_file)

    @staticmethod
    def _get_conf_dict():
        MConfig._try_create_conf_file()
        with open(_config_file_name) as json_file:
            return json.load(json_file)
    
    @staticmethod
    def _save_config(config):
        with open(_config_file_name, 'w') as json_file:
            json.dump(config, json_file)


    
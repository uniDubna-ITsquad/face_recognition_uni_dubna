import configparser
import os
from face_recognition_uni_dubna.MDBQuery import MDBQuery


class Command:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def exec(command):
        if command == 'connect2db':
            conf_db = Config.get_by_name('DATABASE')
            MDBQuery.connect2db(
                dbname=conf_db['Database'],
                user=conf_db['User'],
                password=conf_db['Password'],
                host=conf_db['Host']
            )

            n_db_version = MDBQuery.check_version(float(conf_db['Version']))


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

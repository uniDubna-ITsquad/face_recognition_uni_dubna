import configparser
import os

_config_file_name = 'config.cfg'

class Command:
    @staticmethod
    def init_config_db(user, password, host, port, db_name):
        Command._try_create_conf_file()
        config = configparser.ConfigParser()
        config.read(_config_file_name)
        if 'DATABASE' in config:
            raise Exception('DATABASE aready in config')
        config['DATABASE'] = {
            'Version': '0.01',
            'User': user,
            'Password': password,
            'Host': host,
            'Port': port,
            'Database': db_name,
        }
        with open(_config_file_name, 'w') as configfile:
            config.write(configfile)
    
    def _try_create_conf_file():
        if not os.path.exists(_config_file_name):
            open(_config_file_name, 'w').close()
import os
from time import strftime

logs_folder = 'logs' 

file_logs_info_name = os.path.join('logs', 'log_info.txt')
file_logs_error_name = os.path.join('logs', 'log_error.txt')
file_logs_name = os.path.join('logs', 'log.txt')

class MLogs:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def info(message_name, message):
        return
        identifier = 'I'
        MLogs._write_for_file(
            file_name = file_logs_info_name,
            message_name = message_name,
            message = message
        )
        MLogs._write_for_file(
            file_name = file_logs_name,
            message_name = message_name,
            message = message,
            identifier = identifier
        )

    @staticmethod
    def error(message_name, message):
        return
        identifier = 'E'
        MLogs._write_for_file(
            file_name = file_logs_error_name,
            message_name = message_name,
            message = message
        )
        MLogs._write_for_file(
            file_name = file_logs_name,
            message_name = message_name,
            message = message,
            identifier = identifier
        )

    @staticmethod
    def _write_for_file(*, file_name, message_name, message, identifier = None):
        MLogs._check_log_file(file_name)
        MLogs._append_line_in_file(
            file_name,
            MLogs._message_pattern(
                message_name = message_name,
                message = message,
                identifier = identifier
            )
        )

    @staticmethod
    def _append_line_in_file(file_name, line):
        with open(file_name, 'a') as f_log:
            f_log.write(line + '\n')

    @staticmethod
    def _message_pattern(*, identifier=None, message_name, message):
        cur_time_str = strftime("%y-%m-%d:%H-%M-%S")
        res_message = '{}[{}] [{}] -- {}'.format(
            f'[{identifier}] ' if identifier else '',
            message_name, cur_time_str, message
        )
        return res_message 

    already_exit_files = []
    @staticmethod
    def _check_log_file(full_file_name):
        if full_file_name in MLogs.already_exit_files:
            return
        dirs, file_name = os.path.split(full_file_name)
        MLogs._check_folder_path(dirs)
        if not os.path.exists(full_file_name):
            open(file_logs_name, 'w').close()
        MLogs.already_exit_files.append(full_file_name)

    @staticmethod
    def _check_folder_path(folder_path):
        if os.path.exists(folder_path): 
            return
        dirs = folder_path.split(os.sep)
        for i in range(1, len(dirs) + 1):
            cur_folder_path = os.path.join(*dirs[:i])
            if not os.path.exists(cur_folder_path):
                os.mkdir(cur_folder_path)

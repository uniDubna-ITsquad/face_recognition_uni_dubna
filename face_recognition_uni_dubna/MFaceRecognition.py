import face_recognition as face_rc
import numpy as np


def students_data_require(func):
    def wrapped(*args, **kwargs):
        if not MFaceRecognition._students_data:
            raise Exception('Students data is required')
        return func(*args, **kwargs)
    return wrapped


class MFaceRecognition:

    _students_data = None


    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def get_faces_features_of_image(file_path):
        fc_im = face_rc.load_image_file(file_path)
        im_faces_faetures = face_rc.face_encodings(fc_im)
        return im_faces_faetures

    @staticmethod
    def get_faces_locations_of_image(file_path):
        fc_im = face_rc.load_image_file(file_path)
        im_faces_locations = face_rc.face_locations(fc_im)
        return im_faces_locations

    @staticmethod
    def get_faces_parameters_of_image(file_path):
        fc_im = face_rc.load_image_file(file_path)
        im_faces_faetures = face_rc.face_encodings(fc_im)
        im_faces_locations = face_rc.face_locations(fc_im)
        res = {
            'locations': im_faces_locations,
            'features': im_faces_faetures,
        }
        return res

        
    @staticmethod
    def start_thread_of_processing():
        pass

    @staticmethod
    def set_student_data(value):
        value['features'] = np.array(value['features'])
        value['ids'] = np.array(value['ids'])
        MFaceRecognition._students_data = value

    @staticmethod
    @students_data_require
    def test(feature):
        res_match = face_rc.compare_faces(
            MFaceRecognition._students_data['features'],
            feature
        )
        res_ids = MFaceRecognition._students_data['ids'][res_match]
        if len(res_ids) < 1:
            raise Exception('No match')
        elif len(res_ids) > 1:
            raise Exception('So much match')
        
        return res_ids[0] 
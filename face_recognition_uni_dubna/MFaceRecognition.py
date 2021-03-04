import face_recognition as face_rc


class MFaceRecognition:
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

import face_recognition as face_rc


class MFaceRecognition:
    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def get_features_of_image(file_path):
        fc_im = face_rc.load_image_file(file_path)
        im_faetures = face_rc.face_encodings(fc_im)
        return im_faetures



import psycopg2 as psql

from datetime import datetime, timezone
import time
from time import mktime

# import numpy as np
# from psycopg2.extensions import register_adapter, AsIs


# def addapt_numpy_array(numpy_array):
#     return AsIs(tuple(numpy_array))

# register_adapter(np.ndarray, addapt_numpy_array)

def connection_require(func):
    def wrapped(*args, **kwargs):
        if not MDBQuery.conn:
            raise Exception('Connection to database is required')
        return func(*args, **kwargs)
    return wrapped


class MDBQuery:
    conn = None

    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def connect2db(*, dbname, user, password, host):
        if MDBQuery.conn:
            raise Exception('Already connected')
        conn = psql.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )

        MDBQuery.conn = conn

    @staticmethod
    @connection_require
    def check_version(version):
        n_version = version
        commands = []
        if version < 0.01:
            commands.append(
                """\
                CREATE TABLE public.cameras (
                    ip VARCHAR(255) PRIMARY KEY
                );

                CREATE TABLE public.processed_screens (
                    id SERIAL PRIMARY KEY,
                    path VARCHAR(255) NOT NULL,
                    date TIMESTAMP NOT NULL,
                    total_face SMALLINT DEFAULT NULL,
                    camera_ip VARCHAR(255) NOT NULL,

                    CONSTRAINT fk_camera_ip
                        FOREIGN KEY(camera_ip)
                            REFERENCES cameras(ip)
                            ON DELETE CASCADE
                );

                CREATE TABLE public.screens_features (
                    id BIGSERIAL PRIMARY KEY,
                    screen_id INTEGER NOT NULL,
                    face_location INTEGER[] NOT NULL,
                    face_feature REAL[] NOT NULL,
                    looks_like_student_id INTEGER,

                    CONSTRAINT fk_screen_id
                        FOREIGN KEY(screen_id)
                            REFERENCES processed_screens(id)
                            ON DELETE CASCADE

                );

                CREATE TABLE public.students_names (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                );

                CREATE TABLE public.students_features (
                    id SERIAL PRIMARY KEY,
                    path VARCHAR(255) NOT NULL,
                    feature REAL[] NOT NULL
                );

                CREATE TABLE public.students (
                    student_name_id INTEGER PRIMARY KEY,
                    student_feature_id INTEGER NOT NULL,

                    CONSTRAINT fk_student_name_id
                        FOREIGN KEY(student_name_id)
                            REFERENCES students_names(id)
                            ON DELETE CASCADE,
                    
                    CONSTRAINT fk_student_feature_id
                        FOREIGN KEY(student_feature_id)
                            REFERENCES students_features(id)
                            ON DELETE CASCADE
                );
                """
            )
            n_version = 0.01
        
        try:
            cur = MDBQuery.conn.cursor()
            for cmd in commands:
                cur.execute(cmd)
            cur.close()
            MDBQuery.conn.commit()
        except (Exception, psql.DatabaseError) as e:
            print('In MDBQuery check_version')
            print(e)
            n_version = version
        return n_version

    @staticmethod
    @connection_require
    def insert_student_with_feature(student_name, im_path, feature_im):
        cur = MDBQuery.conn.cursor()
        cur.execute(
            'INSERT INTO students_names (name) VALUES (%s)',
            [student_name]
        )
        cur.execute(
            'SELECT id FROM students_names WHERE name=%s',
            [student_name]
        )
        cur_student_name_id = cur.fetchall()
        if len(cur_student_name_id) != 1:
            raise Exception('Null or Multipler id for students names')
        cur_student_name_id = cur_student_name_id[0][0]

        cur.execute(
            'INSERT INTO students_features (path, feature) VALUES (%s, %s)',
            [im_path, list(feature_im)]
        )
        cur.execute(
            'SELECT id FROM students_features WHERE path=%s',
            [im_path]
        )
        cur_student_feature_id = cur.fetchall()
        if len(cur_student_feature_id) != 1:
            raise Exception('Null or Multipler id for students features')
        cur_student_feature_id = cur_student_feature_id[0][0]
        cur.execute(
            'INSERT INTO students (student_name_id, student_feature_id) VALUES (%s, %s)',
            [cur_student_name_id, cur_student_feature_id]
        )

        cur.close()
        MDBQuery.conn.commit()

    
    @staticmethod
    @connection_require
    def commit_screen(*, screen_path, frame_face_parameters, time = None, cam_ip = 'test'):
        if len(face_parameters_im['locations']) != len(face_parameters_im['features']):
            raise Exception("can't commit screen len locations != len features")
        total_faces = len(face_parameters_im['locations'])
        date_now = time if time != None \
              else datetime.now(timezone.utc)
        cur = MDBQuery.conn.cursor()
        cur.execute(
            "INSERT INTO processed_screens \
                (camera_ip, path, date, total_face) \
            VALUES (%s, %s, %s, %s)",
            [cam_ip, screen_path, date_now, total_faces]
        )

        cur.execute(
            'SELECT id FROM processed_screens WHERE path=%s',
            [screen_path]
        )
        cur_processed_screens_id = cur.fetchall()
        if len(cur_processed_screens_id) != 1:
            raise Exception('path of screen already has been add to processing')
        cur_processed_screens_id = cur_processed_screens_id[0][0]
        # print(cur_processed_screens_id)

        zip_face_parameters = zip(face_parameters_im['locations'], face_parameters_im['features'])
        for loc, feat in zip_face_parameters:
            cur.execute(
            "INSERT INTO screens_features \
                (screen_id, face_location, face_feature) \
            VALUES (%s, %s, %s)",
            [cur_processed_screens_id, list(loc), list(feat)]
        )
        
        cur.close()
        MDBQuery.conn.commit()

    @staticmethod
    @connection_require
    def get_students_id_and_features():
        command = """\
SELECT s.student_name_id, sf.feature
    FROM public.students_features AS sf, public.students AS s
    WHERE  sf.id = s.student_feature_id;
        """
        cur = MDBQuery.conn.cursor()
        cur.execute(command)

        data = cur.fetchall()
        cur.close()
        
        features = [el[1] for el in data]
        ids = [el[0] for el in data]

        return {'ids': ids, 'features': features}

    @staticmethod
    @connection_require
    def get_unprocessed_screens_faces():
        command = """\
SELECT id, face_feature
    FROM public.screens_features
    WHERE  looks_like_student_id IS NULL;
        """
        cur = MDBQuery.conn.cursor()
        cur.execute(command)

        data = cur.fetchall()
        cur.close()

        features = [el[1] for el in data]
        ids = [el[0] for el in data]

        return {'ids': ids, 'features': features}

    @staticmethod
    @connection_require
    def update_screens_face4match_student(screen_face_id, student_id):
        command = f"""\
UPDATE public.screens_features
	SET looks_like_student_id={student_id}
	WHERE id={screen_face_id};
        """
        cur = MDBQuery.conn.cursor()
        cur.execute(command)

        cur.close()
        MDBQuery.conn.commit()

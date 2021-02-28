import psycopg2 as psql


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
                CREATE TABLE public.processed_screens (
                    id SERIAL PRIMARY KEY,
                    path VARCHAR(255) NOT NULL,
                    date TIMESTAMP NOT NULL,
                    total_face SMALLINT DEFAULT NULL
                );

                CREATE TABLE public.screens_features (
                    id BIGSERIAL PRIMARY KEY,
                    screen_id INTEGER NOT NULL,
                    feature REAL[] NOT NULL,
                    looks_like_student_id INTEGER,

                    CONSTRAINT fk_screen_id
                        FOREIGN KEY(screen_id)
                            REFERENCES processed_screens(id)
                            ON DELETE CASCADE

                );

                CREATE TABLE public.students (
                    student_name_id INTEGER PRIMARY KEY,
                    student_feature_id INTEGER NOT NULL,

                    CONSTRAINT fk_student_name_id
                        FOREIGN KEY(student_name_id)
                            REFERENCES processed_screens(id)
                            ON DELETE CASCADE,
                    
                    CONSTRAINT fk_student_feature_id
                        FOREIGN KEY(student_feature_id)
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

    # @staticmethod
    # @connection_require

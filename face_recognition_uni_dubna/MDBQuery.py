import psycopg2 as psql

def connection_require(func):
    def wrapped(*args, **kwargs):
        if not MDBQuery.is_connected:
            raise Exception('Connection to database is required')
        func(*args, **kwargs)
    return wrapped

class MDBQuery:
    is_connected = False
    cur = None

    def __init__(self):
        raise Exception('you cannot create an object of this class')

    @staticmethod
    def connect2db(*, dbname, user, password, host):
        if MDBQuery.is_connected:
            raise Exception('Already connected')
        conn = psql.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )

        MDBQuery.is_connected = True

    # @staticmethod
    # @connection_require
            
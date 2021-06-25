import sqlalchemy

from sqlalchemy.orm import sessionmaker


class ORMClient(object):
    session = None
    _engine = None
    _connection = None

    def __init__(self):
        pass

    def __del__(self):
        self.disconnect()

    def connect(self, host: str, port: int, username: str, password: str, database: str = '') -> None:
        self._engine = sqlalchemy.create_engine(
            f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}',
            encoding="utf8"
        )
        self._connection = self._engine.connect()
        self.session = sessionmaker(bind=self._connection.engine,
                                    autocommit=False,
                                    expire_on_commit=False)()

    def disconnect(self):
        if self._connection is not None:
            self._connection.close()

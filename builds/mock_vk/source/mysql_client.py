import pymysql


class MySQLClient(object):
    connection = None

    username: str = None
    password: str = None
    db: str = None
    hostname: str = None
    port: int = None

    def __init__(self, username: str, password: str, db: str, hostname: str = '127.0.0.1', port: int = 3306) -> None:
        self.username = username
        self.password = password
        self.db = db
        self.hostname = hostname
        self.port = port
    
    def __del__(self) -> None:
        self.disconnect()
    
    def connect(self) -> None:
        self.connection = pymysql.connect(user=self.username,
                                          password=self.password,
                                          host=self.hostname,
                                          database=self.db,
                                          port=self.port,
                                          cursorclass=pymysql.cursors.DictCursor,
                                          autocommit=True)
    
    def disconnect(self) -> None:
        if self.connection is not None:
            self.connection.close()
    
    def execute_query(self, query: str, fetch: bool = False, auto_connect: bool = False, auto_disconnect: bool = False) -> list:
        # Автоматическое подключение.
        if auto_connect:
            self.connect()

        with self.connection.cursor() as cursor:
            cursor.execute(query)

            if fetch:
                return cursor.fetchall()

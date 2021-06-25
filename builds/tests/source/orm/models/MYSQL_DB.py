from orm.common.exceptions import NotEqualException

from sqlalchemy import Column, INT, SMALLINT, VARCHAR, DATETIME, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class ModelTestUsers(DeclarativeBase):
    __tablename__ = "test_users"
    __table_args__ = {'mysql_charset': 'utf8'}

    id = Column(INT, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(16), default=None, nullable=True)
    password = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(64), nullable=False)
    access = Column(SMALLINT, default=None, nullable=True)
    active = Column(SMALLINT, default=None, nullable=True)
    start_active_time = Column(DATETIME, default=None, nullable=True)

    UniqueConstraint('email', name="email")
    UniqueConstraint('ix_test_users_username', name="username")

    def __repr__(self):
        return f"<{self.__class__.__name__} [table='{self.__tablename__}'] [table_args='{self.__table_args__}'] (" \
               f"id='{self.id}'; " \
               f"username='{self.username}'; " \
               f"password='{self.password}'; " \
               f"email='{self.email}'; " \
               f"access='{self.access}'; " \
               f"active='{self.active}'; " \
               f"start_active_time='{self.start_active_time}')"

    def __eq__(self, other) -> bool:
        errors = []
        for attr in ['username', 'password', 'email', 'access', 'active', 'start_active_time']:
            s = getattr(self, attr, None)
            o = getattr(other, attr, None)

            if s != o:
                errors.append(f'Свойство "{attr}": "{s}" != "{o}"')

        if errors:
            raise NotEqualException(f'\n'.join(errors))
        return True

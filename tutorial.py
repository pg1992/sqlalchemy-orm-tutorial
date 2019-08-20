import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
MySQLSession = sessionmaker()
SQLiteSession = sessionmaker()


class User(Base):
    __tablename__ = 'user'

    id = sql.Column(sql.Integer, sql.Sequence('user_id_seq'), primary_key=True)
    name = sql.Column(sql.String(50))
    fullname = sql.Column(sql.String(50))
    nickname = sql.Column(sql.String(50))

    def __repr__(self):
        return "<User(name='{}', fullname='{}', nickname='{}')>".format(
            self.name, self.fullname, self.nickname
        )


def sqlalchemy_version():
    print('SQLAlchemy version: {}'.format(sql.__version__))


def create_mysql_engine():
    eng = sql.create_engine(
        'mysql+mysqldb://pedro:pedro@localhost/test',
        echo=True,
    )

    print('Return value of sqlalchemy.create_engine():', eng)

    MySQLSession.configure(bind=eng)

    return eng


def create_sqlite_engine():
    eng = sql.create_engine(
        'sqlite:///:memory:',
        echo=True,
    )

    print('Return value of sqlalchemy.create_engin():', eng)

    SQLiteSession.configure(bind=eng)

    return eng


def main():
    # Check SQLAlchemy version
    sqlalchemy_version()

    # Create a MySQL engine with msqlclient and create a schema
    mysql_engine = create_mysql_engine()
    Base.metadata.create_all(mysql_engine)
    mysql_session = MySQLSession()

    # Create a SQLite engine in memory and create a schema
    sqlite_engine = create_sqlite_engine()
    Base.metadata.create_all(sqlite_engine)
    sqlite_session = SQLiteSession()

    # Create an instance of the mapped class
    ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
    print('ed_user.name =', ed_user.name)
    print('ed_user.fullname =', ed_user.fullname)
    print('ed_user.nickname =', ed_user.nickname)
    print('ed_user.id =', str(ed_user.id))


if __name__ == '__main__':
    main()

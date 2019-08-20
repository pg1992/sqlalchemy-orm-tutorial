import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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

    return eng


def create_sqlite_engine():
    eng = sql.create_engine(
        'sqlite:///:memory:',
        echo=True,
    )

    print('Return value of sqlalchemy.create_engin():', eng)

    return eng


def main():
    sqlalchemy_version()

    mysql_engine = create_mysql_engine()
    Base.metadata.create_all(mysql_engine)

    sqlite_engine = create_sqlite_engine()
    Base.metadata.create_all(sqlite_engine)


if __name__ == '__main__':
    main()

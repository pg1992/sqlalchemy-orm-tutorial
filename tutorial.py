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
        return "<User(id='%s', name='%s', fullname='%s', nickname='%s')>" % (
            self.id, self.name, self.fullname, self.nickname,
        )


def create_engines_and_sessions():
    conn_strings = [
        'mysql+mysqldb://pedro:pedro@localhost/test',
        'sqlite:///:memory:',
    ]

    sessions_engines = []

    for conn_string in conn_strings:
        engine = sql.create_engine(conn_string, echo=True)
        session = sql.orm.sessionmaker(bind=engine)
        sessions_engines.append((engine, session))

        print('Return value of sqlalchemy.create_engine():', engine)

    return sessions_engines


def main():
    # Check SQLAlchemy version
    print('SQLAlchemy version: {}'.format(sql.__version__))

    # Create all engines, session makers, schemas, and a sessions
    for engine, session in create_engines_and_sessions():
        Base.metadata.create_all(engine)
        session_instance = session()

        # Create an instance of the mapped class
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')

        # Create a pending instance
        session_instance.add(ed_user)

        # Query our user will flush the instance and issue SQL
        our_user = session_instance.query(User).filter_by(name='ed').first()

        # Print each object property
        print('ed_user =', ed_user)
        print('our_user =', our_user)

        # Is the created and queried objects the same?
        print('ed_user is our_user =', ed_user is our_user)


if __name__ == '__main__':
    main()

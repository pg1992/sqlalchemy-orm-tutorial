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
        'sqlite:///:memory:',
        'mysql+mysqldb://pedro:pedro@localhost/test',
    ]

    engines_sessions = []

    for conn_string in conn_strings:
        engine = sql.create_engine(conn_string, echo=True)
        session_class = sql.orm.sessionmaker(bind=engine)
        engines_sessions.append((engine, session_class))

        print('Return value of sqlalchemy.create_engine():', engine)

    return engines_sessions


def main():
    # Check SQLAlchemy version
    print('SQLAlchemy version: {}'.format(sql.__version__))

    # Create all engines, session makers, schemas, and a sessions
    for engine, session_class in create_engines_and_sessions():
        Base.metadata.create_all(engine)
        session = session_class()

        # Create an instance of the mapped class
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
        print('ed_user =', ed_user)

        # Create a pending instance
        session.add(ed_user)

        # Query our user will flush the instance and issue SQL
        our_user = session.query(User).filter_by(name='ed').first()

        # Print each object property
        print('ed_user =', ed_user)
        print('our_user =', our_user)

        # Is the created and queried objects the same?
        print('ed_user is our_user =', ed_user is our_user)

        # Add more users with add_all
        session.add_all([
            User(name='wendy', fullname='Wendy Williams', nickname='windy'),
            User(name='mary', fullname='Mary Contrary', nickname='mary'),
            User(name='fred', fullname='Fred Flintstone', nickname='freddy'),
        ])

        # Change Ed's nickname
        ed_user.nickname = 'eddie'

        # Is there some operation pending?
        print('session.dirty =', session.dirty)

        # Are there new objects to be persisted?
        print('session.new =', session.new)

        # Commit the transaction
        session.commit()

        # Print ed_user showing that now it has an id
        print('ed_user =', ed_user)

        # Change the user name
        ed_user.name = 'Edwardo'

        # Add a an erroneous user
        fake_user = User(name='fakeuser', fullname='Invalid', nickname='12345')
        session.add(fake_user)

        # Query the recent added data in the current session
        wrong_users = session\
            .query(User)\
            .filter(User.name.in_(['Edwardo', 'fakeuser']))\
            .all()
        print('Before rollback:', wrong_users)

        # Oops! Invalid transaction. Rollback!
        session.rollback()

        # Print Ed's name
        print('ed_user.name =', ed_user.name)

        # Is the fake_user on this session?
        print('fake_user in session?', fake_user in session)

        # Query the recent added data in the current session after rollback
        after_rollback = session\
            .query(User)\
            .filter(User.name.in_(['ed', 'fakeuser']))\
            .all()
        print('After rollback:', after_rollback)

        # Query a list of all users ordered by ID
        for instance in session.query(User).order_by(User.id):
            print(instance)

        # Query by ORM-instrumented descriptiors
        for name, fullname in session.query(User.name, User.fullname):
            print('user.name = {}, user.fullname = {}'.format(name, fullname))

        # Return KeyedTuple
        for row in session.query(User, User.name).all():
            print('User: {}, name: {}'.format(row.User, row.name))

        # Rename a column
        for row in session.query(User.name.label('name_label')):
            print('row.name_label =', row.name_label)

        # Control name of the full User entity with aliased
        user_alias = sql.orm.aliased(User, name='user_alias')

        for row in session.query(user_alias, user_alias.name).all():
            print('row.user_alias =', row.user_alias)


if __name__ == '__main__':
    main()

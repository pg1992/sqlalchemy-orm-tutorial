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
        # 'mysql+mysqldb://pedro:pedro@localhost/test',
    ]

    engines_sessions = []

    for conn_string in conn_strings:
        engine = sql.create_engine(conn_string, echo=False)
        session_class = sql.orm.sessionmaker(bind=engine)
        engines_sessions.append((engine, session_class))

        print('Return value of sqlalchemy.create_engine():', engine)

    return engines_sessions


def common_filter_operators(session):
    operators = {
        'equals': session.query(User).filter(User.name == 'ed'),
        'not equals': session.query(User).filter(User.name != 'ed'),
        'LIKE': session.query(User).filter(User.name.like('%ed%')),
        'ILIKE': session.query(User).filter(User.name.ilike('%ed%')),
        'IN': session.query(User).filter(
            User.name.in_(['ed', 'wendy', 'jack'])
        ),
        'NOT IN': session.query(User).filter(
            ~User.name.in_(['ed', 'wendy', 'jack'])
        ),
        'IS NULL': session.query(User).filter(User.name.is_(None)),
        'IS NOT NULL': session.query(User).filter(User.name.isnot(None)),
        'AND with and_': session.query(User).filter(
            sql.and_(User.name == 'ed', User.fullname == 'Ed Jones')
        ),
        'AND with multiple expressions': session.query(User).filter(
            User.name == 'ed', User.fullname == 'Ed Jones',
        ),
        'AND with chained filter': session.query(User)
                                          .filter(User.name == 'ed')
                                          .filter(User.fullname == 'Ed Jones'),
        'OR': session.query(User).filter(
            sql.or_(User.name == 'ed', User.name == 'wendy')
        ),
        'MATCH': session.query(User).filter(User.name.match('wendy')),
    }

    for text, query in operators.items():
        try:
            print('{} -> {}'.format(text, query.all()))
        except Exception as ex:
            print('An error occured:', ex)


def lists_and_scalars(session):
    query = session.query(User)\
                   .filter(User.name.like('%ed%'))\
                   .order_by(User.id)

    print('query.all() =', query.all())
    print('query.first() =', query.first())

    try:
        print('query.one() =', query.one())
    except Exception as ex:
        print('Error:', ex)

    try:
        bogus_query = query.filter(User.id == 99)
        print('query.one() =', bogus_query.one())
    except Exception as ex:
        print('Error:', ex)

    try:
        print('query.one_or_none() =', query.one_or_none())
    except Exception as ex:
        print('Error:', ex)

    try:
        bogus_query = query.filter(User.id == 99)
        print('query.one_or_none() =', bogus_query.one_or_none())
    except Exception as ex:
        print('Error:', ex)

    try:
        query = session.query(User.id).filter(User.name == 'ed')\
                       .order_by(User.id)
        print('query.scalar() =', query.scalar())
    except Exception as ex:
        print('Error:', ex)


def query_examples(session):
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

    # Use Python array slices to implement SQL LIMIT and OFFSET
    for u in session.query(User).order_by(User.id)[1:3]:
        print('user =', u)

    # Use filter_by to implement SQL WHERE
    for name, in session.query(User.name).filter_by(fullname='Ed Jones'):
        print('name =', name)

    # Use filter for a more flexible SQL expression
    for name, in session.query(User.name)\
            .filter(User.fullname == 'Ed Jones'):
        print('name =', name)

    # Join criteria with AND
    for user in session.query(User)\
            .filter(User.name == 'ed')\
            .filter(User.fullname == 'Ed Jones'):
        print('user =', user)


def using_textual_sql(session):
    # Use literal strings with sqlalchemy.text
    for user in session.query(User)\
                       .filter(sql.text('id<224'))\
                       .order_by(sql.text('id')).all():
        print('user.name =', user.name)

    # Bind parameters
    user = session.query(User)\
                  .filter(sql.text("id<:value and name=:name"))\
                  .params(value=224, name='fred')\
                  .order_by(User.id)\
                  .one()
    print('user =', user)

    # Use an entirely string-based statement
    users = session.query(User)\
                   .from_statement(
                        sql.text("SELECT * FROM user WHERE name=:name")
                    )\
                   .params(name='ed')\
                   .all()
    print('users =', users)


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

        # Common filter operators
        common_filter_operators(session)

        # Returning lists or scalars
        lists_and_scalars(session)

        # Using textual SQL
        using_textual_sql(session)


if __name__ == '__main__':
    main()

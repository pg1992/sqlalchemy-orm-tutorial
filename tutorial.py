import sqlalchemy as sql
from models import Base, Address, User


def create_engines_and_sessions():
    conn_strings = [
        'sqlite:///:memory:',
        # 'mysql+mysqldb://pedro:pedro@localhost/test',
    ]

    engines_sessions = []

    for conn_string in conn_strings:
        engine = sql.create_engine(conn_string, echo=True)
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
                        sql.text("SELECT * FROM users WHERE name=:name")
                    )\
                   .params(name='ed')\
                   .all()
    print('users =', users)

    # Link textual SQL to ORM-mapped column expressions
    stmt = sql.text("SELECT name, id, fullname, nickname "
                    "FROM users WHERE name=:name")
    stmt = stmt.columns(User.name, User.id, User.fullname, User.nickname)
    users = session.query(User).from_statement(stmt).params(name='ed').all()
    print('users =', users)

    # Specify the columns from query
    stmt = sql.text("SELECT name, id FROM users WHERE name=:name")
    stmt = stmt.columns(User.name, User.id)
    users = session.query(User.id, User.name)\
                   .from_statement(stmt)\
                   .params(name='ed')\
                   .all()
    print('users = ', users)


def counting_examples(session):
    # Count all users with name like %ed%
    total = session.query(User).filter(User.name.like('%ed%')).count()
    print('Total of %ed% =', total)

    # Count each distinct user name using sqlalchemy.func.count
    for total, name in session.query(sql.func.count(User.name), User.name)\
                              .group_by(User.name)\
                              .all():
        print('{} users named {}'.format(total, name))

    # Achieve simple SELECT count(*) FROM table
    total = session.query(sql.func.count('*')).select_from(User).scalar()
    print('There are {} users'.format(total))

    # If we don't want to use select_from
    total = session.query(sql.func.count(User.id)).scalar()
    print('There are {} users'.format(total))


def working_with_related_objects(session):
    # Create a new user with blank addresses collection
    jack = User(name='jack', fullname='Jack Bean', nickname='gjffdd')
    print('jack.addresses =', jack.addresses)

    # Add addresses to a user
    jack.addresses = [
        Address(email_address='jack@google.com'),
        Address(email_address='j25@yahoo.com'),
    ]
    print('jack.addresses[1] =', jack.addresses[1])
    print('jack.addresses[1].user =', jack.addresses[1].user)
    print('jack.addresses[1].user is jack? ', jack.addresses[1].user is jack)

    # Persist the new user and all its related addresses
    session.add(jack)
    session.commit()

    # Query a user and its associated addresses
    jack = session.query(User).filter_by(name='jack').one()
    print('jack =', jack)
    print('jack.addresses =', jack.addresses)


def querying_with_joins(session):
    # Use a simple implicit join
    for u, a in session.query(User, Address)\
                       .filter(User.id == Address.user_id)\
                       .filter(Address.email_address == 'jack@google.com')\
                       .all():
        print('user =', u)
        print('address =', a)

    # Use actual SQL JOIN
    #   This works because there is only one foreign key
    #   between them.
    result = session.query(User)\
                    .join(Address)\
                    .filter(Address.email_address == 'jack@google.com')\
                    .all()
    print('result with actual SQL JOIN = ', result)

    # When no foreign keys exist
    #   explicit condition
    result = session.query(User)\
                    .join(Address, User.id == Address.user_id)\
                    .all()
    print('result with explict condition =', result)

    #   specify relationship from left to right
    result = session.query(User)\
                    .join(User.addresses)\
                    .all()
    print('result specifying relationship from left to right =', result)

    #   same, with explicti target
    result = session.query(User)\
                    .join(Address, User.addresses)\
                    .all()
    print('same result with explicit target =', result)

    #   same, using a string
    result = session.query(User)\
                    .join('addresses')\
                    .all()
    print('same result using string =', result)

    # LEFT OUTER JOIN
    result = session.query(User).outerjoin(User.addresses).all()
    print('result =', result)

    # Use aliases to query the same table more than once
    adalias1 = sql.orm.aliased(Address)
    adalias2 = sql.orm.aliased(Address)
    for username, email1, email2 in \
        session.query(User.name, adalias1.email_address,
                      adalias2.email_address)\
               .join(adalias1, User.addresses)\
               .join(adalias2, User.addresses)\
               .filter(adalias1.email_address == 'jack@google.com')\
               .filter(adalias2.email_address == 'j25@yahoo.com'):
        print(username, email1, email2)

    # Use subqueries
    #
    # SELECT users.*, adr_count.address_count FROM users LEFT OUTER JOIN
    #        (SELECT user_id, count(*) AS address_count
    #           FROM addresses GROUP_BY user_id) as adr_count
    #     ON users.id=adr_count.user_id
    from sqlalchemy.sql import func
    stmt = session.query(Address.user_id,
                         func.count('*').label('address_count'))\
                  .group_by(Address.user_id)\
                  .subquery()
    for u, count in session.query(User, stmt.c.address_count)\
                           .outerjoin(stmt, User.id == stmt.c.user_id)\
                           .order_by(User.id):
        print('User {} has {} emails'.format(u, count))

    # Associante an "alias" of a mapped class to a subquery
    stmt = session.query(Address)\
                  .filter(Address.email_address != 'j25@yahoo.com')\
                  .subquery()
    adalias = sql.orm.aliased(Address, stmt)
    for user, address in session.query(User, adalias)\
                                .join(adalias, User.addresses):
        print('Users{}{}'.format(user, address))

    # List the name of users that have any email addresses
    from sqlalchemy.sql import exists
    stmt = exists().where(Address.user_id == User.id)
    for name, in session.query(User.name).filter(stmt):
        print('user {} has associated emails'.format(name))

    # Use Query.any() to check if there are any addresses
    for name, in session.query(User.name)\
                        .filter(User.addresses.any()):
        print('user {} has associated emails'.format(name))

    # User Query.any() with a criterion to limit the rows matched
    for match in ['google', 'yahoo']:
        print('users with {} in their email:'.format(match))
        match_str = '%{}%'.format(match)
        for name, in session.query(User.name)\
                            .filter(
                                User.addresses.any(
                                    Address.email_address.like(match_str)
                                )
                            ):
            print('  {}'.format(name))

    # Use has() (which is the same operator as any())
    for name, in session.query(User.name):
        print('emails not from {}:'.format(name))
        for address in session.query(Address)\
                              .filter(~Address.user.has(User.name == name)):
            print('  {}'.format(address.email_address))


def common_relationship_operators(session):
    for user in session.query(User).filter(User.name.like('%ed%')).all():
        # many-to-one equals comparison
        print('user {} has the following emails:'.format(user.name))
        for addr in session.query(Address).filter(Address.user == user).all():
            print('  {}'.format(addr.email_address))

        # many-to-one not equals comparison
        print('user {} does not have the following emails:'.format(user.name))
        for addr in session.query(Address).filter(Address.user != user).all():
            print('  {}'.format(addr.email_address))

    # IS NULL
    #   pycodestyle says it is an error to compare with None, but there
    #   is no sqlalchemy.orm.relation.is_ method like the sqlalchemy.Column.
    print('All email addresses with no associated user:')
    for addr in session.query(Address).filter(Address.user == None).all():
        print('  {}'.format(addr.email_address))

    # contains() is used for one-to-many relationships
    for email in session.query(Address):
        try:
            user = session.query(User)\
                          .filter(User.addresses.contains(email))\
                          .one()
            print('user %s owns email %s' % (user.name, email.email_address))
        except sql.orm.exc.MultipleResultsFound as ex:
            print('There were more than one user that owns this email')
        except sql.orm.exc.NoResultFound as ex:
            print('There is no user that owns this email')
        except Exception as ex:
            print('Unknown error: {}'.format(ex))

    # use any() for collections
    print('users with google emails:')
    for name, in session.query(User.name)\
                        .filter(
                             User.addresses.any(
                                 Address.email_address.like('%google.com')
                             )
                         ):
        print('  {}'.format(name))

    # use any() with keyword argument
    print('user with email ed@google.com')
    for name, in session.query(User.name)\
                        .filter(
                            User.addresses.any(email_address='ed@google.com')
                        ):
        print('  {}'.format(name))

    # use has() for scalar references
    print('all emails from jack')
    for email, in session.query(Address.email_address)\
                         .filter(Address.user.has(name='jack')):
        print('  {}'.format(email))

    # use Query.with_parent() for any relationship
    print('all emails from jack:')
    jack = session.query(User).filter_by(name='jack').one()
    for email, in session.query(Address.email_address)\
                         .with_parent(jack, 'addresses'):
        print('  {}'.format(email))


def eager_loading(session):
    # load User.addresses eagerly with selectinload
    jack = session.query(User)\
                  .options(sql.orm.selectinload(User.addresses))\
                  .filter_by(name='jack')\
                  .one()
    print('user {} has emails {}'.format(jack.name, jack.addresses))

    # eager load User.addresses with joinedload (LEFT OUTER JOIN)
    jack = session.query(User)\
                  .options(sql.orm.joinedload(User.addresses))\
                  .filter_by(name='jack')\
                  .one()
    print('user {} has emails {}'.format(jack.name, jack.addresses))

    # load Address row and related User object, filter on the User named "jack"
    # use contains_eager() to apply "user" columns to the Address.user
    jacks_addresses = session.query(Address)\
                             .join(Address.user)\
                             .filter(User.name == 'jack')\
                             .options(sql.orm.contains_eager(Address.user))\
                             .all()
    jack = jacks_addresses[0].user
    print('user {} has emails {}'.format(jack.name, jacks_addresses))


def deletion(session):
    # delete a user
    jack = session.query(User).filter_by(name='jack').one()
    session.delete(jack)
    total = session.query(User).filter_by(name='jack').count()
    print('there are {} with name jack after session.delete'.format(total))

    # the deletion is not cascaded because we didn't set it up
    total_emails = session.query(Address).filter(
        Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
    ).count()
    print('there are {} orphan emails'.format(total_emails))

    # Oh no! There are orphan emails. Rollback!
    session.rollback()

    # load Jack by primary key
    jack = session.query(User).get(5)
    # remove one Address (lazy load fires off)
    del jack.addresses[1]
    # only one address remains
    total_emails = session.query(Address).filter(
        Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
    ).count()
    print('jack has {} emails'.format(total_emails))

    # cascade delete jack's emails
    session.delete(jack)
    total_users = session.query(User).filter_by(name='jack').count()
    total_emails = session.query(Address).filter(
        Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
    ).count()
    print('there are {} users named jack and {} '
          'emails associated with it'.format(total_users, total_emails))


def main():
    # Check SQLAlchemy version
    print('SQLAlchemy version: {}'.format(sql.__version__))

    # Create all engines, session makers, schemas, and a sessions
    for engine, session_class in create_engines_and_sessions():
        Base.metadata.create_all(engine)
        session = session_class()

        # Create an instance of the mapped class
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
        ed_user.addresses = [Address(email_address='ed@google.com')]
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

        # Counting examples
        counting_examples(session)

        # Working with related objects
        working_with_related_objects(session)

        # Querying with joins
        querying_with_joins(session)

        # All the operators which build on relationships
        common_relationship_operators(session)

        # Reduce the number of queries by applying eager loading
        eager_loading(session)

        # Deleting
        deletion(session)


if __name__ == '__main__':
    main()

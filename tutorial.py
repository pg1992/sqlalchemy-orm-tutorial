import sqlalchemy as sql


def sqlalchemy_version():
    print('SQLAlchemy version: {}'.format(sql.__version__))


def create_engine():
    eng = sql.create_engine(
        'mysql+mysqldb://pedro:pedro@localhost/test',
        echo=True,
    )

    print('Return value of sqlalchemy.create_engine():', eng)

    return eng


def main():
    sqlalchemy_version()
    eng = create_engine()


if __name__ == '__main__':
    main()

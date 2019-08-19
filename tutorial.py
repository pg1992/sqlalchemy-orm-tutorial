import sqlalchemy as sql


def sqlalchemy_version():
    print('SQLAlchemy version: {}'.format(sql.__version__))


def main():
    sqlalchemy_version()


if __name__ == '__main__':
    main()

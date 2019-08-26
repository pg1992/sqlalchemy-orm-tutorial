import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Address(Base):
    __tablename__ = 'addresses'

    id = sql.Column(sql.Integer, primary_key=True)
    email_address = sql.Column(sql.String, nullable=False)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))

    user = sql.orm.relationship('User', back_populates='addresses')

    def __repr__(self):
        return "Address(email_address='%s')" % self.email_address


class User(Base):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String)
    fullname = sql.Column(sql.String)
    nickname = sql.Column(sql.String)

    addresses = sql.orm.relationship('Address', back_populates='user',
                                     cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name, self.fullname, self.nickname,
        )

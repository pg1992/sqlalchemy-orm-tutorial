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


# association table
post_keywords = sql.Table(
    'post_keywords', Base.metadata,
    sql.Column('post_id', sql.ForeignKey('posts.id'), primary_key=True),
    sql.Column('keyword_id', sql.ForeignKey('keywords.id'), primary_key=True)
)


class BlogPost(Base):
    __tablename__ = 'posts'

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    headline = sql.Column(sql.String(255), nullable=False)
    body = sql.Column(sql.Text)

    # many-to-many BlogPost<->Keyword
    keywords = sql.orm.relationship('Keyword',
                                    secondary=post_keywords,
                                    back_populates='posts')

    def __init__(self, headline, body, author):
        self.author = author
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


class Keyword(Base):
    __tablename__ = 'keywords'

    id = sql.Column(sql.Integer, primary_key=True)
    keyword = sql.Column(sql.String(50), nullable=False, unique=True)
    posts = sql.orm.relationship('BlogPost',
                                 secondary=post_keywords,
                                 back_populates='keywords')

    def __init__(self, keyword):
        self.keyword = keyword

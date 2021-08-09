import datetime as dt
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///dev.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

from conduit.database import Model
from conduit.extensions import bcrypt

def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return Column(
        ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)

class User(Model):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    bio = Column(String(300), nullable=True)
    image = Column(String(120), nullable=True)
    token: str = ''

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)


class FavoriterAssoc(Model):
    __tablename__ = "favoriter_assoc"
    favoriter = Column(Integer, ForeignKey("user.id"), primary_key=True)
    favorited_article = Column(Integer, ForeignKey("article.id"), primary_key=True)

class TagAssoc(Model):
    __tablename__ = "tag_assoc"
    tag = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    article = Column(Integer, ForeignKey("article.id"), primary_key=True)


class Tags(Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tagname = Column(String(100))

    def __repr__(self):
        return self.tagname


class Comment(Model):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    body = Column(Text)
    createdAt = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    author_id = reference_col('users', nullable=False)
    author = relationship('User', backref=backref('comments'))
    article_id = reference_col('article', nullable=False)


class Article(Model):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    slug = Column(Text, unique=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    body = Column(Text)
    createdAt = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    author_id = reference_col('users', nullable=False)
    author = relationship('User', backref=backref('articles'))
    favoriters = relationship(
        'User',
        secondary='favoriter_assoc',
        backref='favorites',
        lazy='dynamic')

    tagList = relationship(
        'Tags', secondary='tag_assoc', backref='articles')

    comments = relationship('Comment', backref=backref('article'), lazy='dynamic')

    def favourite(self, profile):
        if not self.is_favourite(profile):
            self.favoriters.append(profile)
            return True
        return False

    def unfavourite(self, profile):
        if self.is_favourite(profile):
            self.favoriters.remove(profile)
            return True
        return False

    def is_favourite(self, profile):
        #return bool(self.query.filter(favoriter_assoc.c.favoriter == profile.id).count())
        return False

    def add_tag(self, tag):
        if tag not in self.tagList:
            self.tagList.append(tag)
            return True
        return False

    def remove_tag(self, tag):
        if tag in self.tagList:
            self.tagList.remove(tag)
            return True
        return False

    @property
    def favoritesCount(self):
        return len(self.favoriters.all())

    @property
    def favorited(self):
        return False

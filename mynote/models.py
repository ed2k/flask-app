import datetime as dt
from re import T
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///logs/dev.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Model = declarative_base()


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
        self.password = password

    def check_password(self, value):
        """Check password."""
        return True

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)


class UserProfile(Model):
    __tablename__ = 'userprofile'

    # id is needed for primary join, it does work with SurrogatePK class
    id = Column(Integer, primary_key=True)

    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref=backref('profile', uselist=False))

    @property
    def following(self):
        # if current_user:
        #     return current_user.profile.is_following(self)
        return False

    @property
    def username(self):
        return self.user.username

    @property
    def bio(self):
        return self.user.bio

    @property
    def image(self):
        return self.user.image

    @property
    def email(self):
        return self.user.email


class TagAssoc(Model):
    __tablename__ = "tag_assoc"
    tag = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    article = Column(Integer, ForeignKey("article.id"), primary_key=True)


class Tags(Model):
    """lowercase a to z and dash
    """
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tagname = Column(String(100))

    def __repr__(self):
        return self.tagname


class Article(Model):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    # unqiue of titles, middle stage for transition from title to tagList
    slug = Column(Text, unique=True)
    # single line of lowercase a to z, dash, one space
    title = Column(String(200))
    body = Column(Text)
    createdAt = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    tagList = relationship(
        'Tags', secondary='tag_assoc', backref='articles')

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


# bootstrap
def my_db_bootstrap():
    try:
        db_session.query(Article).first()
    except:
        print('create all tables')
        Model.metadata.create_all(engine)

my_db_bootstrap()

'''
CREATE TABLE favoriter_assoc (
	favoriter INTEGER, 
	favorited_article INTEGER, 
	FOREIGN KEY(favorited_article) REFERENCES article (id), 
	FOREIGN KEY(favoriter) REFERENCES user (id)
);

CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE tags (
	id INTEGER NOT NULL, 
	tagname VARCHAR(100), 
	PRIMARY KEY (id)
);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	password BLOB, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	bio VARCHAR(300), 
	image VARCHAR(120), 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	UNIQUE (username)
);
CREATE TABLE userprofile (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE article (
	id INTEGER NOT NULL, 
	slug TEXT, 
	title VARCHAR(200), 
	body TEXT, 
	"createdAt" DATETIME NOT NULL, 
	"updatedAt" DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE followers_assoc (
	follower INTEGER, 
	followed_by INTEGER, 
	FOREIGN KEY(followed_by) REFERENCES userprofile (user_id), 
	FOREIGN KEY(follower) REFERENCES userprofile (user_id)
);
CREATE TABLE comment (
	id INTEGER NOT NULL, 
	body TEXT, 
	"createdAt" DATETIME NOT NULL, 
	"updatedAt" DATETIME NOT NULL, 
	author_id INTEGER NOT NULL, 
	article_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(article_id) REFERENCES article (id), 
	FOREIGN KEY(author_id) REFERENCES userprofile (id)
);
CREATE TABLE favoritor_assoc (
	favoriter INTEGER, 
	favorited_article INTEGER, 
	FOREIGN KEY(favorited_article) REFERENCES article (id), 
	FOREIGN KEY(favoriter) REFERENCES userprofile (id)
);
CREATE TABLE tag_assoc (
	tag INTEGER, 
	article INTEGER, 
	FOREIGN KEY(article) REFERENCES article (id), 
	FOREIGN KEY(tag) REFERENCES tags (id)
);

'''
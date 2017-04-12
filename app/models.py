# -*- coding: UTF-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db, login_manager
from sqlalchemy import and_
import os
from config import basedir


class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return repr(User.query.get(self.follower_id)) + " follows " \
            + repr(User.query.get(self.followed_id)) + " at " + \
            repr(self.timestamp)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    hash_password = db.Column(db.String)
    avatar_url = db.Column(db.String, default=None)
    about_me = db.Column(db.String(30))
    location = db.Column(db.String(40))
    sex = db.Column(db.Integer, default=0)
    last_time = db.Column(db.Integer, default=datetime.now())
    valid_time = db.Column(db.DateTime, default=datetime.now())
    type = db.Column(db.Integer, default=0)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    albums = db.relationship('Album', backref='author', lazy='dynamic')

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               )

    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                )

    praises = db.relationship('Praise', backref='praiser', lazy='dynamic')

    collections = db.relationship('Collection', backref='collector', lazy='dynamic')

    messages = db.relationship('Message', backref='receiver', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('the password attribution of user is invalid')

    @password.setter
    def password(self, password):
        self.hash_password = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(self.hash_password, password)

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            db.session.commit()
            message = Message(receive_id=user.id, refer_id=follow.id, type=4)
            db.session.add(message)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            follow = self.followed.filter_by(followed_id=user.id).first()
            db.session.delete(follow)
            message = Message.query.filter_by(refer_id=follow.id, type=4).first()
            if message is not None:
                db.session.delete(message)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def is_collecting(self, post):
        return self.collections.filter_by(post_id=post.id).first() is not None

    def is_praising(self, post):
        return post.praises.filter_by(author_id=self.id).first() is not None

    def collect(self, post):
        if not self.is_collecting(post):
            collection = Collection(author_id=self.id, post_id=post.id)
            db.session.add(collection)
            post.score += 3
            db.session.add(post)
            db.session.commit()
            if self.id != post.author_id:
                message = Message(receive_id=post.author_id, refer_id=collection.id, post_id=post.id, type=2)
                db.session.add(message)
                db.session.commit()

    def uncollect(self, post):
        if self.is_collecting(post):
            collection = self.collections.filter_by(post_id=post.id).first()
            message = Message.query.filter_by(refer_id=collection.id, type=2).first()
            if message is not None:
                post.score -= 3
                db.session.add(post)
                db.session.delete(message)
            db.session.delete(collection)
            db.session.commit()

    def praise(self, post):
        if not self.is_praising(post):
            praise = Praise(author_id=self.id, post_id=post.id)
            db.session.add(praise)
            post.score += 1
            db.session.add(post)
            db.session.commit()
            if self.id != post.author_id:
                message = Message(receive_id=post.author_id, refer_id=praise.id, post_id=post.id, type=1)
                db.session.add(message)
                db.session.commit()

    def unpraise(self, post):
        if self.is_praising(post):
            praise = post.praises.filter_by(post_id=post.id, author_id=self.id).first()
            message = Message.query.filter_by(refer_id=praise.id, type=1).first()
            if message is not None:
                post.score -= 1
                db.session.add(post)
                db.session.delete(message)
            db.session.delete(praise)
            db.session.commit()

    def delete_comment(self, comment):
        Message.query.filter(and_(Message.type == 3, Message.refer_id == comment.id)).delete()
        Report.query.filter(and_(Report.refer_id == comment.id, Report.type == 2)).delete()
        db.session.delete(comment)
        db.session.commit()

    def delete_post(self, post):
        for comment in post.comments.all():
            db.session.delete(comment)
        for praise in post.praises.all():
            db.session.delete(praise)
        Collection.query.filter(Collection.post_id == post.id).delete()
        Message.query.filter(Message.post_id == post.id).delete()
        Report.query.filter(and_(Report.refer_id == post.id, Report.type == 1)).delete()
        for image in Image.query.filter(Image.post_id == post.id).all():
            path = image.url_path.replace('_uploads/photos', 'static/images')
            path = path.replace('http://localhost:5000', basedir + '/app')
            os.remove(path)
            db.session.delete(image)
        db.session.delete(post)
        db.session.commit()

    def is_invalid(self):
        if self.valid_time is None:
            return False
        return self.valid_time > datetime.now()

    def __repr__(self):
        return "User <%s>" % self.username


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(140), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_published = db.Column(db.Boolean, default=True)
    score = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    praises = db.relationship('Praise', backref='post', lazy='dynamic')

    image = db.relationship('Image', uselist=False, backref='post')

    def __repr__(self):
        return "Post <%s> %s" %(self.title, self.timestamp)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), default=None)
    previous_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), default=None)
    next_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), default=None)
    body = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    replied_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=None)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    author = db.relationship('User', foreign_keys=[author_id])
    replied_user = db.relationship('User', foreign_keys=[replied_user_id])

    def get_previous_comment(self):
        if self.previous_comment_id is None:
            return None
        return Comment.query.get(self.previous_comment_id)

    def get_next_comment(self):
        if self.next_comment_id is None:
            return None
        return Comment.query.get(self.next_comment_id)

    def __repr__(self):
        if self.comment_id:
            return self.author.username + " reply " + User.query.get(self.replied_user_id).username \
                + ": " + self.body
        else:
            return self.author.username + " comment post: " + Post.query.get(self.post_id).title


class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    post = db.relationship('Post', uselist=False)

    def __repr__(self):
        return 'Collection: ' + str(self.id)


class Praise(db.Model):
    __tablename__ = 'praises'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return 'Praise: ' + User.query.get(self.author_id).username


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    receive_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # this is refer to the source of message, 1 praise, 2 collection, 3 comment and reply,
    # 4 follow, 5 the followeds's post, 6 reportion
    refer_id = db.Column(db.Integer)
    type = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    readed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    post = db.relationship('Post', uselist=False)

    def __repr__(self):
        return 'Message: ' + str(self.id)


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), default=None)
    url_path = db.Column(db.String)

    def __repr__(self):
        return self.url_path


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))
    name = db.Column(db.String(10))
    url_path = db.Column(db.String)

    def __repr__(self):
        return 'photo: ' + self.album.name + "'s " + self.name


class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String)

    photos = db.relationship('Photo', backref='album', lazy='dynamic')

    def __repr__(self):
        return self.author.username + "'s album:" + self.name


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    refer_id = db.Column(db.Integer)
    # 1 refer to post, 2 refer to comment or reply
    type = db.Column(db.Integer)
    dealed = db.Column(db.Boolean, default=False)
    result = db.Column(db.Integer, default=None)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    author = db.relationship('User')

    def __repr__(self):
        return 'Report: ' + str(self.id)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

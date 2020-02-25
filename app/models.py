from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2._compat import text_type
from datetime import datetime
from hashlib import md5
import coverpy as coverpy

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

followers_artist_table = db.Table('artist_followers',
    db.Column('follower_user', db.Integer, db.ForeignKey('user.uid')),
    db.Column('followed_artist', db.Integer, db.ForeignKey('artist.id')))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.uid')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.uid'))
)

class User(UserMixin, db.Model):

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    info = db.Column(db.String(30))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', cascade="all,delete", lazy='dynamic', foreign_keys='Post.user_id')
    my_posts = db.relationship('Post', backref='mine', cascade="all, delete", lazy='dynamic', foreign_keys='Post.my_id')
    playlists = db.relationship('Playlist', backref='playlists', lazy='dynamic')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == uid),
        secondaryjoin=(followers.c.followed_id == uid),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.uid).count() > 0


# OVERRIDE METHOD
    def get_id(self):
        try:
            return text_type(self.uid)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    my_id = db.Column(db.Integer, db.ForeignKey('user.uid'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    genre = db.Column(db.String(140))
    songs = db.relationship("Song", backref="album")
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

    def get_artwork(self):
        try:
            retrieve = coverpy.CoverPy()
            limit = 1
            result = retrieve.get_cover(self.name, limit)

            return result.artwork(200)

        except coverpy.exceptions.NoResultsException:
            print("Nothing found")
            return "about:blank"

    def __repr__(self):
        return '<Album {}>'.format(self.name)

# table for Playlist <-> Song
playlist_song_table = db.Table('playlist_song',
    db.Column('Playlist_ID', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('Song_ID', db.Integer, db.ForeignKey('song.id')))



class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    rating = db.Column(db.Float, default=2.5)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))

    def rated(self, rating):
        self.rating = rating
        return self

    def __repr__(self):
        return '<Song {}>'.format(self.name)

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    likes = db.Column(db.Integer, default=0)
    albums = db.relationship("Album", backref="artist")

    followers = db.relationship('User', secondary=followers_artist_table, backref='following')

    def __repr__(self):
        return '<Artist {}>'.format(self.name)

    def add_follower(self, user):
        self.followers.append(user)
        self.likes = self.likes + 1
        db.session.commit()

    def remove_follower(self, user):
        self.followers.remove(user)
        self.likes = self.likes - 1
        db.session.commit()

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    likes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))

    songs = db.relationship('Song', secondary=playlist_song_table, backref='playlists')

    def add_song(self, song):
        self.songs.append(song)


    def remove_song(self, song):
        self.songs.remove(song)


    def __repr__(self):
        return '<Playlist {}>'.format(self.name)

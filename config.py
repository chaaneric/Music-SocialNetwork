import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cs304'

    os.environ['SPOTIPY_CLIENT_ID'] = '<INSERT SPOTIFY CLIENT ID>'
    os.environ['SPOTIPY_CLIENT_SECRET'] = '<INSERT SPOTIFY SECRET>'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


from app import app, db
from app.models import User, Post, Album, Song, Artist, Playlist

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User':User, 'Post': Post, 'Album': Album, 'Song': Song, 'Artist': Artist, 'Playlist': Playlist}

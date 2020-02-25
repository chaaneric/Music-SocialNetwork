from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Artist, Album, Post, Playlist, Song
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, PlaylistForm, AddSongForm, RatingForm
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sqlalchemy import func
from sqlalchemy.sql import select
from random import *

@app.route('/')

@app.route('/index')
def index():
	a = len(Album.query.all())
	art = len(Artist.query.all())
	s = len(Song.query.all())
	user_count = len(User.query.all())
	u = None
	if user_count != 0:
		random_number = randint(1, user_count)

		u = User.query.filter_by(uid=random_number).first().username

	return render_template('index.html', albums=a,songs=s,artists=art,username=u, user_count=user_count, title='Home')

@app.route('/artist/top')
@login_required
def ranking():
	most_likes = db.session.query(func.max(Artist.likes)).scalar()
	pops = Artist.query.filter(Artist.likes == most_likes).all()
	return render_template('billboard.html', title='Ranking', pops=pops, most_likes=most_likes)

def averages():
	albums = Album.query.join(Song, Song.album_id==Album.id)
	albums = albums.with_entities(func.avg(Song.rating), Album.genre)
	albums = albums.group_by(Album.genre)
	print(albums)
	for album in albums.all():
		print(str(album[0])+album[1])

	avg_ratings = {}

	# for alb in albums.all():
	# 	sia = Song.query.filter_by(album_id=alb.id)
	# 	rating = sia.with_entities(func.avg(Song.rating)).scalar()
	# 	avg_ratings[alb.genre] = rating
	# 	print(alb.genre)
	# 	print("                    album name! " + alb.name)

	return albums

@app.route('/best')
@login_required
def best_genre():
	avg = averages()
	avg = avg.order_by(func.avg(Song.rating).desc())

	best = avg[0]

	# best = max(avg_ratings, key=lambda i: avg_ratings[i])
	#
	# to_flash = best + " with a rating of " + str(avg_ratings[best])

	to_flash = best[1] + " with a rating of " + str(best[0])
	flash(to_flash)
	return redirect(url_for('ranking'))

@app.route('/worst')
@login_required
def worst_genre():
	# avg_ratings = averages()
	# worst = min(avg_ratings, key=lambda i: avg_ratings[i])
	# to_flash = worst + " with a rating of " + str(avg_ratings[worst])
	# flash(to_flash)
	# return redirect(url_for('ranking'))

	avg = averages()
	avg = avg.order_by(func.avg(Song.rating).asc())

	best = avg[0]

	# best = max(avg_ratings, key=lambda i: avg_ratings[i])
	#
	# to_flash = best + " with a rating of " + str(avg_ratings[best])

	to_flash = best[1] + " with a rating of " + str(best[0])
	flash(to_flash)
	return redirect(url_for('ranking'))


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.now()
		db.session.commit()

@app.route('/search', methods = ['GET', 'POST'])
def search():
	search = request.args.get("search")
	artist_results = Artist.query.filter(Artist.name.contains(search)).all()
	album_results = Album.query.filter(Album.name.contains(search)).all()
	song_results = Song.query.filter(Song.name.contains(search)).all()
	return render_template('search/search_results.html', artist_results=artist_results, album_results=album_results, song_results=song_results)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')


		flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
		return redirect(next_page)

	return render_template('login/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
			last_name=form.last_name.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Registered User {}'.format(form.username.data))
		return redirect(url_for('index'))

	return render_template('login/register.html', form=form)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
	form = PostForm()
	user = User.query.filter_by(username=username).first_or_404()
	playlists = user.playlists.all()

	if form.validate_on_submit():
		post = Post(body=form.body.data, author=current_user, mine=user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('user', username=user.username))

	date = user.last_seen

	date = date.strftime("%Y-%m-%d %H:%M:%S")

	posts = user.my_posts.all()
	return render_template('profile/profile.html', user=user, posts=posts, form=form, playlists=playlists, date=date)

@app.route('/delete/<username>/<post_id>', methods=['POST'])
@login_required
def delete(username, post_id):
	p = Post.query.filter_by(id=post_id).first()
	if p != None:
		db.session.delete(p)
		db.session.commit()
		return redirect(url_for('user', username=username))

@app.route('/delete/playlist/<playlist_id>', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
	p = Playlist.query.filter_by(id=playlist_id).first()
	if p != None:
		db.session.delete(p)
		db.session.commit()
		return redirect(url_for('playlists'))



@app.route('/album/<id>', methods=['GET','POST'])
def album(id):
	album = Album.query.filter_by(id=id).first_or_404()
	form = AddSongForm()
	playlists = current_user.playlists
	form.playlist.choices = [(row.id, row.name) for row in playlists]
	name = album.name
	songs = album.songs
	artist = album.artist

	rate_form = RatingForm()
	if rate_form.validate_on_submit():
		print("AHHHHHHHHHHH")
		song = Song.query.filter_by(id=rate_form.id.data).first_or_404()
		s = song.rated(rating=rate_form.rating.data)
		db.session.add(s)
		db.session.commit()
		flash('You rated ' + song.name + '!')

	if form.validate_on_submit():
		playlist_id = form.playlist.data
		song_id = form.song.data

		playlist = Playlist.query.filter_by(id=playlist_id).first()
		song = Song.query.filter_by(id=song_id).first()

		playlist.add_song(song)

		db.session.commit()
		redirect(url_for('album', id=id))

	album_link = 'blank'
	spotifyURI = 'blank'

	# Generate req to spotipy

	client_credentials_manager = SpotifyClientCredentials()
	sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

	results = sp.search(q='album:' + name, type='album')

	# get correct album that maps to artist


	results = results['albums']['items'] # hardcoded for now if i have time ill do more checks

	if len(results) != 0:

		results = results[0]

		spotifyURI = results['uri']

		album_link = "https://song.link/embed?url=" + spotifyURI



	return render_template('album.html', rate_form=rate_form,
	form=form,album_link=album_link, album=album, name=name, songs=songs, artist=artist, playlists = playlists)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
		form.email.data = current_user.email
	return render_template('profile/edit_profile.html', form=form)

@app.route('/artist/<id>')
@login_required
def artist(id):
	artist = Artist.query.filter_by(id=id).first_or_404()
	albums = artist.albums
	return render_template('artist/artist.html', artist = artist, albums = albums)

@app.route('/playlists', methods=['GET', 'POST'])
@login_required
def playlists():
	form = PlaylistForm()
	playlists = current_user.playlists.all()

	if form.validate_on_submit():
		playlist_name = form.name.data
		p = Playlist(name=playlist_name, playlists=current_user)
		db.session.add(p)
		db.session.commit()
		return redirect(url_for('playlists'))


	return render_template('playlist/playlist.html',form=form, playlists=playlists)

@app.route('/playlist/<playlist_id>')
@login_required
def playlist(playlist_id):
	p = Playlist.query.filter_by(id=playlist_id).first_or_404()
	user = p.playlists
	songs = p.songs

	return render_template('playlist/playlist_details.html', playlist=p, songs=songs, user=user)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/artist/<id>/like')
@login_required
def like(id):
	artist = Artist.query.filter_by(id=id).first_or_404()
	user = current_user
	if artist is None:
		flash('Artist %s not found.' % id)
		return redirect(url_for('index'))

	artist.add_follower(user)

	flash('You followed ' + artist.name + '!')
	return redirect(url_for('artist', id=id))
@app.route('/artist/<id>/dislike')
@login_required
def dislike(id):
	artist = Artist.query.filter_by(id=id).first_or_404()
	user = current_user
	if artist is None:
		flash('Artist %s not found.' % id)
		return redirect(url_for('index'))

	artist.remove_follower(user)

	flash('You unfollowed ' + artist.name + '!')
	return redirect(url_for('artist', id=id))

@app.route('/delete_song_playlist/<playlist_id>/<song_id>', methods=['GET','POST'])
@login_required
def delete_song_playlist(playlist_id, song_id):

	playlist = Playlist.query.filter_by(id=playlist_id).first()
	song = Song.query.filter_by(id=song_id).first()

	playlist.remove_song(song)
	db.session.commit()

	return redirect(url_for('playlist', playlist_id=playlist_id))

@app.route('/follow/<user_id>', methods=['GET', 'POST'])
@login_required
def follow(user_id):
	user = User.query.filter_by(uid=user_id).first()

	current_user.follow(user)

	return redirect(url_for('user', username=user.username))


@app.route('/unfollow/<user_id>', methods=['GET', 'POST'])
@login_required
def unfollow(user_id):
	user = User.query.filter_by(uid=user_id).first()

	current_user.unfollow(user)

	return redirect(url_for('user', username=user.username))



@app.route('/delete/user/<user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
	user = User.query.filter_by(uid=user_id).first()

	db.session.delete(user)
	db.session.commit()

	return redirect(url_for('index'))

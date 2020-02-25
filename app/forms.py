from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField, TextField, DecimalField
from wtforms.validators import DataRequired, ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')



	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username is taken, please use a different one')

	def validate_email(self, email):
		user= User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email is already taken, use a different one')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[Email()])
	about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')

class PostForm(FlaskForm):
	body = TextAreaField('Write a Message!', validators=[DataRequired(), Length(max=200)])
	submit = SubmitField('Post!')

class PlaylistForm(FlaskForm):
	name = StringField('Playlist Name', validators=[DataRequired()])
	submit = SubmitField('Make Playlist')

class AddSongForm(FlaskForm):
	song = TextField("Song")
	playlist = SelectField('Choose Playlist..', coerce=int,validators=[DataRequired()], id='select_playlist')
	submit = SubmitField('Select')

class RatingForm(FlaskForm):
    id = TextField("Song ID")
    rating = DecimalField("Rate from 0 to 5", validators=[DataRequired()])
    submit = SubmitField("Rate!")

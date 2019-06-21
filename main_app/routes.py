from flask import render_template, flash, redirect, url_for, request
from main_app import app, db
from main_app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from main_app.models import User
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@app.route("/")
@app.route("/home")
@login_required
def home_page():
	title = "Home"

	posts = [
		{
			'author': {'username': 'reece02'},
			'body': "My first ever post!!!"
		},
		{
			'author': {'username': 'nita01'},
			'body': "I like to lay by the seaside..."
		}
	]

	return render_template("index.html", title=title, posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
	title = "Sign In"

	if current_user.is_authenticated:
		return redirect(url_for('home_page'))
	

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		
		if user is None or not user.check_password(form.password.data):
			flash("Invalid username or password!")
			return redirect(url_for('login_page'))

		login_user(user, remember=form.remember_me.data)
		
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != "":
			next_page = url_for('home_page')

		return redirect(next_page)


	return render_template("login.html", title=title, form=form)


@app.route("/logout")
def logout_page():
	logout_user()
	return redirect(url_for('home_page'))


@app.route("/register", methods=['GET', 'POST'])
def register_page():
	title = "Register"

	if current_user.is_authenticated:
		return redirect(url_for('home_page'))

	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now registered!!!')

		return redirect(url_for('login_page'))

	return render_template('register.html', title=title, form=form)


@app.route("/user/<username>")
@login_required
def user_page(username):
	user = User.query.filter_by(username=username).first_or_404()
	title = user.username

	posts = [
		{'author': user, 'body': "First post test #1"},
		{'author': user, 'body': "First post test #2"}
	]

	return render_template("user.html", title=title, user=user, posts=posts)


@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile_page():
	title = "Edit Profile"
	form = EditProfileForm()

	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Details updated successfully!!')
		return redirect(url_for('edit_profile_page'))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me

	return render_template('edit_profile.html', title=title, form=form)





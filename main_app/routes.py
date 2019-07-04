from flask import render_template, flash, redirect, url_for, request
from main_app import app, db
from main_app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from main_app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home_page():
	title = "Home"
	form = PostForm()

	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('home_page'))

	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('home_page', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('home_page', page=posts.prev_num) \
		if posts.has_prev else None

	return render_template("index.html", title=title, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


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
	page = request.args.get('page', 1, type=int)

	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user_page', username=user.username, page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('user_page', username=user.username, page=posts.prev_num) \
		if posts.has_prev else None

	return render_template("user.html", title=title, user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile_page():
	title = "Edit Profile"
	form = EditProfileForm(current_user.username)

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


@app.route("/follow/<username>")
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found!'.format(username))
		return redirect(url_for('home_page'))
	if user == current_user:
		flash("You can't follow yourself...")
		return redirect(url_for('home_page'))

	current_user.follow(user)
	db.session.commit()
	flash("You're now following {}!".format(username))
	return redirect(url_for('user_page', username=username))


@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash("User {} not found...".format(username))
		return redirect(url_for('home_page'))
	if user == current_user:
		flash("You can't unfollow yourself...")
		return redirect(url_for('home_page'))

	current_user.unfollow(user)
	db.session.commit()
	flash("You're now not following {}!".format(username))
	return redirect(url_for('user_page', username=username))


@app.route("/explore")
@login_required
def explore():
	title="Explore"

	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) \
		if posts.has_prev else None

	return render_template("index.html", title=title, posts=posts.items, next_url=next_url, prev_url=prev_url)

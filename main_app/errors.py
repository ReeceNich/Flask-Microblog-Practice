from flask import render_template
from main_app import app, db


@app.errorhandler(404)
def not_found_error_page(error):
	title = "404 - Page not Found!"
	return render_template("404.html", title=title), 404


@app.errorhandler(500)
def internal_error(error):
	title = "500 - Internal Error!"
	db.session.rollback()
	return render_template("500.html", title=title), 500
from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import CSRFProtectForm, RegisterForm, LoginForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
  "postgresql://otherjoel:hello@13.57.9.123/otherjoel")
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.get("/")
def redirect_to_register():
    """Redirect to register page."""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.pwd.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(name, pwd, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        # on successful registration, redirect to secret page
        return redirect(f"/users/{user.username}")

    else:
        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.pwd.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]


@app.get("/users/<username>")
def show_user_page(username):
    """
    Display a template the shows information about that user.

    Only logged-in users can see this page.
    """

    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    form = CSRFProtectForm()

    return render_template("user.html", user=user, form=form)

@app.post("/logout")
def logout():
    """Log out user and redirect to root"""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop("username", None)
    else:
        raise Unauthorized()

    return redirect("/")

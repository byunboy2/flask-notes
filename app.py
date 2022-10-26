from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Note
from forms import CSRFProtectForm, RegisterForm, LoginForm, NoteForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = (
# "postgresql://otherjoel:hello@13.57.9.123/otherjoel")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
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
    notes = Note.query.filter_by(author=username).all()
    form = CSRFProtectForm()

    return render_template("user.html", user=user, form=form, notes=notes)


@app.post("/logout")
def logout():
    """Log out user and redirect to root"""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop("username", None)
        return redirect("/")
    else:
        raise Unauthorized()


@app.post("/users/<username>/delete")
def delete_user(username):
    """Delete user from database and their notes, and redirect to root"""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    form = CSRFProtectForm()

    if form.validate_on_submit():
        Note.query.filter_by(username=username).delete()
        User.query.get(username).delete() # add commit, be weary of naming
        session.pop("username", None)
        return redirect("/")
    else:
        raise Unauthorized()


@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def handle_notes(username):
    """Display add note form, and process it"""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    form = NoteForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        note = Note(title=title, content=content, author=username)
        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{note.author}")

    else:
        return render_template("notes.html", form=form)


@app.route("/notes/<int:note_id>/update", methods=["GET", "POST"])
def update_notes(note_id):
    """Display edit note form and update note"""

    note = Note.query.get(note_id) # or 404
    if "username" not in session or note.author != session["username"]:
        raise Unauthorized()

    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{note.author}")

    else:
        return render_template("notes.html", form=form)


@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    """Delete note"""

    note = Note.query.get(note_id)

    if "username" not in session or note.author != session["username"]:
        raise Unauthorized()

    form = CSRFProtectForm()

    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()
        return redirect(f"/users/{note.author}")

    else:
        raise Unauthorized()

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    """Form for user registration"""

    username = StringField("Username",
                           validators=[InputRequired(), Length(max=20)]
                           )
    pwd = PasswordField("Password",
                        validators=[InputRequired(), Length(max=100)])

    email = EmailField("Email",
                       validators=[InputRequired(), Length(max=50)])

    first_name = StringField("First Name",
                             validators=[InputRequired(), Length(max=30)])

    last_name = StringField("Last Name",
                            validators=[InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    """Form for user login"""

    username = StringField("Username",
                           validators=[InputRequired(), Length(max=20)]
                           )
    pwd = PasswordField("Password",
                        validators=[InputRequired(), Length(max=100)])


class NoteForm(FlaskForm):
    """Form for new note"""

    title = StringField("Title",
                        validators=[InputRequired(), Length(max=100)])

    content = TextAreaField("Content",
                            validators=[InputRequired()])


class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""

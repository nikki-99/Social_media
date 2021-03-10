
from flask_wtf import FlaskForm

from wtforms import StringField,SubmitField, TextAreaField
from wtforms.validators import DataRequired



class CommentForm(FlaskForm):
    commented_user = StringField('Give your Name', validators=[DataRequired()])
    body = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField("Post")


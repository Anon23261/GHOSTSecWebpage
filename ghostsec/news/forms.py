from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[DataRequired(), Length(max=500)])
    category = SelectField('Category', choices=[
        ('news', 'Cybersecurity News'),
        ('tutorials', 'Tutorials & Guides'),
        ('tools', 'Tool Reviews'),
        ('research', 'Research & Analysis'),
        ('events', 'Events & Conferences')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma separated)', validators=[DataRequired()])
    image = FileField('Article Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Publish Article')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    parent_id = HiddenField()  # For nested comments
    submit = SubmitField('Post Comment')

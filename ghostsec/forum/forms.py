from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', 
                         choices=[('general', 'General Discussion'),
                                ('kali', 'Kali Linux'),
                                ('python', 'Python Security'),
                                ('pentesting', 'Penetration Testing'),
                                ('ctf', 'CTF Discussion'),
                                ('tools', 'Security Tools'),
                                ('help', 'Help & Support')],
                         validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')

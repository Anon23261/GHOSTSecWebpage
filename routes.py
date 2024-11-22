"""
GhostSec application routes.
"""
from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from . import db, bcrypt
from .models import User, ForumPost, ForumComment, Achievement
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_routes(app):
    @app.route('/')
    @app.route('/home')
    def home():
        posts = ForumPost.query.order_by(ForumPost.date_posted.desc()).limit(5).all()
        return render_template('home.html', title='Home', posts=posts)

    @app.route('/about')
    def about():
        return render_template('about.html', title='About')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form.get('email')).first()
            if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
                login_user(user, remember=request.form.get('remember'))
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            flash('Login unsuccessful. Please check email and password', 'danger')
                
        return render_template('login.html', title='Login')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            if User.query.filter_by(email=request.form.get('email')).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
                
            if User.query.filter_by(username=request.form.get('username')).first():
                flash('Username already taken', 'danger')
                return redirect(url_for('register'))
                
            hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            user = User(
                username=request.form.get('username'),
                email=request.form.get('email'),
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        return render_template('register.html', title='Register')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/profile')
    @login_required
    def profile():
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        posts = ForumPost.query.filter_by(author_id=current_user.id).order_by(ForumPost.date_posted.desc()).all()
        return render_template('profile.html', title='Profile', 
                             achievements=achievements, posts=posts)

    @app.route('/forum')
    def forum():
        page = request.args.get('page', 1, type=int)
        posts = ForumPost.query.order_by(ForumPost.date_posted.desc()).paginate(page=page, per_page=10)
        return render_template('forum.html', title='Forum', posts=posts)

    @app.route('/forum/post/new', methods=['GET', 'POST'])
    @login_required
    def new_post():
        if request.method == 'POST':
            post = ForumPost(
                title=request.form.get('title'),
                content=request.form.get('content'),
                category=request.form.get('category'),
                author_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('forum'))
        return render_template('create_post.html', title='New Post')

    @app.route('/forum/post/<int:post_id>')
    def post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        post.views += 1
        db.session.commit()
        return render_template('post.html', title=post.title, post=post)

    @app.route('/forum/post/<int:post_id>/comment', methods=['POST'])
    @login_required
    def comment_post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        comment = ForumComment(
            content=request.form.get('content'),
            author_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('post', post_id=post.id))

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

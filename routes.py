"""
GhostSec application routes.
"""
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from __init__ import db, bcrypt
from models import User
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
        return render_template('home.html', title='Home')

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
                login_user(user)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            flash('Login unsuccessful. Please check email and password', 'danger')
                
        return render_template('login.html', title='Login')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            user = User(
                username=request.form.get('username'),
                email=request.form.get('email'),
                password=hashed_password,
                created_at=datetime.utcnow()
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

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', title='Dashboard')

    # API routes
    @app.route('/api/user', methods=['GET'])
    @login_required
    def get_user():
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat()
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

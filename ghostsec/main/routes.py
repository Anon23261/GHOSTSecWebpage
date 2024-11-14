from flask import render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from . import main

@main.route('/')
@main.route('/home')
def home():
    try:
        return render_template('home.html', title='Home')
    except Exception as e:
        current_app.logger.error(f"Error in home route: {str(e)}")
        return "An error occurred", 500

@main.route('/about')
def about():
    try:
        return render_template('about.html', title='About')
    except Exception as e:
        current_app.logger.error(f"Error in about route: {str(e)}")
        return "An error occurred", 500

@main.route('/dashboard')
@login_required
def dashboard():
    try:
        return render_template('dashboard.html', title='Dashboard')
    except Exception as e:
        current_app.logger.error(f"Error in dashboard route: {str(e)}")
        return "An error occurred", 500

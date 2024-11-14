from flask import Blueprint, flash, redirect, url_for, current_app
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import current_user, login_user
from sqlalchemy.orm.exc import NoResultFound
from ghostsec import db
from ghostsec.models import User
import os

oauth = Blueprint('oauth', __name__)

# GitHub OAuth setup
github_blueprint = make_github_blueprint(
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    scope=['user:email']
)

# Google OAuth setup
google_blueprint = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    scope=['profile', 'email']
)

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with GitHub.", "error")
        return False

    resp = github.get("/user")
    if not resp.ok:
        flash("Failed to fetch user info from GitHub.", "error")
        return False

    github_info = resp.json()
    github_user_id = str(github_info["id"])

    # Get user email
    emails = github.get("/user/emails").json()
    primary_email = next(email["email"] for email in emails if email["primary"])

    # Find this OAuth token in the database, or create it
    try:
        user = User.query.filter_by(github_id=github_user_id).first()
        if not user:
            user = User.query.filter_by(email=primary_email).first()
            if user:
                # User exists but GitHub not linked
                user.github_id = github_user_id
            else:
                # Create a new user
                user = User(
                    username=github_info["login"],
                    email=primary_email,
                    github_id=github_user_id,
                    is_verified=True
                )
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with GitHub.", "success")
        return False

    except Exception as e:
        current_app.logger.error(f"Error during GitHub login: {str(e)}")
        flash("An error occurred during GitHub login.", "error")
        return False

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", "error")
        return False

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return False

    google_info = resp.json()
    google_user_id = google_info["id"]

    # Find this OAuth token in the database, or create it
    try:
        user = User.query.filter_by(google_id=google_user_id).first()
        if not user:
            user = User.query.filter_by(email=google_info["email"]).first()
            if user:
                # User exists but Google not linked
                user.google_id = google_user_id
            else:
                # Create a new user
                user = User(
                    username=google_info["email"].split('@')[0],
                    email=google_info["email"],
                    google_id=google_user_id,
                    is_verified=True
                )
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with Google.", "success")
        return False

    except Exception as e:
        current_app.logger.error(f"Error during Google login: {str(e)}")
        flash("An error occurred during Google login.", "error")
        return False

@oauth_error.connect_via(github_blueprint)
def github_error(blueprint, error, error_description=None, error_uri=None):
    msg = f"OAuth error from GitHub! error={error}"
    if error_description:
        msg = f"{msg} description={error_description}"
    if error_uri:
        msg = f"{msg} uri={error_uri}"
    current_app.logger.error(msg)
    flash("Failed to sign in with GitHub.", "error")

@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, error, error_description=None, error_uri=None):
    msg = f"OAuth error from Google! error={error}"
    if error_description:
        msg = f"{msg} description={error_description}"
    if error_uri:
        msg = f"{msg} uri={error_uri}"
    current_app.logger.error(msg)
    flash("Failed to sign in with Google.", "error")

from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from ghostsec import db, bcrypt
from ghostsec.models import User
from ghostsec.auth.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             RequestResetForm, ResetPasswordForm, TwoFactorSetupForm,
                             TwoFactorForm)
from ghostsec.utils import save_picture, send_reset_email, generate_totp_uri
import pyotp
import qrcode
import io
import base64

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                birthday=form.birthday.data,
                country=form.country.data
            )
            # Encrypt sensitive data
            user.set_phone_number(form.phone.data)
            
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in', 'success')
            return redirect(url_for('auth.login'))
        return render_template('auth/register.html', title='Register', form=form)
    except Exception as e:
        flash('An error occurred during registration. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                if user.two_factor_enabled:
                    session['user_id'] = user.id
                    return redirect(url_for('auth.two_factor_auth'))
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login unsuccessful. Please check email and password', 'danger')
        return render_template('auth/new_login.html', title='Login', form=form)
    except Exception as e:
        flash('An error occurred during login. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/two_factor")
def two_factor_auth():
    try:
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        form = TwoFactorForm()
        return render_template('auth/two_factor.html', form=form)
    except Exception as e:
        flash('An error occurred during two-factor authentication. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/two_factor/verify", methods=['POST'])
def two_factor_verify():
    try:
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        form = TwoFactorForm()
        if form.validate_on_submit():
            user = User.query.get(session['user_id'])
            totp = pyotp.TOTP(user.two_factor_secret)
            
            if totp.verify(form.token.data):
                login_user(user)
                session.pop('user_id', None)
                return redirect(url_for('main.home'))
            
            flash('Invalid authentication code', 'danger')
        return redirect(url_for('auth.two_factor_auth'))
    except Exception as e:
        flash('An error occurred during two-factor verification. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/two_factor/setup", methods=['GET', 'POST'])
@login_required
def two_factor_setup():
    try:
        if current_user.two_factor_enabled:
            flash('Two-factor authentication is already enabled', 'info')
            return redirect(url_for('auth.account'))
        
        form = TwoFactorSetupForm()
        
        if request.method == 'GET':
            secret = pyotp.random_base32()
            session['2fa_secret'] = secret
            totp = pyotp.TOTP(secret)
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(generate_totp_uri(current_user.email, secret))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR code to base64 for display
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_code = base64.b64encode(buffered.getvalue()).decode()
            
            return render_template('auth/two_factor_setup.html', 
                                 form=form, 
                                 qr_code=qr_code,
                                 secret=secret)
        
        if form.validate_on_submit():
            secret = session.get('2fa_secret')
            totp = pyotp.TOTP(secret)
            
            if totp.verify(form.token.data):
                current_user.two_factor_secret = secret
                current_user.two_factor_enabled = True
                db.session.commit()
                session.pop('2fa_secret', None)
                flash('Two-factor authentication has been enabled', 'success')
                return redirect(url_for('auth.account'))
            
            flash('Invalid authentication code', 'danger')
        return render_template('auth/two_factor_setup.html', form=form)
    except Exception as e:
        flash('An error occurred during two-factor setup. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/logout")
def logout():
    try:
        logout_user()
        return redirect(url_for('main.home'))
    except Exception as e:
        flash('An error occurred during logout. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    try:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data, 'profile_pics')
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.birthday = form.birthday.data
            current_user.country = form.country.data
            current_user.set_phone_number(form.phone.data)
            
            # Update social media
            current_user.twitter = form.twitter.data
            current_user.linkedin = form.linkedin.data
            current_user.github = form.github.data
            
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('auth.account'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.first_name.data = current_user.first_name
            form.last_name.data = current_user.last_name
            form.birthday.data = current_user.birthday
            form.country.data = current_user.country
            form.phone.data = current_user.get_phone_number()
            form.twitter.data = current_user.twitter
            form.linkedin.data = current_user.linkedin
            form.github.data = current_user.github
        return render_template('auth/account.html', title='Account', form=form)
    except Exception as e:
        flash('An error occurred during account update. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = RequestResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('auth.login'))
        return render_template('auth/reset_request.html', title='Reset Password', form=form)
    except Exception as e:
        flash('An error occurred during password reset request. Please try again.', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        user = User.verify_reset_token(token)
        if user is None:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('auth.reset_request'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))
        return render_template('auth/reset_token.html', title='Reset Password', form=form)
    except Exception as e:
        flash('An error occurred during password reset. Please try again.', 'danger')
        return redirect(url_for('main.home'))

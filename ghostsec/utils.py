import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from ghostsec import mail
import pyotp

def save_picture(form_picture, folder):
    """Save profile or item pictures with random name"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)

    # Resize image
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # Save picture
    i.save(picture_path)
    return picture_fn

def send_reset_email(user):
    """Send password reset email"""
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@ghostsec.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def generate_totp_uri(email, secret):
    """Generate TOTP URI for QR code"""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name="GHOSTSec"
    )

def encrypt_file(file_path, key):
    """Encrypt a file using Fernet"""
    from cryptography.fernet import Fernet
    
    if not os.path.exists(file_path):
        return False
        
    f = Fernet(key)
    
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    encrypted_data = f.encrypt(file_data)
    
    with open(file_path + '.encrypted', 'wb') as file:
        file.write(encrypted_data)
        
    return True

def decrypt_file(file_path, key):
    """Decrypt a file using Fernet"""
    from cryptography.fernet import Fernet
    
    if not os.path.exists(file_path):
        return False
        
    f = Fernet(key)
    
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
    
    try:
        decrypted_data = f.decrypt(encrypted_data)
        
        with open(file_path[:-10], 'wb') as file:
            file.write(decrypted_data)
            
        return True
    except:
        return False

def sanitize_filename(filename):
    """Sanitize a filename to prevent directory traversal"""
    return ''.join(c for c in filename if c.isalnum() or c in '._- ')

def is_safe_file_type(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'md'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

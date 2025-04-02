from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail
from flask import url_for

def send_password_reset_email(user):
    token = user.reset_token
    msg = Message('Password Reset Request',
                 sender=current_app.config['MAIL_DEFAULT_SENDER'],
                 recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email.
'''
    msg.html = render_template('auth/email/reset_password.html', 
                             user=user, token=token)
    mail.send(msg)
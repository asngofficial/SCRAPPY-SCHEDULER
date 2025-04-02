from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user
from werkzeug.urls import url_parse
from .forms import LoginForm
from app.models import User
from . import bp
from app.extensions import db
from datetime import datetime
from app.email import send_password_reset_email 
from .forms import LoginForm, RegistrationForm  # Add RegistrationForm to imports
from flask_login import logout_user, login_required

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    form = RegistrationForm()  # You'll need to create this form
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate a reset token (expires in 1 hour)
            reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send email (we'll implement this next)
            send_password_reset_email(user)
            
            flash('Check your email for instructions to reset your password', 'info')
            return redirect(url_for('auth.login'))
        
        flash('Email not found', 'warning')
    
    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        logout_user()
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_expires < datetime.utcnow():
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        flash('Your password has been reset. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('home.index')
                return redirect(next_page)
            
            flash('Invalid email or password', 'danger')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)
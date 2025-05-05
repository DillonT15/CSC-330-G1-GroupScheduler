from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User
from .forms import LoginForm, RegisterForm, EditProfileForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        hashed_password = generate_password_hash(form.password.data)
        # Create and store the new user
        user = User(email=email, password=hashed_password, is_verified=True)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))



#New Placeholder routes created for each functionality on main page
@bp.route('/post-listing')
def post_listing():
    return render_template('post_listing.html')

@bp.route('/browse')
def browse_listings():
    return render_template('browse_listings.html')

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.major = form.major.data

        # Handle optional password change
        if form.new_password.data:
            current_user.password = generate_password_hash(form.new_password.data)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.edit_profile'))

    return render_template('edit_profile.html', form=form)

@bp.route('/notifications')
def view_notifications():
    return render_template('notifications.html')

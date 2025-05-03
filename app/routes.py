from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import * # Import all models from models.py
from .forms import * # Import all forms from forms.py

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


@bp.route('/post-listing', methods=['GET','POST'])
@login_required
def post_listing():
    form = CreateStudyGroupForm()
    if form.validate_on_submit():
        group = StudyGroup(
            title       = form.title.data,
            subject     = form.subject.data,
            course      = form.course.data,
            description = form.description.data,
            time        = form.time.data,
            tags        = form.tags.data,
            owner       = current_user
        )
        db.session.add(group)
        db.session.commit()
        flash('Study group created!', 'success')
        return redirect(url_for('main.browse_listings'))
    return render_template('post_listing.html', form=form)


@bp.route('/browse')
@login_required
def browse_listings():
    # pull all groups, most recent first
    study_groups = StudyGroup.query.order_by(StudyGroup.created_at.desc()).all()
    return render_template('browse_listings.html',
                           study_groups=study_groups)

#New Placeholder routes created for each functionality on main page

@bp.route('/edit-profile')
def edit_profile():
    return render_template('edit_profile.html')

@bp.route('/notifications')
def view_notifications():
    return render_template('notifications.html')

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import * # Import all models from models.py
from .forms import * # Import all forms from forms.py

bp = Blueprint('main', __name__)

def create_notification(group_id, message):
    """Create notifications for all members of a group except current user"""
    group = StudyGroup.query.get(group_id)
    if group:
        for member in group.members:
            if member.id != current_user.id:  # Don't notify the current user
                notification = Notification(
                    user_id=member.id,
                    message=message,
                    group_id=group_id
                )
                db.session.add(notification)
        db.session.commit()

#Defaults to login when not logged in, defaults to main listings when logged in
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.browse_listings'))
    return redirect(url_for('main.login'))

#New route /home created for top left home button. Only works if user is logged in.
@bp.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('main.login'))
    

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


@bp.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def view_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    post_form = PostForm()
    chat_form = ChatForm()

    # Handle PostForm submission
    if post_form.submit.data and post_form.validate_on_submit():
        # Get or create thread
        thread = Thread.query.filter_by(study_group_id=group.id).first()
        if not thread:
            thread = Thread(
                title="General Discussion",
                study_group_id=group.id,
                thread_content="General discussion for this study group"
            )
            db.session.add(thread)
            db.session.commit()
        
        # Create new post
        new_post = Post(
            thread_id=thread.thread_id,
            user_id=current_user.id,
            title=post_form.title.data,
            description=post_form.description.data,
            meeting_time=post_form.meeting_time.data
        )
        db.session.add(new_post)
        db.session.commit()
        
        # Create notification for group members
        create_notification(
            group.id, 
            f"New post in {group.title}: {post_form.title.data}"
        )
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.view_group', group_id=group.id))
    
    # Handle ChatForm submission
    elif chat_form.submit.data and chat_form.validate_on_submit():
        new_message = GroupChatMessage(
            group_id=group.id,
            user_id=current_user.id,
            content=chat_form.message.data
        )
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('main.view_group', group_id=group.id))

    # Get posts and chat messages
    posts = Post.query.join(Thread).filter(Thread.study_group_id == group.id).order_by(Post.date_and_time.desc()).all()
    chat_messages = GroupChatMessage.query.filter_by(group_id=group.id).order_by(GroupChatMessage.timestamp.asc()).all()
    
    # Render template with all needed data
    return render_template(
        'view_group.html',
        group=group,
        form=post_form,
        chat_form=chat_form,
        posts=posts,
        chat_messages=chat_messages
    )

# ───────────────────────────────────────────────────────────
#  JOIN / LEAVE
# ───────────────────────────────────────────────────────────
@bp.post("/join/<int:group_id>")
@login_required
def join_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    if group.add_member(current_user):
        db.session.commit()
        flash("Joined ✓", "success")
    else:
        flash("You’re already a member.", "info")
    return redirect(request.referrer or url_for("main.browse_listings"))

@bp.post("/leave/<int:group_id>")
@login_required
def leave_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    if group.remove_member(current_user):
        db.session.commit()
        flash("Left group.", "success")
    return redirect(request.referrer or url_for("main.browse_listings"))

# ───────────────────────────────────────────────────────────
#  FAVORITE / UNFAVORITE
# ───────────────────────────────────────────────────────────
@bp.post("/favorite/<int:group_id>")
@login_required
def toggle_favorite(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    if group in current_user.favorite_groups:
        current_user.favorite_groups.remove(group)
        flash("Removed from favorites", "info")
    else:
        current_user.favorite_groups.append(group)
        flash("★ Added to favorites", "success")
    db.session.commit()
    return redirect(request.referrer or url_for("main.browse_listings"))

# ───────────────────────────────────────────────────────────
#  “Joined Groups” & “Favorites” tabs
# ───────────────────────────────────────────────────────────
@bp.get("/joined")
@login_required
def joined_groups():
    return render_template("browse_listings.html",
                           study_groups=current_user.joined_groups,
                           heading="My Study Groups")

@bp.get("/favorites")
@login_required
def favorite_groups():
    return render_template("browse_listings.html",
                           study_groups=current_user.favorite_groups,
                           heading="★ Favorites")



#New Placeholder routes created for each functionality on main page

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

@bp.route('/profile')
@login_required
def view_profile():
    return render_template('view_profile.html')

@bp.route('/notifications')
@login_required
def view_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@bp.route('/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True  # Use is_read instead of read
        db.session.commit()
        if notification.group_id:
            return redirect(url_for('main.view_group', group_id=notification.group_id))
    return redirect(url_for('main.view_notifications'))

@bp.route('/mark-all-read')
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read', 'success')
    return redirect(url_for('main.view_notifications'))




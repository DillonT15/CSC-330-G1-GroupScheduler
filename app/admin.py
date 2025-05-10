from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from . import db
from .models import User, StudyGroup, Post

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.before_request
def check_admin():
    """Ensure only admins can access admin routes"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash("You don't have permission to access the admin panel.", "danger")
        return redirect(url_for("main.index"))

@admin_bp.route("/")
def index():
    """Admin dashboard"""
    return redirect(url_for("admin.users"))

@admin_bp.route("/users")
def users():
    """User management"""
    users = User.query.all()
    return render_template("admin.html", users=users)

@admin_bp.route("/toggle-admin/<int:uid>", methods=["POST"])
def toggle_admin(uid):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(uid)
    
    # Prevent removing own admin status
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "danger")
        return redirect(url_for("admin.users"))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "granted admin privileges to" if user.is_admin else "revoked admin privileges from"
    flash(f"Successfully {action} {user.email}.", "success")
    return redirect(url_for("admin.users"))

@admin_bp.route("/ban-user/<int:uid>", methods=["POST"])
def ban_user(uid):
    """Ban a user by deleting their account"""
    user = User.query.get_or_404(uid)
    
    # Prevent banning self
    if user.id == current_user.id:
        flash("You cannot ban yourself.", "danger")
        return redirect(url_for("admin.users"))
    
    email = user.email
    
    # Remove the user's owned groups
    for group in user.owned_groups:
        db.session.delete(group)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User {email} has been banned and their account removed.", "success")
    return redirect(url_for("admin.users"))
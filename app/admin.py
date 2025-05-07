from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from . import db
from .models import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin",
                     template_folder="templates/admin")



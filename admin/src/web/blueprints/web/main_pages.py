"""
Blueprint Web principal: páginas base (index, home, logout).
"""
from flask import Blueprint, render_template, session, redirect, url_for
from src.core.models.user import User

main = Blueprint('main', __name__)


@main.route("/")
def index():
    return render_template("auth/login.html")


@main.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user = User.query.get(session["user_id"])
    return render_template("shared/home.html", user=user)


@main.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("main.index"))



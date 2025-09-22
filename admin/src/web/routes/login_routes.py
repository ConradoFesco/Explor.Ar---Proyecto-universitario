# src/web/routes/login_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models.user import User
from src.web import db   # importa tu instancia SQLAlchemy

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("mail")
        password = request.form.get("password")
        if not email or not password:
            return render_template('login.html', error="Complete todos los campos")

        user = User.query.filter_by(mail=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Bienvenido!", "success")
            return redirect(url_for("layout.html"))  # ajusta a tu ruta de inicio
        else:
            flash("Credenciales inválidas", "error")
            return redirect(url_for("home"))

    return render_template("login.html")

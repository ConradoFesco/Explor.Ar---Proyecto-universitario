from src.web import create_app
from src.web.extensions import db
from src.web.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        # Solo si la contraseña parece estar en texto plano
        if not u.password.startswith("pbkdf2:"):
            u.password = generate_password_hash(u.password)
    db.session.commit()

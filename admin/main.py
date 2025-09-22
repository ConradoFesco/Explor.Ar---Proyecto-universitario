from src.web import create_app
from src.web.routes.login_routes import login_bp

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 
    app.register_blueprint(login_bp)

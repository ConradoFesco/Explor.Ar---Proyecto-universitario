"""
Registro centralizado de todos los blueprints de la aplicación.
"""


def register_blueprints(app):
    """
    Registra todos los blueprints de la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    # Blueprint principal (rutas de vistas HTML)
    from .routes.main_routes import main
    app.register_blueprint(main)
    
    # Blueprint de autenticación
    from .routes.auth_routes import login_bp
    app.register_blueprint(login_bp, url_prefix="/api")
    
    # Blueprint de perfil
    from .routes.profile_routes import profile_bp
    app.register_blueprint(profile_bp)
    
    # Blueprint de tags
    from .routes.tag_routes import tag_api
    app.register_blueprint(tag_api, url_prefix="/api")
    
    # Blueprint de sitios históricos
    from .routes.HistoricSite_Routes import site_api
    app.register_blueprint(site_api, url_prefix="/api")
    
    # Blueprint de estados
    from .routes.state_routes import state_api
    app.register_blueprint(state_api, url_prefix="/api")
    
    # Blueprint de categorías
    from .routes.category_routes import category_api
    app.register_blueprint(category_api, url_prefix="/api")
    
    # Blueprint de eventos
    from .routes.event_routes import event_api
    app.register_blueprint(event_api, url_prefix="/api")
    
    # Blueprint de flags
    from .routes.flag_routes import flag_api
    app.register_blueprint(flag_api, url_prefix="/flags")
    
    # Blueprint de usuarios (API)
    from .routes.user_routes import user_api
    app.register_blueprint(user_api, url_prefix='/api/users')


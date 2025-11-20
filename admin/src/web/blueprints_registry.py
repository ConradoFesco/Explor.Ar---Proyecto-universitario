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
    from .blueprints.web.main_pages import main
    app.register_blueprint(main)
    
    # Blueprint de autenticación
    from .blueprints.api.auth_routes import login_bp
    app.register_blueprint(login_bp, url_prefix="/api")
    
    # Blueprint de perfil (Web) y API password update
    from .blueprints.web.profile_pages import profile_web
    app.register_blueprint(profile_web)
    from .blueprints.api.profile_routes import profile_bp
    app.register_blueprint(profile_bp, url_prefix="/api")
    
    # Blueprint de tags
    from .blueprints.api.tag_routes import tag_api
    app.register_blueprint(tag_api, url_prefix="/api")
    
    # Blueprint de sitios históricos
    from .blueprints.api.historic_site_routes import site_api
    app.register_blueprint(site_api, url_prefix="/api")
    from .blueprints.api.review_routes import review_api
    app.register_blueprint(review_api, url_prefix="/api")
    
    # Blueprint de estados
    from .blueprints.api.state_routes import state_api
    app.register_blueprint(state_api, url_prefix="/api")
    
    # Blueprint de categorías
    from .blueprints.api.category_routes import category_api
    app.register_blueprint(category_api, url_prefix="/api")
    
    # Blueprint de eventos
    from .blueprints.api.event_routes import event_api
    app.register_blueprint(event_api, url_prefix="/api")
    
    # Blueprint de flags (API y Web)
    from .blueprints.api.flag_routes import flag_api
    app.register_blueprint(flag_api, url_prefix="/api")
    from .blueprints.web.flags_pages import flags_web
    app.register_blueprint(flags_web)
    
    # Blueprint de configuración pública
    from .blueprints.api.config_routes import config_api
    app.register_blueprint(config_api, url_prefix="/api")
    
    # Blueprint de usuarios (API) y Web
    from .blueprints.api.user_routes import user_api
    app.register_blueprint(user_api, url_prefix='/api/users')
    from .blueprints.web.users_pages import users_web
    app.register_blueprint(users_web)

    # Blueprint Web para sitios, eventos de sitios y tags
    from .blueprints.web.sites_pages import sites_web
    app.register_blueprint(sites_web)
    from .blueprints.web.sites_events_pages import sites_events_web
    app.register_blueprint(sites_events_web)
    from .blueprints.web.tags_pages import tags_web
    app.register_blueprint(tags_web)

    # Blueprint Web para reseñas
    from .blueprints.web.reviews_pages import reviews_web
    app.register_blueprint(reviews_web)

"""
Registro centralizado de todos los blueprints de la aplicación.
"""

def register_blueprints(app):
    """
    Registra todos los blueprints de la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    from .blueprints.web.main_pages import main
    app.register_blueprint(main)
    from .blueprints.web.profile_pages import profile_web
    app.register_blueprint(profile_web)
    from .blueprints.web.flags_pages import flags_web
    app.register_blueprint(flags_web)
    from .blueprints.web.users_pages import users_web
    app.register_blueprint(users_web)
    from .blueprints.web.sites_pages import sites_web
    app.register_blueprint(sites_web)
    from .blueprints.web.sites_events_pages import sites_events_web
    app.register_blueprint(sites_events_web)
    from .blueprints.web.tags_pages import tags_web
    app.register_blueprint(tags_web)
    from .blueprints.web.reviews_pages import reviews_web
    app.register_blueprint(reviews_web)

    from .blueprints.api.auth_routes import login_bp
    app.register_blueprint(login_bp, url_prefix="/api")
    from .blueprints.api.historic_site_routes import site_api
    app.register_blueprint(site_api, url_prefix="/api")
    from .blueprints.api.review_routes import review_api
    app.register_blueprint(review_api, url_prefix="/api")
    from .blueprints.api.config_routes import config_api
    app.register_blueprint(config_api, url_prefix="/api")
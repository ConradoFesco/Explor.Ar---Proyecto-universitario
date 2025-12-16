from minio import Minio


class Storage:
    def __init__(self, app=None):
        self._client = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Inicializa la conexión a MinIO con la configuración de la app"""
        endpoint = app.config['MINIO_SERVER'].replace("http://", "").replace("https://", "")

        self._client = Minio(
            endpoint,
            access_key=app.config['MINIO_ACCESS_KEY'],
            secret_key=app.config['MINIO_SECRET_KEY'],
            secure=app.config.get('MINIO_SECURE', False)
        )
        app.storage = self._client
        return app


storage = Storage()
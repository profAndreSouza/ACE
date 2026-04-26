from flask import Flask
from .routes.producao import producao_bp
from .routes.logistica import logistica_bp
from .routes.views import views_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(producao_bp, url_prefix="/api/producao")
    app.register_blueprint(logistica_bp, url_prefix="/api/logistica")

    return app

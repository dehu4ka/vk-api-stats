from flask import Flask
from api.client import RTCameraClient
from services.stats import format_duration


def create_app() -> Flask:
    app = Flask(__name__)

    client = RTCameraClient()
    app.config["RT_CLIENT"] = client

    app.jinja_env.globals["format_duration"] = format_duration

    from routes.dashboard import bp as dashboard_bp
    from routes.cameras import bp as cameras_bp
    from routes.archives import bp as archives_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cameras_bp)
    app.register_blueprint(archives_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)

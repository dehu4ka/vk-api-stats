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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    create_app().run(host=args.host, port=args.port, debug=args.debug)


# gunicorn entry point: gunicorn "app:create_app()"

from flask import Flask

app = Flask(__name__)


def create_app():
    app_ctx = app.app_context()
    app_ctx.push()

    from . import routes
    return app

from flask import Flask

from . import pages


def create_app():  # application factory
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app

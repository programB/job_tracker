from dotenv import load_dotenv
from flask import Flask

from . import pages

answer = load_dotenv()
print(f"loaded env?: {answer}")


def create_app():  # application factory
    app = Flask(__name__)
    app.config.from_prefixed_env()

    app.register_blueprint(pages.bp)
    return app

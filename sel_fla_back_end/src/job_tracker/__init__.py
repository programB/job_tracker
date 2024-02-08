from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/api/example_endpoint/")
    def example_endpoint():
        return "This is an example answer"

    return app

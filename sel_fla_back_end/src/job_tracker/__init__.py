import connexion


def create_app():
    app = connexion.App(__name__, specification_dir="./")
    app.add_api("job_tracker_backend_api.yml")

    return app

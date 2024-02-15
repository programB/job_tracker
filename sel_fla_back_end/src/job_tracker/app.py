import connexion
from connexion.resolver import RelativeResolver


def create_app():

    app = connexion.App(__name__, specification_dir="./")
    resolver = RelativeResolver(__package__ + ".api")
    app.add_api("job_tracker_backend_api.yml", resolver=resolver)

    return app

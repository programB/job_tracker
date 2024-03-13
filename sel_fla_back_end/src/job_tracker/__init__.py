import connexion
from connexion.resolver import RelativeResolver

from job_tracker import config
from job_tracker.database import db
from job_tracker.extensions import ma, scheduler


def create_app(custom_config=config.RegularConfig):

    containing_package_name = __package__
    application_name = containing_package_name

    # Create connexion app
    connexion_app = connexion.FlaskApp(
        application_name,
        specification_dir=config.root_dir,
    )
    # Get underlying flask app
    base_flask_app = connexion_app.app

    # Apply configuration to the flask app
    base_flask_app.config.from_object(custom_config)

    # Initialize any extensions (db, serializer, etc.)
    # (usually these are applied to the flask app)
    #   1. Order does matter (db before ma).
    #   2. SQLAlchemy must know all the models to initialize itself
    #      properly hence importing them here.
    #      (if models were imported implicitly in any previous steps,
    #       or at the top of the file this is not needed).
    from job_tracker.models import Company, JobOffer, Tag  # noqa: F401

    db.init_app(base_flask_app)
    ma.init_app(base_flask_app)
    scheduler.init_app(base_flask_app)

    # Register blueprints (including indirect registration by extensions)
    # resolver = None if __package__ is None else RelativeResolver(__package__ + ".api")
    resolver = RelativeResolver(containing_package_name + ".api")
    openapi_spec = config.root_dir.joinpath("job_tracker_backend_api.yml")
    connexion_app.add_api(openapi_spec, resolver=resolver)

    # Any additional routes (eg. added temporarily for a quick test and
    # besides those already added through blueprints) can go here

    # Add any tasks to the scheduler here
    # (or import module(s) with functions decorated with @scheduler.task)
    # and start the scheduler.
    import job_tracker.tasks  # noqa: F401

    scheduler.start()

    # Init the db here (within the context of created app !)
    with base_flask_app.app_context():
        db.create_all()

    # Finally return the app
    return connexion_app

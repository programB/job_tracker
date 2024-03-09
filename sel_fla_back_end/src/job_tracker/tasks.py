import logging
import string
from datetime import datetime
from random import choices, randint

from job_tracker.database import db
from job_tracker.extensions import scheduler
from job_tracker.models import Company


@scheduler.task("interval", id="demo_task", seconds=4)
def schedule_demo_task():
    logging.error(
        "This task runs every 4 seconds printing random number: %s", randint(1, 49)
    )


# Cron-like syntax for running at every minute of an hour (:01, :01,...,:59)
# See https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
# for details.
@scheduler.task(
    trigger="cron",
    id="put_some_data_into_db_task",
    minute="*/1",
    max_instances=1,
    misfire_grace_time=10,  # seconds
)
def put_some_data_into_db():
    random_n = randint(1, 1000)
    letter_set = string.ascii_lowercase
    c_name = "".join(choices(letter_set, k=10))
    logging.error(
        (
            "This task runs once on every minute in and hour and adds one fake "
            "company to the database. Time: %s  Added: Company %s-%s"
        ),
        datetime.now().time().isoformat(),
        c_name,
        random_n,
    )
    with scheduler.app.app_context():
        # Database tables must exists in the db at this point
        fake_company = Company(
            name=f"Company {c_name}-{random_n}",
            address=f"{random_n} Empty str.",
            town="Gotham",
            postalcode="00-000",
            website=f"https://phonycompany-{c_name}.com/",
        )
        db.session.add(fake_company)
        db.session.commit()  # Flask-APScheduler requires this gets called

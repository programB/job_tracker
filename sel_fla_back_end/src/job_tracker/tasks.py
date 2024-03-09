import logging
from random import randint

from job_tracker.extensions import scheduler


@scheduler.task("interval", id="demo_task", seconds=4)
def schedule_demo_task():
    logging.error(
        "This task runs every 4 seconds printing random number: %s", randint(1, 49)
    )

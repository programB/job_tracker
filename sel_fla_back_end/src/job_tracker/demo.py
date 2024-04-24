import sqlparse
from flask import current_app
from sqlalchemy import exc
from sqlalchemy.sql import text

from .config import root_dir

demo_data_script = root_dir.joinpath("demo_data.sql")


def load_demo_data(db):
    # This function must be executed in active application context
    # for db connection to work
    current_app.logger.info("Trying do load demo data to the db")
    try:
        full_script = demo_data_script.read_text()
        statements = sqlparse.split(
            sqlparse.format(full_script, reindent=False, strip_comments=True)
        )

        for statement in statements:
            if len(statement.strip()) > 0:
                try:
                    db.session.execute(text(statement))
                    current_app.logger.info("Data loaded")
                except (exc.DataError, exc.IntegrityError):
                    db.session.rollback()
                    current_app.logger.info("Data already in db")
                    continue
    except exc.OperationalError:
        current_app.logger.exception(
            ("Failed to connect to the database while trying to load demo data.")
        )
    else:
        db.session.commit()

import os
import pathlib
import tempfile
from datetime import datetime

import pytest

from job_tracker import create_app
from job_tracker.config import BaseConfig
from job_tracker.database import db
from job_tracker.models import Company, JobOffer, Tag
from job_tracker.extensions import scheduler

data_dir = pathlib.Path(__file__).parent.resolve().joinpath("data")
fake_offers_f = data_dir.joinpath("test_offers.dat")


# This is not a fixture !
def init_db_and_load_fake_data(sqldb):
    """Loads sample date into the database.

    This function has to run in the app context.
    This function uses models to do its job.
    """
    date_format = "%Y-%m-%d %H:%M:%S"

    sqldb.drop_all()
    sqldb.create_all()
    # INSERT INTO company
    # (company_id, name, address, town, postalcode, website)
    # VALUES
    # (1, "Company 1", "1 Empty str.", "Gotham", "00-000", "https://phonycompany1.com/"),  # noqa: E501
    # (2, "Company 2", "2 Rogue str.", "Gotham", "00-000", "https://phonycompany2.com/")  # noqa: E501
    # ;
    company1 = Company(
        name="Company 1",
        address="1 Empty str.",
        town="Gotham",
        postalcode="00-000",
        website="https://phonycompany1.com/",
    )
    company2 = Company(
        name="Company 2",
        address="2 Rogue str.",
        town="Gotham",
        postalcode="00-000",
        website="https://phonycompany2.com/",
    )
    sqldb.session.add_all([company1, company2])

    # INSERT INTO joboffer
    # (joboffer_id, company_id, title, posted, contracttype, jobmode, joblevel, monthlysalary, detailsurl, collected)   # noqa: E501
    # VALUES
    # (1, 1, 'Test offer 1', '2012-06-18 10:34:09', 'full time', 'in office', 'junior', 5000, 'https://fakeaddress.com/1', '2024-01-15 15:40:00'),  # noqa: E501
    # (2, 1, 'Test offer 2', '2024-01-09 17:01:00', 'full time', 'in office', 'senior', 10000, 'https://fakeaddress.com/2', '2024-01-15 15:40:01'),  # noqa: E501
    # (3, 2, 'Test offer 3', '2024-01-06 8:00:00', 'part time', 'remote', 'trainee', 3000, 'https://otherfakeaddress.com/3', '2024-01-15 15:40:02')  # noqa: E501
    # ;
    # joboffer1 = JobOffer(
    #     title="Test offer 1",
    #     company=company1,
    #     posted=datetime.strptime("2012-06-18 10:34:09", date_format),
    #     collected=datetime.strptime("2024-01-15 15:40:00", date_format),
    #     contracttype="full time",
    #     jobmode="in office",
    #     joblevel="junior",
    #     monthlysalary=5000,
    #     detailsurl="https://fakeaddress.com/1",
    # )
    # joboffer2 = JobOffer(
    #     title="Test offer 2",
    #     company=company1,
    #     posted=datetime.strptime("2024-01-09 17:01:00", date_format),
    #     collected=datetime.strptime("2024-01-15 15:40:01", date_format),
    #     contracttype="full time",
    #     jobmode="in office",
    #     joblevel="senior",
    #     monthlysalary=10000,
    #     detailsurl="https://fakeaddress.com/2",
    # )
    # joboffer3 = JobOffer(
    #     title="Test offer 3",
    #     company=company2,
    #     posted=datetime.strptime("2024-01-06 8:00:00", date_format),
    #     collected=datetime.strptime("2024-01-15 15:40:02", date_format),
    #     contracttype="part time",
    #     jobmode="remote",
    #     joblevel="trainee",
    #     monthlysalary=3000,
    #     detailsurl="https://otherfakeaddress.com/3",
    # )
    # sqldb.session.add_all([joboffer1, joboffer2, joboffer3])

    # Load offers from the file
    list_of_fake_offers = []
    with fake_offers_f.open("r") as dataf:
        for line in dataf:
            offer_tup = eval(line[:-2])
            joboffer = JobOffer(
                title=offer_tup[2],
                company=company1 if offer_tup[1] == 1 else company2,
                posted=datetime.strptime(offer_tup[3], date_format),
                collected=datetime.strptime(offer_tup[9], date_format),
                contracttype=offer_tup[4],
                jobmode=offer_tup[5],
                joblevel=offer_tup[6],
                monthlysalary=offer_tup[7],
                detailsurl=offer_tup[8],
            )
            list_of_fake_offers.append(joboffer)
    sqldb.session.add_all(list_of_fake_offers)

    # INSERT INTO tag
    # (tag_id, name)
    # VALUES
    # (1, "Java"),
    # (2, "Selenium"),
    # (3, "Python")
    # ;
    tag1 = Tag(name="Java")
    tag2 = Tag(name="Selenium")
    tag3 = Tag(name="Python")

    # INSERT INTO joboffertag
    # (joboffer_id, tag_id)
    # VALUES
    # (1, 1),
    # (1, 2),
    # (2, 3),
    # (2, 2)
    # ;
    joboffer1 = list_of_fake_offers[0]
    joboffer2 = list_of_fake_offers[1]
    # 3rd and consecutive joboffers are not added since they will not have any tags
    joboffer1.tags.append(tag1)
    joboffer1.tags.append(tag2)
    joboffer2.tags.append(tag3)
    joboffer2.tags.append(tag2)
    sqldb.session.add_all([tag1, tag2, tag3])

    sqldb.session.commit()


@pytest.fixture
def connexion_app_instance():
    """Create and configure a new app instance for each test."""

    # Create a temporary file for storing sqlite database.
    # Since this fixture is being run before every test,
    # this will ensure every test runs in isolation with
    # its own, fresh copy of the database.
    db_fd, db_fpath = tempfile.mkstemp(prefix="tmp_db_", suffix=".db")
    # print(f"temporary database file is at: {db_fpath}")

    # Create the app with a test configuration.
    class TestConfig(BaseConfig):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_fpath}"

    conxn_app = create_app(custom_config=TestConfig)

    # This only exists because app factory starts the scheduler
    # probably it should be started externally based environment variables
    jobs = scheduler.get_jobs()
    for job in jobs:
        job.remove()

    # Get the underlying flask app from the connexion app instance.
    wrapped_flask_app = conxn_app.app

    # Create the database and load test data.
    with wrapped_flask_app.app_context():
        init_db_and_load_fake_data(sqldb=db)

    yield conxn_app

    # After the test close and remove the db file.
    os.close(db_fd)
    os.remove(db_fpath)
    # This only exists because app factory starts the scheduler
    # probably it should be started externally based environment variables
    scheduler.shutdown(wait=False)


# def test_app_object_creation(connexion_app_instance):
#     """Test if app instance is Connexion rather then Flask application instance."""
#     # FlaskApp IS the correct type to compare to.
#     assert isinstance(connexion_app_instance, FlaskApp)


@pytest.fixture
def httpx_test_client(connexion_app_instance):
    """Returns a test client for the app."""
    # This test client is not the same as the one used by Flask -
    # - it's based on httpx library https://www.python-httpx.org
    # Hints:
    # Call:
    # r = client.get('https://www.example.org/', params={"key": "value",})
    # params is used like the query_string in original client
    # Methods:
    # r.text
    # r.content (use instead of r.data for binary data)
    # r.json()
    return connexion_app_instance.test_client()

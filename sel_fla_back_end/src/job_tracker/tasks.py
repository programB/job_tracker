import logging
import string
from contextlib import contextmanager
from datetime import datetime
from random import choices, randint

from selenium import webdriver

from job_tracker.config import root_dir
from job_tracker.database import db
from job_tracker.extensions import scheduler
from job_tracker.models import Company, JobOffer, Tag
from job_tracker.pracujpl_POM import Distance, PracujplMainPage, ResultsPage

datafile = root_dir.joinpath("search_results.txt")


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


@contextmanager
def selenium_driver(selenium_grid_url, selenium_grid_port="4444"):

    custom_options = webdriver.ChromeOptions()

    if selenium_grid_url:
        driver = webdriver.Remote(
            command_executor=selenium_grid_url + ":" + selenium_grid_port,
            options=custom_options,
        )
    else:
        # Use local driver (local browser)
        # if no Selenium Grid server url was given
        driver = webdriver.Chrome(options=custom_options)

    yield driver

    driver.quit()


@scheduler.task(
    trigger="cron",
    id="fetch_offers_task",
    minute="*/5",
    max_instances=1,
    misfire_grace_time=30,  # seconds
)
def fetch_offers():

    with selenium_driver(None) as driver:
        main_page = PracujplMainPage(driver, reject_cookies=True)

        if main_page.search_mode == "default":
            main_page.search_mode = "it"
        is_tag_list_available = main_page.search_mode == "it"
        main_page.employment_type = ["full_time"]
        main_page.location_and_distance = ("Warszawa", Distance.TEN_KM)
        main_page.search_term = "Tester"

        main_page.start_searching()

        results_page = ResultsPage(driver)
        all_offers = results_page.all_offers

    with scheduler.app.app_context():
        for offer in all_offers:
            if not JobOffer.query.get(offer.id):  # new, not yet stored offer
                if not Company.query.get(offer.company_id):  # not yet stored company
                    new_company = Company(
                        company_id=offer.company_id,
                        name=offer.company_name,
                        address="",
                        town="",
                        postalcode="",
                        website=offer.company_link,
                    )
                    db.session.add(new_company)
                else:
                    logging.warning("Company (id = %s) already in db", offer.company_id)

                new_offer = JobOffer(
                    joboffer_id=offer.id,
                    company_id=offer.company_id,
                    title=offer.title,
                    posted=offer.publication_date,
                    collected=offer.webscrap_timestamp,
                    contracttype=offer.contract_type,
                    jobmode="",  # TODO: Not collected at the moment
                    joblevel=offer.job_level,
                    monthlysalary=offer.salary,
                    detailsurl=offer.link,
                )
                if is_tag_list_available:
                    for tag in offer.technology_tags:
                        existing_tag = Tag.query.filter(Tag.name == tag).one_or_none()
                        if existing_tag:
                            new_offer.tags.append(existing_tag)
                        else:
                            new_tag = Tag(name=tag)
                            db.session.add(new_tag)
                            new_offer.tags.append(new_tag)
                db.session.add(new_offer)
                db.session.commit()
            else:
                logging.warning("Offer (id = %s) already in db", offer.id)

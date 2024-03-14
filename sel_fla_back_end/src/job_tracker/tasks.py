import logging
import os
from contextlib import contextmanager
from random import randint

from selenium import webdriver

from job_tracker.database import db
from job_tracker.extensions import scheduler
from job_tracker.models import Company, JobOffer, Tag
from job_tracker.pracujpl_POM import Distance, PracujplMainPage, ResultsPage


@scheduler.task("interval", id="demo_task", seconds=4)
def schedule_watchdog_task():
    anum = randint(1, 49)  # nosec B311
    logging.error("This task runs every 4 seconds printing random number: %s", anum)


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


# Cron-like syntax
# See https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
# for details.
@scheduler.task(
    trigger="cron",
    id="fetch_offers_task",
    minute="*/5",
    max_instances=1,
    misfire_grace_time=30,  # seconds
)
def fetch_offers():
    # Use selenium grid service.
    # If SELENIUM_GRID_URL env. is not set
    # local selenium instalation will be used.
    selenium_grid_url = os.getenv("SELENIUM_GRID_URL")
    selenium_grid_port = os.getenv("SELENIUM_GRID_PORT", "4444")
    with selenium_driver(selenium_grid_url, selenium_grid_port) as driver:
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
                    salary=offer.salary,
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

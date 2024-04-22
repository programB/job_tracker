import os
from contextlib import contextmanager

import urllib3.exceptions as UE
from flask import current_app
from selenium import webdriver
from sqlalchemy import exc

from job_tracker.database import db
from job_tracker.extensions import scheduler
from job_tracker.models import Company, JobOffer, Tag
from job_tracker.pracujpl_POM import Distance, PracujplMainPage, ResultsPage

# Search for job offers with criteria set through
# .env file or enviroment variables
# (fallback is for when nothing was passed)
search_term = os.getenv("SEARCH_TERM", "Tester")
search_employment_type = os.getenv("SEARCH_EMPLOYMENT_TYPE", "full_time")
search_location = os.getenv("SEARCH_LOCATION", "Warszawa")
# Search radius is not yet user settable at this time
# and fixed to 10 km here
search_radius = Distance.TEN_KM

@scheduler.task("interval", id="i_am_still_alive_task", seconds=15)
def i_am_still_alive_task():
    with scheduler.app.app_context():
        current_app.logger.info(
            "This task runs every 15 seconds to demonstrate scheduler is doing it's job"
        )


@contextmanager
def selenium_driver(SELENIUM_URL: str | None, SELENIUM_PORT="4444"):

    custom_options = webdriver.ChromeOptions()

    try:
        if SELENIUM_URL:
            driver = webdriver.Remote(
                command_executor=SELENIUM_URL + ":" + SELENIUM_PORT,
                options=custom_options,
            )
        else:
            # Use local driver (local browser)
            # if no Selenium server url was given
            driver = webdriver.Chrome(options=custom_options)
    except UE.MaxRetryError:
        current_app.logger.exception(
            (
                "Failed to connect to the selenium service while trying to "
                "scrap new offers - nothing was collected or stored."
            )
        )
        raise
    else:
        yield driver

        driver.quit()


# Cron-like syntax
# See https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
# for details.
@scheduler.task(
    trigger="cron",
    id="fetch_offers_task",
    minute="0",
    hour="12",
    max_instances=1,
    misfire_grace_time=3600,  # seconds
)
def fetch_offers():
    # Aquire app_context for the sake of database conectivity and app.logger
    with scheduler.app.app_context():
        # Use selenium service.
        # If SELENIUM_URL env. is not set
        # local selenium instalation will be used.
        SELENIUM_URL = os.getenv("SELENIUM_URL")
        SELENIUM_PORT = os.getenv("SELENIUM_PORT", "4444")
        with selenium_driver(SELENIUM_URL, SELENIUM_PORT) as driver:
            current_app.logger.info("Job offers scraping started")
            try:
                main_page = PracujplMainPage(driver, reject_cookies=True)

                if main_page.search_mode == "default":
                    main_page.search_mode = "it"
                is_tag_list_available = main_page.search_mode == "it"
                main_page.employment_type = [search_employment_type]
                main_page.location_and_distance = (search_location, search_radius)
                main_page.search_term = search_term

                main_page.start_searching()

                results_page = ResultsPage(driver)
                all_offers = results_page.all_offers
            except ConnectionError:
                current_app.logger.error(
                    "Pracuj.pl website unreachable. No offers were collected."
                )
                return
            current_app.logger.info("Job offers scraping completed")

        current_app.logger.info("Adding collected job offers to the database")
        try:
            for offer in all_offers:
                if not JobOffer.query.get(offer.id):  # new, not yet stored offer
                    if not Company.query.get(
                        offer.company_id
                    ):  # not yet stored company
                        new_company = Company(
                            company_id=offer.company_id,
                            name=offer.company_name,
                            address="",
                            town="",
                            postalcode="",
                            website=offer.company_link,
                        )
                        try:
                            db.session.add(new_company)
                        except (exc.DataError, exc.IntegrityError) as e:
                            db.session.rollback()
                            current_app.logger.error(
                                (
                                    "failed to add company while processing "
                                    "offer_id %s. Offer skipped.: %s"
                                ),
                                offer.id,
                                str(e),
                            )
                            continue
                    else:
                        current_app.logger.info(
                            "Company (id = %s) already in db", offer.company_id
                        )

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
                            existing_tag = Tag.query.filter(
                                Tag.name == tag
                            ).one_or_none()
                            if existing_tag:
                                new_offer.tags.append(existing_tag)
                            else:
                                new_tag = Tag(name=tag)
                                try:
                                    db.session.add(new_tag)
                                except (exc.DataError, exc.IntegrityError) as e:
                                    db.session.rollback()
                                    current_app.logger.error(
                                        (
                                            "failed to add new tag while processing "
                                            "offer_id %s. Offer skipped.: %s"
                                        ),
                                        offer.id,
                                        str(e),
                                    )
                                    continue
                                new_offer.tags.append(new_tag)
                    try:
                        db.session.add(new_offer)
                        db.session.commit()
                    except (exc.DataError, exc.IntegrityError) as e:
                        db.session.rollback()
                        current_app.logger.error(
                            "failed to add new offer (offer_id %s). Offer skipped.: %s",
                            offer.id,
                            str(e),
                        )
                        continue
                else:
                    current_app.logger.info("Offer (id = %s) already in db", offer.id)
            current_app.logger.info("Finished adding offers to the database")
        except exc.OperationalError:
            current_app.logger.exception(
                (
                    "Failed to connect to the database while trying to store "
                    "new offers - none were stored."
                )
            )

import logging

from selenium import webdriver

from .pracujpl_POM import Distance, PracujplMainPage, ResultsPage

# import random
# import time


# from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
main_page = PracujplMainPage(driver, reject_cookies=True)
# main_page.gohome()
# driver.maximize_window()

if main_page.search_mode == "default":
    main_page.search_mode = "it"
tags = main_page.search_mode == "it"
# main_page.search_mode = "default"

# main_page.employment_type.select(["full_time"])
# logging.warning(
#     f"Current selection of employment types is: \
# {main_page.employment_type}"
# )
# logging.warning("selectnig full_time")

main_page.employment_type = ["full_time"]

# logging.warning(
#     f"Current selection of employment types is: \
# {main_page.employment_type}"
# )
# time.sleep(1)

# main_page.location_field.send_keys("Warszawa")
# main_page.location_field.send_keys(Keys.ENTER)
# main_page.distance = Distance.HUNDRED_KM
# main_page.location = "Warszawa"
# logging.warning(f"Current distance setting is: {main_page.distance}")
# time.sleep(3)
# main_page.distance = Distance.HUNDRED_KM

main_page.location_and_distance = ("Warszawa", Distance.FIFTY_KM)

# main_page.search_field.send_keys("Tester")
# main_page.location_field.send_keys(Keys.ENTER)
# logging.warning(f"Current value of search_term is: {main_page.search_term}")
# logging.warning("Setting it to: Tester")

main_page.search_term = "Tester"

# logging.warning(f"Current value of search_term is: {main_page.search_term}")
# time.sleep(3)

# submit_btn = main_page.btn_search_submit
# submit_btn.click()

main_page.start_searching()

# time.sleep(3)


results_page = ResultsPage(driver)
# time.sleep(2)

cur_subpage_element, cur_subpage_number = results_page.get_current_subpage()
logging.warning(
    "Current subpage is: %s and its number is : %s",
    cur_subpage_element,
    cur_subpage_number,
)
logging.warning(
    "Total number of subpages is: %s",
    results_page.tot_no_of_subpages,
)
# time.sleep(2)

# desired_subpage = random.randrange(1, results_page.tot_no_of_subpages)
# desired_subpage = 3
# results_page.goto_subpage(desired_subpage)
# cur_subpage_element, cur_subpage_number = results_page.current_subpage()
# logging.warning(
#     f"Current subpage is: {cur_subpage_element} and \
# its number is : {cur_subpage_number}"
# )

# subpage_offers = results_page.subpage_offers
# time.sleep(2)
# time.sleep(60)
# print(f"no of offers: {len(subpage_offers)}")
# for offer in subpage_offers:
#     print(f"Offer: {offer.title} (id: {offer.id})")
#     print(f" company:  {offer.company_name}")
#     print(f" salary:   {offer.salary}")
#     print(f" level:    {offer.job_level}")
#     print(f" contract: {offer.contract_type}")
#     print(f" link:     {offer.link}")
#     print("----------------------------")

all_offers = results_page.all_offers
# time.sleep(2)
# time.sleep(60)
print(f"total number of offers: {len(all_offers)}")
# for offer in all_offers:
#     print(f"Offer: {offer.title} (id: {offer.id})")
#     print(f" company:  {offer.company_name}")
#     print(f" salary:   {offer.salary}")
#     print(f" level:    {offer.job_level}")
#     print(f" contract: {offer.contract_type}")
#     print(f" link:     {offer.link}")
#     print("----------------------------")
datafile_path = "../../../Temp_data/search_result.txt"
with open(datafile_path, "w", encoding="utf-8") as datafile:
    for i, offer in enumerate(all_offers):
        datafile.write(f"({i})  Offer: {offer.title} (id: {offer.id})\n")
        datafile.write(f" company:  {offer.company_name}\n")
        datafile.write(f" salary:   {offer.salary}\n")
        datafile.write(f" level:    {offer.job_level}\n")
        datafile.write(f" contract: {offer.contract_type}\n")
        datafile.write(f" link:     {offer.link}\n")
        if tags:
            datafile.write(f" tags:     {offer.technology_tags}\n")
        datafile.write("----------------------------\n")
driver.quit()

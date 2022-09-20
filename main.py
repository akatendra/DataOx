from datetime import datetime
import time
import scraper
import database
import logging.config
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, wait
from random import randint


def spent_time():
    global start_time
    sec_all = time.time() - start_time
    if sec_all > 60:
        minutes = sec_all // 60
        sec = sec_all % 60
        time_str = f'| {int(minutes)} min {round(sec, 1)} sec'
    else:
        time_str = f'| {round(sec_all, 1)} sec'
    start_time = time.time()
    return time_str


def sleep_time(max_sec):
    rand_time = randint(1, max_sec)
    time.sleep(rand_time)


def scroll_page(browser):
    scroll_pause_time = 0.5

    # Get scroll height
    page_height = browser.execute_script("return document.body.scrollHeight")
    scroll_step = page_height // 10
    scroll = scroll_step
    while scroll <= page_height:
        # Scroll down to one step
        browser.execute_script(f"window.scrollTo(0, {scroll});")

        # Wait to load page
        time.sleep(scroll_pause_time)

        scroll += scroll_step


def run_flow(url1, url2, start_page, end_page, parse_func, write_to_db_func):
    global browsers
    # Initialize web browser
    logger.info(f'Hi from run_flow func!')
    browser = scraper.get_chrome_browser()
    logger.debug(
        f'Browser for pages {url1 + url2} | {start_page}-{end_page} opened: {spent_time()}')

    browsers.append(browser)

    current_page = start_page
    while current_page <= end_page:
        logger.debug(f'Take in work page: {current_page}')
        if current_page == 1:
            page_url = url1 + url2
        else:
            page_url = f'{url1}page-{current_page}/{url2}'
        browser.get(page_url)

        # Scroll to pagination for loading all images.
        scroll_page(browser)

        ####################################################################
        ####################  PAGE PROCESSING  #############################
        ####################################################################
        logger.debug(
            '##################################################################')
        logger.debug(f'Scraping page #{current_page}...')
        logger.debug(
            '##################################################################')
        html = browser.page_source
        logger.debug(
            f'Page_source of page {current_page} received: {spent_time()}')
        output_data = parse_func(browser, html)
        logger.debug(
            f'Output_data of page {current_page} received: {spent_time()}')
        # xlsx.append_xlsx_file(output_data, output_filename, page_number)
        write_to_db_func(output_data)

        # Go to pagination bar to simulate human behavior
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        pagination_bar = browser.find_element(By.XPATH,
                                              '//div[@class="pagination"]')
        browser.execute_script("arguments[0].scrollIntoView();",
                               pagination_bar)

        current_url = browser.current_url
        logger.debug(f'Current URL in run_process: {current_url}')

        ####################################################################
        current_page += 1

        # Wait random seconds
        sleep_time(5)

    # Stop script
    browser.quit()


def thread_pool(func, url1, url2, pages, parse_func, write_to_db_func):
    futures = []
    with ThreadPoolExecutor() as executor:
        for page in pages:
            futures.append(
                executor.submit(func, url1, url2, page[0], page[1], parse_func,
                                write_to_db_func))
            # Wait random seconds
            sleep_time(10)
            logger.debug(
                f'ThreadPoolExecutor take in work pages: {url} | {page[0]}-{page[1]}')
    # Wait for ending of all running processes
    wait(futures)


if __name__ == "__main__":
    # Set up logging
    logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    # Set the variables values
    time_begin = start_time = time.time()
    url = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273'
    url1 = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/'
    url2 = 'c37l1700273'
    output_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    browsers = []
    # End of variables values setting

    # Import parse functions
    parser = scraper.parse_html

    # Import writing to DB functions
    write_db = database.write_to_db

    logger.info('Start...')

    # Adding multithreading

    # 6 threads
    # pages = [(1, 14), (15, 32), (33, 48), (49, 63), (64, 82), (83, 100)]
    # pages = [(1, 50), (51, 100)]
    pages = [(1, 33), (34, 67), (68, 100)]
    # pages = [(1, 2)]

    thread_pool(run_flow,
                url1,
                url2,
                pages,
                parser,
                write_db
                )

    # Closing all unclosed browsers
    for browser in browsers:
        if browser.service.is_connectable():
            browser.quit()

    time_end = time.time()
    elapsed_time = time_end - time_begin
    if elapsed_time > 60:
        elapsed_minutes = elapsed_time // 60
        elapsed_sec = elapsed_time % 60
        elapsed_time_str = f'| {int(elapsed_minutes)} min {round(elapsed_sec, 1)} sec'
    else:
        elapsed_time_str = f'| {round(elapsed_time, 1)} sec'
    logger.info(
        f'Elapsed run time: {elapsed_time_str} seconds | New items: {scraper.counter}')

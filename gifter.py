from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException
import time
import browser_cookie3
import requests
import re
import logging
import os
import sys

_LOGGER = logging.getLogger(__name__)

def openBox(driver):
	_LOGGER.info("Checking if box is waiting to be clicked.")
	time.sleep(5)
	try:
		readyBox = driver.find_element_by_id("box_click_target")
	except (NoSuchElementException, StaleElementReferenceException) as e:
		_LOGGER.info(e)
		readyBox = False
		return readyBox

	if readyBox:
		_LOGGER.info("Clicking box now...")
		try:
			readyBox.click()
		except ElementNotVisibleException as e:
			_LOGGER.info(e)
		return True

def navigateVideoObstacle(driver, videoID, ctnBtn):
	try:
		_LOGGER.info("Looking for " + videoID)
		videoElement = driver.find_element_by_id(videoID)
	except (NoSuchElementException, StaleElementReferenceException) as e:
		_LOGGER.info(e)
		return

	# BUG on Amazon's end. Continue button will activate regardless of playing YT video
	try:
		_LOGGER.info("Letting video play for 15 seconds...")
		if videoID != "youtube-outer-container":
			videoElement.click()
	except ElementNotVisibleException as e:
		_LOGGER.info(e)
		return

	while ctnBtn.is_enabled() != True:
		_LOGGER.info("Continue button is disabled. Sleeping for 5 seconds...")
		time.sleep(5)
		try:
			ctnBtn = driver.find_element_by_css_selector("input.a-button-input.continue_button_inner")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.info(e)
			return

	try:
		_LOGGER.info("Clicking continue button.")
		ctnBtn.click()
		time.sleep(1)
	except ElementNotVisibleException as e:
		_LOGGER.info(e)
		return

def detectVideoObstacle(driver):
	try:
		_LOGGER.info("Detecting video obstacle type...")
		driver.find_element_by_id("youtube-outer-container")
		videoID = "youtube-outer-container"
	except (NoSuchElementException, StaleElementReferenceException) as e:
		_LOGGER.debug(e)
		videoID = "airy-container"

	try:
		_LOGGER.info("Finding continue button")
		ctnBtn = driver.find_element_by_css_selector("input.a-button-input.continue_button_inner")
	except (NoSuchElementException, StaleElementReferenceException) as e:
		_LOGGER.info(e)
		return
	
	navigateVideoObstacle(driver, videoID, ctnBtn)


def readGAResult(driver):
	time.sleep(5)
	_LOGGER.info("Reading result of giveaway.")
	result = driver.find_element_by_css_selector("span#title.a-size-base-plus.a-color-secondary.qa-giveaway-result-text.a-text-bold").text
	if result != "Domenico, you didnt win":
		while True:
			time.sleep(1)
	_LOGGER.info(result)

def playGA(driver, href):
	driver.get(href)

	detectVideoObstacle(driver)
	time.sleep(3)
	openBox(driver)
	readGAResult(driver)

def main():
	cj = browser_cookie3.firefox()
	#r = requests.get("http://www.amazon.com", cookies=cj) 

	#print(r.content)

	opts = Options()
	opts.add_argument("--headless")
	opts.add_argument("--window-size=1920x1080")
#    kwargs = {}
    #opts.add_argument("user-agent={}".format(self._useragent))
#    kwargs['chrome_options'] = opts
#    driver = webdriver.Chrome(**kwargs

	driver = webdriver.Chrome('binary_downloader/chromedriver')  # Optional argument, if not specified will search path.
	driver.get('http://amazon.com');

	for i in cj:
		if "amazon" not in i.domain:
			continue
		else:
			cookie_dict = {'name': i.name, 'value': i.value}
			driver.add_cookie(cookie_dict)
	driver.get('https://www.amazon.com/ga/giveaways?pageId=5');

	time.sleep(3)

	urls = []
	dom = driver.find_elements_by_css_selector("a.a-link-normal.item-link");
	for i in dom:
		urls.append(i.get_attribute("href"))

	for i in urls:
		playGA(driver, i)

	exit()

def setup_logging(enable_degbug=False):
    # set up logging to file - see previous section for more details
    logging_level = logging.DEBUG if enable_degbug else logging.INFO
    root_path = os.path.dirname(
        os.path.abspath(sys.modules['__main__'].__file__))
    log_path = os.path.join(root_path, 'gifter.log')
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s: %(asctime)s] %(name)-12s %(message)s',
        datefmt='%m-%d %H:%M',
        filename=log_path,
        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger('').addHandler(console)  # add handler to the root logger

if __name__ == '__main__':
	setup_logging()
	_LOGGER.info("Running main()")
	main()
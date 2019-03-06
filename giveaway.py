import sys
import time
import random
import logging
import browser_cookie3

from detector import Detector

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException

_LOGGER = logging.getLogger(__name__)


class GAClient():

	def __init__(self):
		self._cj = browser_cookie3.firefox()
		self.driver = webdriver.Chrome('binary_downloader/chromedriver')
		self.driver.get('https://www.amazon.com/ga/giveaways?pageId=1');
		self._itemURLs = []
		self._ID = random.randint(1, 1000)
		self.detector = Detector()
	
	def playGA(self, href):
		self.driver.get(href)

		if self.detector.detectResult(self.driver) == False:
			self.detector.detectObstacles(self.driver)
			time.sleep(5)
			self.detector.detectResult(self.driver)

	def addCookies(self):
		for cookie in self._cj:
			if "amazon" not in cookie.domain:
				continue
			else:
				cookie_dict = {'name': cookie.name, 'value': cookie.value}
				self.driver.add_cookie(cookie_dict)

	def grabURLs(self, page):
		self._itemURLs = []
		self.driver.get('https://www.amazon.com/ga/giveaways?pageId={}'.format(page));
		time.sleep(3)

		elements = self.driver.find_elements_by_css_selector("a.a-link-normal.item-link");

		for element in elements:
			self._itemURLs.append(element.get_attribute("href"))

	def run(self, startPage):
		GAClient.addCookies(self)

		try:
			endPage = int(self.driver.find_element_by_id('giveaway-numbers-container').text.split("of ", 1)[1].split(" ", 1)[0])
			if (endPage % 24) >= 1:
				endPage = (endPage // 24) + 1
			else:
				endPage = endPage // 24
		except NoSuchElementException as e:
			endPage = 100

		for page in range(startPage, endPage):
			GAClient.grabURLs(self, page)

			for url in self._itemURLs:
				_LOGGER.debug("Client ID: " + str(self._ID) + "\nPage: " + str(page) + "\nPlaying give away with this url: " + url)
				GAClient.playGA(self, url)
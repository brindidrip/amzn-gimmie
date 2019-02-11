import os
import sys
import time
import requests
import re
import logging
import browser_cookie3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException

_LOGGER = logging.getLogger(__name__)


class Unwrapper():

	def __init__(self):
		self._cj = browser_cookie3.firefox()
		self._driver = webdriver.Chrome('binary_downloader/chromedriver')
		self._driver.get('http://amazon.com');
		self._itemURLs = []
	
	def openBox(self):
		_LOGGER.info("Checking if box is waiting to be clicked.")
		time.sleep(5)
		try:
			readyBox = self._driver.find_element_by_id("box_click_target")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			readyBox = False
			return readyBox

		if readyBox:
			_LOGGER.info("Clicking box now...")
			try:
				readyBox.click()
			except ElementNotVisibleException as e:
				_LOGGER.debug(e)
			return True

	def navigateVideoObstacle(self, videoID, ctnBtn):
		try:
			_LOGGER.info("Looking for " + videoID)
			videoElement = self._driver.find_element_by_id(videoID)
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.info(e)
			return

		# BUG on Amazon's end. Continue button will activate regardless of playing YT video
		try:
			_LOGGER.info("Letting video play for 15 seconds...")
			if videoID != "youtube-outer-container":
				videoElement.click()
		except ElementNotVisibleException as e:
			_LOGGER.debug(e)
			return

		while ctnBtn.is_enabled() != True:
			_LOGGER.info("Continue button is disabled. Sleeping for 5 seconds...")
			time.sleep(5)
			try:
				ctnBtn = self._driver.find_element_by_css_selector("input.a-button-input.continue_button_inner")
			except (NoSuchElementException, StaleElementReferenceException) as e:
				_LOGGER.debug(e)
				return

		try:
			_LOGGER.info("Clicking continue button.")
			ctnBtn.click()
			time.sleep(1)
		except ElementNotVisibleException as e:
			_LOGGER.debug(e)
			return

	def detectVideoObstacle(self):
		try:
			_LOGGER.info("Detecting video obstacle type...")
			self._driver.find_element_by_id("youtube-outer-container")
			videoID = "youtube-outer-container"
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			videoID = "airy-container"

		try:
			_LOGGER.info("Finding continue button")
			ctnBtn = self._driver.find_element_by_css_selector("input.a-button-input.continue_button_inner")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			return
		
		Unwrapper.navigateVideoObstacle(self, videoID, ctnBtn)

	def readGAResult(self):
		time.sleep(5)
		_LOGGER.info("Reading result of giveaway.")
		result = self._driver.find_element_by_css_selector("span#title.a-size-base-plus.a-color-secondary.qa-giveaway-result-text.a-text-bold").text
		if result != "Domenico, you didn't win":
			while True:
				time.sleep(1)
		_LOGGER.info(result)

	def playGA(self, href):
		self._driver.get(href)

		Unwrapper.detectVideoObstacle(self)
		time.sleep(3)
		Unwrapper.openBox(self)
		Unwrapper.readGAResult(self,)

	def addCookies(self):
		for cookie in self._cj:
			if "amazon" not in cookie.domain:
				continue
			else:
				cookie_dict = {'name': cookie.name, 'value': cookie.value}
				self._driver.add_cookie(cookie_dict)

	def grabURLs(self, pages):
		self._driver.get('https://www.amazon.com/ga/giveaways?pageId=1');
		time.sleep(3)

		elements = self._driver.find_elements_by_css_selector("a.a-link-normal.item-link");

		for element in elements:
			self._itemURLs.append(element.get_attribute("href"))

	def start(self):
		# Decide how many pages to go through
		_LOGGER.info("Adding cookies")
		Unwrapper.addCookies(self)
		_LOGGER.info("Grabbing URLs")
		Unwrapper.grabURLs(self, 0)

		for url in self._itemURLs:
			_LOGGER.info("Playing give away with this url: " + url)
			Unwrapper.playGA(self, url)
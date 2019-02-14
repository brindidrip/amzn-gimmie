import sys
import os
import time
import logging

from resolver import Resolver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException

_LOGGER = logging.getLogger(__name__)


class Detector():

	def __init__(self):
		self.resolver = Resolver()

	def detectResult(self, driver):
		try:
			_LOGGER.info("Reading result of giveaway.")
			result = driver.find_element_by_css_selector("span#title.a-size-base-plus.a-color-secondary.qa-giveaway-result-text.a-text-bold").text
		except NoSuchElementException as e:
			_LOGGER.debug(e)
			return False

		if result != "Brindid, you didn't win":
			while True:
				time.sleep(1)
		_LOGGER.info(result)

	def detectBox(self, driver):
		try:
			_LOGGER.info("Checking if box is waiting to be clicked.")
			# Sleep for bouncing animation
			time.sleep(3)
			boxElem = driver.find_element_by_id("box_click_target")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			return False

		self.resolver.resolveBox(driver, boxElem)

	def detectCaptcha(self, driver):
		try:
			_LOGGER.info("Detecting captcha...")
			imgElem = driver.find_element_by_xpath("//div[@id='image_captcha']/img")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			return False

		try:
			os.makedirs("res/images")
		except FileExistsError as e:
			_LOGGER.debug(e)
			pass
		
		if self.resolver.resolveCaptcha(driver, imgElem) == False:
			Detector.detectCaptcha(self, driver)

	def detectVideoObstacle(self, driver):
		try:
			_LOGGER.info("Detecting video YT obstacle type...")
			driver.find_element_by_id("youtube-outer-container")
			videoID = "youtube-outer-container"
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			videoID = False

		if videoID == False:
			try:
				_LOGGER.info("Detecting video AR obstacle type...")
				driver.find_element_by_id("airy-container")
				videoID = "airy-container"
			except (NoSuchElementException, StaleElementReferenceException) as e:
				_LOGGER.debug(e)
				return False

		try:
			_LOGGER.info("Finding continue button")
			ctnBtn = driver.find_element_by_css_selector("input.a-button-input.continue_button_inner")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			ctnBtn = False
			return False
		
		self.resolver.resolveVideoObstacle(videoID, ctnBtn, driver)

	def detectObstacles(self, driver):
		Detector.detectCaptcha(self, driver)
		Detector.detectVideoObstacle(self, driver)
		Detector.detectBox(self, driver)
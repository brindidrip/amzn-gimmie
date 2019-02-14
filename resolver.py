import sys
import logging
import time
import urllib

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException

from PIL import Image
from pytesseract import image_to_string

_LOGGER = logging.getLogger(__name__)


class Resolver():

	def __init__(self):
		self._captchaPath = 'res/images/captcha.jpg'

	def resolveBox(self, driver, boxElem):
		try:
			_LOGGER.info("Clicking box now...")
			boxElem.click()
		except ElementNotVisibleException as e:
			_LOGGER.debug(e)
			return False

	def resolveVideoObstacle(self, videoID, ctnBtn, driver):
		try:
			_LOGGER.info("Looking for " + videoID)
			videoElement = driver.find_element_by_id(videoID)
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.info(e)
			return False

		# BUG on Amazon's end. Continue button will activate regardless of playing YT video
		try:
			_LOGGER.info("Letting video play for 15 seconds...")
			if videoID != "youtube-outer-container":
				videoElement.click()
		except ElementNotVisibleException as e:
			_LOGGER.debug(e)
			return False

		while ctnBtn.is_enabled() != True:
			_LOGGER.info("Continue button is disabled. Sleeping for 5 seconds...")
			time.sleep(5)
			try:
				ctnBtn = driver.find_element_by_css_selector("input.a-button-input.continue_button_inner")
			except (NoSuchElementException, StaleElementReferenceException) as e:
				_LOGGER.debug(e)
				return False

		try:
			_LOGGER.info("Clicking continue button.")
			ctnBtn.click()
			time.sleep(1)
		except ElementNotVisibleException as e:
			_LOGGER.debug(e)
			return False

	def resolveCaptcha(self, driver, imgElem):
		_LOGGER.info("Resolving captcha...")

		urllib.request.urlretrieve(imgElem.get_attribute('src'), self._captchaPath)
		# Let image finish generating
		time.sleep(4)

		image = Image.open(self._captchaPath, mode='r')

		captcha = image_to_string(image, config='--psm 9')
		_LOGGER.debug("Captcha: " + captcha)

		try:
			_LOGGER.info("Inserting captcha")
			input = driver.find_element_by_id("image_captcha_input")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			return

		input.send_keys(captcha)

		try:
			_LOGGER.info("Finding continue button")
			ctnBtn = driver.find_element_by_css_selector("input.a-button-input")
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

		try:
			_LOGGER.info("Checking if captcha was successful")
			result = driver.find_element_by_id("a-alert-content")
		except (NoSuchElementException, StaleElementReferenceException) as e:
			_LOGGER.debug(e)
			return

		if result.text == "Your answer is not correct":
			return False
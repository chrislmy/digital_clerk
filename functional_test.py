from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC 
import os
import time
import unittest
import HtmlTestRunner


class LoginHomeTest(unittest.TestCase):
	def setUp(self):
		self.options = webdriver.ChromeOptions()
		self.options.add_argument('--ignore-certificate-errors')
		self.options.add_argument('--ignore-ssl-errors')
		self.dir_path = os.path.dirname(os.path.realpath(__file__))
		self.chromedriver = self.dir_path + "/chromedriver"
		os.environ["webdriver.chrome.driver"] = self.chromedriver
		self.browser = webdriver.Chrome(chrome_options=self.options, executable_path=self.chromedriver)
		self.browser.get('https://digital-clerk.azurewebsites.net/login_home')

	def tearDown(self):
		self.browser.close()

	def testLoginTitle(self):
		browser = self.browser
		self.assertIn('Digital Clerk', self.browser.title)

	def testLoginHTMLReturn(self):
		home_info = []
		home_info = self.browser.find_element_by_class_name('ome-info')

if __name__=='__main__':
	unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='functional_test_output'))
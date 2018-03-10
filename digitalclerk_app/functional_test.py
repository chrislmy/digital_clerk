from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC 
import os
import time
import unittest
import HtmlTestRunner

# Tests that need to be run on production server.
# class DashboardTests(unittest.TestCase):
# 	def setUp(self):
# 		self.options = webdriver.ChromeOptions()
# 		self.options.add_argument('--ignore-certificate-errors')
# 		self.options.add_argument('--ignore-ssl-errors')
# 		self.dir_path = os.path.dirname(os.path.realpath(__file__))
# 		self.chromedriver = self.dir_path + "/chromedriver"
# 		os.environ["webdriver.chrome.driver"] = self.chromedriver
# 		self.browser = webdriver.Chrome(chrome_options=self.options, executable_path=self.chromedriver)
# 		self.browser.get('http://127.0.0.1:8000/dashboard')

# 	def tearDown(self):
# 		time.sleep(1)
# 		self.browser.close()

# 	def testHomePageLayout(self):
# 		self.assertIn('Dashboard', self.browser.title)
# 		module_link = self.browser.find_element_by_xpath('//*[@id="test-module-link"]')
# 		module_link.click()
# 		self.assertIn('COMP103P', self.browser.title)

class OfficeHourDashboard(unittest.TestCase):
	def setUp(self):
		self.options = webdriver.ChromeOptions()
		self.options.add_argument('--ignore-certificate-errors')
		self.options.add_argument('--ignore-ssl-errors')
		self.dir_path = os.path.dirname(os.path.realpath(__file__))
		self.chromedriver = self.dir_path + "/chromedriver"
		os.environ["webdriver.chrome.driver"] = self.chromedriver
		self.browser = webdriver.Chrome(chrome_options=self.options, executable_path=self.chromedriver)
		self.browser.get('http://127.0.0.1:8000/dashboard/module_details/COMP103P')

	def tearDown(self):
		time.sleep(1)
		self.browser.close()

	def testOfficeHourCalendar(self):
		self.assertIn('COMP103P', self.browser.title)
		calendar_date = self.browser.find_element_by_xpath('//*[@id="officeHourCalendar"]/div[2]/div/table/tbody/tr/td/div/div/div[4]/div[2]/table/thead/tr/td[6]')
		calendar_date.click()
		self.browser.implicitly_wait(5)

	def testAddOfficeHour(self):
		self.assertIn('COMP103P', self.browser.title)
		calendar_date = self.browser.find_element_by_xpath('//*[@id="officeHourCalendar"]/div[2]/div/table/tbody/tr/td/div/div/div[4]/div[2]/table/thead/tr/td[6]')
		calendar_date.click()
		self.browser.implicitly_wait(5)
		title_input = self.browser.find_element_by_xpath('//*[@id="id_office_hour_title"]')
		location_input = self.browser.find_element_by_xpath('//*[@id="id_location"]')
		title_input.send_keys('Test Title LOL')
		location_input.send_keys('In my House LUL')
		add_office_hour_btn = self.browser.find_element_by_xpath('//*[@id="editOfficeHour"]')

	def testAddOfficeHourNoDetail(self):
		self.assertIn('COMP103P', self.browser.title)
		calendar_date = self.browser.find_element_by_xpath('//*[@id="officeHourCalendar"]/div[2]/div/table/tbody/tr/td/div/div/div[4]/div[2]/table/thead/tr/td[6]')
		calendar_date.click()
		self.browser.implicitly_wait(10)
		title_input = self.browser.find_element_by_xpath('//*[@id="id_office_hour_title"]')
		location_input = self.browser.find_element_by_xpath('//*[@id="id_location"]')
		location_input.send_keys('In my House LUL')
		add_office_hour_btn = self.browser.find_element_by_xpath('//*[@id="editOfficeHour"]')
		add_office_hour_btn.click()

	def testEditOfficeHour(self):
		self.assertIn('COMP103P', self.browser.title)
		test_event = self.browser.find_element_by_xpath('//*[@id="officeHourCalendar"]/div[2]/div/table/tbody/tr/td/div/div/div[5]/div[2]/table/tbody/tr/td[7]/a')
		test_event.click()
		self.browser.implicitly_wait(10)
		title_input = self.browser.find_element_by_xpath('//*[@id="id_office_hour_title"]')
		for x in range(0, 8):
			title_input.send_keys(Keys.BACKSPACE)
			time.sleep(0.3)
		title_input.send_keys('More Input')
		edit_btn = self.browser.find_element_by_xpath('//*[@id="editOfficeHour"]')
		edit_btn.click()

if __name__=='__main__':
	unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='functional_test_output'))


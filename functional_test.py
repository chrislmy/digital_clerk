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
		time.sleep(1)
		self.browser.close()

	def testLoginHomeLayout(self):
		home_info = self.browser.find_element_by_class_name('home-info')
		feature_info = self.browser.find_element_by_class_name('features-section')
		self.assertIn('Digital Clerk', self.browser.title)

	def testLoginAdminSuccess(self):
		login_admin_btn = self.browser.find_element_by_id('admin-login-button')
		login_admin_btn.click()
		self.browser.implicitly_wait(5)
		admin_username_field = self.browser.find_element_by_xpath('//*[@id="admin-username-field"]')
		admin_password_field = self.browser.find_element_by_id('admin-password-field')
		admin_username_field.send_keys('digitalclerk-admin')
		admin_password_field.send_keys('Hunter23')
		self.browser.find_element_by_xpath('//*[@id="adminLoginBtn"]').click()
		self.assertIn('Digital Clerk: Admin', self.browser.title)

	def testLoginAdminFailure(self):
		login_admin_btn = self.browser.find_element_by_id('admin-login-button')
		login_admin_btn.click()
		self.browser.implicitly_wait(5)
		admin_username_field = self.browser.find_element_by_xpath('//*[@id="admin-username-field"]')
		admin_password_field = self.browser.find_element_by_id('admin-password-field')
		admin_username_field.send_keys('wrong-admin')
		admin_password_field.send_keys('wrong-password')
		self.browser.find_element_by_xpath('//*[@id="adminLoginBtn"]').click()
		self.assertIn('Digital Clerk', self.browser.title)

	def testLoginWithUCLSuccess(self):
		# Click login as super admin
		login_ucl_btn = self.browser.find_element_by_id('login-home-login-button')
		login_ucl_btn.click()
		self.assertIn('UCL', self.browser.title)

		self.browser.implicitly_wait(5)
		username_field = self.browser.find_element_by_xpath('//*[@id="username"]')
		password_field = self.browser.find_element_by_xpath('//*[@id="password"]')
		username_field.send_keys('zcabmyl')
		password_field.send_keys('Sejarahsux1*')
		self.browser.find_element_by_xpath('//*[@id="index"]/div/div/div/div[1]/article/form/div/button').click()

	def testLoginWithUCLFailure(self):
		# Click login as super admin
		login_ucl_btn = self.browser.find_element_by_id('login-home-login-button')
		login_ucl_btn.click()
		self.assertIn('UCL', self.browser.title)

		self.browser.implicitly_wait(5)
		username_field = self.browser.find_element_by_xpath('//*[@id="username"]')
		password_field = self.browser.find_element_by_xpath('//*[@id="password"]')
		username_field.send_keys('wrong-username')
		password_field.send_keys('wrong-password*')
		self.browser.find_element_by_xpath('//*[@id="index"]/div/div/div/div[1]/article/form/div/button').click()
		self.assertIn('UCL Single Sign-on', self.browser.title)

if __name__=='__main__':
	unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='functional_test_output'))
from lettuce import *
from lettuce_webdriver.util import assert_false
from lettuce_webdriver.util import AssertContextManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import ChromeOptions, Chrome

use_firefox = True

class MyFirefox(webdriver.Firefox):
    def loaded(self):
        try:
            return 0 == self.execute_script("return jQuery.active")
        except WebDriverException:
            pass

    def wait_for_it(self):
        WebDriverWait(self, 10).until(MyFirefox.loaded, "Timeout waiting for page to load")

    def text_present(self, text):
        try:
            body = self.find_element_by_tag_name("body")
        except NoSuchElementException:
            return False
        return text in body.text

class MyChrome(Chrome):
    def loaded(self):
        try:
            return 0 == self.execute_script("return jQuery.active")
        except WebDriverException:
            pass

    def wait_for_it(self):
        WebDriverWait(self, 10).until(MyChrome.loaded, "Timeout waiting for page to load")

    def text_present(self, text):
        try:
            body = self.find_element_by_tag_name("body")
        except NoSuchElementException:
            return False
        return text in body.text

@before.all
def setup_browser():
    if use_firefox:
        world.browser = MyFirefox()
        world.browser.maximize_window()
    else:
        options = ChromeOptions()
        options.add_argument("--start-maximized");
        world.browser = MyChrome(executable_path='../../chromedriver', chrome_options=options)

@after.all
def tear_down(total):
    print "Total %d of %d scenarios passed!" % ( total.scenarios_ran, total.scenarios_passed )
    world.browser.quit()

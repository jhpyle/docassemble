from lettuce import *
from lettuce_webdriver.util import assert_false
from lettuce_webdriver.util import AssertContextManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

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

@before.all
def setup_browser():
    world.browser = MyFirefox()

@after.all
def tear_down(total):
    print "Total %d of %d scenarios passed!" % ( total.scenarios_ran, total.scenarios_passed )
    world.browser.quit()

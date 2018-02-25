from lettuce import step, world
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from random import randint
import time
import os
import re
import sys

def do_wait():
    if world.wait_seconds > 0:
        if world.wait_seconds > 3:
            time.sleep(world.wait_seconds + randint(-2, 2))
        else:
            time.sleep(world.wait_seconds)

def do_wait():
    if world.wait_seconds > 0:
        time.sleep(world.wait_seconds)

@step('I spend at least ([0-9]+) seconds? on each page')
def change_wait_seconds(step, secs):
    world.wait_seconds = float(secs)

@step('I click inside the signature area')
def click_inside(step):
    elem = WebDriverWait(world.browser, 10).until(
        EC.presence_of_element_located((By.ID, "sigcanvas"))
    )
    action = webdriver.common.action_chains.ActionChains(world.browser)
    action.move_to_element_with_offset(elem, 20, 20)
    action.click()
    action.perform()

@step('I am using the server "([^"]+)"')
def using_server(step, server):
    world.da_path = re.sub(r'/+$', r'', server)

@step('I log in with "([^"]+)" and "([^"]+)"')
def login(step, username, password):
    world.browser.get(world.da_path + "/user/sign-in")
    world.browser.wait_for_it()
    elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="Email"]').get_attribute("for"))
    elem.clear()
    elem.send_keys(username)
    elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="Password"]').get_attribute("for"))
    elem.clear()
    elem.send_keys(password)
    world.browser.find_element_by_xpath('//button[text()="Sign in"]').click()
    world.browser.wait_for_it()

@step('I upload the file "([^"]*)"')
def do_upload(step, value):
    elem = world.browser.find_element_by_xpath("//input[@type='file']")
    elem.clear()
    elem.send_keys(os.getcwd() + "/" + value)

@step('I set the text area to "([^"]*)"')
def set_text_area(step, value):
    elem = world.browser.find_element_by_xpath("//textarea")
    elem.clear()
    elem.send_keys(value)

@step('If I see it, I will click the link "([^"]+)"')
def click_link_if_exists(step, link_name):
    do_wait()
    try:
        world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
        world.browser.wait_for_it()
    except:
        pass

@step('I wait forever')
def wait_forever(step):
    time.sleep(999999)
    world.browser.wait_for_it()

@step('I start the interview "([^"]+)"')
def start_interview(step, interview_name):
    do_wait()
    world.browser.get(world.da_path + "/?i=" + interview_name + '&reset=1')
    world.browser.wait_for_it()

@step('I click the back button')
def click_back_button(step):
    do_wait()
    world.browser.find_element_by_css_selector('button.dabackicon').click()
    world.browser.wait_for_it()

@step('I click the question back button')
def click_question_back_button(step):
    do_wait()
    world.browser.find_element_by_id('questionbackbutton').click()
    world.browser.wait_for_it()

@step('I click the button "([^"]+)"')
def click_button(step, button_name):
    do_wait()
    success = False
    try:
        world.browser.find_element_by_xpath('//button[text()="' + button_name + '"]').click()
        success = True
    except:
       pass
    if not success:
       for elem in world.browser.find_elements_by_xpath('//a[text()="' + button_name + '"]'):
           try:
               elem.click()
               success = True
           except:
               pass
           if success:
               break
    assert success
    world.browser.wait_for_it()

@step('I click the "([^"]+)" button')
def click_button_post(step, choice):
    do_wait()
    success = False
    try:
        world.browser.find_element_by_xpath('//button[text()="' + button_name + '"]').click()
        success = True
    except:
        pass
    if not success:
        for elem in world.browser.find_elements_by_xpath('//a[text()="' + button_name + '"]'):
            try:
                elem.click()
                success = True
            except:
                pass
            if success:
                break
    assert success
    world.browser.wait_for_it()

@step('I click the link "([^"]+)"')
def click_link(step, link_name):
    do_wait()
    world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
    world.browser.wait_for_it()

@step('I select "([^"]+)" from the menu')
def menu_select(step, link_name):
    do_wait()
    try:
        world.browser.find_element_by_css_selector('#mobile-toggler').click()
    except:
        world.browser.find_element_by_css_selector('a.dropdown-toggle').click()
    time.sleep(0.5)
    world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
    world.browser.wait_for_it()

@step('I go to the help screen')
def click_help_tab(step):
    do_wait()
    world.browser.find_element_by_id('helptoggle').click()
    world.browser.wait_for_it()

@step('I go back to the question screen')
def click_back_to_question_button(step):
    do_wait()
    world.browser.find_element_by_id('backToQuestion').click()
    world.browser.wait_for_it()

@step('I click the second link "([^"]+)"')
def click_second_link(step, link_name):
    do_wait()
    world.browser.find_element_by_xpath('(//a[text()="' + link_name + '"])[2]').click()
    world.browser.wait_for_it()

@step('I should see the phrase "([^"]+)"')
def see_phrase(step, phrase):
    assert world.browser.text_present(phrase)

@step('I should not see the phrase "([^"]+)"')
def not_see_phrase(step, phrase):
    assert not world.browser.text_present(phrase)

@step("I should see the phrase '([^']+)'")
def see_phrase_sq(step, phrase):
    assert world.browser.text_present(phrase)

@step("I should not see the phrase '([^']+)'")
def not_see_phrase_sq(step, phrase):
    assert not world.browser.text_present(phrase)

@step('I set "([^"]+)" to "([^"]*)"')
def set_field(step, label, value):
    try:
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    except:
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label//a[text()="' + label + '"])/parent::label').get_attribute("for"))
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)

@step('I select "([^"]+)" as the "([^"]+)"')
def select_option(step, value, label):
    elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    for option in elem.find_elements_by_tag_name('option'):
        if option.text == value:
            option.click()
            break

@step('I choose "([^"]+)"')
def select_option_from_only_select(step, value):
    elem = world.browser.find_element_by_xpath('//select')
    for option in elem.find_elements_by_tag_name('option'):
        if option.text == value:
            option.click()
            break

@step('I wait (\d+) seconds?')
def wait_seconds(step, seconds):
    time.sleep(float(seconds))
    world.browser.wait_for_it()

@step('I should see that "([^"]+)" is "([^"]+)"')
def value_of_field(step, label, value):
    elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    assert elem.get_attribute("value") == value

@step('I set the text box to "([^"]*)"')
def set_text_box(step, value):
    elem = world.browser.find_element_by_xpath("//input[contains(@alt, 'Input box')]")
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)

@step('I set text box ([0-9]+) to "([^"]*)"')
def set_text_box(step, num, value):
    num = int(num) - 1
    elems = world.browser.find_elements_by_xpath("//input[contains(@alt, 'Input box')]")
    try:
        elems[num].clear()
    except:
        pass
    elems[num].send_keys(value)

@step('I click the "([^"]+)" option under "([^"]+)"')
def set_mc_option_under(step, option, label):
    div = world.browser.find_element_by_xpath('//label[text()="' + label + '"]/following-sibling::div')
    try:
        span = div.find_element_by_xpath('.//span[text()="' + option + '"]')
    except:
        span = div.find_element_by_xpath('.//span[text()[contains(.,"' + option + '")]]')
    option_label = span.find_element_by_xpath("..")
    option_label.click()
        
@step('I click the "([^"]+)" option')
def set_mc_option(step, choice):
    try:
        span_elem = world.browser.find_element_by_xpath('//span[text()="' + choice + '"]')
    except NoSuchElementException:
        span_elem = world.browser.find_element_by_xpath('//span[text()[contains(.,"' + choice + '")]]')
    label_elem = span_elem.find_element_by_xpath("..")
    label_elem.click()

@step('I click the option "([^"]+)" under "([^"]+)"')
def set_mc_option_under_pre(step, option, label):
    div = world.browser.find_element_by_xpath('//label[text()="' + label + '"]/following-sibling::div')
    try:
        span = div.find_element_by_xpath('.//span[text()="' + option + '"]')
    except:
        span = div.find_element_by_xpath('.//span[text()[contains(.,"' + option + '")]]')
    option_label = span.find_element_by_xpath("..")
    option_label.click()
        
@step('I click the option "([^"]+)"')
def set_mc_option_pre(step, choice):
    try:
        span_elem = world.browser.find_element_by_xpath('//span[text()="' + choice + '"]')
    except NoSuchElementException:
        span_elem = world.browser.find_element_by_xpath('//span[text()[contains(.,"' + choice + '")]]')
    label_elem = span_elem.find_element_by_xpath("..")
    label_elem.click()

@step('I should see "([^"]+)" as the title of the page')
def title_of_page(step, title):
    assert world.browser.title == title

@step('I should see "([^"]+)" as the URL of the page')
def url_of_page(step, url):
    assert world.browser.current_url == url

@step('I exit by clicking "([^"]+)"')
def exit_button(step, button_name):
    do_wait()
    world.browser.find_element_by_xpath('//button[text()="' + button_name + '"]').click()
    time.sleep(1.0)


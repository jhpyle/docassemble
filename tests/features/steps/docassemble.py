try:
    from aloe import step, world
except ImportError:
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

number_from_ordinal = dict(first=1, second=2, third=3, fourth=4, fifth=5, sixth=6, seventh=7, eighth=8, ninth=9, tenth=10)

def do_wait():
    if world.wait_seconds > 0:
        if world.wait_seconds > 3:
            time.sleep(world.wait_seconds + randint(-2, 2))
        else:
            time.sleep(world.wait_seconds)

@step(r'I spend at least ([0-9]+) seconds? on each page')
def change_wait_seconds(step, secs):
    world.wait_seconds = float(secs)

@step(r'I click inside the signature area')
def click_inside(step):
    elem = WebDriverWait(world.browser, 10).until(
        EC.presence_of_element_located((By.ID, "dasigcanvas"))
    )
    action = webdriver.common.action_chains.ActionChains(world.browser)
    action.move_to_element_with_offset(elem, 20, 20)
    action.click()
    action.perform()
    action.move_to_element_with_offset(elem, 20, 40)
    action.click()
    action.perform()
    action.move_to_element_with_offset(elem, 40, 40)
    action.click()
    action.perform()
    action.move_to_element_with_offset(elem, 40, 20)
    action.click()
    action.perform()

@step(r'I am using the server "([^"]+)"')
def using_server(step, server):
    world.da_path = re.sub(r'/+$', r'', server)

@step(r'I log in with "([^"]+)" and "([^"]+)"')
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

@step(r'I upload the file "([^"]*)"')
def do_upload(step, value):
    elem = world.browser.find_element_by_xpath("//input[@type='file']")
    elem.clear()
    elem.send_keys(os.getcwd() + "/" + value)

@step(r'I set the text area to "([^"]*)"')
def set_text_area(step, value):
    elem = world.browser.find_element_by_xpath("//textarea")
    elem.clear()
    elem.send_keys(value)

@step(r'If I see it, I will click the link "([^"]+)"')
def click_link_if_exists(step, link_name):
    do_wait()
    try:
        try:
            world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
            world.browser.wait_for_it()
        except:
            link_name += ' '
            world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
            world.browser.wait_for_it()
    except:
        pass

@step(r'I wait forever')
def wait_forever(step):
    time.sleep(999999)
    world.browser.wait_for_it()

@step(r'I launch the interview "([^"]+)"')
def launch_interview(step, interview_name):
    world.browser.get(world.da_path + "/interview?i=" + interview_name + '&reset=2')
    time.sleep(1)

@step(r'I start the interview "([^"]+)"')
def start_interview(step, interview_name):
    do_wait()
    world.browser.get(world.da_path + "/interview?i=" + interview_name + '&reset=2')
    world.browser.wait_for_it()
    elems = world.browser.find_elements_by_xpath('//h1[text()="Error"]')
    assert len(elems) == 0

@step(r'I start the possibly error-producing interview "([^"]+)"')
def start_error_interview(step, interview_name):
    do_wait()
    world.browser.get(world.da_path + "/interview?i=" + interview_name + '&reset=2')
    world.browser.wait_for_it()

@step(r'I reload the screen')
def reload_screen(step):
    do_wait()
    world.browser.get(re.sub(r'\#.*', '', world.browser.current_url))
    world.browser.wait_for_it()

@step(r'I click the back button')
def click_back_button(step):
    do_wait()
    world.browser.find_element_by_css_selector('button.dabackicon').click()
    world.browser.wait_for_it()

@step(r'I click the question back button')
def click_question_back_button(step):
    do_wait()
    world.browser.find_element_by_css_selector('.daquestionbackbutton').click()
    world.browser.wait_for_it()

@step(r'I click the button "([^"]+)"')
def click_button(step, button_name):
    world.browser.find_element_by_id('dapagetitle').click()
    do_wait()
    success = False
    try:
        world.browser.find_element_by_xpath('//button/span[text()="' + button_name + '"]').click()
        success = True
    except:
       pass
    if not success:
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

@step(r'I click the "([^"]+)" button')
def click_button_post(step, choice):
    do_wait()
    success = False
    try:
        world.browser.find_element_by_xpath('//button/span[text()="' + button_name + '"]').click()
        success = True
    except:
        pass
    if not success:
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

@step(r'I click the link "([^"]+)"')
def click_link(step, link_name):
    do_wait()
    try:
        world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
    except:
        link_name += " "
        world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
    world.browser.wait_for_it()

@step(r'I select "([^"]+)" from the menu')
def menu_select(step, link_name):
    do_wait()
    try:
        world.browser.find_element_by_css_selector('#damobile-toggler').click()
    except:
        world.browser.find_element_by_css_selector('a.dropdown-toggle').click()
    time.sleep(0.5)
    world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
    world.browser.wait_for_it()

@step(r'I go to the help screen')
def click_help_tab(step):
    do_wait()
    world.browser.find_element_by_id('dahelptoggle').click()
    world.browser.wait_for_it()

@step(r'I go back to the question screen')
def click_back_to_question_button(step):
    do_wait()
    world.browser.find_element_by_id('dabackToQuestion').click()
    world.browser.wait_for_it()

@step(r'I click the (first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) link "([^"]+)"')
def click_nth_link(step, ordinal, link_name):
    do_wait()
    try:
        world.browser.find_element_by_xpath('(//a[text()="' + link_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
    except:
        link_name += " "
        world.browser.find_element_by_xpath('(//a[text()="' + link_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
    world.browser.wait_for_it()

@step(r'I should see the phrase "([^"]+)"')
def see_phrase(step, phrase):
    take_screenshot()
    assert world.browser.text_present(phrase)

@step(r'I should not see the phrase "([^"]+)"')
def not_see_phrase(step, phrase):
    assert not world.browser.text_present(phrase)

@step("I should see the phrase '([^']+)'")
def see_phrase_sq(step, phrase):
    assert world.browser.text_present(phrase)

@step("I should not see the phrase '([^']+)'")
def not_see_phrase_sq(step, phrase):
    assert not world.browser.text_present(phrase)

@step(r'I set "([^"]+)" to "([^"]*)"')
def set_field(step, label, value):
    try:
        try:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
        except:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label//a[text()="' + label + '"])/parent::label').get_attribute("for"))
    except:
        label += " "
        try:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
        except:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label//a[text()="' + label + '"])/parent::label').get_attribute("for"))
    #try:
    elem.clear()
    #except:
    #    pass
    elem.send_keys(value)

@step(r'I set the (first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) "([^"]+)" to "([^"]*)"')
def set_nth_field(step, ordinal, label, value):
    try:
        try:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']').get_attribute("for"))
        except:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label//a[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']/parent::label').get_attribute("for"))
    except:
        label += " "
        try:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']').get_attribute("for"))
        except:
            elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label//a[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']/parent::label').get_attribute("for"))
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)
    elem.send_keys("\t")

@step(r'I select "([^"]+)" in the combobox')
def set_combobox(step, value):
    togglers = world.browser.find_elements_by_xpath("//button[contains(@class, 'dacomboboxtoggle')]")
    assert len(togglers) > 0
    togglers[0].click()
    time.sleep(0.5)
    found = False
    for elem in world.browser.find_elements_by_css_selector("div.combobox-container a.dropdown-item"):
        if elem.text == value:
            found = True
            elem.click()
            break
    assert found

@step(r'I set the combobox text to "([^"]*)"')
def set_combobox_text(step, value):
    elem = world.browser.find_element_by_css_selector("div.combobox-container input[type='text']")
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)

@step(r'I select "([^"]+)" as the "([^"]+)"')
def select_option(step, value, label):
    try:
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    except:
        label += " "
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    found = False
    for option in elem.find_elements_by_tag_name('option'):
        if option.text == value:
            found = True
            option.click()
            break
    assert found

@step(r'I select "([^"]+)" as the (first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) "([^"]+)"')
def select_nth_option(step, value, ordinal, label):
    try:
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label[text()="' + label + '"])[' + str(1+2*(number_from_ordinal[ordinal] - 1)) + ']').get_attribute("for"))
    except:
        label += " "
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('(//label[text()="' + label + '"])[' + str(1+2*(number_from_ordinal[ordinal] - 1)) + ']').get_attribute("for"))
    found = False
    for option in elem.find_elements_by_tag_name('option'):
        if option.text == value:
            found = True
            option.click()
            break
    assert found

@step(r'I choose "([^"]+)"')
def select_option_from_only_select(step, value):
    elem = world.browser.find_element_by_xpath('//select')
    for option in elem.find_elements_by_tag_name('option'):
        if option.text == value:
            option.click()
            break

@step(r'I wait (\d+) seconds?')
def wait_seconds(step, seconds):
    time.sleep(float(seconds))
    world.browser.wait_for_it()

@step(r'I should see that "([^"]+)" is "([^"]+)"')
def value_of_field(step, label, value):
    try:
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    except:
        label += " "
        elem = world.browser.find_element_by_id(world.browser.find_element_by_xpath('//label[text()="' + label + '"]').get_attribute("for"))
    assert elem.get_attribute("value") == value

@step(r'I set the text box to "([^"]*)"')
def set_text_box(step, value):
    elem = world.browser.find_element_by_xpath("//input[contains(@alt, 'Input box')]")
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)

@step(r'I set text box ([0-9]+) to "([^"]*)"')
def set_text_box(step, num, value):
    num = int(num) - 1
    elems = world.browser.find_elements_by_xpath("//input[contains(@alt, 'Input box')]")
    try:
        elems[num].clear()
    except:
        pass
    elems[num].send_keys(value)

@step(r'I click the "([^"]+)" option under "([^"]+)"')
def set_mc_option_under(step, option, label):
    try:
        div = world.browser.find_element_by_xpath('//label[text()="' + label + '"]/following-sibling::div')
    except:
        label += " "
        div = world.browser.find_element_by_xpath('//label[text()="' + label + '"]/following-sibling::div')
    try:
        span = div.find_element_by_xpath('.//span[text()="' + option + '"]')
    except:
        span = div.find_element_by_xpath('.//span[text()[contains(.,"' + option + '")]]')
    option_label = span.find_element_by_xpath("..")
    option_label.click()

@step(r'I click the "([^"]+)" option')
def set_mc_option(step, choice):
    try:
        span_elem = world.browser.find_element_by_xpath('//form[@id="daform"]//span[text()="' + choice + '"]')
    except NoSuchElementException:
        span_elem = world.browser.find_element_by_xpath('//form[@id="daform"]//span[text()[contains(.,"' + choice + '")]]')
    label_elem = span_elem.find_element_by_xpath("..")
    label_elem.click()

@step(r'I click the option "([^"]+)" under "([^"]+)"')
def set_mc_option_under_pre(step, option, label):
    try:
        div = world.browser.find_element_by_xpath('//label[text()="' + label + '"]/following-sibling::div')
    except:
        label += " "
        div = world.browser.find_element_by_xpath('//label[text()="' + label + '"]/following-sibling::div')
    try:
        span = div.find_element_by_xpath('.//span[text()="' + option + '"]')
    except:
        span = div.find_element_by_xpath('.//span[text()[contains(.,"' + option + '")]]')
    option_label = span.find_element_by_xpath("..")
    option_label.click()

@step(r'I click the option "([^"]+)"')
def set_mc_option_pre(step, choice):
    try:
        span_elem = world.browser.find_element_by_xpath('//span[text()="' + choice + '"]')
    except NoSuchElementException:
        span_elem = world.browser.find_element_by_xpath('//span[text()[contains(.,"' + choice + '")]]')
    label_elem = span_elem.find_element_by_xpath("..")
    label_elem.click()

@step(r'I should see "([^"]+)" as the title of the page')
def title_of_page(step, title):
    assert world.browser.title == title

@step(r'I should see "([^"]+)" as the URL of the page')
def url_of_page(step, url):
    assert world.browser.current_url == url

@step(r'I exit by clicking "([^"]+)"')
def exit_button(step, button_name):
    do_wait()
    success = False
    try:
        world.browser.find_element_by_xpath('//button/span[text()="' + button_name + '"]').click()
        success = True
    except:
        pass
    if not success:
        try:
            world.browser.find_element_by_xpath('//button[text()="' + button_name + '"]').click()
            success = True
        except:
            pass
    time.sleep(1.0)

@step(r'I save a screenshot to "([^"]+)"')
def save_screenshot(step, filename):
    world.browser.get_screenshot_as_file(filename)

@step(r'I set the window size to ([0-9]+)x([0-9]+)')
def change_window_size(step, xdimen, ydimen):
    world.browser.set_window_size(xdimen, ydimen)

@step(r'I unfocus')
def unfocus(step):
    world.browser.find_element_by_id('dapagetitle').click()

@step(r'I click the final link "([^"]+)"')
def finally_click_link(step, link_name):
    do_wait()
    try:
        world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()
    except:
        link_name += " "
        world.browser.find_element_by_xpath('//a[text()="' + link_name + '"]').click()


@step(r'I screenshot the page')
def save_screenshot(step):
    take_screenshot()

@step(r'I want to store screenshots in the folder "([^"]+)"')
def save_screenshot(step, directory):
    if world.headless:
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)
        world.screenshot_folder = directory
        world.screenshot_number = 0

def take_screenshot():
    if world.headless and world.screenshot_folder:
        world.screenshot_number += 1
        elem = world.browser.find_element_by_id("dabody")
        world.browser.set_window_size(1005, elem.size["height"] + 150)
        world.browser.get_screenshot_as_file(os.path.join(world.screenshot_folder, "%05d.png") % (world.screenshot_number,))
        world.browser.execute_script("window.open('');")
        world.browser.switch_to.window(world.browser.window_handles[1])
        world.browser.get(world.da_path + "/interview?i=" + world.interview_name + '&json=1')
        with open(os.path.join(world.screenshot_folder, "%05d.json") % (world.screenshot_number,), "w", encoding='utf-8') as f:
            the_json = json.loads(re.sub(r'^[^{]*{', '{', re.sub(r'</pre></body></html>$', '', world.browser.page_source)).strip())
            f.write(json.dumps(the_json, indent=1))
        world.browser.close()
        world.browser.switch_to.window(world.browser.window_handles[0])

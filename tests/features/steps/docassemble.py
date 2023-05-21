import time
import os
import re
import json
import shutil
from random import randint, random
from behave import step, use_step_matcher  # pylint: disable=import-error,no-name-in-module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

use_step_matcher('re')

number_from_ordinal = {'first': 1,
                       'second': 2,
                       'third': 3,
                       'fourth': 4,
                       'fifth': 5,
                       'sixth': 6,
                       'seventh': 7,
                       'eighth': 8,
                       'ninth': 9,
                       'tenth': 10}


def do_wait(context):
    if context.wait_seconds > 0:
        if context.wait_seconds > 3:
            time.sleep(context.wait_seconds + randint(-2, 2))
        else:
            time.sleep(context.wait_seconds)


@step(r'I spend at least (?P<secs>[0-9]+) seconds? on each page')
def change_wait_seconds(context, secs):
    context.wait_seconds = float(secs)


@step(r'I click inside the signature area')
def click_inside(context):
    elem = WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "dasigcanvas"))
    )
    action = ActionChains(context.browser)
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


@step(r'I am using the server "(?P<server>[^"]+)"')
def using_server(context, server):
    context.da_path = re.sub(r'/+$', r'', server)


@step(r'I log in with "(?P<username>[^"]+)" and "(?P<password>[^"]+)"')
def login(context, username, password):
    context.browser.get(context.da_path + "/user/sign-in")
    context.browser.wait_for_it()
    elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="Email"]').get_attribute("for"))
    elem.clear()
    elem.send_keys(username)
    elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="Password"]').get_attribute("for"))
    elem.clear()
    elem.send_keys(password)
    context.browser.find_element(By.XPATH, '//button[text()="Sign in"]').click()
    context.browser.wait_for_it()


@step(r'I upload the file "(?P<value>[^"]*)"')
def do_upload(context, value):
    time.sleep(2)
    div = context.browser.find_element(By.CSS_SELECTOR, 'div.file-caption')
    context.browser.execute_script('arguments[0].style = ""; arguments[0].style.display = "none";', div)
    div = context.browser.find_element(By.CSS_SELECTOR, 'div.btn-file')
    context.browser.execute_script('arguments[0].style = ""; arguments[0].style.position = "inherit";', div)
    span = context.browser.find_element(By.CSS_SELECTOR, 'span.hidden-xs')
    context.browser.execute_script('arguments[0].style = ""; arguments[0].style.display = "none";', span)
    elem = context.browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
    context.browser.execute_script('arguments[0].style = ""; arguments[0].style.display = "block"; arguments[0].style.visibility = "visible"; arguments[0].style.opacity = "100";', elem)
    elem.clear()
    elem.send_keys(value)
    time.sleep(2)


@step(r'I set the text area to "(?P<value>[^"]*)"')
def set_text_area(context, value):
    elem = context.browser.find_element(By.XPATH, "//textarea")
    elem.clear()
    elem.send_keys(value)


@step(r'If I see it, I will click the link "(?P<link_name>[^"]+)"')
def click_link_if_exists(context, link_name):
    do_wait(context)
    try:
        try:
            context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()
            context.browser.wait_for_it()
        except:
            link_name += ' '
            context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()
            context.browser.wait_for_it()
    except:
        pass


@step(r'I wait forever')
def wait_forever(context):
    time.sleep(999999)
    context.browser.wait_for_it()


@step(r'I launch the interview "(?P<interview_name>[^"]+)"')
def launch_interview(context, interview_name):
    context.browser.get(context.da_path + "/interview?i=" + interview_name + '&reset=2')
    time.sleep(1)


@step(r'I start the interview "(?P<interview_name>[^"]+)"')
def start_interview(context, interview_name):
    do_wait(context)
    context.interview_name = interview_name
    context.browser.get(context.da_path + "/interview?i=" + interview_name + '&reset=2')
    context.browser.wait_for_it()
    elems = context.browser.find_elements(By.XPATH, '//h1[text()="Error"]')
    assert len(elems) == 0


@step(r'I start the possibly error-producing interview "(?P<interview_name>[^"]+)"')
def start_error_interview(context, interview_name):
    do_wait(context)
    context.browser.get(context.da_path + "/interview?i=" + interview_name + '&reset=2')
    context.browser.wait_for_it()


@step(r'I reload the screen')
def reload_screen(context):
    do_wait(context)
    context.browser.get(re.sub(r'\#.*', '', context.browser.current_url))
    context.browser.wait_for_it()


@step(r'I click the back button')
def click_back_button(context):
    do_wait(context)
    context.browser.find_element(By.CSS_SELECTOR, 'button.dabackicon').click()
    context.browser.wait_for_it()


@step(r'I click the question back button')
def click_question_back_button(context):
    do_wait(context)
    context.browser.find_element(By.CSS_SELECTOR, '.daquestionbackbutton').click()
    context.browser.wait_for_it()


@step(r'I click the button "(?P<button_name>[^"]+)"')
def click_button(context, button_name):
    try:
        context.browser.find_element(By.ID, 'daMainQuestion').click()
    except:
        pass
    do_wait(context)
    success = False
    try:
        element = context.browser.find_element(By.XPATH, '//button[text()="' + button_name + '"]')
        context.browser.execute_script('$(arguments[0]).click()', element)
        success = True
    except:
        pass
    if not success:
        for elem in context.browser.find_elements(By.XPATH, '//a[text()="' + button_name + '"]'):
            if elem.is_displayed():
                try:
                    context.browser.execute_script('$(arguments[0]).click()', elem)
                    success = True
                except:
                    pass
                if success:
                    break
    if not success:
        try:
            elem = context.browser.find_element(By.XPATH, '//button/span[text()="' + button_name + '"]')
            context.browser.execute_script('$(arguments[0]).click()', elem)
            success = True
        except:
            pass
    assert success
    context.browser.wait_for_it()


@step(r'I click the (?P<ordinal>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) button "(?P<button_name>[^"]+)"')
def click_nth_button(context, ordinal, button_name):
    try:
        context.browser.find_element(By.ID, 'daMainQuestion').click()
    except:
        pass
    do_wait(context)
    success = False
    try:
        context.browser.find_element(By.XPATH, '(//button[text()="' + button_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
        success = True
    except:
        pass
    if not success:
        try:
            context.browser.find_element(By.XPATH, '(//button/span[text()="' + button_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
            success = True
        except:
            pass
    assert success
    context.browser.wait_for_it()


@step(r'I click the "(?P<button_name>[^"]+)" button')
def click_button_post(context, button_name):
    do_wait(context)
    success = False
    try:
        context.browser.find_element(By.XPATH, '//button[text()="' + button_name + '"]').click()
        success = True
    except:
        pass
    if not success:
        try:
            context.browser.find_element(By.XPATH, '//button/span[text()="' + button_name + '"]').click()
            success = True
        except:
            pass
    if not success:
        for elem in context.browser.find_elements(By.XPATH, '//a[text()="' + button_name + '"]'):
            try:
                elem.click()
                success = True
            except:
                pass
            if success:
                break
    assert success
    context.browser.wait_for_it()


@step(r'I click the link "(?P<link_name>[^"]+)"')
def click_link(context, link_name):
    do_wait(context)
    try:
        context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()
    except:
        link_name += " "
        context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()
    context.browser.wait_for_it()


@step(r'I click the help icon for "(?P<link_name>[^"]+)"')
def click_help_icon_link(context, link_name):
    do_wait(context)
    context.browser.find_element(By.XPATH, '//label[text()="' + link_name + '"]/a').click()
    context.browser.wait_for_it()


@step(r'I select "(?P<link_name>[^"]+)" from the menu')
def menu_select(context, link_name):
    do_wait(context)
    try:
        context.browser.find_element(By.CSS_SELECTOR, '#damobile-toggler').click()
    except:
        context.browser.find_element(By.CSS_SELECTOR, 'a.dropdown-toggle').click()
    time.sleep(0.5)
    context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()
    context.browser.wait_for_it()


@step(r'I go to the help screen')
def click_help_tab(context):
    do_wait(context)
    context.browser.find_element(By.ID, 'dahelptoggle').click()
    time.sleep(0.5)
    context.browser.wait_for_it()


@step(r'I go back to the question screen')
def click_back_to_question_button(context):
    do_wait(context)
    context.browser.find_element(By.ID, 'dabackToQuestion').click()
    time.sleep(0.5)
    context.browser.wait_for_it()


@step(r'I click the (?P<ordinal>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) link "(?P<link_name>[^"]+)"')
def click_nth_link(context, ordinal, link_name):
    do_wait(context)
    try:
        context.browser.find_element(By.XPATH, '(//a[text()="' + link_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
    except:
        try:
            context.browser.find_element(By.XPATH, '(//a/span[text()="' + link_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
        except:
            link_name += " "
            try:
                context.browser.find_element(By.XPATH, '(//a[text()="' + link_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
            except:
                context.browser.find_element(By.XPATH, '(//a/span[text()="' + link_name + '"])[' + str(number_from_ordinal[ordinal]) + ']').click()
    context.browser.wait_for_it()


@step(r'I should see the phrase "(?P<phrase>[^"]+)"')
def see_phrase(context, phrase):
    take_screenshot(context)
    assert context.browser.text_present(phrase)


@step(r'I should not see the phrase "(?P<phrase>[^"]+)"')
def not_see_phrase(context, phrase):
    assert not context.browser.text_present(phrase)


@step("I should see the phrase '(?P<phrase>[^']+)'")
def see_phrase_sq(context, phrase):
    assert context.browser.text_present(phrase)


@step("I should not see the phrase '(?P<phrase>[^']+)'")
def not_see_phrase_sq(context, phrase):
    assert not context.browser.text_present(phrase)


@step(r'I set "(?P<label>[^"]+)" to "(?P<value>[^"]*)"')
def set_field(context, label, value):
    try:
        try:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]').get_attribute("for"))
        except:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label//a[text()="' + label + '"])/parent::label').get_attribute("for"))
    except:
        label += " "
        try:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]').get_attribute("for"))
        except:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label//a[text()="' + label + '"])/parent::label').get_attribute("for"))
    # try:
    elem.clear()
    # except:
    #     pass
    elem.send_keys(value)


@step(r'I set the (?P<ordinal>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) "(?P<label>[^"]+)" to "(?P<value>[^"]*)"')
def set_nth_field(context, ordinal, label, value):
    try:
        try:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']').get_attribute("for"))
        except:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label//a[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']/parent::label').get_attribute("for"))
    except:
        label += " "
        try:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']').get_attribute("for"))
        except:
            elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label//a[text()="' + label + '"])[' + str(number_from_ordinal[ordinal]) + ']/parent::label').get_attribute("for"))
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)
    elem.send_keys("\t")


@step(r'I select "(?P<value>[^"]+)" in the combobox')
def set_combobox(context, value):
    togglers = context.browser.find_elements(By.XPATH, "//button[contains(@class, 'dacomboboxtoggle')]")
    assert len(togglers) > 0
    togglers[0].click()
    time.sleep(0.5)
    found = False
    for elem in context.browser.find_elements(By.CSS_SELECTOR, "div.combobox-container .dropdown-item"):
        if elem.text == value:
            found = True
            elem.click()
            break
    assert found


@step(r'I set the combobox text to "(?P<value>[^"]*)"')
def set_combobox_text(context, value):
    elem = context.browser.find_element(By.CSS_SELECTOR, "div.combobox-container input[type='text']")
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)


@step(r'I select "(?P<value>[^"]+)" from the combobox dropdown')
def select_combobox_option(context, value):
    found = False
    for elem in context.browser.find_elements(By.CSS_SELECTOR, "div.combobox-container .dropdown-item"):
        if elem.text == value:
            found = True
            elem.click()
            break
    assert found


@step(r'I select "(?P<value>[^"]+)" as the "(?P<label>[^"]+)"')
def select_option(context, value, label):
    try:
        elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]').get_attribute("for"))
    except:
        label += " "
        elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]').get_attribute("for"))
    found = False
    for option in elem.find_elements(By.TAG_NAME, 'option'):
        if option.text == value:
            found = True
            option.click()
            break
    assert found


@step(r'I select "(?P<value>[^"]+)" as the (?P<ordinal>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) "(?P<label>[^"]+)"')
def select_nth_option(context, value, ordinal, label):
    try:
        elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label[text()="' + label + '"])[' + str(1+2*(number_from_ordinal[ordinal] - 1)) + ']').get_attribute("for"))
    except:
        label += " "
        elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '(//label[text()="' + label + '"])[' + str(1+2*(number_from_ordinal[ordinal] - 1)) + ']').get_attribute("for"))
    found = False
    for option in elem.find_elements(By.TAG_NAME, 'option'):
        if option.text == value:
            found = True
            option.click()
            break
    assert found


@step(r'I choose "(?P<value>[^"]+)"')
def select_option_from_only_select(context, value):
    elem = context.browser.find_element(By.XPATH, '//select')
    for option in elem.find_elements(By.TAG_NAME, 'option'):
        if option.text == value:
            option.click()
            break


@step(r'I wait (?P<seconds>[\d\.]+) seconds?')
def wait_seconds(context, seconds):
    time.sleep(float(seconds) + random())
    context.browser.wait_for_it()


@step(r'I should see that "(?P<label>[^"]+)" is "(?P<value>[^"]+)"')
def value_of_field(context, label, value):
    try:
        elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]').get_attribute("for"))
    except:
        label += " "
        elem = context.browser.find_element(By.ID, context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]').get_attribute("for"))
    assert elem.get_attribute("value") == value


@step(r'I set the text box to "(?P<value>[^"]*)"')
def set_text_box(context, value):
    elem = context.browser.find_element(By.XPATH, "//input[contains(@alt, 'Input box')]")
    try:
        elem.clear()
    except:
        pass
    elem.send_keys(value)


@step(r'I set text box (?P<num>[0-9]+) to "(?P<value>[^"]*)"')
def set_text_box_alt(context, num, value):
    num = int(num) - 1
    elems = context.browser.find_elements(By.XPATH, "//input[contains(@alt, 'Input box')]")
    try:
        elems[num].clear()
    except:
        pass
    elems[num].send_keys(value)


@step(r'I click the "(?P<option>[^"]+)" option under "(?P<label>[^"]+)"')
def set_mc_option_under(context, option, label):
    try:
        div = context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]/following-sibling::div')
    except:
        label += " "
        div = context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]/following-sibling::div')
    try:
        span = div.find_element(By.XPATH, './/span[text()="' + option + '"]')
    except:
        span = div.find_element(By.XPATH, './/span[text()[contains(.,"' + option + '")]]')
    option_label = span.find_element(By.XPATH, "..")
    option_label.click()


@step(r'I click the "(?P<choice>[^"]+)" option')
def set_mc_option(context, choice):
    try:
        span_elem = context.browser.find_element(By.XPATH, '//form[@id="daform"]//span[text()="' + choice + '"]')
    except NoSuchElementException:
        span_elem = context.browser.find_element(By.XPATH, '//form[@id="daform"]//span[text()[contains(.,"' + choice + '")]]')
    label_elem = span_elem.find_element(By.XPATH, "..")
    label_elem.click()


@step(r'I click the option "(?P<option>[^"]+)" under "(?P<label>[^"]+)"')
def set_mc_option_under_pre(context, option, label):
    try:
        div = context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]/following-sibling::div')
    except:
        label += " "
        div = context.browser.find_element(By.XPATH, '//label[text()="' + label + '"]/following-sibling::div')
    try:
        span = div.find_element(By.XPATH, './/span[text()="' + option + '"]')
    except:
        span = div.find_element(By.XPATH, './/span[text()[contains(.,"' + option + '")]]')
    option_label = span.find_element(By.XPATH, "..")
    option_label.click()


@step(r'I click the option "(?P<choice>[^"]+)"')
def set_mc_option_pre(context, choice):
    try:
        span_elem = context.browser.find_element(By.XPATH, '//span[text()="' + choice + '"]')
    except NoSuchElementException:
        span_elem = context.browser.find_element(By.XPATH, '//span[text()[contains(.,"' + choice + '")]]')
    label_elem = span_elem.find_element(By.XPATH, "..")
    label_elem.click()


@step(r'I click the (?P<ordinal>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) option "(?P<choice>[^"]+)"')
def set_nth_mc_option_pre(context, ordinal, choice):
    try:
        span_elem = context.browser.find_element(By.XPATH, '(//span[text()="' + choice + '"])[' + str(number_from_ordinal[ordinal]) + ']')
    except NoSuchElementException:
        span_elem = context.browser.find_element(By.XPATH, '(//span[text()[contains(.,"' + choice + '")]])[' + str(number_from_ordinal[ordinal]) + ']')
    label_elem = span_elem.find_element(By.XPATH, "..")
    label_elem.click()
    # span_elem.click()


@step(r'I should see "(?P<title>[^"]+)" as the title of the page')
def title_of_page(context, title):
    assert context.browser.title == title


@step(r'I should see "(?P<url>[^"]+)" as the URL of the page')
def url_of_page(context, url):
    assert context.browser.current_url == url


@step(r'I exit by clicking "(?P<button_name>[^"]+)"')
def exit_button(context, button_name):
    do_wait(context)
    success = False
    try:
        context.browser.find_element(By.XPATH, '//button[text()="' + button_name + '"]').click()
        success = True
    except:
        pass
    if not success:
        try:
            context.browser.find_element(By.XPATH, '//button/span[text()="' + button_name + '"]').click()
            success = True
        except:
            pass
    time.sleep(1.0)


@step(r'I save a screenshot to "(?P<filename>[^"]+)"')
def save_screenshot(context, filename):
    context.browser.get_screenshot_as_file(filename)


@step(r'I set the window size to (?P<xdimen>[0-9]+)x(?P<ydimen>[0-9]+)')
def change_window_size(context, xdimen, ydimen):
    context.browser.set_window_size(xdimen, ydimen)


@step(r'I unfocus')
def unfocus(context):
    context.browser.find_element(By.ID, 'daMainQuestion').click()


@step(r'I click the final link "(?P<link_name>[^"]+)"')
def finally_click_link(context, link_name):
    do_wait(context)
    try:
        context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()
    except:
        link_name += " "
        context.browser.find_element(By.XPATH, '//a[text()="' + link_name + '"]').click()


@step(r'I screenshot the page')
def save_screenshot_page(context):
    take_screenshot(context)


@step(r'I want to store screenshots in the folder "(?P<directory>[^"]+)"')
def save_screenshot_folders(context, directory):
    if context.headless:
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)
        context.screenshot_folder = directory
        context.screenshot_number = 0


def take_screenshot(context):
    if context.headless and context.screenshot_folder:
        context.screenshot_number += 1
        elem = context.browser.find_element(By.ID, "dabody")
        context.browser.set_window_size(1005, elem.size["height"] + 150)
        context.browser.get_screenshot_as_file(os.path.join(context.screenshot_folder, "%05d.png") % (context.screenshot_number,))
        context.browser.execute_script("window.open('');")
        context.browser.switch_to.window(context.browser.window_handles[1])
        context.browser.get(context.da_path + "/interview?i=" + context.interview_name + '&json=1')
        with open(os.path.join(context.screenshot_folder, "%05d.json") % (context.screenshot_number,), "w", encoding='utf-8') as f:
            the_json = json.loads(re.sub(r'^[^{]*{', '{', re.sub(r'</pre></body></html>$', '', context.browser.page_source)).strip())
            f.write(json.dumps(the_json, indent=1))
        context.browser.close()
        context.browser.switch_to.window(context.browser.window_handles[0])


@step(r'I click the (?P<ordinal>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) choice help')
def click_nth_choice_help(context, ordinal):
    context.browser.find_element(By.XPATH, '(//div[contains(@class, "dachoicehelp")])[' + str(number_from_ordinal[ordinal]) + ']').click()


@step(r'I click accept in the alert')
def accept_alert(context):
    time.sleep(1)
    context.browser.switch_to.alert.accept()


@step(r'I switch to the new tab')
def switch_tab(context):
    context.browser.switch_to.window(context.browser.window_handles[-1])


@step(r'I scroll to the bottom')
def scroll_bottom(context):
    context.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")

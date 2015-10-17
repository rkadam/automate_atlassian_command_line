__author__ = 'Raju Kadam'

import os
from selenium.webdriver import *
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import sys

class WikiBrowser:
    def __init__(self, driver):
        self.driver = driver
        self.browser = None

    def connect(self):
        self.browser = self.driver()
        self.browser.set_window_size(1120, 550)

    # noinspection PyBroadException
    def login(self, login_type, base_url, userid, password):
        try:
            if self.browser is None:
                self.connect()
        except:
            print "Unable to create Selenium Driver Instance."
            sys.exit(0)

        browser = self.browser
        login_elem_dict = self.get_login_elements(login_type, base_url)
        #print login_elem_dict
        new_base_url = None

        if not self.verify_admin_access():
            try:
                browser.get(login_elem_dict['param_login_url'])
                browser.implicitly_wait(1)
                os_name = browser.find_element_by_id(login_elem_dict['param_user'])
                os_name.clear()
                os_name.send_keys(userid)

                os_password = browser.find_element_by_id(login_elem_dict['param_password'])
                os_password.clear()
                os_password.send_keys(password)

                browser.find_element_by_id(login_elem_dict['param_submit']).click()
                time.sleep(1)

                # On Premise Atlassian application usually asks for Authentication for one more time.
                new_base_url = login_elem_dict['param_new_base_url']
                browser.get(new_base_url + "/admin/console.action")
                if login_type == 'other':
                    browser.find_element_by_id('password').send_keys(password)
                    browser.find_element_by_id('authenticateButton').click()

                # Verify that we are on Administration Console.
                # This will confirm, we are logged in as Global Administrator.
                print browser.find_element_by_class_name('admin-heading').text
                print browser.find_element_by_class_name('admin-subtitle').text

            except NoSuchElementException:
                print "Unable to login to Wiki Application, exiting."
                browser.close()
                sys.exit(0)

        return browser,new_base_url

    def get_login_elements(self, login_to, base_url):

        if login_to == 'atlassian.net':
            return {
                    'param_user': 'username',
                    'param_password': 'password',
                    'param_submit': 'login',
                    'param_login_url': base_url + "/login?dest-url=/wiki",
                    'param_new_base_url': base_url + "/wiki"
            }

        return {
                'param_user': 'os_username',
                'param_password': 'os_password',
                'param_submit': 'loginButton',
                'param_login_url': base_url + '/login.action',
                'param_new_base_url': base_url
                }

    def update_general_configuration(self, browser, new_base_url):
        general_config_url = new_base_url + "/admin/editgeneralconfig.action"
        browser.get(general_config_url)
        site_title = browser.find_element_by_id('siteTitle')
        site_title.clear()
        site_title.send_keys('Pongbot\'s confluence')
        browser.find_element_by_id('confirm').click()
        browser.quit()

    def update_global_custom_colour_scheme(self, browser, new_base_url, new_color_scheme_file):
        # Let's get to "View Colour Scheme Settings" screen (lookandfeel.action)
        custom_colour_scheme_url = new_base_url + "/admin/lookandfeel.action"
        browser.get(custom_colour_scheme_url)
        browser.find_element_by_id("edit-scheme-link").click()
        time.sleep(2)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "cancel")))

        # Clicking "Edit" link above makes all hidden elements in div "edit-scheme" visible for FireFox, Chrome.
        # Let's make sure these hidden elements are visible for PhantomJS browser too.
        browser.execute_script("document.getElementById('edit-scheme').style.display='block'")

        global_custom_color_scheme_dict = {}
        with open(new_color_scheme_file) as colour_scheme_file:
            for line in colour_scheme_file:
                colour_name, colour_value = line.partition("=")[::2]
                global_custom_color_scheme_dict[colour_name] = colour_value.strip()

        for colour_name, colour_value in global_custom_color_scheme_dict.iteritems():
            colour_element = browser.find_element_by_id(colour_name)
            colour_element.clear()
            colour_element.send_keys(colour_value)

        browser.find_element_by_name("confirm").click()
        browser.quit()

    def verify_admin_access(self):
        browser = self.browser
        try:
            browser.implicitly_wait(1)
            browser.find_element_by_id("system-admin-menu")
            return True
        except NoSuchElementException:
            return False


if '__main__' == __name__:
    #wiki_browser = WikiBrowser(Firefox)
    wiki_browser = WikiBrowser(PhantomJS)
    # on premise Wiki
    #(browser, new_base_url) = wiki_browser.login('other', 'https://localhost:2990', 'admin', 'admin')
    # On Demand, Atlassian.net wiki
    #(browser, new_base_url) = wiki_browser.login('atlassian.net', 'https://example.atlassian.net', 'userid', 'password')
    wiki_browser.update_global_custom_colour_scheme(browser, new_base_url, "config/wiki_global_custom_colour_scheme.dev")
    #wiki_browser.update_general_configuration(browser,new_base_url)

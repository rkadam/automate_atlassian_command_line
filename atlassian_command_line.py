__author__ = 'Raju Kadam'

import os
from selenium.webdriver import *
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import xml.etree.ElementTree as ET
import click
import random

import time
import sys

import requests
# Disable warnings about not verifying SSL access.
requests.packages.urllib3.disable_warnings()

header_params = {"content-type": "application/json"}


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
                assert browser.find_element_by_class_name('admin-heading').text == 'Administration Console'
                assert browser.find_element_by_class_name('admin-subtitle').text == 'The Administration Console is the interface for managing and maintaining Confluence.'

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
        click.echo('Current title: %s' % site_title.get_attribute("value"))
        site_title.clear()
        site_title.send_keys('Pongbot\'s confluence %s' % str(random.randint(1,10)))
        click.echo('New title: %s' % site_title.get_attribute("value"))
        browser.find_element_by_id('confirm').click()

    def update_global_color_scheme(self, browser, new_base_url, new_color_scheme_file):
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

    def get_wiki_space_list(self, space_type, base_url, userid, password):
        spaces = []

        space_list_rest_url = base_url + ("/rest/prototype/1/space?max-results=10000&type=%s" % space_type)
        click.echo(space_list_rest_url)
        result = requests.get(space_list_rest_url,  headers=header_params, auth=(userid, password), verify=False)
        result.raise_for_status()

        # REST api spits out response in XML format instead of JSON!
        result_root = ET.fromstring(result.content)

        # Get all "space" nodes
        space_nodes = result_root.findall('space')
        for node in space_nodes:
            spaces.append(node.attrib['key'])

        return spaces

    def update_wiki_spaces_color_scheme(self, browser, base_url, userid, password):
        # This function will update color scheme for all wiki spaces to global color scheme.
        # "global" will return only team wiki spaces
        # "personal" will return only personal wiki spaces
        # "all" will return all wiki spaces available.
        space_keys = self.get_wiki_space_list("global", base_url, userid, password)
        click.echo(space_keys)

        # if needed, Update color scheme for each wiki space
        for key in space_keys:
            browser.get(base_url + "/spaces/lookandfeel.action?key=" + key)
            edit_button = browser.find_element_by_id('edit')
            if edit_button.get_attribute('name') == 'global':
                click.echo("Global color scheme is now activated for Wiki Space %s" % key)
                edit_button.click()
                #time.sleep(1)
            else:
                click.echo("Global color scheme is already selected for space: %s" % key)

    def verify_admin_access(self):
        browser = self.browser
        try:
            browser.implicitly_wait(1)
            browser.find_element_by_id("system-admin-menu")
            return True
        except NoSuchElementException:
            return False

    command_dictionary = {
        'update_global_color_scheme': update_global_color_scheme,
        'update_general_configuration': update_general_configuration,
        'update_wiki_spaces_color_scheme': update_wiki_spaces_color_scheme
    }


if '__main__' == __name__:
    '''
    wiki_browser = WikiBrowser(Firefox)
    #wiki_browser = WikiBrowser(PhantomJS)

    # on premise Wiki
    #(browser, new_base_url) = wiki_browser.login('other', 'https://localhost:2990', 'admin', 'admin')

    #On Demand, Atlassian.net wiki
    (browser, new_base_url) = wiki_browser.login('atlassian.net', 'https://example.atlassian.net', 'userid', 'password')
    wiki_browser.update_global_color_scheme(browser, new_base_url, "config/wiki_global_custom_colour_scheme.dev")
    wiki_browser.update_general_configuration(browser, new_base_url)

    browser.close()
    browser.quit()
    '''


@click.command()
@click.option('--app-type', type=click.Choice(['atlassian.net', 'other']),
              default='atlassian.net',
              help='Enter type of application that you want to automate.')
@click.option('--base-url', default='https://pongbot.atlassian.net', help="Enter base URL for Atlassian application")
@click.option('--userid', prompt='Enter your userid')
@click.option('--password', prompt='Enter your credentials', hide_input=True, confirmation_prompt=True)
@click.option('--action', multiple=True, default=['update_global_color_scheme'])
def start(app_type, base_url, userid, password, action):
    """
    Atlassian Command Line aka ACL - Automate the tasks that you can not!
    :param: app_type, base_url, userid, password, action
    :return:
    """
    """
    :param string:
    :return:
    """
    click.echo('Automating application located at %s' % base_url)
    click.echo()

    #wiki_browser = WikiBrowser(Firefox)
    wiki_browser = WikiBrowser(PhantomJS)
    (browser, new_base_url) = wiki_browser.login(app_type, base_url, userid, password)
    #wiki_browser.update_global_custom_colour_scheme(browser, new_base_url, "config/wiki_global_custom_colour_scheme.dev")

    for act in action:
        click.echo('Executing command: %s' % act)
        if act == 'update_global_color_scheme':
            wiki_browser.command_dictionary[act](wiki_browser, browser, new_base_url, "config/wiki_global_custom_colour_scheme.dev")
            #wiki_browser.update_global_color_scheme(browser, new_base_url, "config/wiki_global_custom_colour_scheme.default")

        if act == 'update_general_configuration':
            wiki_browser.command_dictionary[act](wiki_browser, browser, new_base_url)
            #wiki_browser.update_general_configuration(browser, new_base_url)

        if act == 'update_wiki_spaces_color_scheme':
            wiki_browser.command_dictionary[act](wiki_browser, browser, new_base_url, userid, password)
            #wiki_browser.update_wiki_spaces_color_scheme(browser, new_base_url, userid, password)

        click.echo()

    browser.close()
    browser.quit()

__author__ = 'Raju Kadam'

import os
from selenium.webdriver import *
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import xml.etree.ElementTree as ET
import click
import random

import time
import datetime
import sys

import requests
import shutil

# Disable warnings about not verifying SSL access.
requests.packages.urllib3.disable_warnings()

header_params = {"content-type": "application/json"}

# TODO:
# Current priority is to have working entry available for Codegeist participation.
# Later we will use Composition to share the common methods and let individual classes do their distinct work.
# Using Composition, we will keep all common functions such as connect(), get_login_elements(), login(),
#   verify_admin_access(), check_ldap_sync_status() in *AtlassianBrowser* (it will be a new class).
# And application specific methods such as
#   disable_project_notification_schemes(), check_jira_mail_queue_status() will remain in *JIRABrowser*
#   update_global_color_scheme(), update_general_configuration() and update_wiki_spaces_color_scheme() remain in *WikiBrowser*
# Till that happens you will see little bit overlapping between all these classes.

class JIRABrowser:
    def __init__(self, driver):
        self.driver = driver
        self.browser = None

    def connect(self):
        self.browser = self.driver()
        self.browser.set_window_size(1120, 550)

    def get_login_elements(self, login_to, base_url):

        if login_to == 'atlassian.net':
            return {
                    'param_user': 'username',
                    'param_password': 'password',
                    'param_submit': 'login',
                    'param_login_url': base_url + "/login",
                    'param_new_base_url': base_url
            }

        return {
                'param_user': 'login-form-username',
                'param_password': 'login-form-password',
                'param_submit': 'login-form-submit',
                'param_login_url': base_url + '/login.jsp',
                'param_new_base_url': base_url
                }

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

                #click.echo('Login as Admin user')

                # On Premise Atlassian application usually asks Authentication for one more time.
                new_base_url = login_elem_dict['param_new_base_url']
                browser.get(new_base_url + "/secure/admin/ViewApplicationProperties.jspa")
                if login_type == 'other':
                    browser.find_element_by_id('login-form-authenticatePassword').send_keys(password)
                    browser.find_element_by_id('login-form-submit').click()

                # Verify that we are on Administration Console.
                # This will confirm, we are logged in as a Global Administrator.
                assert browser.find_element_by_id('admin-search-link').text == 'Search JIRA admin'

            except NoSuchElementException:
                print "Unable to login to JIRA Application, exiting."
                browser.close()
                browser.quit()
                sys.exit(0)

        return browser, new_base_url

    def verify_admin_access(self):
        browser = self.browser
        try:
            browser.implicitly_wait(1)
            browser.find_element_by_id("system-admin-menu")
            return True
        except NoSuchElementException:
            return False

    def get_jira_project_list(self, base_url, userid, password):
        jira_project_list_rest_url = base_url + "/rest/api/2/project"
        result = requests.get(jira_project_list_rest_url,  headers=header_params, auth=(userid, password), verify=False)
        result.raise_for_status()

        result_len = len(result.json())

        project_id_dict = {}
        for i in range(0, result_len):
            project_id_dict[result.json()[i]['key']] = result.json()[i]['id']
            #click.echo(result.json()[i]['key'] + ":" + result.json()[i]['id'])

        return project_id_dict

    def disable_project_notification_schemes(self, browser, base_url, userid, password):
        project_notification_url = base_url + '/secure/project/SelectProjectScheme!default.jspa?projectId=%s'

        project_dict = self.get_jira_project_list(base_url, userid, password)
        for project_key, project_id in project_dict.iteritems():
            browser.get(project_notification_url % project_id)
            scheme_dropdown_element = Select(browser.find_element_by_id('schemeIds_select'))
            current_selected_option = scheme_dropdown_element.first_selected_option
            current_notification_scheme_name = current_selected_option.text.strip()
            if current_notification_scheme_name != 'None':
                scheme_dropdown_element.select_by_visible_text('None')
                browser.find_element_by_id('associate_submit').click()
                click.echo('For Project "%s", Notification Scheme changed from "%s" to None' % (project_key, current_notification_scheme_name))

    def check_jira_mail_queue_status (self, browser, base_url, mail_threshold_limit):
        click.echo("Override default mail-threshold-limit (100) if necessary.")
        click.echo()
        mail_queue_url = base_url + '/secure/admin/MailQueueAdmin!default.jspa'

        # Visit Mail Queue page
        browser.get(mail_queue_url)
        current_queue_status_text = browser.find_element_by_class_name('jiraformbody').text
        current_email_in_queue_count = current_queue_status_text.strip().split()[4]
        if int(current_email_in_queue_count) > mail_threshold_limit:
            # TODO: Send Email to Admins
            click.echo('Emails Queued in JIRA: %s' % current_email_in_queue_count)
            click.echo('Emails are piling in JIRA Mail queue. Please have a look at earliest')

    def get_jira_attachments(self, browser, base_url, userid, password, jql, download_dir):
        click.echo("Override default values to jql (created=now()) and download-dir (./downloads)if necessary.")
        click.echo()

        auth = (userid, password)

        #jira_search_rest_url = base_url + "/rest/api/2/search?" + urllib.urlencode(jql) +"&fields=attachment"
        jira_search_rest_url = base_url + "/rest/api/2/search?jql=" + requests.utils.quote(jql) +"&fields=attachment"

        #click.echo(jira_search_rest_url)

        issue_starting_index = 0
        total_issue_entries_available = 100
        issue_limit_per_fetch = 50

        while issue_starting_index < total_issue_entries_available:
            updated_jira_search_rest_url = jira_search_rest_url + "&startAt=" + str(issue_starting_index) + "&maxResults=" + str(issue_limit_per_fetch)
            #click.echo(updated_jira_search_rest_url)

            search_result = requests.get(updated_jira_search_rest_url, headers=header_params, auth=auth, verify=False)
            search_result.raise_for_status()

            result_issue_entries = search_result.json()["issues"]
            #click.echo(result_issue_entries)
            result_issue_count_fetch_in_this_iteration = len(result_issue_entries)
            total_issue_entries_available = search_result.json()["total"]

            click.echo("Starting Index - " + str(issue_starting_index) + ", Issues fetched in this iteration - " + str(result_issue_count_fetch_in_this_iteration)
            + ", Total Issues to be fetched - " + str(total_issue_entries_available))
            for i in range(0, result_issue_count_fetch_in_this_iteration):
                # Get Attachment info.
                if 'fields' in result_issue_entries[i] and 'attachment' in result_issue_entries[i]['fields']:
                    attachment_info = result_issue_entries[i]['fields']['attachment']
                    if attachment_info != None:
                        total_attachments = len(attachment_info)
                        for attach_index in range(0, total_attachments):
                            click.echo("Downloading attachment - " + attachment_info[attach_index]['content'] + " for Issue: " + result_issue_entries[i]['key'])

                            attachment_response = requests.get(attachment_info[attach_index]['content'], auth=auth, stream=True)
                            attachment_response.raise_for_status()
                            with open(download_dir + "/" + attachment_info[attach_index]['filename'], 'wb') as f:
                                    attachment_response.raw.decode_content = True
                                    shutil.copyfileobj(attachment_response.raw, f)

            issue_starting_index = search_result.json()['startAt'] + issue_limit_per_fetch

    def check_ldap_sync_status(self, browser, base_url, ldap_sync_threshold_limit):
        click.echo("Override default ldap-sync-threshold-limit (4) hours if necessary.")
        click.echo()

        # If last LDAP sync happened more than ldap_sync_threshold_limit hours ago, warn JIRA Admin
        ldap_sync_status_url = base_url + '/plugins/servlet/embedded-crowd/directories/list'
        browser.get(ldap_sync_status_url)

        # Get last successful SYNC time information. Example: Last synchronised at 7/16/15 9:52 AM (took 25s)
        ldap_sync_status_string_aray = browser.find_element_by_class_name('sync-info').text.strip().split()
        last_successful_sync_status_time = '%s %s %s' % (ldap_sync_status_string_aray[3], ldap_sync_status_string_aray[4], ldap_sync_status_string_aray[5])
        click.echo('Last Successful Sync Status Time: %s' % last_successful_sync_status_time)

        # Do arithmetic to find out how many hours before this sync happened.
        last_sync_datetime = datetime.datetime.strptime(last_successful_sync_status_time, "%m/%d/%y %I:%M %p")
        current_daytime = datetime.datetime.now()
        time_delta = current_daytime - last_sync_datetime
        hours, minutes, seconds = self.convert_timedelta(time_delta)
        sync_status_message = 'Time elapsed since last LDAP sync: {} hour(s), {} minute(s)'.format(hours, minutes)
        click.echo(sync_status_message)

        if hours > ldap_sync_threshold_limit:
            click.echo("Something is wrong with LDAP sync process. Please verify at your earliest your convenience.")

    def convert_timedelta(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return hours, minutes, seconds

    command_dictionary = {
        'disable_project_notification_schemes': disable_project_notification_schemes,
        'check_jira_mail_queue_status': check_jira_mail_queue_status,
        'check_ldap_sync_status': check_ldap_sync_status,
        'get_jira_attachments': get_jira_attachments
    }


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
                # This will confirm, we are logged in as a Global Administrator.
                assert browser.find_element_by_class_name('admin-heading').text == 'Administration Console'
                assert browser.find_element_by_class_name('admin-subtitle').text == 'The Administration Console is the interface for managing and maintaining Confluence.'

            except NoSuchElementException:
                print "Unable to login to Wiki Application, exiting."
                browser.close()
                sys.exit(0)

        return browser, new_base_url

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
        click.echo("Right now it just changes siteTitle value to 'Pongbot\'s confluence <random number 1-10>")
        click.echo("Future we will provide configuration file to update all general configuration values.")
        click.echo("Future is Bright, just stay tight!")
        click.echo()

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
        click.echo("Update default color values from file config/wiki_global_custom_colour_scheme.default if necessary")
        click.echo()
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
        #click.echo(space_list_rest_url)
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
        #click.echo(space_keys)

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

@click.command()
# General Parameters needed for Atlassian Command Line use.
@click.option('--app-type', type=click.Choice(['atlassian.net', 'other']),
              default='atlassian.net',
              help='Enter type of application that you want to automate. ->Default: atlassian.net<-')
@click.option('--app-name', type=click.Choice(['Confluence', 'JIRA', 'Bitbucket Server']),
              default='Confluence',
              help='Enter Atlassian Application that you want to automate. ->Default: Confluence<-')
@click.option('--browser-name', type=click.Choice(['Firefox', 'PhantomJS']),
              default='Firefox',
              help='"Firefox" and "PhantomJS" are the only supported Browsers. For cronjobs, you need to use PhantomJS. ->Default: Firefox<-')
@click.option('--base-url', default='https://pongbot.atlassian.net', help="Enter base URL for Atlassian application. ->Default: https://pongbot.atlassian.net<-")
@click.option('--userid', prompt='Enter Administrator Userid', help="Provide userid with Application Administration permissions. Use 'admin' to play with pongbot.atlassian.net")
@click.option('--password', prompt='Enter your credentials', hide_input=True, confirmation_prompt=True, help="Use password 'pongbot' to play with test instance pongbot.atlassian.net")
@click.option('--action', '-a', multiple=True,
              help="Available actions:                            Wiki -> 'update_global_color_scheme', 'update_general_configuration', 'update_wiki_spaces_color_scheme' "
                   "              JIRA -> 'check_mail_queue_status', 'disable_all_project_notifications', 'check_ldap_sync_status', 'get_jira_attachments'")
# Parameters for Mail Queue Check
@click.option('--mail-threshold-limit', default=100, help="If emails in queue are greater than this limit, then ACL will alert user. ->Default: 100<-")
# Parameters for LDAP Sync Status check
@click.option('--ldap-sync-threshold-limit', default=4, help="If last LDAP sync happened more than given 'ldap_sync_threshold_limit' hours, then ACL will alert user. ->Default: 4 (hours)<-")
# Parameters for Attachment Download
@click.option('--jql', default='created=now()', help='Enter JQL to get attachments for all JIRA tickets. ->Default: created = now()<-')
@click.option('--download-dir', default='./downloads', help='Enter complete path for a directory where you want attachments to be downloaded. ->Default Download Directory=./downloads<-')
def start(app_type, app_name, browser_name, base_url, userid,
          password, action, mail_threshold_limit, ldap_sync_threshold_limit,
          jql, download_dir):
    """
    Atlassian Command Line aka ACL - Automate the tasks that you can not!

    """
    """
    :param string:
    :return:
    """
    click.echo()
    # Remove forward slash from user if user entered in base_url
    base_url = base_url.rstrip('/')
    click.echo('Automating application located at %s' % base_url)
    click.echo()

    if app_name == 'Confluence':

        wiki_browser = None

        if browser_name == 'Firefox':

            wiki_browser = WikiBrowser(Firefox)
        else:
            wiki_browser = WikiBrowser(PhantomJS)

        (browser, new_base_url) = wiki_browser.login(app_type, base_url, userid, password)

        for act in action:
            click.echo('Executing Confluence command: %s' % act)
            if act == 'update_global_color_scheme':
                wiki_browser.command_dictionary[act](wiki_browser, browser, new_base_url, "config/wiki_global_custom_colour_scheme.default")
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

    if app_name == 'JIRA':
        jira_browser = None
        if browser_name == 'Firefox':
            jira_browser = JIRABrowser(Firefox)
        else:
            jira_browser = JIRABrowser(PhantomJS)

        (browser, new_base_url) = jira_browser.login(app_type, base_url, userid, password)

        for act in action:
            click.echo('Executing JIRA command: %s' % act)
            if act == 'disable_project_notification_schemes':
                jira_browser.command_dictionary[act](jira_browser, browser, new_base_url, userid, password)

            if act == 'check_jira_mail_queue_status':
                jira_browser.command_dictionary[act](jira_browser, browser, new_base_url, mail_threshold_limit)

            if act == 'check_ldap_sync_status':
                jira_browser.command_dictionary[act](jira_browser, browser, new_base_url, ldap_sync_threshold_limit)

            if act == 'get_jira_attachments':
                jira_browser.command_dictionary[act](jira_browser, browser, new_base_url, userid, password, jql, download_dir)

            click.echo()

        browser.close()
        browser.quit()
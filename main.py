
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import csv
import sys
import argparse
from random import randint

if sys.version_info < (3, 5):
    print("Python version is NOT OK, need 3.5 at least")
    sys.exit(1)

STATUS_CLICKED = 'clicked'
STATUS_NOT_CLICKED = 'not clicked'


class InstagramFollower:

    driver = None
    username = None
    password = None
    account = None
    max_followers_num = 10
    max_clicks_num = 10
    follow_status_report_file = None
    unfollow_status_report_file = None
    unfollow_list_file = None

    def __init__(
        self,
            chrome_location,
            chrome_driver_location,
            username,
            password,
            account,
            max_followers_num=10,
            max_clicks_num=10,
            follow_status_report_file=None,
            unfollow_status_report_file=None,
            unfollow_list_file=None,
    ):
        """
        InstagramFollower constructor

        :param chrome_location: path to Chrome browser binary
        :param chrome_driver_location: path to Chrome driver
        :param username: Instagram username to login
        :param password: Instagram password to login
        :param account: Instagram account to process followers
        :param max_followers_num: Max follswers number to fetch
        :param max_clicks_num: Max clicks num to perform on Follow/Following button
        :param follow_status_report_file: CSV file to write follos status report to
        :param unfollow_status_report_file: CSV file to write unfollow status report to
        :param unfollow_list_file: CSV file to read unfollow users list

        """
        options = webdriver.ChromeOptions()
        options.binary_location = chrome_location
        #options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36")
        chrome_driver_binary = chrome_driver_location
        self.driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
        self.account = account
        self.username = username
        self.password = password
        self.max_followers_num = max_followers_num
        self.max_clicks_num = max_clicks_num
        self.follow_status_report_file = follow_status_report_file
        self.unfollow_status_report_file = unfollow_status_report_file
        self.unfollow_list_file = unfollow_list_file

    def login(self):
        """
        Perform login with specified earlier in constructor login and password
        :return:
        """
        # Load page
        self.driver.get("https://www.instagram.com/accounts/login/")

        time.sleep(randint(3, 9))

        # Login
        self.driver.find_element_by_xpath("//div/input[@name='username']").send_keys(self.username)
        self.driver.find_element_by_xpath("//div/input[@name='password']").send_keys(self.password)

        time.sleep(randint(3, 9))
        self.driver.find_element_by_xpath("//span/button").click()

        # Wait for the login page to load
        WebDriverWait(self.driver, 20)
    #    WebDriverWait(driver, 60).until(
    #        EC.presence_of_element_located((By. LINK_TEXT, "See All"))
    #    )
        time.sleep(randint(7, 9))

    def get_followers(self, max_followers_num=None):
        """
        Get list of followers for the account limited by max_followers_num
        :param max_followers_num: max followers num to fetch
        :return: list of dicts of elements as
        {
            'username': follower_username_elem,
            'button': follow_button_elem,
        }
        """
        # Load account page
        self.driver.get("https://www.instagram.com/{}".format(self.account))

        time.sleep(randint(3, 9))
        # Click the 'Followers' link
        try:
            self.driver.find_element_by_partial_link_text("follower").click()
        except:
            logging.critical("Can not find 'Followers' link on /{} page".format(self.account))
            return

        # Paths within followers modal
        username_xpath = "//div/div/div/div/div/ul/div/li/div/div/div/div/a"
        follow_button_xpath = "//div/div/div/div/div/ul/div/li/div/div/span/button"

        # Wait for the followers modal to load
        WebDriverWait(self.driver, 20).until(
            # Until we have followers available
            EC.presence_of_element_located((By.XPATH, username_xpath))
        )

        # Scrollable div
        scroll_div_xpath = "//div/div/div/div/div/ul/div"
        scroll_div_element = self.driver.find_element_by_xpath(scroll_div_xpath)

        followers_num = 0
        while True:
            # List of visible followers
            follower_username_elems = self.driver.find_elements_by_xpath(username_xpath)

            # limit number of followers to extract
            followers_num = len(follower_username_elems)
            if max_followers_num is not None and followers_num >= max_followers_num:
                break # while True

            # Last/bottom follower
            last_follower_username_elem = follower_username_elems.pop()

            # Current height of scrollable div
            height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_div_element)

            # Bring last/bottom follower into view - scroll div down
            self.driver.execute_script("arguments[0].scrollIntoView()", last_follower_username_elem)

            # Wait to actually scroll page
            time.sleep(randint(2, 5))

            # Height of scrollable div after attempt to scroll down
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_div_element)

            if new_height <= height:
                # No increase in height - looks like we are we at the very bottom
                break

        # All elements are fetched onto the page and are available for scraping
        follower_username_elems = self.driver.find_elements_by_xpath(username_xpath)
        follow_button_elems = self.driver.find_elements_by_xpath(follow_button_xpath)

        follower_username_elems_iter = iter(follower_username_elems)
        follow_button_elems_iter = iter(follow_button_elems)

        # Prepare easy-to-understand pairs of
        # {
        #   'username': username_elem,
        #   'button': button_elem,
        # }
        # Yes, this algo assumes that elements in username and button lists are position-related,
        # i.e. follower_username_elems[15] relates to follow_button_elems[15]
        # this is because we assume driver.find_elements_by_xpath() returns elements according to their appearance in DOM model,
        # which is exactly so right now
        # In case this change in future, we can sort elements by Y position, for example
        pairs = []
        while True:
            try:
                # Advance in lists
                follower_username_elem = next(follower_username_elems_iter)
                follow_button_elem = next(follow_button_elems_iter)

                # Prepare easy-to-use pairs
                pairs.append({
                    'username': follower_username_elem,
                    'button': follow_button_elem,
                })
            except StopIteration:
                # Exit criterion = no next element
                break # while True

        logging.info("found {} followers of {}".format(len(pairs), self.account))

        return pairs

    def follow(self, elements, max_clicks_num=None):
        """
        Click on "follow" button for specified list of elements
        :param elements: list of dicts of elements as
        {
            'username': follower_username_elem,
            'button': follow_button_elem,
        }
        :param max_clicks_num: max number of clicks to perform
        :return: list of dicts of statuses of the following form:
        {
            'username': username_elem.text,
            'status': status,
            'info': info,
        }
        """

        # Sanity check
        if elements is None:
            return

        statuses = []
        clicks_num = 0
        for pair in elements:

            # Verify max clicks num
            if max_clicks_num is not None and clicks_num >= max_clicks_num:
                break # for elements

            username_elem = pair['username']
            button_elem = pair['button']

            if button_elem.text == "Follow":
                # Click the 'Follow' button
                try:
                    button_elem.click()
                    clicks_num += 1
                    status = STATUS_CLICKED
                    info = ''
                    logging.info("following {}".format(username_elem.text))
                except:
                    status = STATUS_NOT_CLICKED
                    info = 'click error'
                    logging.info("click error {}".format(username_elem.text))

                # pause for server to accept
                time.sleep(randint(5, 9))
            else:
                status = STATUS_NOT_CLICKED
                info = button_elem.text
                logging.info("skip {}".format(username_elem.text))

            statuses.append({
                'username': username_elem.text,
                'status': status,
                'info': info,
            })

        return statuses

    def unfollow(self, elements, usernames_to_unfollow):
        """
        Click on "Following" button for users provded in usernames_to_unfollow
        :param elements: list of dicts of elements as
        {
            'username': follower_username_elem,
            'button': follow_button_elem,
        }
        :param usernames_to_unfollow: list of strings of usernames
        :return: list of dicts of statuses of the following form:
        {
            'username': username_elem.text,
            'status': status,
            'info': info,
        }
        """

        # Sanity check
        if elements is None:
            return
        if usernames_to_unfollow is None:
            return

        statuses = []
        for pair in elements:
            username_elem = pair['username']
            button_elem = pair['button']

            if username_elem.text in usernames_to_unfollow:
                # We have found username to unfollow
                if button_elem.text == "Following":
                    # We are following this username
                    # Click the 'Following' button and Unfollow user
                    try:
                        button_elem.click()
                        status = STATUS_CLICKED
                        info = ''
                        logging.info("unfollowing {}".format(username_elem.text))
                    except:
                        status = STATUS_NOT_CLICKED
                        info = 'click error'
                        logging.info("click error {}".format(username_elem.text))

                    # pause for server to accept
                    time.sleep(randint(5, 9))
                else:
                    # We are not following this username
                    satus = STATUS_NOT_CLICKED
                    info = button_elem.text

                statuses.append({
                    'username': username_elem.text,
                    'status': status,
                    'info': info,
                })

        return statuses

    @staticmethod
    def export_statuses_to_csv(file, statuses):
        """
        Export list of statuses into CSV file
        :param file: path to file. File will be overwritten
        :param statuses: list of dicts of the form
        {
            'username': username_elem.text,
            'status': status,
            'info': info,
        }
        :return: None
        """
        if statuses is None:
            return

        writer = csv.DictWriter(open(file, 'a+'), fieldnames=[
            'username',
            'status',
            'info',
        ])
        writer.writeheader()

        for status in statuses:
            writer.writerow(status)

    @staticmethod
    def import_unfollow_users_from_csv(file):
        """
        Import list of users to unfollow
        :param file: path to file
        :return: None
        """
        unfollow_list = []
        try:
            csvfile = open(file)
            dialect = "unix"
            reader = csv.DictReader(csvfile, dialect=dialect)
            for row in reader:
                logging.info(row['username'])
                unfollow_list.append(row['username'])
        except:
            logging.info("Can not read CSV file")
            return []

        return unfollow_list

    def run(self):
        """
        Main function - run Instagram Follower
        :return:
        """
        try:
            # Login
            self.login()

            # Get limited number of followers
            followers_elements = self.get_followers(max_followers_num=self.max_followers_num)

            # Click follow to limited number of extracted followers
            statuses = self.follow(
                elements=followers_elements,
                max_clicks_num=self.max_clicks_num
            )

            # Report follow status
            InstagramFollower.export_statuses_to_csv(self.follow_status_report_file, statuses)

            # Read list of users to unfollow
            usernames_to_unfollow = InstagramFollower.import_unfollow_users_from_csv(self.unfollow_list_file)

            # Click unfollow
            statuses = self.unfollow(followers_elements, usernames_to_unfollow)

            # And report unfollow status
            InstagramFollower.export_statuses_to_csv(self.unfollow_status_report_file, statuses)
        finally:
            self.driver.quit()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='Instagram Follower',
        epilog='==============='
    )
    argparser.add_argument(
        '--chrome-location',
        type=str,
        default="/usr/bin/google-chrome-stable",
        help='Path to Chrome. Default - "/usr/bin/google-chrome-stable"'
    )
    argparser.add_argument(
        '--chrome-driver-location',
        type=str,
        default="./chromedriver",
        help='Path to Chrome Driver. Default - "./chromedriver"'
    )
    argparser.add_argument(
        '--account',
        type=str,
        default="emilia_clarke",
        help='Account to process followers. Default - "emilia_clarke"'
    )
    argparser.add_argument(
        '--username',
        type=str,
        default=None,
        help='Instagram username to login. Default - not set'
    )
    argparser.add_argument(
        '--password',
        type=str,
        default=None,
        help='Instagram password to login. Default - not set'
    )
    argparser.add_argument(
        '--follow-status-report-file',
        type=str,
        default=None,
        help='CSV file to report follow status to'
    )
    argparser.add_argument(
        '--unfollow-status-report-file',
        type=str,
        default=None,
        help='CSV file to report unfollow status to'
    )
    argparser.add_argument(
        '--unfollow-list-file',
        type=str,
        default='unfollow.csv',
        help='CSV file where to read users from. Default - unfowllow.csv'
    )
    argparser.add_argument(
        '--max-followers-num',
        type=int,
        default=10,
        help='Max number of followers to fetch. Default - 10'
    )
    argparser.add_argument(
        '--max-clicks-num',
        type=int,
        default=10,
        help='Max clicks on Follow/Following to do. Default - 10'
    )
    args = argparser.parse_args()

    # Options
    chrome_location = args.chrome_location
    chrome_driver_location = args.chrome_driver_location
    account = args.account
    username = args.username
    password = args.password
    max_followers_num = args.max_followers_num
    max_clicks_num = args.max_clicks_num
    follow_status_report_file = "follow_status_for_{}.csv".format(account) if args.follow_status_report_file is None else args.follow_status_report_file
    unfollow_status_report_file = "unfollow_status_for_{}.csv".format(account) if args.unfollow_status_report_file is None else args.unfollow_status_report_file
    unfollow_list_file = "unfollow.csv" if args.unfollow_list_file is None else args.unfollow_list_file

    exit = False
    if not chrome_location:
        print("Please specify Chrome location")
        exit = True
    if not chrome_driver_location:
        print("Please specify Chrome Driver location")
        exit = True
    if not account:
        print("Please specify account to process")
        exit = True
    if not username:
        print("Please specify Instagram username to login")
        exit = True
    if not password:
        print("Please specify Instagram password to login")
        exit = True
    if exit:
        print("Can not continue")
        print("Use --help option for details on available options")
        sys.exit(1)

    # Setup logging
    logging.basicConfig(
        filename=None,
        level=logging.NOTSET,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    # Main
    follower = InstagramFollower(
        chrome_location=chrome_location,
        chrome_driver_location=chrome_driver_location,
        account=account,
        username=username,
        password=password,
        max_followers_num=max_followers_num,
        max_clicks_num=max_clicks_num,
        follow_status_report_file=follow_status_report_file,
        unfollow_status_report_file=unfollow_status_report_file,
        unfollow_list_file=unfollow_list_file,
    )
    follower.run()

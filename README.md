# instagram-follower
Instagram Follower - special for Anna Wasal

# Introduction

Described URL `http://instagram.com/ploterline/followers/` endpoint isn't really easy-to-use RESTful endpoint 
Instagram fetches information with AJAXs after user click the Followers button.
Quick research did not allow me to find a way to get that information without using Selenium, which can load/render 
the javascript that displays the followers to the user. So, we have a Selenium-based solution which mocks human behavior, including random pauses between actions.
For such a solution Google Chrome Browser is required

## Requirements

  * Google Chrome
  * Google Chrome Driver
  * Python 3.5

## Installation

Google Chrome browser is required
```bash
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/chrome.list
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
apt-get update
apt-get install google-chrome-stable
```

Google Driver is required. It can be dowloaded from
```bash
https://sites.google.com/a/chromium.org/chromedriver/downloads
```
or from
```bash
https://chromedriver.storage.googleapis.com/index.html?path=2.34/
```
Unzip downloaded file before usage. However, Llinux 64-bit version is already included into this repo, so you may not need to download your driver.


## Usage

Basic usage
```bash
python3 main.py --username=INSTAGRAM_USER --password=INSTAGRAM_PASSWORD --account=emilia_clarke
```

Tool writes CSV log into `follow_status_for_ACCOUNT_NAME.csv` file for clicked 'Follow' buttons.
Tool writes CSV log into `unfollow_status_for_ACCOUNT_NAME.csv` file for clicked 'Following' buttons.
Tool reads list of usernames to unfollow from `unfollow.csv` file

### Available Options
  * --chrome-location
        default="/usr/bin/google-chrome-stable",
        Path to Chrome. Default - "/usr/bin/google-chrome-stable"
        Rationale - Chrome Browser can be located in dirrent palces
        
  * --chrome-driver-location
        default="./chromedriver",
        Path to Chrome Driver. Default - "./chromedriver"
        Rationale - Chrome Browser Driver can be located in dirrent palces

  * --account'
        default="emilia_clarke",
        Account to process followers. Default - "emilia_clarke"
        Rationale - we need to know on which account to process followers
        
  * --username
        default=None,
        Instagram username to login. Default - not set
        Rationale - Instagram requires username in order to login
        
  * --password
        default=None,
        Instagram password to login. Default - not set
        Rationale - Instagram requires password in order to login
        
  * --max-followers-num
        type=int,
        default=10,
        Max number of followers to fetch. Default - 10
        Rationale - account can have millions of followers. We need to have control over the process
        
  * --max-clicks-num
        type=int,
        default=10,
        Max clicks on Follow/Following to do. Default - 10
        Rationale - account can have millions of followers. We need to have control over the process


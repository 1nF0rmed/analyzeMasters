from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import config
import random
import json
import time
import re

#chrome_options = Options()
#chrome_options.add_argument("--user-data-dir=chrome-data")
binaryPath = "/usr/lib/chromium-browser/chromedriver"
driver = webdriver.Chrome(binaryPath)

# Load the csv file
df = pd.read_csv("university_links.csv")

user = config.user
passw = config.passw

def loadCookies():
    data = ""
    with open("yocket.json", "r") as f:
        data = f.read()
    
    cookieData = json.loads(data)
    
    return cookieData

def parseProfile(driver):
    try:
        scores = driver.find_element_by_xpath("//span[contains(text(), 'Quant')]")
        scoresData = scores.get_attribute("innerHTML")
    except:
        scoresData="NULL"

    # Parse to get the integer values
    scoresData = re.findall(r"(\d+)", scoresData)

    # Separate values
    quantScore = scoresData[0] if len(scoresData)>1 else "NULL"
    verbalScore = scoresData[1] if len(scoresData)>1 else "NULL"

    return (quantScore, verbalScore)


"""
# Load the cookies and set up the browser
print("[LOG] Loading cookies")
for cookie in loadCookies():
    print("Cookie: "+str(cookie))
    driver.add_cookie(cookie)
"""

# Login to Yocket

driver.get("https://yocket.in/account/login")
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[2]/form/div[2]/input').send_keys(user)
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[2]/form/div[3]/button').click()
time.sleep(15)
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[3]/form/div[2]/div[2]/input').send_keys(passw)
time.sleep(15)
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[3]/form/div[3]/button').click()

time.sleep(120)

first = True

f = open("scoreSeparatedData.csv", "w")
for index, row in df.iterrows():
    name = row["University Name"].replace(',', '')
    degree = row["Degree Focus"]
    link = row["Link"]

    print("[LOG] Collecting data: "+name)

    for i in range(1, 9):
        # Load page
        driver.get(link+"?page="+str(i))

        """
        # Load the cookies and set up the browser
        print("[LOG] Loading cookies")
        for cookie in loadCookies():
            cookie.pop('sameSite')
            print("Cookie: "+str(cookie))
            driver.add_cookie(cookie)
        """

        # Wait until data is loaded
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".col-sm-6")))
        admits = driver.find_elements_by_class_name("panel-body")

        # Print count of admits in page
        print("Count: "+str(len(admits)))
        if len(admits)==0:
            break

        # Go to the end of the page to ensure all content is loaded
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)

        """
        # Check if data wasn't loaded
        if len(admits)<5:
            # Attempt max 2 times
            for i in range(0, 2):
                time.sleep(15)
                driver.get(link+"?page="+str(i))
                admits = driver.find_elements_by_class_name("col-sm-6")
                if len(admits)<5:
                    break
        
        # Check if data wasn't loaded
        if len(admits)<5:
            break
        """

        # Loop through the admits
        for admit in admits:
            # Get tags that contain
            # GRE, TOEFL, GPA/CGPA, Work Exp
            details = admit.find_elements_by_css_selector(".col-sm-3.col-xs-6")

            row_details = ""

            # Get profile link
            profileLink = admit.find_element_by_tag_name('a')

            # TODO: Load the user profile and get Quant and Verbal Score
            # Xpath for Span tag containing data: //span[contains(text(), 'Quant')]
            main_window = driver.current_window_handle

            profileLink.send_keys(Keys.CONTROL + Keys.RETURN)

            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)

            driver.switch_to_window(driver.window_handles[1])

            (quant, verbal) = parseProfile(driver)

            # BUG: Doesn't close the new window
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')

            driver.switch_to_window(main_window)

            row_details+=str(quant)+","+str(verbal)+","

            # Sleep for some time between profiles
            time.sleep(random.randrange(2,8))

            # Get through the details
            
            print("Count: "+str(len(details)))
            if len(details)==0:
                continue
            for detail in details:
                data = detail.get_attribute('innerHTML')

                # Parse and get the data type and the value
                dtype = re.findall(r"<strong>(.*?)<\/strong><br>", data)
                dtype = dtype[0].strip() if len(dtype)>0 else "NULL"
                value = re.findall(r"\d+\.*\d*", data)
                value = value[0].strip() if len(value)>0 else "NULL"

                # If no data type was found then move to next admit
                if dtype=="NULL":
                    break
                row_details += value+","
    
            if len(details)>2:
                # Get the breif about the application
                brief = admit.find_element_by_css_selector(".col-sm-9")
                briefInnerHTML = brief.get_attribute('innerHTML')

                # Get the application year from the brief
                year = re.findall(r"(\d\d\d\d)", briefInnerHTML)
                year = year[0].strip() if len(year)>0 else "NULL"

                row_details += year
                row_details += ","+name

                print(row_details)
                f.write(row_details+"\n")

            if len(row_details)>3:
                print("")
            
        # Sleep
        sleepTime = random.randrange(10,30)
        print("[LOG] Sleeping for: "+str(sleepTime))
        time.sleep(sleepTime)
    first = False

f.close()
driver.close()
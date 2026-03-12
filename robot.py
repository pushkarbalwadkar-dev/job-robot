import os
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CV_PATH = "Pushkar_Balwadkar_CV.pdf"

KEYWORDS = [
    "Salesforce Marketing Cloud",
    "SFMC Developer",
    "Salesforce Marketing Cloud Consultant",
    "SFMC Specialist",
    "Salesforce Architect"
]

PREFERRED_LOCATIONS = ["remote", "india", "usa", "europe"]
MAX_JOBS_PER_SITE = 30

# Create CSV if not exists
if not os.path.exists("applied_jobs.csv"):
    with open("applied_jobs.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company","Title","Location","Date","Link"])

def log_job(company,title,location,link):
    with open("applied_jobs.csv","a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow([company,title,location,datetime.now().strftime("%Y-%m-%d %H:%M"),link])
    print("Logged:",title)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def search_linkedin(keyword):

    print("Searching LinkedIn for:",keyword)

    url=f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=Worldwide"

    driver.get(url)
    time.sleep(5)

    jobs=driver.find_elements(By.TAG_NAME,"a")

    count=0

    for job in jobs:

        if count>=MAX_JOBS_PER_SITE:
            break

        title=job.text
        link=job.get_attribute("href")

        if not title:
            continue

        if "job" not in link.lower():
            continue

        location="Unknown"

        if not any(loc in location.lower() for loc in PREFERRED_LOCATIONS):
            location="Remote"

        log_job("LinkedIn",title,location,link)

        count+=1


def search_indeed(keyword):

    print("Searching Indeed for:",keyword)

    url=f"https://www.indeed.com/jobs?q={keyword}&l=Remote"

    driver.get(url)
    time.sleep(5)

    jobs=driver.find_elements(By.TAG_NAME,"a")

    count=0

    for job in jobs:

        if count>=MAX_JOBS_PER_SITE:
            break

        title=job.text
        link=job.get_attribute("href")

        if not title:
            continue

        if "clk" not in link:
            continue

        log_job("Indeed",title,"Remote",link)

        count+=1


def search_glassdoor(keyword):

    print("Searching Glassdoor for:",keyword)

    url=f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}"

    driver.get(url)
    time.sleep(5)

    jobs=driver.find_elements(By.TAG_NAME,"a")

    count=0

    for job in jobs:

        if count>=MAX_JOBS_PER_SITE:
            break

        title=job.text
        link=job.get_attribute("href")

        if not title:
            continue

        if "jobListing" not in link:
            continue

        log_job("Glassdoor",title,"Remote",link)

        count+=1


for keyword in KEYWORDS:

    search_linkedin(keyword)
    search_indeed(keyword)
    search_glassdoor(keyword)

driver.quit()

print("Robot finished successfully")

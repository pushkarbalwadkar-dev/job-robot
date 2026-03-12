import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

# ---------------- CONFIG ----------------

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

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------- CSV SETUP ----------------

if not os.path.exists("applied_jobs.csv"):
    with open("applied_jobs.csv","w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company","Job Title","Location","Date","Link"])


def log_job(company,title,location,link):

    with open("applied_jobs.csv","a",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            company,
            title,
            location,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            link
        ])

    print("Logged:",title)


# ---------------- LINKEDIN SEARCH ----------------

def search_linkedin(keyword):

    print("Searching LinkedIn:",keyword)

    url=f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location=Worldwide"

    response=requests.get(url,headers=HEADERS)

    soup=BeautifulSoup(response.text,"html.parser")

    jobs=soup.find_all("a")

    count=0

    for job in jobs:

        if count>=MAX_JOBS_PER_SITE:
            break

        title=job.text.strip()

        link=job.get("href")

        if not title:
            continue

        location="Remote"

        if not any(loc in location.lower() for loc in PREFERRED_LOCATIONS):
            continue

        log_job("LinkedIn",title,location,link)

        count+=1


# ---------------- INDEED SEARCH ----------------

def search_indeed(keyword):

    print("Searching Indeed:",keyword)

    url=f"https://www.indeed.com/jobs?q={keyword}&l=Remote"

    response=requests.get(url,headers=HEADERS)

    soup=BeautifulSoup(response.text,"html.parser")

    jobs=soup.select("a")

    count=0

    for job in jobs:

        if count>=MAX_JOBS_PER_SITE:
            break

        title=job.text.strip()

        link=job.get("href")

        if not title:
            continue

        if link and "/rc/clk" not in link:
            continue

        full_link="https://www.indeed.com"+link

        location="Remote"

        log_job("Indeed",title,location,full_link)

        count+=1


# ---------------- GLASSDOOR SEARCH ----------------

def search_glassdoor(keyword):

    print("Searching Glassdoor:",keyword)

    url=f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}"

    response=requests.get(url,headers=HEADERS)

    soup=BeautifulSoup(response.text,"html.parser")

    jobs=soup.select("a")

    count=0

    for job in jobs:

        if count>=MAX_JOBS_PER_SITE:
            break

        title=job.text.strip()

        link=job.get("href")

        if not title:
            continue

        if "jobListing" not in str(link):
            continue

        full_link="https://www.glassdoor.com"+link

        location="Remote"

        log_job("Glassdoor",title,location,full_link)

        count+=1


# ---------------- MAIN ROBOT ----------------

print("SFMC Job Robot Started")

for keyword in KEYWORDS:

    search_linkedin(keyword)

    search_indeed(keyword)

    search_glassdoor(keyword)

print("Robot finished successfully")

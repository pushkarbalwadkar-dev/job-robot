import requests
import pandas as pd
from datetime import datetime
from config import KEYWORDS, PREFERRED_LOCATIONS, MAX_JOBS

jobs = []

def keyword_match(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS)

def location_match(location):

    if not location:
        return True

    location = location.lower()

    for loc in PREFERRED_LOCATIONS:
        if loc in location:
            return True

    return False


def add_job(company, title, location, link):

    jobs.append({
        "company": company,
        "title": title,
        "location": location,
        "link": link,
        "date": datetime.now()
    })


def fetch_remoteok():

    print("Fetching RemoteOK")

    try:

        data = requests.get("https://remoteok.com/api").json()

        for job in data:

            title = job.get("position")
            company = job.get("company")
            location = job.get("location")
            link = job.get("url")

            if not title:
                continue

            add_job(company, title, location, link)

    except Exception as e:
        print("RemoteOK error:", e)


def fetch_arbeitnow():

    print("Fetching Arbeitnow")

    try:

        data = requests.get("https://www.arbeitnow.com/api/job-board-api").json()

        for job in data["data"]:

            title = job.get("title")
            company = job.get("company_name")
            location = job.get("location")
            link = job.get("url")

            add_job(company, title, location, link)

    except Exception as e:
        print("Arbeitnow error:", e)


def filter_jobs():

    filtered = []

    for job in jobs:

        if not keyword_match(job["title"]):
            continue

        if not location_match(job["location"]):
            continue

        filtered.append(job)

    return filtered


print("Starting job robot")

fetch_remoteok()
fetch_arbeitnow()

print("Total jobs fetched:", len(jobs))

filtered_jobs = filter_jobs()

print("Jobs after filtering:", len(filtered_jobs))

df = pd.DataFrame(filtered_jobs)

if len(df) > MAX_JOBS:
    df = df.head(MAX_JOBS)

df.to_csv("jobs.csv", index=False)

print("Saved jobs.csv successfully")

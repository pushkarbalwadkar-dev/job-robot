import requests
import pandas as pd
import os
from datetime import datetime
from config import KEYWORDS, PREFERRED_LOCATIONS, MAX_RESULTS

jobs = []

def keyword_match(title):

    title = title.lower()

    for k in KEYWORDS:
        if k in title:
            return True

    return False


def location_match(location):

    if not location:
        return True

    location = location.lower()

    for l in PREFERRED_LOCATIONS:
        if l in location:
            return True

    return False


def add_job(company,title,location,link):

    jobs.append({
        "company":company,
        "title":title,
        "location":location,
        "link":link,
        "date":datetime.now()
    })


def fetch_remoteok():

    print("Scanning RemoteOK")

    data = requests.get("https://remoteok.com/api").json()

    for job in data:

        title = job.get("position")
        company = job.get("company")
        location = job.get("location")
        link = job.get("url")

        if not title:
            continue

        add_job(company,title,location,link)


def fetch_arbeitnow():

    print("Scanning Arbeitnow")

    data = requests.get(
        "https://www.arbeitnow.com/api/job-board-api"
    ).json()["data"]

    for job in data:

        add_job(
            job.get("company_name"),
            job.get("title"),
            job.get("location"),
            job.get("url")
        )


def filter_jobs():

    filtered = []

    for j in jobs:

        if not keyword_match(j["title"]):
            continue

        if not location_match(j["location"]):
            continue

        filtered.append(j)

    return filtered


print("Starting AI Job Hunter")

fetch_remoteok()
fetch_arbeitnow()

print("Jobs collected:",len(jobs))

filtered = filter_jobs()

print("Jobs after filtering:",len(filtered))

df = pd.DataFrame(filtered)

df = df.drop_duplicates(subset=["title","company"])

df = df.head(MAX_RESULTS)

df.to_csv("jobs.csv",index=False)

print("Saved jobs.csv")

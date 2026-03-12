import requests
import pandas as pd
from datetime import datetime
from config import KEYWORDS, PREFERRED_LOCATIONS, MAX_RESULTS

jobs = []


# -------------------------------
# Keyword filter
# -------------------------------
def keyword_match(title):

    if not title:
        return False

    title = title.lower()

    for keyword in KEYWORDS:
        if keyword.lower() in title:
            return True

    return False


# -------------------------------
# Location filter
# -------------------------------
def location_match(location):

    if location is None:
        return True

    location = location.lower()

    for loc in PREFERRED_LOCATIONS:
        if loc.lower() in location:
            return True

    return False


# -------------------------------
# Add job safely
# -------------------------------
def add_job(company, title, location, link):

    jobs.append({
        "company": company if company else "Unknown",
        "title": title if title else "Unknown",
        "location": location if location else "Unknown",
        "link": link if link else "",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })


# -------------------------------
# Fetch RemoteOK jobs
# -------------------------------
def fetch_remoteok():

    print("Scanning RemoteOK")

    try:

        response = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )

        data = response.json()

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


# -------------------------------
# Fetch Arbeitnow jobs
# -------------------------------
def fetch_arbeitnow():

    print("Scanning Arbeitnow")

    try:

        response = requests.get(
            "https://www.arbeitnow.com/api/job-board-api",
            timeout=20
        )

        data = response.json()["data"]

        for job in data:

            title = job.get("title")
            company = job.get("company_name")
            location = job.get("location")
            link = job.get("url")

            add_job(company, title, location, link)

    except Exception as e:
        print("Arbeitnow error:", e)


# -------------------------------
# Filter collected jobs
# -------------------------------
def filter_jobs():

    filtered = []

    for job in jobs:

        if not keyword_match(job["title"]):
            continue

        if not location_match(job["location"]):
            continue

        filtered.append(job)

    return filtered


# -------------------------------
# MAIN
# -------------------------------
print("Starting Job Robot")

fetch_remoteok()
fetch_arbeitnow()

print("Total jobs collected:", len(jobs))

filtered_jobs = jobs

print("Jobs after filtering:", len(filtered_jobs))


# -------------------------------
# Create DataFrame safely
# -------------------------------
if len(filtered_jobs) == 0:

    print("No matching jobs found today")

    df = pd.DataFrame(columns=[
        "company",
        "title",
        "location",
        "link",
        "date"
    ])

else:

    df = pd.DataFrame(filtered_jobs)

    df = df.drop_duplicates(subset=["title", "company"])

    df = df.head(MAX_RESULTS)


# -------------------------------
# Save CSV
# -------------------------------
df.to_csv("jobs.csv", index=False)

print("jobs.csv saved successfully")
print("Total jobs saved:", len(df))

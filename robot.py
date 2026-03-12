import requests
import pandas as pd
from datetime import datetime
import openai
import os
from config import KEYWORDS, PREFERRED_LOCATIONS, MAX_JOBS_PER_SITE

openai.api_key = os.getenv("OPENAI_API_KEY")

jobs = []

def location_allowed(location):

    if location is None:
        return True

    location = location.lower()

    for loc in PREFERRED_LOCATIONS:
        if loc in location:
            return True

    return False


def keyword_match(title):

    title = title.lower()

    for k in KEYWORDS:
        if k.lower() in title:
            return True

    return False


def generate_cover_letter(title, company):

    prompt = f"""
Write a short professional cover letter for a job application.

Role: {title}
Company: {company}

Candidate skills:
Salesforce Marketing Cloud, SFMC Developer, Automation Studio,
Journey Builder, Email Studio.

Keep it under 120 words.
"""

    try:

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        return response.choices[0].message.content

    except Exception:

        return "Generated cover letter unavailable"


def fetch_remoteok():

    url = "https://remoteok.com/api"

    try:

        data = requests.get(url).json()

        count = 0

        for job in data:

            if count > MAX_JOBS_PER_SITE:
                break

            title = job.get("position")
            company = job.get("company")
            link = job.get("url")
            location = job.get("location")

            if not title:
                continue

            if not keyword_match(title):
                continue

            if not location_allowed(location):
                continue

            cover = generate_cover_letter(title, company)

            jobs.append({
                "company": company,
                "title": title,
                "location": location,
                "link": link,
                "cover_letter": cover,
                "date": datetime.now()
            })

            count += 1

    except Exception as e:

        print("RemoteOK error:", e)


def fetch_arbeitnow():

    url = "https://www.arbeitnow.com/api/job-board-api"

    try:

        data = requests.get(url).json()["data"]

        count = 0

        for job in data:

            if count > MAX_JOBS_PER_SITE:
                break

            title = job.get("title")
            company = job.get("company_name")
            location = job.get("location")
            link = job.get("url")

            if not keyword_match(title):
                continue

            if not location_allowed(location):
                continue

            cover = generate_cover_letter(title, company)

            jobs.append({
                "company": company,
                "title": title,
                "location": location,
                "link": link,
                "cover_letter": cover,
                "date": datetime.now()
            })

            count += 1

    except Exception as e:

        print("Arbeitnow error:", e)


print("Fetching jobs...")

fetch_remoteok()
fetch_arbeitnow()

df = pd.DataFrame(jobs)

if len(df) > 0:

    df.drop_duplicates(subset=["title", "company"], inplace=True)

    df.to_csv("jobs.csv", index=False)

    print("Saved", len(df), "jobs")

else:

    print("No jobs found today")

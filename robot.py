import os
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai

# ---------------- CONFIG ----------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY
CV_PATH = "Pushkar_Balwadkar_CV.pdf"
KEYWORDS = [
    "Salesforce Marketing Cloud",
    "SFMC Developer",
    "Salesforce Marketing Cloud Consultant",
    "SFMC Specialist",
    "Salesforce Architect"
]
MAX_JOBS_PER_SITE = 30

# Preferred locations (case-insensitive)
PREFERRED_LOCATIONS = ["Remote", "France", "Paris", "USA", "Europe", "Canada", "Australia", "Dubai", "UAE", "Worldwide", "luxembourg", "Netherlands"]

# ---------------- LOGGING ----------------
def log_application(company, job_title, location, link):
    if job_title and link:
        with open('applied_jobs.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([company, job_title, location, datetime.now().strftime("%Y-%m-%d %H:%M"), link])
        print(f"Logged application: {job_title} at {company} ({location})")
    else:
        print(f"Skipped logging because title or link missing for {company}")

# ---------------- AI COVER LETTER ----------------
def generate_cover_letter(job_title, company_name, job_description):
    prompt = f"""
    Write a short personalized cover letter for a {job_title} role at {company_name}.
    Use these details: {job_description}.
    Highlight Salesforce Marketing Cloud experience.
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=250
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Dear Hiring Manager, I am very interested in this position."

# ---------------- START BROWSER ----------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# ---------------- LOGIN CREDENTIALS ----------------
CREDENTIALS = {
    "linkedin": (os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD")),
    "glassdoor": (os.getenv("GLASSDOOR_EMAIL"), os.getenv("GLASSDOOR_PASSWORD")),
    "indeed": (os.getenv("INDEED_EMAIL"), os.getenv("INDEED_PASSWORD")),
}

# ---------------- SITE CONFIG ----------------
SITE_CONFIG = {
    "linkedin": {
        "login_url": "https://www.linkedin.com/login",
        "username_field": "username",
        "password_field": "password",
        "job_class": "job-card-list__title",
        "company_class": "job-card-container__company-name",
        "location_class": "job-card-container__metadata-item",
        "apply_button_class": "jobs-apply-button",
        "company_name": "LinkedIn Company"
    },
    "glassdoor": {
        "login_url": "https://www.glassdoor.com/profile/login_input.htm",
        "username_field": "userEmail",
        "password_field": "userPassword",
        "job_class": "jobLink",
        "company_class": None,
        "location_class": None,
        "apply_button_class": None,
        "company_name": "Glassdoor Company"
    },
    "indeed": {
        "login_url": "https://secure.indeed.com/account/login",
        "username_field": "login-email-input",
        "password_field": "login-password-input",
        "job_class": "jobTitle",
        "company_class": "companyName",
        "location_class": "companyLocation",
        "apply_button_class": "iaP",
        "company_name": "Indeed Company"
    }
}

# ---------------- LOGIN FUNCTION ----------------
def login_site(site_name):
    if site_name not in SITE_CONFIG or site_name not in CREDENTIALS:
        print(f"Skipping login for {site_name} (missing config or credentials)")
        return
    email, password = CREDENTIALS[site_name]
    if not email or not password:
        print(f"Skipping login for {site_name} (email/password missing)")
        return
    config = SITE_CONFIG[site_name]
    driver.get(config["login_url"])
    time.sleep(2)
    try:
        username_elem = driver.find_element(By.ID, config["username_field"])
        password_elem = driver.find_element(By.ID, config["password_field"])
        username_elem.send_keys(email)
        password_elem.send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)
        print(f"Logged in to {site_name}")
    except Exception as e:
        print(f"Could not log in to {site_name}: {e}")

# ---------------- SEARCH AND APPLY ----------------
def search_and_apply(site_name, keyword):
    if site_name not in SITE_CONFIG:
        print(f"Skipping {site_name} (no config)")
        return
    config = SITE_CONFIG[site_name]
    jobs_applied = 0

    # Build search URL
    if site_name == "linkedin":
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&f_LF=f_AL"
    elif site_name == "glassdoor":
        search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}&locT=C&locId=0"
    elif site_name == "indeed":
        search_url = f"https://www.indeed.com/jobs?q={keyword}&l=Remote"
    else:
        print(f"Search URL not defined for {site_name}, skipping")
        return

    driver.get(search_url)

    # Explicit wait for jobs
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, config["job_class"]))
        )
        jobs = driver.find_elements(By.CLASS_NAME, config["job_class"])
    except Exception as e:
        print(f"Could not load jobs for {site_name}: {e}")
        return

    for job_el in jobs:
        if jobs_applied >= MAX_JOBS_PER_SITE:
            break
        try:
            job_title = job_el.text.strip()
            job_link = job_el.get_attribute("href") or job_el.get_attribute("data-job-link") or None

            # Company
            company_name = config["company_name"]
            try:
                if config["company_class"]:
                    company_elem = job_el.find_element(By.CLASS_NAME, config["company_class"])
                    company_name = company_elem.text.strip()
            except:
                pass

            # Location
            location = "Remote"
            try:
                if config["location_class"]:
                    location_elem = job_el.find_element(By.CLASS_NAME, config["location_class"])
                    location = location_elem.text.strip()
            except:
                pass

            # Skip if location not in preferred
            if not any(pref.lower() in location.lower() for pref in PREFERRED_LOCATIONS):
                print(f"Skipped {job_title} at {company_name} due to location: {location}")
                continue

            # AI Cover Letter
            job_description = "Job description placeholder"
            cover_letter = generate_cover_letter(job_title, company_name, job_description)

            # Easy Apply
            if config["apply_button_class"]:
                try:
                    job_el.click()
                    time.sleep(2)
                    apply_btn = driver.find_element(By.CLASS_NAME, config["apply_button_class"])
                    apply_btn.click()
                    time.sleep(2)
                    driver.find_element(By.XPATH, "//input[@type='file']").send_keys(os.path.abspath(CV_PATH))
                    time.sleep(1)
                    try:
                        textarea = driver.find_element(By.TAG_NAME, "textarea")
                        textarea.send_keys(cover_letter)
                    except:
                        pass
                    driver.find_element(By.XPATH, "//button[contains(text(),'Submit')]").click()
                    time.sleep(2)
                except Exception as e:
                    print(f"Skipped auto-apply for {job_title} at {company_name}: {e}")

            log_application(company_name, job_title, location, job_link)
            jobs_applied += 1

        except Exception as e:
            print(f"Error processing job: {e}")

# ---------------- MAIN LOOP ----------------
with open("sites.txt", "r") as f:
    sites = [line.strip().lower() for line in f.readlines() if line.strip()]

for site in sites:
    login_site(site)
    for kw in KEYWORDS:
        search_and_apply(site, kw)

driver.quit()
print("Robot finished running all sites!")

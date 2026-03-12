import os
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import openai

# ---------- CONFIG ----------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

KEYWORDS = ["Salesforce Marketing Cloud", "SFMC Developer", "Marketing Cloud Consultant", "SFMC Specialist"]

# ---------- LOGGING FUNCTION ----------
def log_application(company, job_title, location, link):
    with open('applied_jobs.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([company, job_title, location, datetime.now().strftime("%Y-%m-%d %H:%M"), link])

# ---------- AI COVER LETTER ----------
def generate_cover_letter(job_title, company_name, job_description):
    prompt = f"""
    Write a short personalized cover letter for a {job_title} role at {company_name}.
    Use these details: {job_description}.
    Highlight Salesforce Marketing Cloud experience.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=250
    )
    return response.choices[0].text.strip()

# ---------- START BROWSER ----------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# ---------- LINKEDIN LOGIN ----------
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

driver.get("https://www.linkedin.com/login")
time.sleep(2)
driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(3)

# ---------- GLASSDOOR LOGIN ----------
GLASSDOOR_EMAIL = os.getenv("GLASSDOOR_EMAIL")
GLASSDOOR_PASSWORD = os.getenv("GLASSDOOR_PASSWORD")

driver.get("https://www.glassdoor.com/profile/login_input.htm")
time.sleep(2)
driver.find_element(By.ID, "userEmail").send_keys(GLASSDOOR_EMAIL)
driver.find_element(By.ID, "userPassword").send_keys(GLASSDOOR_PASSWORD)
driver.find_element(By.NAME, "submit").click()
time.sleep(3)

# ---------- INDEED LOGIN ----------
INDEED_EMAIL = os.getenv("INDEED_EMAIL")
INDEED_PASSWORD = os.getenv("INDEED_PASSWORD")

driver.get("https://secure.indeed.com/account/login")
time.sleep(2)
driver.find_element(By.ID, "login-email-input").send_keys(INDEED_EMAIL)
driver.find_element(By.ID, "login-password-input").send_keys(INDEED_PASSWORD)
driver.find_element(By.ID, "login-submit-button").click()
time.sleep(3)

# ---------- JOB SEARCH FUNCTION ----------
def search_jobs(site_name, search_url, job_element_class, company_name_placeholder="Company", location_placeholder="Remote"):
    driver.get(search_url)
    time.sleep(3)
    jobs = driver.find_elements(By.CLASS_NAME, job_element_class)
    for job_el in jobs[:3]:  # apply to first 3 for safety
        job_title = job_el.text
        job_link = job_el.get_attribute("href")
        company_name = company_name_placeholder
        location = location_placeholder
        job_description = "Job description placeholder"
        cover_letter = generate_cover_letter(job_title, company_name, job_description)
        # TODO: Here add auto-apply code (attach CV + cover letter)
        log_application(company_name, job_title, location, job_link)

# ---------- LINKEDIN JOBS ----------
for kw in KEYWORDS:
    search_jobs("LinkedIn",
                f"https://www.linkedin.com/jobs/search/?keywords={kw}&f_LF=f_AL",
                "job-card-list__title",
                "LinkedIn Company",
                "Remote")

# ---------- GLASSDOOR JOBS ----------
for kw in KEYWORDS:
    search_jobs("Glassdoor",
                f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={kw}&locT=C&locId=0",
                "jobLink",
                "Glassdoor Company",
                "Remote")

# ---------- INDEED JOBS ----------
for kw in KEYWORDS:
    search_jobs("Indeed",
                f"https://www.indeed.com/jobs?q={kw}&l=Remote",
                "jobTitle",
                "Indeed Company",
                "Remote")

driver.quit()
print("Robot finished running!")

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
CV_PATH = "Pushkar_Balwadkar_CV.pdf"
KEYWORDS = ["Salesforce Marketing Cloud", "SFMC Developer", "Salesforce Marketing Cloud Consultant", "SFMC Specialist", "Salesforce Architect"]

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

# ---------- LOGIN CREDENTIALS ----------
CREDENTIALS = {
    "linkedin": (os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD")),
    "glassdoor": (os.getenv("GLASSDOOR_EMAIL"), os.getenv("GLASSDOOR_PASSWORD")),
    "indeed": (os.getenv("INDEED_EMAIL"), os.getenv("INDEED_PASSWORD")),
    # Add more secrets if other sites require login
}

# ---------- SITE SPECIFIC CONFIG ----------
SITE_CONFIG = {
    "linkedin": {"login_url":"https://www.linkedin.com/login", "username_field":"username", "password_field":"password", "job_class":"job-card-list__title", "apply_button_class":"jobs-apply-button", "company_name":"LinkedIn Company"},
    "glassdoor": {"login_url":"https://www.glassdoor.com/profile/login_input.htm", "username_field":"userEmail", "password_field":"userPassword", "job_class":"jobLink", "apply_button_class":None, "company_name":"Glassdoor Company"},
    "indeed": {"login_url":"https://secure.indeed.com/account/login", "username_field":"login-email-input", "password_field":"login-password-input", "job_class":"jobTitle", "apply_button_class":"iaP", "company_name":"Indeed Company"},
    # Add config for other sites
}

# ---------- LOGIN FUNCTION ----------
def login_site(site_name):
    if site_name not in SITE_CONFIG or site_name not in CREDENTIALS:
        print(f"No login info for {site_name}, skipping login")
        return
    email, password = CREDENTIALS[site_name]
    config = SITE_CONFIG[site_name]
    driver.get(config["login_url"])
    time.sleep(2)
    driver.find_element(By.ID, config["username_field"]).send_keys(email)
    driver.find_element(By.ID, config["password_field"]).send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(3)
    print(f"Logged in to {site_name}")

# ---------- SEARCH AND APPLY FUNCTION ----------
def search_and_apply(site_name, keyword):
    if site_name not in SITE_CONFIG:
        print(f"No config for {site_name}, skipping")
        return
    config = SITE_CONFIG[site_name]
    
    # Create search URL
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
    time.sleep(3)
    jobs = driver.find_elements(By.CLASS_NAME, config["job_class"])
    for job_el in jobs[:3]:  # first 3 jobs per site per keyword
        try:
            job_title = job_el.text
            job_link = job_el.get_attribute("href")
            company_name = config["company_name"]
            location = "Remote"
            job_description = "Job description placeholder"
            cover_letter = generate_cover_letter(job_title, company_name, job_description)
            
            # EASY APPLY SIMULATION
            if config["apply_button_class"]:
                try:
                    job_el.click()
                    time.sleep(2)
                    apply_btn = driver.find_element(By.CLASS_NAME, config["apply_button_class"])
                    apply_btn.click()
                    time.sleep(2)
                    driver.find_element(By.XPATH, "//input[@type='file']").send_keys(os.path.abspath(CV_PATH))
                    time.sleep(1)
                    textarea = driver.find_element(By.TAG_NAME, "textarea")
                    textarea.send_keys(cover_letter)
                    time.sleep(1)
                    driver.find_element(By.XPATH, "//button[contains(text(),'Submit')]").click()
                    time.sleep(2)
                except:
                    print(f"Skipped auto-apply for {job_title} at {company_name}")
            
            log_application(company_name, job_title, location, job_link)
            print(f"Applied to: {job_title} at {company_name}")
        except Exception as e:
            print(f"Error applying to job: {e}")

# ---------- MAIN LOOP ----------
with open("sites.txt", "r") as f:
    sites = [line.strip().lower() for line in f.readlines() if line.strip()]

for site in sites:
    login_site(site)
    for kw in KEYWORDS:
        search_and_apply(site, kw)

driver.quit()
print("Robot finished running all sites!")

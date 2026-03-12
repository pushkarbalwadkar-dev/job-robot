print("Hello I am your job robot")
import csv
from datetime import datetime

def log_application(company, job_title, location, link):
    with open('applied_jobs.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([company, job_title, location, datetime.now().strftime("%Y-%m-%d %H:%M"), link])

# Example usage after applying to a job
log_application("ABC Corp", "SFMC Developer", "Remote", "https://linkedin.com/job123")

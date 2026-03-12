import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText   # ← THIS LINE WAS MISSING


EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
TO = os.getenv("EMAIL_TO")


# Check if CSV exists
if not os.path.exists("jobs.csv"):
    print("jobs.csv not found")
    exit()


df = pd.read_csv("jobs.csv")


# Stop if file is empty
if df.empty:
    print("No jobs found today")
    exit()


html = "<h2>Daily SFMC Jobs</h2><ul>"

for _, job in df.iterrows():

    html += f"<li><b>{job['title']}</b> - {job['company']} \
    (<a href='{job['link']}'>Apply</a>)</li>"

html += "</ul>"


msg = MIMEText(html, "html")

msg["Subject"] = "Daily SFMC Job Report"
msg["From"] = EMAIL
msg["To"] = TO


with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, TO, msg.as_string())


print("Email sent successfully")

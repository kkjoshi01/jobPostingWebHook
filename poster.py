import requests
import os
from dotenv import load_dotenv
import dateutil
from datetime import datetime

load_dotenv()

HOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
REED_API_KEY = os.environ["REED_API_KEY"]
REED_URL = "https://www.reed.co.uk/api/1.0/search"

ALLOWED_TITLES = [
        "Software Engineer",
        "Backend Engineer",
        "Frontend Engineer",
        "Full Stack Engineer",
        "Machine Learning Engineer",
        "Mobile Engineer"
    ]

def post_job(job):
    title = job.get('jobTitle', 'No title provided')
    company = job.get('employerName', 'No company provided')
    location = job.get('locationName', 'No location provided')
    link = job.get('jobUrl', 'No link provided')
    minSalary = job.get('minimumSalary', 'N/A')
    maxSalary = job.get('maximumSalary', 'N/A')
    minSalary = str("£" + minSalary) if minSalary != None else 'N/A'
    maxSalary = str("£" + maxSalary)  if maxSalary != None else 'N/A'

    message = f"## **{title}**\n"
    message += f"- **{minSalary} - {maxSalary}**\n"
    message += f"- Company: **{company}**\n"
    message += f"- Location: **{location}**\n"
    message += f"- __[Job Link]({link})__\n"
    r = requests.post(HOOK_URL, json={"content": message})
    r.raise_for_status()

def fetch_jobs(numberofJobs : int):
    params = {
        "keywords": "(\"Software Engineer\" OR \"Backend Engineer\" OR \"Frontend Engineer\" OR \"Machine Learning Engineer\" OR \"Mobile Engineer\") AND (\"Graduate\" OR \"Junior\")",
        "resultsToTake": numberofJobs,
        "locationName": "London",
        "distanceFromLocation": 200,
        "permanent": True,
        "fullTime": True,
        "graduate": True
    }
    headers = {
        "Accept": "application/json",
    }

    r = requests.get(REED_URL, params=params, headers=headers, timeout=30, auth=(REED_API_KEY, ''))
    r.raise_for_status()
    return r.json().get('results', [])

def passed_deadline(job):
    deadline = datetime.strptime(job.get('expirationDate'), "%d/%m/%Y") if job.get('expirationDate') else None
    if deadline:
        return deadline < datetime.today()
    return False

def main():
    jobs = fetch_jobs(10)
    for job in jobs:
        job_title = job.get('jobTitle', '')
        if passed_deadline(job):
            print(f"Job {job.get('jobTitle')} has passed its deadline.")
            job = fetch_jobs(1)[0]  # Fetch a new job to replace the expired one

        if str(job_title).find("Senior") or str(job_title).find("Lead"):
            job = fetch_jobs(1)[0]  # Fetch a new job to replace the expired one
        
        try:
            post_job(job)
        except Exception as e:
            print(f"Error posting job {job.get('jobTitle')}: {e}")

if __name__ == "__main__":
    main()

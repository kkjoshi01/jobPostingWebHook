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

def fmt_money(amount):
    if amount is None:
        return "N/A"
    try: 
        return f"£{int(float(amount)):,}"
    except (ValueError, TypeError):
        return str(amount)
    
def markdown_render(title, company, location, link, minSalary=None, maxSalary=None, postedDate=None, deadline=None):
    header = f"**[{title}]({link})**" if link else f"**{title}**"
    salary_line = ""
    if minSalary is not None and maxSalary is not None:
        salary_line = f"💷 **{fmt_money(minSalary)} - {fmt_money(maxSalary)}**"
    else:
        salary_line = f"💷 **{fmt_money(minSalary or maxSalary)}**"
    
    meta = []
    if postedDate:
        meta.append(f"📅 Posted: **{postedDate}**")
    if deadline:
        meta.append(f"⏳ Deadline: **{deadline}**")

    meta_line = "   •  ".join(meta) if meta else ""

    lines = [
        header+"\n",
        f"🏢 **{company}**  •   📍 **{location}**",
    ]
    if salary_line:
        lines.append(salary_line)
    if meta_line:
        lines.append(meta_line)
    lines.append("\n---")
    lines.append("\n")

    return "\n".join(lines)

def post_job(job):
    title = job.get('jobTitle', 'No title provided')
    company = job.get('employerName', 'No company provided')
    location = job.get('locationName', 'No location provided')
    link = job.get('jobUrl', 'No link provided')
    minSalary = job.get('minimumSalary', 'N/A')
    maxSalary = job.get('maximumSalary', 'N/A')
    postedDate = job.get('date', 'N/A')
    deadline = job.get('expirationDate', 'N/A')

    message = markdown_render(title, company, location, link, minSalary, maxSalary, postedDate, deadline)

    r = requests.post(HOOK_URL, json={"content": message})
    r.raise_for_status()

def fetch_jobs(numberofJobs : int):
    params = {
        "keywords": "(\"Software Engineer\" OR \"Backend Engineer\" OR \"Frontend Engineer\" OR \"Machine Learning Engineer\" OR \"Mobile Engineer\") AND (\"Graduate\" OR \"Junior\")",
        "resultsToTake": numberofJobs,
        "locationName": "London",
        "distanceFromLocation": 350,
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
    jobs = fetch_jobs(1)
    for job in jobs:
        print(job)
        job_title = str(job.get('jobTitle', ''))
        print(job_title)
        if passed_deadline(job):
            continue

        if job_title.find("Senior") != -1 and job_title.find("Lead") != -1:
            print("SSkipped")
            continue
        
        try:
            post_job(job)
        except Exception as e:
            print(f"Error posting job {job.get('jobTitle')}: {e}")

if __name__ == "__main__":
    main()

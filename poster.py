import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json, hashlib
from state import load_seen, save_seen

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

IGNORE_KEYWORDS = [
    "Lead",
    "Senior",
    "Manager"
]

def stable_id(job : dict) -> str:
    jobid = job.get("jobId", "")
    if jobid:
        return f"reed:{jobid}"
    base = "|".join([
        job.get("jobUrl", ""),
        job.get("jobTitle", ""),
        job.get("employerName", ""),
        job.get("locationName", ""),
    ]).lower()
    return "reedhash:" + hashlib.sha256(base.encode()).hexdigest()

def fmt_money(amount):
    if amount is None:
        return "N/A"
    try: 
        return f"£{int(float(amount)):,}"
    except (ValueError, TypeError):
        return str(amount)
    
def build_embed(title, company, location, link, minSalary=None, maxSalary=None, postedDate=None, deadline=None):
    lo, hi = fmt_money(minSalary), fmt_money(maxSalary)
    salary = None
    if lo and hi:
        salary = f"💷 {lo} - {hi}"
    elif lo or hi:
        salary = f"💷 {lo or hi}"

    fields = []
    if company:
        fields.append({"name": "🏢 Company", "value": company, "inline": True})
    if location:
        fields.append({"name": "📍 Location", "value": location, "inline": True})
    if salary:
        fields.append({"name": "💷 Salary", "value": salary, "inline": False})
    if postedDate:
        fields.append({"name": "📅 Posted", "value": str(postedDate), "inline": True})
    if deadline:
        fields.append({"name": "⏳ Deadline", "value": str(deadline), "inline": True})

    embed = {
        "title": title,
        "url": link,
        "color": 0x2ECC71,   # green accent
        "fields": fields,
        "footer": {"text": "Job feed via Reed API"},

    }
    return embed


def post_job(job):
    title = job.get('jobTitle', 'No title provided')
    company = job.get('employerName', 'No company provided')
    location = job.get('locationName', 'No location provided')
    link = job.get('jobUrl', 'No link provided')
    minSalary = job.get('minimumSalary')
    maxSalary = job.get('maximumSalary')
    postedDate = job.get('date', 'N/A')
    deadline = job.get('expirationDate', 'N/A')

    embed = build_embed(title, company, location, link, minSalary, maxSalary, postedDate, deadline)
    print(f"Posting job: {title} at {company}")

    resp = requests.post(
        HOOK_URL,
        json={"embeds": [embed]}
    )
    resp.raise_for_status()

def fetch_jobs(limit: int = 100, page_size: int = 25):
    headers = {"Accept": "application/json"}
    all_results = []
    for skip in range(0, limit, page_size):
        params = {
            "keywords": "(\"Software Engineer\" OR \"Backend Engineer\" OR \"Frontend Engineer\" OR \"Machine Learning Engineer\" OR \"Mobile Engineer\") AND (\"Graduate\" OR \"Junior\")",
            "resultsToTake": page_size,
            "resultsToSkip": skip,
            "locationName": "London",
            "distanceFromLocation": 350,
            "permanent": "true",
            "fullTime": "true",
            "graduate": "true"
        }
        r = requests.get(REED_URL, params=params, headers=headers, timeout=30, auth=(REED_API_KEY, ''))
        r.raise_for_status()
        results = r.json().get('results', [])
        if not results:
            break
        all_results.extend(results)
    return all_results


def passed_deadline(job):
    deadline = datetime.strptime(job.get('expirationDate'), "%d/%m/%Y") if job.get('expirationDate') else None
    if deadline:
        return deadline < datetime.today()
    return False

def main():
    jobs = fetch_jobs(limit=100)
    print(f"Fetched {len(jobs)} jobs")
    seen_global = load_seen()
    print(f"Loaded {len(seen_global)} previously seen jobs")
    seen_in_run = set()
    newly_posted = set()
    for job in jobs:
        sid = stable_id(job)
        if sid in seen_global or sid in seen_in_run:
            continue
        seen_in_run.add(sid)

        job_title = str(job.get('jobTitle', ''))
        
        if passed_deadline(job):
            continue

        if any(keyword.lower() in job_title.lower() for keyword in IGNORE_KEYWORDS):
            print(f"Ignoring job: {job_title}")
            continue
        
        try:
            print(f"Posting job: {job_title}")
            post_job(job)
            newly_posted.add(sid)
        except Exception as e:
            print(f"Error posting job {job.get('jobTitle')}: {e}")

    if newly_posted:
        seen_global |= newly_posted
        save_seen(seen_global)


if __name__ == "__main__":
    main()

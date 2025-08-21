import requests
import os
from dotenv import load_dotenv

load_dotenv()

HOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
ADZUNA_APP_ID = os.environ["ADZUNA_APP_ID"]
ADZUNA_KEY = os.environ["ADZUNA_APP_KEY"]
ADZUNA_URL = f"https://api.adzuna.com/v1/api/jobs/gb/search/1"

ALLOWED_TITLES = [
        "Software Engineer",
        "Backend Engineer",
        "Frontend Engineer",
        "Full Stack Engineer",
        "Machine Learning Engineer"
    ]

def post_job(job):
    title = job.get('title', 'No title provided')
    company = job.get('company', {}).get('display_name', 'No company provided')
    location = (job.get('location') or {}).get('display_name', 'No location provided')
    link = job.get('redirect_url', 'No link provided')

    message = f"**{title}**\n"
    message += f"Company: {company}\n"
    message += f"Location: {location}\n"
    message += f"Link: {link}\n"
    r = requests.post(HOOK_URL, json={"content": message})
    r.raise_for_status()

def fetch_jobs():
    
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_KEY,
        "what": "Software Engineer",
        "results_per_page": 10,
        "where": "London"
    }
    headers = {
        "Accept": "application/json"
    }
    r = requests.get(ADZUNA_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get('results', [])

def allowed_job(job):
    title = job.get('title', '').lower()
    return any(allowed_title.lower() in title for allowed_title in ALLOWED_TITLES)

def main():
    jobs = fetch_jobs()
    for job in jobs:
        if not allowed_job(job):
            continue
        try:
            post_job(job)
        except Exception as e:
            print(f"Error posting job {job.get('title')}: {e}")

if __name__ == "__main__":
    main()

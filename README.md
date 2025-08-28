# jobPostingWebHook
Discord Webhook for Job Searching

## Usage Instructions
### Prerequisites
- Python (v3.8 or higher)
- A Discord server with webhook permissions
- Reed.co.uk API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kkjoshi01/jobPostingWebHook.git
   cd jobPostingWebHook
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Discord Webhook**
   - Go to your Discord server settings
   - Navigate to Integrations > Webhooks
   - Create a new webhook and copy the webhook URL

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```
   DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
   REED_API_KEY=your_reed_api_key_here
   ```
   To automate, add the API Keys to Github Secrets and use the JobPoster Workflow to run hourly-automated jobs.

### Running the Application

```bash
python poster.py
```

### Configuration Options

- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
- `REED_API_KEY` : Your Reed.co.uk API key
- `JOB_SEARCH_KEYWORDS`: Comma-separated list of keywords to search for


### Example Output

The bot will send formatted messages to your Discord channel with:
- Job title and company
- Location and salary range
- Direct link to the job posting
- Timestamp of when the job was found

### Troubleshooting

- **Webhook not working**: Verify your Discord webhook URL is correct
- **No jobs found**: Check your search keywords and ensure job sources are accessible




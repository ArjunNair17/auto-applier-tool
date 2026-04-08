# Auto-Applier Tool

Autonomous job-application agent that reads job URLs from CSV, matches pre-tailored resumes by folder order, fills ATS forms via Playwright, pauses for manual intervention on CAPTCHA/free-text/email verification, and logs results.

## Features

- ✅ Parse job URLs from CSV file
- ✅ Match resumes from numbered folders (`01_*/`, `02_*/`) by row index
- ✅ Detect ATS systems (Greenhouse, Lever in v1)
- ✅ Auto-fill forms from profile data
- ✅ Resume upload
- ✅ Pause for manual intervention (CAPTCHA, free-text, email verification)
- ✅ Track results in CSV
- ✅ Rate-limited to 1–5 apps/hour

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Prepare your job list:**
   Create `data/jobs.csv` with columns:
   ```
   job_url,company_name
   https://boards.greenhouse.io/example/jobs/12345,Example Company
   https://jobs.lever.co/example/67890,Another Company
   ```

3. **Organize resumes:**
   Create numbered folders matching your CSV rows:
   ```
   job_applications/
   ├── 01_Example Company/
   │   └── Arjun_Resume.pdf
   ├── 02_Another Company/
   │   └── Arjun_Resume.pdf
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

   On first run, you'll be prompted to enter your profile information (name, email, phone, etc.) which will be saved to `config/profile.json`.

## How It Works

1. Reads `data/jobs.csv` for job URLs and company names
2. Matches resumes from numbered folders by row index
3. Opens each job URL in a headed browser
4. Detects the ATS system (Greenhouse/Lever)
5. Auto-fills standard fields from your profile
6. Uploads the matched resume
7. Pauses for manual intervention if needed (CAPTCHA, free-text questions, email verification)
8. Submits the application
9. Logs results to `data/applications.csv`
10. Waits 12–60 minutes before the next application (rate limiting)

## Output

Application results are tracked in `data/applications.csv`:

| Column | Description |
|--------|-------------|
| job_id | Row index from input CSV |
| company | Company name |
| job_url | Job posting URL |
| status | `applied`, `manual_required`, `failed`, `needs_email_verification`, `skipped` |
| resume_path | Path to resume used |
| timestamp | When application was attempted |
| notes | Any errors or notes |

## Supported ATS Systems

- ✅ Greenhouse (`boards.greenhouse.io`)
- ✅ Lever (`jobs.lever.co`)
- ⏳ Workday (planned)
- ⏳ Ashby (planned)

## Manual Intervention

When the application requires manual action (CAPTCHA, free-text, email verification):

1. The browser will pause and wait
2. A message will display what's needed
3. Complete the action manually in the browser
4. Press Enter in your terminal to continue

## Rate Limiting

The tool automatically spaces applications 12–60 minutes apart (randomized) to avoid detection and follow best practices for job applications.

## Development

```bash
# Run tests
pytest

# Install dev dependencies
pip install pytest pytest-playwright
```

## License

MIT

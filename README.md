# JPY → INR Daily Rate Tracker

Tracks **1 Japanese Yen → Indian Rupee** every day, appends to `rates.csv`,
and **opens a GitHub Issue** whenever the rate drops on consecutive days —
so you get a native GitHub notification (web, email, or mobile app).

---

## How it works

| Step | What happens |
|------|-------------|
| GitHub Actions runs daily at 08:00 UTC | Triggers `check_rate.py` |
| Script fetches live rate | Free exchangerate-api.com — no API key needed |
| Rate appended to `rates.csv` | Auto-committed back to the repo |
| Consecutive-drop check | If today < yesterday < day-before … a GitHub Issue is opened |
| GitHub notifies you | Via web, email, or the GitHub mobile app |

---

## Setup (one-time, zero secrets needed)

### 1. Fork / clone this repo

### 2. Enable Issues on your repo
Settings → Features → ✅ Issues

### 3. Create the `rate-alert` label (optional but nice)
Issues → Labels → New label → name it `rate-alert`

### 4. Check your GitHub notification settings
github.com → Settings → Notifications — Issues should be on by default.

That's it. GITHUB_TOKEN is provided automatically by Actions — no secrets to add.

---

## Manual test
Actions → JPY/INR Rate Tracker → Run workflow

---

## Customise
- Run time: cron in .github/workflows/track_rate.yml
- Currency pair: change JPY/INR in fetch_rate()
- Streak length: change >= 2 in consecutive_drops()

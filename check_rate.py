import csv
import os
import sys
from datetime import date

import requests

CSV_FILE = "rates.csv"
FIELDNAMES = ["date", "jpy_to_inr"]


def fetch_rate() -> float:
    url = "https://api.exchangerate-api.com/v4/latest/JPY"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return round(response.json()["rates"]["INR"], 6)


def load_csv() -> list[dict]:
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="") as f:
        return list(csv.DictReader(f))


def save_rate(today: str, rate: float):
    rows = load_csv()
    existing = next((r for r in rows if r["date"] == today), None)
    if existing:
        existing["jpy_to_inr"] = str(rate)
    else:
        rows.append({"date": today, "jpy_to_inr": str(rate)})
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def consecutive_drops(rows: list[dict]) -> tuple[bool, list[dict]]:
    if len(rows) < 2:
        return False, []
    sorted_rows = sorted(rows, key=lambda r: r["date"])
    streak = [sorted_rows[-1]]
    for i in range(len(sorted_rows) - 2, -1, -1):
        prev = float(sorted_rows[i]["jpy_to_inr"])
        curr = float(streak[0]["jpy_to_inr"])
        if curr < prev:
            streak.insert(0, sorted_rows[i])
        else:
            break
    return (True, streak) if len(streak) >= 2 else (False, [])


def open_github_issue(streak: list[dict]):
    token = os.environ.get("GITHUB_TOKEN")
    repo  = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GITHUB_TOKEN / GITHUB_REPOSITORY not set — skipping issue creation.")
        return

    first_rate = float(streak[0]["jpy_to_inr"])
    last_rate  = float(streak[-1]["jpy_to_inr"])
    drop_pct   = round((first_rate - last_rate) / first_rate * 100, 3)
    days       = len(streak)

    table_rows = "\n".join(
        f"| {r['date']} | \u20b9{r['jpy_to_inr']} |" for r in streak
    )

    title = f"\U0001f4c9 JPY/INR dropped {days} days in a row \u2014 {streak[-1]['date']}"
    body = f"""## \u26a0\ufe0f Consecutive drop detected

1 JPY has fallen for **{days} consecutive days** ({drop_pct}% total drop).

| Date | 1 JPY = INR |
|------|------------|
{table_rows}

> From \u20b9{first_rate} on {streak[0]['date']} \u2192 \u20b9{last_rate} on {streak[-1]['date']}

---
*Opened automatically by the [JPY/INR Rate Tracker](.github/workflows/track_rate.yml) workflow.*
"""

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"title": title, "body": body, "labels": ["rate-alert"]}

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    print(f"GitHub Issue opened: {resp.json().get('html_url', '')}")


def main():
    today = str(date.today())
    print(f"Fetching JPY \u2192 INR rate for {today}\u2026")

    rate = fetch_rate()
    print(f"  1 JPY = \u20b9{rate}")

    save_rate(today, rate)
    print(f"  Saved to {CSV_FILE}")

    rows = load_csv()
    dropping, streak = consecutive_drops(rows)

    if dropping:
        print(f"  \u26a0\ufe0f  Consecutive drop over {len(streak)} days \u2014 opening GitHub Issue\u2026")
        open_github_issue(streak)
    else:
        print("  \u2705 No consecutive drop detected.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

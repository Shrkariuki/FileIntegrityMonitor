"""
File Integrity Monitor with Email Alerts
- Uses SHA-256 to fingerprint files in MONITOR_DIR
- Keeps a baseline in BASELINE_FILE (JSON)
- Periodically checks for NEW / MODIFIED / DELETED files
- Sends an email alert for each detected event (uses SMTP)
- Reads email credentials from a local .env (not committed)
"""

import os
import time
import hashlib
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO") or EMAIL_USER  # fallback to self
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))  # seconds

# Monitoring config (change as desired)
MONITOR_DIR = os.getenv("MONITOR_DIR", os.path.join(os.getcwd(), "watched_folder"))
BASELINE_FILE = os.getenv("BASELINE_FILE", "baseline.json")
LOG_FILE = os.getenv("LOG_FILE", "fim_events.log")

# --- Utility: compute SHA-256 hash of file contents ---
def get_file_hash(path: str) -> str:
    """Return the SHA256 hex digest for the given file path. If unreadable, return None."""
    try:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError, IsADirectoryError) as e:
        # Could not read file (locked, removed mid-read, directory)
        return None

# --- Email alerting ---
def send_email_alert(subject: str, body: str) -> None:
    """Send an email alert via Gmail SMTP (uses EMAIL_USER & EMAIL_PASS from .env)."""
    if not EMAIL_USER or not EMAIL_PASS:
        print("⚠️ Email credentials not set. Skipping email send.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print(f"📧 Email sent: {subject}")
    except Exception as e:
        print(f"⚠️ Failed to send email: {e}")

# --- Logging to a simple text log ---
def append_log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"⚠️ Could not write to log file: {e}")

# --- Baseline persistence helpers ---
def load_baseline() -> dict:
    if os.path.exists(BASELINE_FILE):
        try:
            with open(BASELINE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_baseline(baseline: dict) -> None:
    try:
        with open(BASELINE_FILE, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save baseline: {e}")

# --- Main detection loop ---
def monitor_loop() -> None:
    os.makedirs(MONITOR_DIR, exist_ok=True)
    print(f"🛡️ Monitoring folder: {MONITOR_DIR}")
    append_log(f"Monitoring started for {MONITOR_DIR}")
    baseline = load_baseline()

    # If baseline empty, create baseline and exit first run (or continue)
    if not baseline:
        print("No baseline found — creating baseline from current files.")
        baseline = {}
        for root, _, files in os.walk(MONITOR_DIR):
            for fname in files:
                p = os.path.join(root, fname)
                h = get_file_hash(p)
                if h:
                    baseline[p] = h
        save_baseline(baseline)
        append_log("Baseline created.")
        print(f"Baseline created ({len(baseline)} files). Monitoring will start now.")

    # Continuous monitoring
    while True:
        current = {}
        # Build the current snapshot
        for root, _, files in os.walk(MONITOR_DIR):
            for fname in files:
                p = os.path.join(root, fname)
                h = get_file_hash(p)
                if h:  # only record readable files
                    current[p] = h

        # Detect new files
        new_files = [p for p in current if p not in baseline]
        # Detect modified files
        modified_files = [p for p in current if p in baseline and baseline[p] != current[p]]
        # Detect deleted files
        deleted_files = [p for p in baseline if p not in current]

        # Handle events
        for p in new_files:
            msg = f"New file detected: {p}"
            print("➕", msg)
            append_log(msg)
            body = f"New file detected:\n\nPath: {p}\nTime: {datetime.now()}\nHash: {current[p]}\n"
            send_email_alert("FIM Alert: New file detected", body)

        for p in modified_files:
            old = baseline.get(p)
            new = current.get(p)
            msg = f"Modified file: {p}"
            print("🔁", msg)
            append_log(msg)
            body = (
                f"File modified:\n\nPath: {p}\nTime: {datetime.now()}\n\n"
                f"Old hash: {old}\nNew hash: {new}\n"
            )
            send_email_alert("FIM Alert: File modified", body)

        for p in deleted_files:
            old = baseline.get(p)
            msg = f"Deleted file: {p}"
            print("❌", msg)
            append_log(msg)
            body = (
                f"File deleted:\n\nPath: {p}\nTime: {datetime.now()}\n\n"
                f"Last known hash: {old}\n"
            )
            send_email_alert("FIM Alert: File deleted", body)

        # Persist the current snapshot as the new baseline
        save_baseline(current)
        baseline = current

        # Sleep until next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
        append_log("Monitoring stopped by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        append_log(f"Fatal error: {e}")

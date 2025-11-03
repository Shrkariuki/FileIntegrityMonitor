# 🛡️ File Integrity Monitor

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-success)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Security](https://img.shields.io/badge/Security-FIM%20Tool-critical)

> A lightweight **Python-based File Integrity Monitoring (FIM)** tool that continuously watches directories for file changes — including creations, deletions, and modifications — and instantly sends **email alerts** when suspicious activity is detected.

---

## 🚀 Features

- 🔍 **Real-time Monitoring** — Detects file additions, deletions, or modifications instantly  
- 🔐 **SHA256 Hash Validation** — Ensures file integrity using cryptographic hashing  
- 📧 **Email Notifications** — Sends alerts directly to your inbox when changes occur  
- ⚙️ **Secure Configuration** — `.env` file stores credentials securely (excluded from Git)  
- 🧩 **Customizable Watch Paths** — Easily define any directory to monitor  

---

## 🧰 Tech Stack

| Component | Description |
|------------|-------------|
| **Language** | Python 3.12+ |
| **Libraries** | `watchdog`, `hashlib`, `python-dotenv`, `smtplib` |
| **OS Support** | Windows, Linux, macOS |

---

## ⚙️ Installation & Setup

python -m venv venv
venv\Scripts\activate   # On Windows
# or
source venv/bin/activate   # On macOS/Linux
Install dependencies

bash
Copy code
pip install -r requirements.txt
If missing, create it:

bash
Copy code
pip freeze > requirements.txt
🔐 Configuration

Create a .env file in the project root:

bash
Copy code
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_app_password
TO_EMAIL=recipient_email@example.com
WATCHED_FOLDER=D:\cybersecurity-tools\watched_folder

⚠️ Important Security Tips

Do not use your real password — create an App Password for email SMTP.

.env is excluded from version control via .gitignore.

▶️ Run the Monitor
bash
Copy code
python main.py
Example output:

yaml
Copy code
🛡️ Monitoring folder: D:\cybersecurity-tools\watched_folder
➕ New file detected: report.pdf
❌ Deleted file: secret.txt
⚠️ Modified file: config.yaml
📧 Email alert sent successfully!
📬 Email Alert Example
Every alert includes:

File path

Change type (Created, Modified, Deleted)

Timestamp

📁 Folder Structure
bash
Copy code
file_integrity_monitor/
│
├── main.py              # Main monitoring script
├── .env                 # Environment variables (ignored by git)
├── .gitignore           # Ignore patterns
├── README.md            # Documentation
└── requirements.txt     # Dependencies


🧠 How It Works
Watchdog continuously listens for file system events.

Hash comparison (SHA256) verifies whether files have been tampered with.

When a change is detected, SMTP sends an alert email with the details.

The .env keeps your credentials safe and out of GitHub commits.

💡 Future Enhancements
📨 Multi-recipient notifications

📊 Logging to a secure database or CSV

🌐 Web dashboard for visualization

🔔 Integration with SIEM or intrusion detection systems



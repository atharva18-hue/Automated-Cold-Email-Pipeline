import smtplib
import csv
import time
import random
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'atharvachavhan18@gmail.com'
APP_PASSWORD = 'ccfbudvkzretumns'  # Gmail App Password

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'Data', 'recipients_list.csv')
RESUME_PATH = os.path.join(BASE_DIR, 'Assets', 'AanayaVerma.pdf')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'Templates', 'email_template_v1.txt')
FAILED_CSV_PATH = os.path.join(BASE_DIR, 'Data', 'failed_emails.csv')
LOG_PATH = os.path.join(BASE_DIR, 'run_log.txt')

LINKEDIN = "Your LinkedIn URL"
PHONE = "Your Phone Number"

MAX_RETRIES = 3
RETRY_DELAY = 15
PREVIEW_MODE = False        # 🔹 True = Preview Only, False = Send Real Emails
EMAIL_DELAY_MIN = 10
EMAIL_DELAY_MAX = 25

# -------------------------------------------------------------------

def log(message):
    """Write logs to console + file."""
    print(message)
    with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def load_template(path):
    """Load and split template into subject + body."""
    log(f"[DEBUG] Loading template from {path}...")
    if not os.path.exists(path):
        log(f"FATAL ERROR: Template file not found at {path}")
        return None, None
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.startswith("Subject:"):
        log("ERROR: Template must start with 'Subject: ...'")
        return None, None
    subject_line = content.split('\n', 1)[0].replace('Subject:', '').strip()
    body = content.split('\n', 1)[1].strip()
    log("[DEBUG] Template loaded successfully.")
    return subject_line, body

def personalize_text(text, data):
    """Replace placeholders like {{Company}}, {{FirstName}}."""
    for key, val in data.items():
        text = text.replace(f"{{{{{key}}}}}", str(val or ''))
    return text

def create_email_message(recipient, subject_template, body_template):
    """Create personalized email with HTML + attachment."""
    email = recipient.get('Email', '')
    name = recipient.get('FirstName', '').strip()
    subject = personalize_text(subject_template, recipient)
    body = personalize_text(body_template, recipient)

    greeting_html = f"<p>Hi {name},</p>" if name else ""
    greeting_text = f"Hi {name},\n\n" if name else ""

    footer_html = (
        f"<br><br>Best,<br><b>Aanaya Verma</b><br>"
        f"{SENDER_EMAIL}<br>{PHONE}<br>"
        f"<a href='{LINKEDIN}' target='_blank'>LinkedIn</a>"
    )
    footer_text = (
        f"\n\nBest,\nAanaya Verma\n{SENDER_EMAIL}\n"
        f"{PHONE}\nLinkedIn: {LINKEDIN}"
    )

    body_html = body.replace('\n', '<br>')
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(greeting_text + body + footer_text, 'plain'))
    msg.attach(MIMEText(greeting_html + body_html + footer_html, 'html'))

    if os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename='AanayaVerma_Resume.pdf')
            msg.attach(attach)
    else:
        log(f"[WARN] Resume not found at {RESUME_PATH}")
    return msg

def is_valid_email(email):
    return bool(email) and '@' in email

def send_email(recipient, subject_template, body_template, server):
    """Send one email (with retries)."""
    email = (recipient.get('Email') or '').strip()
    if not email:
        log(f"[DEBUG] Skipping: empty email.")
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            msg = create_email_message(recipient, subject_template, body_template)

            if PREVIEW_MODE:
                log(f"\n[PREVIEW] To: {email}\nSubject: {msg['Subject']}\nBody:\n{personalize_text(body_template, recipient)}\n")
                return True

            server.sendmail(SENDER_EMAIL, email, msg.as_string())
            log(f"✅ Sent to {email} ({recipient.get('Company', 'N/A')})")
            return True

        except Exception as e:
            log(f"⚠️ Attempt {attempt} failed for {email}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    return False

def main():
    log("\n--------------------------------------------------")
    log("[DEBUG] Script started.")

    subject_template, body_template = load_template(TEMPLATE_PATH)
    if not subject_template:
        log("[FATAL] Template load failed.")
        return

    sent_count = 0
    failed_emails = []

    # Load CSV
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    total = len(reader)
    log(f"[DEBUG] Loaded {total} recipients.")

    # SMTP setup
    server = None
    if not PREVIEW_MODE:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        log("[DEBUG] SMTP login successful.")

    # Process each email
    for i, row in enumerate(reader, 1):
        email = (row.get('Email') or '').strip()
        status = (row.get('Status') or '').lower()

        if status == 'sent':
            log(f"[SKIP] Already sent: {email}")
            continue

        if not is_valid_email(email):
            log(f"[INVALID] Skipping: {email}")
            row['Status'] = 'invalid'
            failed_emails.append(email)
        else:
            success = send_email(row, subject_template, body_template, server)
            if success:
                row['Status'] = 'sent'
                sent_count += 1
            else:
                row['Status'] = 'failed'
                failed_emails.append(email)

        # Update CSV each time
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=reader[0].keys())
            writer.writeheader()
            writer.writerows(reader)

        print(f"[Progress] {i}/{total} | ✅ Sent: {sent_count} | ❌ Failed: {len(failed_emails)}", end='\r')

        if PREVIEW_MODE:
            break

        delay = random.randint(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
        log(f"[DEBUG] Waiting {delay}s before next email...")
        time.sleep(delay)

    if server:
        server.quit()

    # Export failed emails
    if failed_emails:
        failed_rows = [r for r in reader if r['Status'] in ('failed', 'invalid')]
        with open(FAILED_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=reader[0].keys())
            writer.writeheader()
            writer.writerows(failed_rows)
        log(f"[EXPORT] Failed/Invalid emails saved to {FAILED_CSV_PATH}")

    log("✅ Pipeline complete.")
    log(f"Total: {total} | Sent: {sent_count} | Failed: {len(failed_emails)}")

if __name__ == "__main__":
    main()

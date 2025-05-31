import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

# Access variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def send_mails(content: str, emails: list) -> dict:
    subject = "motivation"
    try:
        msg = MIMEText(content, 'plain')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(USERNAME, PASSWORD)
            server.sendmail(SENDER_EMAIL, emails, msg.as_string())
        
        return {"status": "Sent Successfully!"}
    except Exception as e:
        return {"status": f"Not sent Successfully! Error: {str(e)}"}



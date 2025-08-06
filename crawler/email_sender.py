import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from dotenv import load_dotenv
import markdown

# Load credentials from .env
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = [email.strip() for email in os.getenv("EMAIL_TO", "").split(",") if email.strip()]

def send_markdown_email(md_path: str):
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_TO:
        raise ValueError("Missing email credentials or recipients in .env")

    # Load and process Markdown content
    with open(md_path, "r", encoding="utf-8") as f:
        article_body = f.read()

    # Define header and footer
    header_md = "Good morning,\n\nHere is your weekly fitness industry news summary.\n"
    footer_md = "\nHave an amazing day,\n\n*Fitness Weekly Bot*"

    # Full plain text content
    full_md = f"{header_md}\n\n{article_body}\n\n{footer_md}"

    # Convert to HTML (header/footer + body)
    header_html = "<p><strong>Good morning,</strong><br>Here is your weekly fitness industry news summary.</p>"
    footer_html = "<p>Have an amazing day,<br><em>Fitness Weekly Bot</em></p>"
    article_html = markdown.markdown(article_body)
    full_html = f"{header_html}\n{article_html}\n{footer_html}"

    # Build multipart email
    msg = MIMEMultipart("alternative")
    today = date.today().strftime("%B %d, %Y")
    msg['Subject'] = f"Fitness Industry News - {today}"
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(EMAIL_TO)

    # Attach plain text and HTML versions
    msg.attach(MIMEText(full_md, "plain"))
    msg.attach(MIMEText(full_html, "html"))

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {msg['To']} with subject: {msg['Subject']}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
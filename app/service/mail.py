import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from app.config import SMTP_LOGIN, SMTP_PORT, SMTP_EMAIL, SMTP_SERVER, \
        SMTP_ENABLED, SMTP_PASSWORD

from app.template.init import jinja


def notify_user_created(new_user: User, current_user: User) -> bool:

    return


def notify_report_published(report: Report, current_user: User) -> bool:

    return


def send_html_email(recipient_email, subject, html_message):
    """
    Sends an HTML-encoded email through SMTP using predefined constants.

    Parameters:
    - recipient_email: The email address of the recipient.
    - subject: The subject of the email.
    - html_message: The HTML content of the email.

    Returns:
    - True if the email was sent successfully, False otherwise.
    """

    if not SMTP_ENABLED:
        return

    try:
        # Create the MIMEMultipart message object
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)

        # Attach the HTML message to the email
        msg.attach(MIMEText(html_message, 'html'))


        # Connect to the SMTP server using SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)  # Log in to the SMTP server
            server.sendmail(SMTP_EMAIL, recipient_email, msg.as_string())  # Send the email

        print("Email sent successfully!")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

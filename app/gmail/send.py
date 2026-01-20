import base64
from email.mime.text import MIMEText

def send_email(service, to, subject, body, approval_status, cc=None, bcc=None):
    if approval_status != "APPROVED":
        raise PermissionError("Email send blocked: approval required")

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

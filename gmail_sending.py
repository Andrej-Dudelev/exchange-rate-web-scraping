from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
import os 
import base64

# Kelias iki OAuth 2.0 credentials.json failo
CREDENTIALS_FILE = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.sending"]

def gmail_sending(subject, body, recipient_email):
    """
    Siunčia el. laišką naudojant Gmail API.
    """
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )

    service = build("gmail", "v1", credentials=creds)
    message = MIMEText(body)
    message["to"] = recipient_email
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    # koduojame ir siunciame el.laiska
    message = {"raw": raw_message}
    service.users().messages().send(userId="me", body=message).execute()
    print("El. laiskas issiustas:", subject)
  

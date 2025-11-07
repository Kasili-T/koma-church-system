# accounts/mpesa.py
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

# Your Mpesa credentials
MPESA_CONSUMER_KEY = "aOufe5D70rWbAdn5Vjmt9fdEk9b72FbmFp4QHWAPTedGCib2"
MPESA_CONSUMER_SECRET = "cuOWjZVCx5I5h20ku9WCRNOgCFnlYkGko7dscXvrJJjWq9611qrAhksXxlOK8Fi9"
MPESA_SHORTCODE = "600999"
MPESA_PASSKEY = "YOUR_PASSKEY"
MPESA_ENV = "sandbox"  # change to "production" later

if MPESA_ENV == "sandbox":
    MPESA_BASE_URL = "https://sandbox.safaricom.co.ke"
else:
    MPESA_BASE_URL = "https://api.safaricom.co.ke"

def get_access_token():
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json().get("access_token")

def lipa_na_mpesa(amount, phone_number, account_reference, transaction_desc):
    token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": float(amount),
        "PartyA": phone_number,  # User phone number
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/accounts/mpesa-callback/",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }
    response = requests.post(f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    return response.json()

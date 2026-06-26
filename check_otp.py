import os, sys
sys.path.append('d:/STARTUP/GARDA/website')
from app import create_app
app = create_app()
with app.app_context():
    db = app.db_firestore
    docs = db.collection('website').stream()
    for doc in docs:
        data = doc.to_dict()
        print(f"ID: {doc.id}, Email: {data.get('email')}, OTP: {data.get('otp_code')}")

import os
import django
import requests
import hashlib
import time
from datetime import datetime

# =============================================================
# 🔑 THE IMPERIAL BRIDGE: CONNECTING STANDALONE TO DJANGO
# =============================================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UNSCCDC.settings') # Use your project name
django.setup()

# Now we can safely import your models
from api.models import School, SchoolPayLedger, Student
from api.views import sync_schoolpay_transaction

def fetch_schoolpay_transactions():
    BASE_URL = "https://schoolpay.co.ug/paymentapi"
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    # 1. 🛡️ Multi-Tenant Registry: Get all schools registered for SchoolPay
    schools = School.objects.exclude(school_code="") 
    
    for school in schools:
        # Generate the mandatory MD5 security hash
        hash_input = school.school_code + today_str + school.api_password
        request_hash = hashlib.md5(hash_input.encode()).hexdigest().upper()
        
        endpoint_url = f"{BASE_URL}/AndroidRS/SyncSchoolTransactions/{school.school_code}/{today_str}/{request_hash}"
        
        try:
            response = requests.get(endpoint_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                if data.get("returnCode") == 0:
                    txs = data.get("supplementaryFeePayments", [])
                    for tx in txs:
                        # 💎 THE BRAIN SYNC 💎
                        # Calls the function we put in api/views.py
                        success, msg = sync_schoolpay_transaction(school, tx)
                        if success:
                            print(f"✅ [STATION {school.name}]: {msg}")
                        else:
                            # This skips if receipt already exists (Idempotency)
                            pass 
                            
        except Exception as e:
            print(f"📡 [LINK ERROR] {school.name}: {e}")

# =============================================================
# 🚀 THE INFINITE NATIONAL MONITOR (RUNNING EVERY 60 SECONDS)
# =============================================================
if __name__ == "__main__":
    print("---------------------------------------------------")
    print("👑 UNSCCDC NATIONAL SCHOOLPAY WORKER ACTIVE")
    print("---------------------------------------------------")
    while True:
        fetch_schoolpay_transactions()
        time.sleep(60) # Rest for 1 minute before next sweep
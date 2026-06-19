import requests
import json
from api.models import School, Student, SchoolPayLedger

def fetch_all_school_transactions():
    """
    🌍 THE Hub Hub Hub Hub Hub Hub Hub MULTI-SCHOOL Hub Hub Hub Hub Hub Hub Hub 
    Polls the SchoolPay API for every institution registered in the Hub.
    """
    schools = School.objects.filter(is_verified=True) # Only verified schools
    
    for school in schools:
        if not school.school_code or not school.api_password:
            continue
            
        print(f"--- 📡 Syncing: {school.name} ---")
        
        try:
            # 💎 REAL-TIME BANK API UPLINK
            # We replace this with the real SchoolPay/Bank Endpoint
            url = f"https://api.schoolpay.co.ug/v1/transactions/" 
            headers = {"Authorization": f"Bearer {school.api_password}"}
            params = {"school_code": school.school_code}

            # In production, this call gets the real money data
            # response = requests.get(url, headers=headers, params=params)
            # data = response.json()
            
            # --- 🛡️ FOR YOUR Hub Hub Hub TEST Hub Hub Hub ---
            # We assume 'data' contains new transactions from the gateway
            pass 

        except Exception as e:
            print(f"--- 🛑 UPLINK ERROR for {school.name}: {e} ---")

def process_incoming_payload(payload, school):
    """
    Processes a single transaction payload from the bank.
    """
    # Find student by PRN (payment_code)
    student = Student.objects.filter(payment_code=payload['student_prn']).first()
    
    if student:
        # Check if transaction already exists to prevent double counting
        if not SchoolPayLedger.objects.filter(receipt_number=payload['receipt']).exists():
            SchoolPayLedger.objects.create(
                student=student,
                school=school,
                amount=payload['amount'],
                receipt_number=payload['receipt'],
                category=payload.get('category', 'Tuition'),
                raw_data=payload
            )
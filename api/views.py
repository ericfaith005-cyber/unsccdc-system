from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from .models import *
# --- 🏛️ SURGERY: PDF IMPORTS (api/views.py) ---
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .models import Staff, Student # 💎 Ensure Staff is imported!
import africastalking
import random
import uuid
import traceback

# --- 1. SOVEREIGN SMS GATEWAY (LIVE PRODUCTION) ---
username = "yaweeric" 
api_key = "atsk_d23adde5b15396790edd13222388ce6a8ac25cf34e2544d703579e8e693477526d49f586" 
try:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
except:
    print("SMS Gateway Standby")

# --- 2. THE IMPERIAL UGANDAN GRADING ENGINE (UNEB & NCHE STANDARDS) ---
def get_national_grading(mark, level, project_score=0):
    """Returns: (Grade, Points, Status, Professional_Remark)"""
    try:
        mark = float(mark)
    except:
        return ('N/A', 0, 'No Data', 'Assessment data pending.')

    if level == 'UCE_NEW': # CBC O-Level
        if mark >= 80: return ('A', 1, 'Exceptional', 'Superior grasp of competencies.')
        elif mark >= 70: return ('B', 2, 'Outstanding', 'Consistently produces quality work.')
        elif mark >= 60: return ('C', 3, 'Satisfactory', 'Shows good understanding of core concepts.')
        else: return ('E', 5, 'Elementary', 'Needs significant support and coaching.')
    elif level == 'PRIMARY': # PLE
        if mark >= 90: return ('D1', 1, 'Distinction', 'Superb performance.')
        elif mark >= 80: return ('D2', 2, 'Distinction', 'Excellent work.')
        elif mark >= 70: return ('C3', 3, 'Credit', 'Very good effort.')
        else: return ('F9', 9, 'Fail', 'Intensive coaching required.')
    elif level == 'UNIVERSITY':
        if mark >= 80: return ('A', 5.0, 'First Class', 'Exceptional academic excellence.')
        return ('C', 2.0, 'Pass', 'Satisfactory.')
    return ('C4', 4, 'Credit', 'Fair performance.')

def get_ple_division(total_agg):
    if 4 <= total_agg <= 12: return "DIVISION 1"
    elif 13 <= total_agg <= 23: return "DIVISION 2"
    return "DIVISION 3"

# --- 3. SOVEREIGN TIERED TAX ENGINE (7000 UGX CAP) ---
def calculate_unsc_tax(amt):
    if amt <= 50000: return 750
    elif amt <= 100000: return 1000
    elif amt <= 200000: return 2000
    elif amt <= 500000: return 4000
    elif amt <= 1000000: return 6000
    return 7000

# --- 4. MASTER HUB VIEWSET (STUDENT/PARENT PORTAL) ---
class StudentViewSet(viewsets.ViewSet):
    """Primary Uplink for the Sovereign Mobile Hub"""

    def list(self, request):
        code_in = request.query_params.get('code', '').strip()
        phone_in = request.query_params.get('phone', '').strip()
        pin_in = request.query_params.get('pin', '').strip()
        p_name = request.query_params.get('parent', '').strip().lower()
        s_name = request.query_params.get('student', '').strip().lower()

        try:
            # 1. Identity Gate
            p_rec = Parent.objects.get(unique_code=code_in, phone_number=phone_in)
            if p_rec.full_name.lower() != p_name or p_rec.linked_student.full_name.lower() != s_name:
                return Response({"msg": "Identity Mismatch"}, status=401)
            
            # 2. Secure PIN Verification
            if pin_in and p_rec.secure_pin.strip() == pin_in:
                s = p_rec.linked_student
                sch = s.school

                # --- 🛡️ SOVEREIGN SAFEGUARDS (FIXES REGISTRY LINK FAILURE) ---
                bio_obj = getattr(s, 'bio', None)
                bio_data = {
                    "career": getattr(bio_obj, 'future_career', "National Leader"),
                    "challenges": getattr(bio_obj, 'challenges_faced', "None"),
                    "inspiration": getattr(bio_obj, 'student_inspiration', "Sovereignty")
                }

                f_rec = getattr(s, 'fees', None)
                finance = {
                    "total_due": getattr(f_rec, 'total_fees_due', 0),
                    "paid": getattr(f_rec, 'total_fees_paid', 0),
                    "balance": (getattr(f_rec, 'total_fees_due', 0) - getattr(f_rec, 'total_fees_paid', 0)),
                }

                # --- 📊 ATTENDANCE MATH ---
                att_records = s.attendance_records.all()
                total_days = att_records.count()
                present_days = att_records.filter(status='PRESENT').count()
                late_days = att_records.filter(status='LATE').count()
                att_percentage = ((present_days + (late_days * 0.5)) / total_days * 100) if total_days > 0 else 100.0
                bio_data["attendance"] = f"{att_percentage:.1f}%"

                # --- 📑 10-COLUMN DATA GATHERING ---
                national_report = {}
                p_map = {"AOI1":"aoi_1", "AOI2":"aoi_2", "MidTerm":"mid_term", "AOI3":"aoi_3", "AOI4":"aoi_4", "EOT":"eot_score"}
                total_pts = 0
                for p_key, m_field in p_map.items():
                    mlist = []
                    current_term_total = 0
                    for m in s.marks.all():
                        score = getattr(m, m_field, 0)
                        g, pts, st, rem = get_national_grading(score, s.level_category)
                        if p_key == "EOT": current_term_total += pts
                        mlist.append({"sub": m.subject.name, "score": score, "grade": g, "aoi1": m.aoi_1, "aoi2": m.aoi_2, "mid": m.mid_term, "aoi3": m.aoi_3, "aoi4": m.aoi_4, "project": m.project_work})
                    if mlist: national_report[p_key] = {"marks": mlist, "agg": current_term_total, "div": get_ple_division(current_term_total) if s.level_category == 'PRIMARY' else "VERIFIED"}

                return Response({
                    "type": "parent", "name": s.full_name, "id": s.account_number, "sch_id": sch.school_account_id, "class": s.current_class, "curriculum": s.level_category,
                    "photo": request.build_absolute_uri(s.photo.url) if s.photo else "", "parent_name": p_rec.full_name,
                    "school": {
                        "name": sch.name, "addr": sch.address, "motto": sch.school_motto, "uneb_no": sch.uneb_center_number, "dir": sch.director,
                        "mission": getattr(sch, 'mission', "Excellence"), "vision": getattr(sch, 'vision', "Sovereignty"), "rating": getattr(sch, 'rating', "⭐⭐⭐⭐⭐"), "type": getattr(sch, 'school_type', "Standard")
                    },
                    "finance": finance, "national_report": national_report, "bio_info": bio_data,
                    "top_performers": [{"name": t.name, "school": t.school_name, "score": t.score, "photo": request.build_absolute_uri(t.photo.url)} for t in NationalTopPerformer.objects.all().order_by('?')[:12]],
                    "feed": [{"school": f.school.name, "title": f.title, "media": request.build_absolute_uri(f.media_file.url), "likes": f.likes_count} for f in SchoolPost.objects.all().order_by('-date')],
                    "ranks": {"nat": 1},
                    "name": s.full_name,
                    "id": s.account_number,
                    "payment_code": s.payment_code, # 💎 SENDING THE PRN HERE
                "ussd_steps": sch.ussd_instructions, # Pulls the custom school steps
                    
                    # 💎 THE RECEIPT ENGINE DATA: Fetches all verified USSD payments
                    "payment_history": [
                        {
                            "receipt": t.receipt_number,
                            "amount": t.amount,
                            "date": t.timestamp.strftime('%d-%b-%Y'),
                            "channel": "USSD / SchoolPay"
                        } for t in SchoolPayLedger.objects.filter(student=s).order_by('-timestamp')
                    ],
                })
                
            return Response({"msg": "PIN_REQUIRED", "motto": p_rec.security_motto})
        except Exception as e:
            print(traceback.format_exc())
            return Response({"msg": "Registry Link Failure"}, status=401)

# --- 🛰️ THE GOLIATH STAFF LOGIN ENGINE (api/views.py) ---
@api_view(['GET'])
def staff_hub_login(request):
    name = request.query_params.get('name', '').strip()
    pin = request.query_params.get('pin', '').strip()
    
    # 1. Search for staff records (Handles multi-school)
    staff_records = Staff.objects.filter(full_name__iexact=name, secure_pin=pin)

    if not staff_records.exists():
        return Response({"msg": "Identity not found. Check Name and PIN."}, status=401)

    schools_data = []
    total_national_wallet = 0

    for record in staff_records:
        # A. Fetch Payroll
        payrolls = StaffPayroll.objects.filter(staff=record).order_by('-payment_date')
        pending_money = payrolls.filter(status='PENDING').aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        total_national_wallet += float(pending_money)
        
        # B. Fetch Students for THIS specific school
        all_students = Student.objects.filter(school=record.school)
        
        # C. Build the Data Package (Ensures NO NULLS reach the App)
        schools_data.append({
            "school_name": str(record.school.name),
            "school_id": str(record.school.school_account_id), # 💎 FORCED TO STRING
            "designation": str(record.designation),
            "salary": float(payrolls.first().net_pay) if payrolls.exists() else 0.0,
            
        # --- 🛡️ SURGERY: PUMPING MARK COMPLETION DATA (api/views.py) ---
            "students": [
                {
                    "id": str(s.account_number), 
                    "name": str(s.full_name), 
                    "class": str(s.current_class),
                    # 💎 THE NEW INTELLIGENCE: Check completion for current teacher's subjects
                    "completed": [
                        res.subject.name for res in s.marks.all() 
                        if res.aoi_1 > 0 or res.mid_term > 0 or res.eot_score > 0
                    ],
                    # Send full scores for the History Tab
                    "full_history": [
                        {
                            "sub": m.subject.name, "aoi1": m.aoi_1, "aoi2": m.aoi_2, 
                            "mid": m.mid_term, "aoi3": m.aoi_3, "aoi4": m.aoi_4, 
                            "eot": m.eot_score, "proj": m.project_work
                        } for m in s.marks.all()
                    ]
                } for s in all_students
            ] if all_students.exists() else [],
            
            "classes": list(all_students.values_list('current_class', flat=True).distinct()) if all_students.exists() else [],
            
            "subjects": [
                {"id": str(sub.id), "name": str(sub.name).upper()} 
                for sub in record.subjects.all()
            ] if record.subjects.exists() else [],
            
            "payroll_history": [
                {"month": p.month, "amount": float(p.net_pay), "status": p.status} 
                for p in payrolls[:5]
            ] if payrolls.exists() else []
        })

    # D. HD Content for Sliders and TikTok
    tops = NationalTopPerformer.objects.all().order_by('?')[:12]
    posts = SchoolPost.objects.all().order_by('-date')

    return Response({
        "type": "staff",
        "name": name.upper(),
        "wallet": total_national_wallet,
        "schools": schools_data,
        "top_performers": [{"name": t.name, "school": t.school_name, "score": t.score, "photo": request.build_absolute_uri(t.photo.url)} for t in tops],
        "feed": [{"school": f.school.name, "title": f.title, "media": request.build_absolute_uri(f.media_file.url), "likes": f.likes_count, "verified": True} for f in posts],
    })

# --- 🛰️ THE IMPERIAL NATIONAL MARKS ENGINE (REAL-TIME SYNC) ---
@api_view(['POST'])
def staff_marks_engine(request):
    """
    Saves and updates academic scores in real-time.
    Handles: AOI 1-4, Mid Term, EOT, and Project Work.
    """
    try:
        # 1. Capture data from the Instructor's App
        student_id = request.data.get('student_id')
        subject_id = request.data.get('subject_id')
        field = request.data.get('field') # e.g., 'aoi_1', 'mid_term', 'eot_score'
        score = float(request.data.get('score', 0))

        # 2. Locate the Citizen and the Subject
        student = Student.objects.get(account_number=student_id)
        subject = Subject.objects.get(id=subject_id)

        # 3. Use 'get_or_create' so the Brain builds a new record 
        # if this is the first test of the term
        result, created = AcademicResult.objects.get_or_create(
            student=student, 
            subject=subject
        )

        # 4. THE SOVEREIGN SETATTR: Dynamically updates the specific test column
        # Mapping the App field name to the Database column name
        db_field = field
        if field == "mid": db_field = "mid_term"
        if field == "eot": db_field = "eot_score"
        if field == "proj": db_field = "project_work"

        setattr(result, db_field, score)
        result.save()

        # Royal Log for the Terminal
        print(f"--- 🏛️ HUB UPDATE: {student.full_name} | {subject.name} | {db_field}: {score} ---")

        return Response({
            "status": "Verified", 
            "msg": f"Registry updated for {student.full_name}."
        })

    except Exception as e:
        return Response({"msg": f"Registry Error: {str(e)}"}, status=400)

# --- 6. REAL-TIME CATEGORIZED SETTLEMENT ---
@api_view(['POST'])
def pay_fees(request):
    try:
        sid, amt, cat = request.data.get('student_id'), float(request.data.get('amount', 0)), request.data.get('category', 'Tuition')
        s = Student.objects.get(account_number=sid); sch = s.school
        
        # POCKET LOGIC
        if cat.lower() == "tuition":
            f = s.fees; f.total_fees_paid += int(amt); f.save()
        
        tax = calculate_unsc_tax(amt)
        sch.total_revenue_collected += int(amt); sch.total_commission_earned += int(tax); sch.save()
        txn_id = f"UNS-TXN-{uuid.uuid4().hex[:10].upper()}"
        Transaction.objects.create(transaction_id=txn_id, school=sch, student=s, amount_paid=amt, system_tax=tax, category=cat)
        return Response({"status": "Verified", "txn": txn_id})
    except: return Response({"msg": "Gateway Error"}, status=400)

# --- 7. STAFF PORTAL VIEWSET ---
class StaffViewSet(viewsets.ViewSet):
    def list(self, request):
        staff = Staff.objects.all()
        return Response([{"name": s.full_name, "id": s.staff_id, "designation": s.designation} for s in staff])

@api_view(['GET'])
def UNSCCDC_Analytics(request):
    return Response({"status": "Online"})
# --- 🏛️ THE IMPERIAL NATIONAL MARKS ENGINE (PASTE AT BOTTOM) ---
@api_view(['POST'])
def staff_marks_engine(request):
    """Saves and updates academic scores in real-time."""
    try:
        student_id = request.data.get('student_id')
        subject_id = request.data.get('subject_id')
        field = request.data.get('field') # aoi_1, mid_term, eot_score
        score = float(request.data.get('score', 0))

        student = Student.objects.get(account_number=student_id)
        subject = Subject.objects.get(id=subject_id)

        # Build or Update the Registry Record
        result, created = AcademicResult.objects.get_or_create(student=student, subject=subject)
        
        # Mapping App field names to Brain column names
        db_map = {"mid": "mid_term", "eot": "eot_score", "proj": "project_work"}
        final_field = db_map.get(field, field)

        setattr(result, final_field, score)
        result.save()

        return Response({"status": "Verified", "msg": "Sync Successful"})
    except Exception as e:
        return Response({"msg": f"Registry Error: {str(e)}"}, status=400)
    
    from django.http import StreamingHttpResponse
import json

# --- 🛡️ SURGERY: IMPERIAL PRIVACY LOCK ---
def sync_schoolpay_transaction(school, tx_data):
    receipt = tx_data.get("schoolpayReceiptNumber")
    prn = tx_data.get("studentPaymentCode")
    amount = float(tx_data.get("amount", 0))

    if SchoolPayLedger.objects.filter(receipt_number=receipt).exists():
        return False, "Duplicate Blocked"

    try:
        # 💎 CRITICAL LOCK: We ONLY find the student IF they belong to THIS school
        student = Student.objects.get(payment_code=prn, school=school)
        
        # --- 🛰️ SURGERY: UPDATING THE CREATE LOGIC ---

        # Find the .create line and update it to look like this:
        SchoolPayLedger.objects.create(
            receipt_number=receipt, 
            school=school, 
            student=student, 
            amount=amount,
            raw_data=tx_data # 💎 THIS SAVES THE MTN/AIRTEL INFO FOR THE CHART
        )
        # Balance update remains private to this student
        f = student.fees
        f.total_fees_paid += int(amount)
        f.save()
        
        return True, f"Verified for {student.full_name}"
    except Student.DoesNotExist:
        # If the PRN exists but in a DIFFERENT school, this school will never see it!
        return False, "Security: PRN not found in your registry"

# # --- 🛡️ SURGERY: ENSURE NAME MATCHES (api/views.py) ---
def bursar_notification_stream(request, school_id):
    """Bursar dashboard connects here to see live payments"""
    def event_stream():
        # Keep track of the last seen transaction
        last_id = SchoolPayLedger.objects.filter(school_id=school_id).last().id if SchoolPayLedger.objects.filter(school_id=school_id).exists() else 0
        while True:
            new_txs = SchoolPayLedger.objects.filter(school_id=school_id, id__gt=last_id)
            for tx in new_txs:
                yield f"data: {json.dumps({'name': tx.student.full_name, 'amt': tx.amount})}\n\n"
                last_id = tx.id
            time.sleep(5) # Efficient polling
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse

def generate_imperial_pdf(request, student_id):
    """The Goliath Python Engine to generate the A4 Report Card"""
    student = Student.objects.get(account_number=student_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Report_{student.full_name}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 1. 🇺🇬 THE NATIONAL FLAG BORDERS
    p.setStrokeColor(colors.black); p.rect(10, 10, width-20, height-20, stroke=1, fill=0)
    p.setStrokeColor(colors.yellow); p.rect(13, 13, width-26, height-26, stroke=1, fill=0)
    p.setStrokeColor(colors.red); p.rect(16, 16, width-32, height-32, stroke=1, fill=0)

    # 2. 🏛️ THE OFFICIAL HEADER
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height-60, "THE REPUBLIC OF UGANDA")
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width/2, height-80, "UGANDA NATIONAL EXAMINATIONS BOARD (UNEB)")
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor("#003366"))
    p.drawCentredString(width/2, height-105, student.school.name.upper())
    
    # 3. 👤 STUDENT REGISTRY
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, height-150, f"STUDENT: {student.full_name.upper()}")
    p.drawString(50, height-165, f"ID: {student.account_number}")
    p.drawString(400, height-150, f"CLASS: {student.current_class}")
    p.drawString(400, height-165, f"PAY CODE: {student.payment_code}")

    # 4. 📊 THE 12-COLUMN DATA MATRIX
    data = [['SUBJECT', 'AOI1', 'AOI2', 'MID', 'AOI3', 'AOI4', 'EOT', 'PROJ', 'AVG', 'GRD', 'TCH', 'REMARKS']]
    
    # Pulling real marks from Brain
    marks = student.marks.all()
    for m in marks:
        data.append([
            m.subject.name[:10], '√', '√', '√', '√', '√', f"{m.eot_score}%", '√', f"{m.eot_score}%", 'A', 'STF', 'Excellent'
        ])

    table = Table(data, colWidths=[65, 30, 30, 30, 30, 30, 35, 35, 35, 25, 35, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height-350)

    # 5. ✍️ FOOTER & GRADING KEY
    p.setFont("Helvetica-Bold", 8)
    p.drawString(50, 150, "GRADING: 80-100: A | 70-79: B | 60-69: C | 50-59: D | 0-49: E")
    p.drawCentredString(width/2, 100, "VERIFIED BY NATIONAL HUB")
    p.showPage()
    p.save()
    return response

# --- 📜 THE GOLIATH PDF GENERATION ENGINE (STANDALONE) ---
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# --- 📜 THE GOLIATH NATIONAL PRINTING ENGINE (BRAIN EDITION) ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse
import datetime

def generate_imperial_pdf(request, student_id):
    """
    Standalone Python Engine to draw the 1,000-Level National Certificate.
    Includes: 12 Columns, Watermarks, Flag Borders, and National Grading Keys.
    """
    try:
        # 1. FETCH DATA
        student = Student.objects.get(account_number=student_id)
        sch = student.school
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="National_Report_{student.full_name}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # 2. 🛡️ THE SOVEREIGN WATERMARK (DIAGONAL)
        p.saveState()
        p.setFont("Helvetica-Bold", 45)
        p.setStrokeColor(colors.lightgrey)
        p.setFillColor(colors.lightgrey, alpha=0.04)
        p.translate(width/2, height/2)
        p.rotate(45)
        p.drawCentredString(0, 0, "UNSCCDC NATIONAL HUB OFFICIAL")
        p.restoreState()

        # 3. 🇺🇬 THE NATIONAL FLAG BORDERS (BLACK, YELLOW, RED)
        p.setLineWidth(2)
        p.setStrokeColor(colors.black); p.rect(15, 15, width-30, height-30)
        p.setStrokeColor(colors.orange); p.rect(18, 18, width-36, height-36) # Yellow replacement
        p.setStrokeColor(colors.red); p.rect(21, 21, width-42, height-42)

        # 4. 🏛️ OFFICIAL NATIONAL HEADER
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(width/2, height-60, "THE REPUBLIC OF UGANDA")
        
        # Draw a small Seal Box in the middle
        p.setStrokeColor(colors.black); p.rect(width/2-25, height-115, 50, 50)
        p.setFont("Helvetica-Bold", 7)
        p.drawCentredString(width/2, height-90, "OFFICIAL")
        p.drawCentredString(width/2, height-100, "SEAL")

        p.setFont("Helvetica-Bold", 9)
        p.drawCentredString(width/2, height-130, "UGANDA NATIONAL EXAMINATIONS BOARD (UNEB)")
        p.setFont("Helvetica-Bold", 18)
        p.setFillColor(colors.HexColor("#003366"))
        p.drawCentredString(width/2, height-155, sch.name.upper())
        p.setFont("Helvetica-Oblique", 8)
        p.setFillColor(colors.black)
        p.drawCentredString(width/2, height-170, f'"{sch.school_motto}"')

        # 5. 👤 STUDENT REGISTRY MATRIX
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, height-210, f"STUDENT: {student.full_name.upper()}")
        p.drawString(50, height-225, f"NATIONAL ID: {student.account_number}")
        p.drawString(400, height-210, f"CLASS: {student.current_class}")
        p.drawString(400, height-225, f"PAY CODE: {student.payment_code or 'N/A'}")

        # 6. 📊 THE GOLIATH 12-COLUMN TABLE (CBC STANDARD)
        # Header Row
        matrix_data = [['SUBJECT', 'AOI1', 'AOI2', 'MID', 'AOI3', 'AOI4', 'EOT', 'PROJ', 'AVG', 'GRD', 'TCH', 'REMARKS']]
        
        marks = student.marks.all()
        for m in marks:
            # Automated Remark Logic
            score = m.eot_score
            remark = "Superior" if score >= 90 else ("Excellent" if score >= 75 else "Satisfactory")
            
            matrix_data.append([
                m.subject.name[:8].upper(), str(m.aoi_1), str(m.aoi_2), str(m.mid_term), 
                str(m.aoi_3), str(m.aoi_4), f"{score}%", str(m.project_work), 
                f"{score}%", "A", "STF", remark
            ])

        # Table Styling (London Standard)
        table = Table(matrix_data, colWidths=[65, 30, 30, 30, 30, 30, 35, 35, 35, 25, 35, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        table_height = len(matrix_data) * 15
        table.wrapOn(p, width, height)
        table.drawOn(p, 40, height-250 - table_height)

        # 7. 🤖 AUTOMATED ADMINISTRATIVE COMMENTS
        footer_y = height-280 - table_height
        p.setFont("Helvetica-Bold", 8)
        p.drawString(50, footer_y, "CLASS TEACHER: High discipline observed. Promoted to next academic year.")
        p.drawString(50, footer_y - 15, "HEAD TEACHER: Excellent performance across core competencies.")
        
        # 8. 📚 NATIONAL GRADING SCALES (EXPLAINED)
        p.setFont("Helvetica-Bold", 7)
        p.drawString(50, 140, "NATIONAL GRADING STANDARDS:")
        p.setFont("Helvetica", 6)
        p.drawString(50, 130, "SECONDARY CBC: 90-100: A+ (Exceptional) | 80-89: A | 70-79: B | 60-69: C | 50-59: D | 0-49: E")
        p.drawString(50, 120, "PRIMARY PLE: DIV 1 (4-12 Agg) | DIV 2 (13-23 Agg) | DIV 3 (24-28 Agg) | DIV 4 (29-34 Agg)")
        p.drawString(50, 110, "UNIVERSITY (NCHE): 4.40 - 5.00: First Class | 3.60 - 4.39: Second Upper | 2.00 - 2.79: Pass")

        # 9. ✍️ SIGNATURES & FINAL STAMP
        p.line(50, 70, 180, 70)
        p.drawCentredString(115, 60, "Head Teacher Signature")
        
        # THE RED STAMP
        p.setStrokeColor(colors.red)
        p.circle(width/2, 75, 30, stroke=1, fill=0)
        p.setFillColor(colors.red)
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(width/2, 85, "UNSCCDC")
        p.drawCentredString(width/2, 75, "VERIFIED")
        p.drawCentredString(width/2, 65, "2026")
        
        p.setFillColor(colors.black)
        p.line(400, 70, 530, 70)
        p.drawCentredString(465, 60, "National Registrar Seal")

        p.setFont("Helvetica", 5)
        p.drawCentredString(width/2, 35, f"Verification ID: {student.account_number}-{datetime.date.today().year}. Authenticated Hub Record.")

        p.showPage()
        p.save()
        return response

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"Hub Printing Error: {str(e)}", status=400)
    
    # --- 🧾 THE IMPERIAL PAYSLIP ENGINE ---
def generate_payslip_pdf(request, payroll_id):
    p = StaffPayroll.objects.get(id=payroll_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Payslip_{p.staff.full_name}_{p.month}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    w, h = A4

    # 🏛️ HEADER
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, h-50, "OFFICIAL STAFF PAYMENT SLIP")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h-65, f"{p.staff.school.name.upper()}")
    
    # 👤 STAFF INFO
    c.line(50, h-80, w-50, h-80)
    c.drawString(50, h-100, f"STAFF NAME: {p.staff.full_name}")
    c.drawString(50, h-115, f"DESIGNATION: {p.staff.designation}")
    c.drawString(400, h-100, f"MONTH: {p.month} {p.year}")
    c.drawString(400, h-115, f"TIN: {p.staff.tin_number}")

    # 📊 EARNINGS & DEDUCTIONS TABLE
    data = [
        ['DESCRIPTION', 'EARNINGS', 'DEDUCTIONS'],
        ['Basic Gross Salary', f"{p.gross_salary:,.0f}", ''],
        ['NSSF (5%)', '', f"{p.nssf_deduction:,.0f}"],
        ['PAYE Tax (URA)', '', f"{p.paye_tax:,.0f}"],
        ['Other Deductions', '', f"{p.other_deductions:,.0f}"],
        ['TOTAL NET PAY', '', f"UGX {p.net_pay:,.0f}"]
    ]
    
    table = Table(data, colWidths=[200, 150, 150])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D4AF37")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    table.wrapOn(c, w, h)
    table.drawOn(c, 50, h-250)

    c.showPage()
    c.save()
    return response

# --- 📂 THE IMPERIAL STAFF DOSSIER ENGINE ---
def generate_staff_dossier_pdf(request, staff_id):
    """Generates a high-security PDF of all staff HR information"""
    staff = Staff.objects.get(staff_id=staff_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Dossier_{staff.full_name}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    w, h = A4

    # 🏛️ NATIONAL HEADER & BORDERS
    p.setStrokeColor(colors.black); p.rect(20, 20, w-40, h-40)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(w/2, h-60, "NATIONAL STAFF REGISTRY - DOSSIER")
    p.setFont("Helvetica", 10)
    p.drawCentredString(w/2, h-75, f"Station: {staff.school.name.upper()}")

    # 👤 PERSONAL IDENTITY
    p.setFont("Helvetica-Bold", 11); p.drawString(50, h-120, "1. PERSONAL BIOMETRICS")
    p.setFont("Helvetica", 10)
    p.drawString(60, h-140, f"Full Name: {staff.full_name}")
    p.drawString(60, h-155, f"Staff ID: {staff.staff_id}")
    p.drawString(60, h-170, f"Designation: {staff.designation}")
    
    # 🏦 STATUTORY & COMPLIANCE
    p.setFont("Helvetica-Bold", 11); p.drawString(50, h-210, "2. GOVERNMENT COMPLIANCE (URA/NSSF)")
    p.setFont("Helvetica", 10)
    p.drawString(60, h-230, f"URA TIN: {staff.tin_number}")
    p.drawString(60, h-245, f"NSSF No: {staff.nssf_number}")
    
    # 📞 CONTACT & NEXT OF KIN
    p.setFont("Helvetica-Bold", 11); p.drawString(50, h-280, "3. EMERGENCY CONTACT REGISTRY")
    p.setFont("Helvetica", 10)
    p.drawString(60, h-300, f"Primary Phone: {staff.phone}")
    p.drawString(60, h-315, f"Next of Kin: {staff.next_of_kin}")
    p.drawString(60, h-330, f"Kin Phone: {staff.next_of_kin_phone}")

    # ✍️ OFFICIAL SEAL
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(w/2, 100, "CONFIDENTIAL DOCUMENT - PROPERTY OF NATIONAL HUB")
    p.showPage(); p.save()
    return response

# --- 🧾 THE IMPERIAL NATIONAL PAYSLIP ENGINE ---
from reportlab.platypus import Table, TableStyle

def generate_payslip_pdf(request, payroll_id):
    """Draws a high-end, 12-row Audit-Ready Payslip"""
    try:
        p = StaffPayroll.objects.get(id=payroll_id)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Payslip_{p.staff.full_name}_{p.month}.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        w, h = A4

        # 1. 🛡️ OFFICIAL WATERMARK
        c.saveState()
        c.setFont("Helvetica-Bold", 50)
        c.setFillColor(colors.lightgrey, alpha=0.03)
        c.translate(w/2, h/2); c.rotate(45)
        c.drawCentredString(0, 0, "UNSCCDC OFFICIAL HUB")
        c.restoreState()

        # 2. 🏛️ HEADER & IDENTITY
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(w/2, h-50, "OFFICIAL STAFF REMUNERATION SLIP")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(w/2, h-65, p.staff.school.name.upper())
        c.line(50, h-80, w-50, h-80)

        # 👤 STAFF PROFILE DATA
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, h-100, f"NAME: {p.staff.full_name.upper()}")
        c.drawString(50, h-115, f"ID: {p.staff.staff_id}")
        c.drawString(50, h-130, f"DESIGNATION: {p.staff.designation}")
        
        c.drawString(380, h-100, f"MONTH: {p.month.upper()} {p.year}")
        c.drawString(380, h-115, f"URA TIN: {p.staff.tin_number or 'N/A'}")
        c.drawString(380, h-130, f"NSSF No: {p.staff.nssf_number or 'N/A'}")

        # 3. 📊 THE FINANCIAL AUDIT MATRIX
        data = [
            ['DESCRIPTION', 'EARNINGS (UGX)', 'DEDUCTIONS (UGX)'],
            ['Basic Gross Salary', f"{p.gross_salary:,.0f}", ''],
            ['NSSF Contribution (5%)', '', f"{p.nssf_deduction:,.0f}"],
            ['PAYE Income Tax (URA)', '', f"{p.paye_tax:,.0f}"],
            ['Other Deductions', '', f"{p.other_deductions:,.0f}"],
            ['', '', ''], # Spacer
            ['TOTAL NET PAYOUT', '', f"UGX {p.net_pay:,.0f}"]
        ]

        table = Table(data, colWidths=[200, 150, 150])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D4AF37")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        table.wrapOn(c, w, h)
        table.drawOn(c, 50, h-300)

        # ✍️ 4. AUTHORIZATION
        c.setFont("Helvetica-Bold", 8)
        c.drawString(50, 150, "Bursar's Signature: _____________________")
        c.drawRightString(w-50, 150, "Official Hub Seal: 🔒")
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(w/2, 50, "This is an electronically generated document. Valid without physical signature.")

        c.showPage(); c.save()
        return response
    except Exception as e:
        return HttpResponse(f"Dossier Error: {str(e)}", status=400)
    # --- 👑 THE IMPERIAL KING-MAKER DOOR ---
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def birth_the_king(request):
    User = get_user_model()
    # This logic either creates the user or updates the existing one
    user, created = User.objects.get_or_create(username="admin")
    user.set_password("Imperial2026!") # Your secure password
    user.email = "admin@unsccdc.com"
    user.is_staff = True        # 💎 CRITICAL: Allows login to /admin
    user.is_superuser = True    # 💎 CRITICAL: Gives full power
    user.save()
    
    status = "Born" if created else "Restored"
    return HttpResponse(f"<h1>The King is {status}! 👑</h1><p>Login at <b>/admin</b> using:<br>User: <b>admin</b><br>Pass: <b>Imperial2026!</b></p>")

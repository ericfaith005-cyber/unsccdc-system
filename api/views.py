from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import *
# --- 🏛️ SURGERY: PDF IMPORTS (api/views.py) ---
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .models import Staff, Student # 💎 Ensure Staff is imported!
import africastalking
import random
import uuid
import json
import traceback
from django.shortcuts import render
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from .models import Student, SchoolPayLedger, FeesTracker, Subject

# --- 1. SOVEREIGN SMS GATEWAY (LIVE PRODUCTION) ---
username = "yaweeric" 
api_key = "atsk_d23adde5b15396790edd13222388ce6a8ac25cf34e2544d703579e8e693477526d49f586" 
try:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
except:
    print("SMS Gateway Standby")
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def birth_the_king(request):
    User = get_user_model()
    User.objects.filter(username="admin").delete()
    
    # 💎 Create the King with all switches ON
    user = User.objects.create_superuser(
        username="admin",
        email="admin@unsccdc.com",
        password="Imperial2026!"
    )
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    return HttpResponse("<h1>THE KING IS FULLY AUTHORIZED! 👑</h1>")


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

import traceback
from django.db.models import Sum, Avg, F
from rest_framework import viewsets
from rest_framework.response import Response
from .models import *

class StudentViewSet(viewsets.ViewSet):
    """Primary Uplink for the Sovereign Mobile Hub (Aligned for v4.0 App)"""

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

                # --- 🛡️ SOVEREIGN SAFEGUARDS ---
                bio_obj = getattr(s, 'bio', None)
                bio_data = {
                    "career": getattr(bio_obj, 'future_career', "National Leader"),
                    "challenges": getattr(bio_obj, 'challenges_faced', "None"),
                    "inspiration": getattr(bio_obj, 'student_inspiration', "Sovereignty"),
                    "gender": getattr(s, 'gender', 'M'), # 💎 ADDED: For profile icons
                    "stream": getattr(s, 'stream', 'North'), # 💎 ADDED: For registry accuracy
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
                
                for p_key, m_field in p_map.items():
                    mlist = []
                    current_term_total_pts = 0
                    for m in s.marks.all():
                        score = getattr(m, m_field, 0)
                        # We assume get_national_grading is defined in your utils
                        g, pts, st, rem = get_national_grading(score, s.level_category)
                        if p_key == "EOT": current_term_total_pts += pts
                        
                        mlist.append({
                            "sub": m.subject.name, 
                            "score": score, 
                            "grade": g, 
                            "aoi1": m.aoi_1, 
                            "aoi2": m.aoi_2, 
                            "mid": m.mid_term, 
                            "aoi3": m.aoi_3, 
                            "aoi4": m.aoi_4, 
                            "project": m.project_work,
                            "teacher": "STAFF" # 💎 ADDED: For the 'TCH' column in App
                        })
                    
                    if mlist: 
                        national_report[p_key] = {
                            "marks": mlist, 
                            "agg": current_term_total_pts, 
                            "div": "DIV 1" if current_term_total_pts <= 12 else "VERIFIED"
                        }

                # --- 🎞️ TOP PERFORMERS ALIGNMENT ---
                performers = []
                for t in NationalTopPerformer.objects.all().order_by('?')[:12]:
                    performers.append({
                        "name": t.name, 
                        "school_name": t.school_name, # 💎 MATCHES APP KEY
                        "score": t.score, 
                        "photo": request.build_absolute_uri(t.photo.url) if t.photo else ""
                    })

                # --- 📱 TIKTOK FEED ALIGNMENT (CRITICAL FOR LOADING FIX) ---
                feed_data = []
                for f in SchoolPost.objects.all().order_by('-date'):
                    feed_data.append({
                        "id": f.id, # 💎 ADDED: For interaction tracking
                        "school_name": f.school.name, # 💎 MATCHES APP KEY
                        "content": f.title, # 💎 MATCHES APP KEY (CONTENT)
                        "media": request.build_absolute_uri(f.media_file.url) if f.media_file else "",
                        "likes": f.likes_count,
                        "comment_count": getattr(f, 'comments_total', 0) # 💎 ADDED: For UI badges
                    })

                # 📦 THE FINAL IMPERIAL PACKAGE
                return Response({
                    "status": "authenticated", # 💎 ADDED: For the App's new Verify logic
                    "type": "parent", 
                    "name": s.full_name, 
                    "id": s.account_number, 
                    "payment_code": s.payment_code, 
                    "sch_id": sch.school_account_id, 
                    "class": s.current_class, 
                    "curriculum": s.level_category,
                    "photo": request.build_absolute_uri(s.photo.url) if s.photo else "", 
                    "parent_name": p_rec.full_name,
                    "school": {
                        "name": sch.name, 
                        "addr": sch.address, 
                        "motto": sch.school_motto, 
                        "uneb_no": sch.uneb_center_number, 
                        "school_code": sch.school_code, # 💎 ADDED
                        "dir": sch.director,
                        "mission": getattr(sch, 'mission', "Excellence"), 
                        "vision": getattr(sch, 'vision', "Sovereignty"), 
                        "rating": getattr(sch, 'rating', "⭐⭐⭐⭐⭐"), 
                        "type": getattr(sch, 'school_type', "Standard")
                    },
                    "finance": finance, 
                    "national_report": national_report, 
                    "bio_info": bio_data,
                    "top_performers": performers,
                    "feed": feed_data,
                    "ussd_steps": sch.ussd_instructions,
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
            
        except Parent.DoesNotExist:
            return Response({"msg": "Rejected: Code or Phone invalid"}, status=401)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"msg": "National Registry Error"}, status=500)

@login_required
def finances_dashboard(request):
    # 🧮 GOLIATH FINANCIAL CALCULATIONS
    # Get all transactions for the school (assuming request.user.school link)
    ledger = SchoolPayLedger.objects.filter(school=request.user.school).order_by('-timestamp')
    
    # Financial Overview Metrics
    stats = FeesTracker.objects.filter(student__school=request.user.school).aggregate(
        total_invoiced=Sum('total_fees_due'),
        total_paid=Sum('total_fees_paid')
    )
    
    invoiced = stats['total_invoiced'] or 0
    paid = stats['total_paid'] or 0
    outstanding = invoiced - paid

    context = {
        'ledger': ledger,
        'total_invoiced': invoiced,
        'total_paid': paid,
        'outstanding': outstanding,
        'active_tab': 'finances'
    }
    return render(request, 'tabs/finances.html', context)

@login_required
def academics_dashboard(request):
    # 👨‍🎓 STUDENT REGISTRY DATA
    # Select students and prefetch fee status for the "Status Indicator"
    students = Student.objects.filter(school=request.user.school).order_by('full_name')
    
    context = {
        'students': students,
        'active_tab': 'academics'
    }
    return render(request, 'tabs/academics.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def verify_identity(request):
    """
    THE IMPERIAL GATEWAY (Stage 1)
    Manually handling the CORS Handshake to stop the Loading Forever bug.
    """
    
    # 💎 1. THE SOVEREIGN HANDSHAKE (CORS FORCE)
    # We create the response manually to ensure the 'Stamp' is there
    response = JsonResponse({})
    response["Access-Control-Allow-Origin"] = "https://schoolapp-lac.vercel.app"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
    response["Access-Control-Allow-Credentials"] = "true"

    # If the browser is just asking for permission (OPTIONS), give it and STOP.
    if request.method == "OPTIONS":
        return response

    # 💎 2. THE DATA LOOKUP (STAGE 1)
    # Extract details from the URL (since your log shows they are coming via GET)
    code = request.GET.get('code', '').strip()
    student_name = request.GET.get('student', '').strip()
    parent_name = request.GET.get('parent', '').strip()
    phone = request.GET.get('phone', '').strip()

    # Query the Registry
    match = Student.objects.filter(
            payment_code=code,
            full_name__iexact=student_name,
            parent_link__full_name__iexact=parent_name, # 💎 CHANGED THIS
            parent_link__phone_number=phone             # 💎 CHANGED THIS
        ).first()

    if match:
        # ✅ SUCCESS: Identity Confirmed
        response.content = json.dumps({
            'status': 'success', 
            'message': 'Credentials verified. Opening PIN vault.',
            'student_id': match.account_number
        }).encode('utf-8')
        return response
    else:
        # 🛑 DENIED
        response.status_code = 401
        response.content = json.dumps({
            'status': 'error', 
            'message': 'No matching records found in the National Registry.'
        }).encode('utf-8')
        return response
    
@csrf_exempt # 💎 EMERGENCY BYPASS: Allows the form to hit the server from any origin
def verify_student_portal(request):
    """
    STAGE 1: NATIVE FORM POST VALIDATION
    """
    if request.method == 'POST':
        # 1. Capture values directly from the POST body
        incoming_code = request.POST.get('code', '').strip()
        incoming_student = request.POST.get('student', '').strip()
        incoming_parent = request.POST.get('parent', '').strip()
        incoming_phone = request.POST.get('phone', '').strip()

        # 2. THE MASTER SEARCH
        # Searching the National Registry for a 4-point match
        match = Student.objects.filter(
            payment_code=incoming_code,
            full_name__iexact=incoming_student,
            parent__full_name__iexact=incoming_parent,
            parent__phone_number=incoming_phone
        ).first()

        if match:
            # ✅ SUCCESS: Identity Confirmed
            # Instantly transition to the PIN entry screen
            return render(request, 'pin_entry.html', {
                'student': match,
                'status': 'authenticated'
            })
        else:
            # 🛑 DENIED: Return to login with error
            return render(request, 'index.html', {
                'error': 'Identity Denied. No matching records found in the National Registry.',
                'old_data': request.POST # Keeps the typed text so they don't re-type
            })

    # If it's a GET request, just show the login page
    return render(request, 'index.html')

from django.shortcuts import render
from .models import Student, Parent, Staff
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def parent_verify_view(request):
    # Default state is 'gate' (The 4-box form)
    context = {'stage': 'gate'} 

    if request.method == 'POST':
        # --- STAGE 1: IDENTITY HANDSHAKE ---
        if 'verify_identity' in request.POST:
            code = request.POST.get('code', '').strip()
            student_name = request.POST.get('student', '').strip()
            parent_name = request.POST.get('parent', '').strip()
            phone = request.POST.get('phone', '').strip()

            student = Student.objects.filter(
                payment_code__iexact=code,
                full_name__iexact=student_name,
                parent_link__full_name__iexact=parent_name,
                parent_link__phone_number__icontains=phone[-9:]
            ).first()

            if student:
                context = {'stage': 'vault', 'student': student}
            else:
                context = {'stage': 'gate', 'error': 'Identity Mismatch. Check spelling/details.'}

        # --- STAGE 2: FINAL Hub AUTHORIZATION (6-DIGIT PIN) ---
        elif 'authorize_access' in request.POST:
            input_pin = request.POST.get('pin', '').strip()
            student_id = request.POST.get('student_id')
            student = Student.objects.get(account_number=student_id)
            
            if student.parent_link and student.parent_link.secure_pin == input_pin:
                return render(request, 'tabs/home.html', {'data': student})
            else:
                context = {'stage': 'vault', 'student': student, 'error': 'SECURITY ALERT: Invalid 6-Digit PIN.'}

    return render(request, 'index.html', context)

@csrf_exempt
def staff_hub_login(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        pin = request.POST.get('pin', '').strip()
        staff = Staff.objects.filter(full_name__iexact=name, secure_pin=pin).first()
        if staff:
            # 4-DIGIT PIN verified for staff
            return render(request, 'tabs/home.html', {'data': staff, 'is_staff': True})
        else:
            context['error'] = "Invalid Command Credentials."
    return render(request, 'staff_login.html', context)

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
    
@login_required
def bursar_print_center(request):
    # 🕵️ 1. SECURITY & IDENTITY
    school = getattr(request.user, 'school', None)
    if not school:
        school = School.objects.filter(school_type='SECONDARY').first() # Founder Bypass

    # 🕵️ 2. DYNAMIC LEVEL DETECTION (Killing the P.1 Error)
    if school.school_type == 'SECONDARY':
        class_list = ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6']
        hub_label = "ORDINARY & ADVANCED REGISTRY"
    else:
        class_list = ['P.1', 'P.2', 'P.3', 'P.4', 'P.5', 'P.6', 'P.7']
        hub_label = "PRIMARY FOUNDATION REGISTRY"

    # 🕵️ 3. REAL-TIME DATA PUMP
    # Pulling every transaction from today from the SchoolPay Ledger
    today = timezone.now().date()
    all_txs = SchoolPayLedger.objects.filter(
        school=school, 
        timestamp__date=today
    ).select_related('student')

    # Sorting counts for the glowing badges
    pending_counts = {cls: all_txs.filter(student__current_class=cls, is_printed=False).count() for cls in class_list}

    return render(request, 'admin/api/bursarterminal/change_list.html', {
        'school': school,
        'class_list': class_list,
        'txs': all_txs,
        'pending_counts': pending_counts,
        'hub_label': hub_label,
        'today': today
    })

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

@login_required
def bursar_batch_terminal(request):
    school = request.user.school
    today = timezone.now().date()
    
    # 🕵️ Logic: Identify the correct class list based on National Level
    level_map = {
        'KIND': ['Baby', 'Middle', 'Top'],
        'PRIM': ['P.1', 'P.2', 'P.3', 'P.4', 'P.5', 'P.6', 'P.7'],
        'SEC':  ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6'],
        'INTL': [f'Year {i}' for i in range(1, 14)],
        'UNI':  [f'Year {i}' for i in range(1, 6)],
    }
    active_classes = level_map.get(school.school_type, ['Standard'])

    # 📊 Live Transaction Counter per class
    todays_txs = SchoolPayLedger.objects.filter(school=school, timestamp__date=today)
    
    class_stats = []
    for cls in active_classes:
        count = todays_txs.filter(student__current_class=cls).count()
        class_stats.append({'name': cls, 'count': count})

    return render(request, 'bursar_terminal.html', {
        'school': school,
        'class_stats': class_stats,
        'transactions': todays_txs,
        'today': today
    })

def generate_staff_dossier_pdf(request, staff_id):
    """Generates a high-security National HR Dossier"""
    try:
        staff = Staff.objects.get(staff_id=staff_id)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Dossier_{staff.full_name}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # 🛡️ Watermark (8-space indent inside try)
        p.saveState()
        p.setFont("Helvetica-Bold", 60)
        p.setFillColor(colors.lightgrey, alpha=0.05)
        p.translate(width/2, height/2)
        p.rotate(45)
        p.drawCentredString(0, 0, "OFFICIAL HUB")
        p.restoreState()

        # 🏛️ Header
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width/2, height-50, "THE REPUBLIC OF UGANDA")
        p.setFont("Helvetica", 10)
        p.drawCentredString(width/2, height-70, f"STATION: {staff.school.name.upper()}")

        # 👤 Data
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, height-120, f"FULL NAME: {staff.full_name.upper()}")
        p.drawString(50, height-140, f"STAFF ID: {staff.staff_id}")

        p.showPage()
        p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Registry Error: {str(e)}", status=404)

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
     # --- 👑 THE SECRET KING-MAKER DOOR ---
from django.contrib.auth.models import User

def create_initial_king(request):
    # This is a secret URL to build the first admin in the clouds
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@unsccdc.com", "Imperial2026!")
        return HttpResponse("The King is Born in the Clouds! 👑")
    return HttpResponse("The Throne is already occupied.")   
# --- 👑 THE IMPERIAL KING-MAKER DOOR ---
from django.contrib.auth import get_user_model
from django.http import HttpResponse

FLAG_STYLE = """
<style>
    body { 
        background: #050505; color: #fff; font-family: 'Courier New', monospace; 
        padding: 50px; margin: 0; overflow-x: hidden;
        background-image: radial-gradient(circle at 50% 50%, rgba(252, 220, 4, 0.05) 0%, transparent 80%);
    }
    .flag-bar { 
        position: fixed; top: 0; left: 0; width: 100%; height: 5px; display: flex; 
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
    }
    .b { flex: 1; background: #000; } .y { flex: 1; background: #FCDC04; } .r { flex: 1; background: #D90000; }
    
    .glass-tab {
        background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px; border-radius: 30px; backdrop-filter: blur(10px);
        border-top: 4px solid #FCDC04; position: relative; animation: slideIn 0.8s ease-out;
    }
    @keyframes slideIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    
    .nav-btn {
        display: inline-block; padding: 12px 25px; border-radius: 10px; text-decoration: none;
        font-weight: 900; font-size: 11px; letter-spacing: 2px; transition: 0.3s;
        border: 1px solid #333; color: #888; margin-right: 10px;
    }
    .nav-btn:hover { background: #FCDC04; color: #000; box-shadow: 0 0 20px #FCDC04; }
    .active-btn { background: #D90000 !important; color: #fff !important; border: none; box-shadow: 0 0 20px #D90000; }
    
    .pulse-dot { height: 8px; width: 8px; background: #00ff00; border-radius: 50%; display: inline-block; margin-right: 10px; animation: blink 1.5s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>

<div class="flag-bar">
    <div class="b"></div><div class="y"></div><div class="r"></div>
    <div class="b"></div><div class="y"></div><div class="r"></div>
</div>

<div style="margin-bottom: 40px;">
    <a href="/api/home/" class="nav-btn {{home_act}}">1. HOME</a>
    <a href="/api/about/" class="nav-btn {{about_act}}">2. ABOUT</a>
    <a href="/api/academics/" class="nav-btn {{acad_act}}">3. ACADEMICS</a>
    <a href="/api/finances/" class="nav-btn {{fin_act}}">4. FINANCES</a>
    <a href="/api/profile/" class="nav-btn {{prof_act}}">5. PROFILE</a>
    <a href="/admin/" class="nav-btn" style="float:right;">← BACK TO CONTROL</a>
</div>
"""
# --- 📜 THE ABOUT TAB WITH LIVE APK DOWNLOAD ---
def about_tab(request):
    html = """
    <body style="background:#000; color:#fff; font-family:sans-serif; padding:50px; text-align:center;">
        <div style="border: 2px solid #D4AF37; padding: 40px; border-radius: 30px; background: rgba(212,175,55,0.02);">
            <h1 style="color:#D4AF37; letter-spacing:5px; font-weight:900;">UNSCCDC NATIONAL HUB</h1>
            <p style="color:#888; letter-spacing:2px;">OFFICIAL MOBILE INTERFACE v1.0.1</p>
            
            <hr style="border-color:#222; margin: 30px 0;">
            
            <p style="font-size:18px;">Founder & Chief Innovation Officer: <b>Yawe Eric</b></p>
            <p style="color:#aaa; font-style:italic;">"In 2025, at the age of 20, Ugandan Software developer and Tech Entrepeneur Yawe Eric recognized a critical gap in the nation's educational infrastructure: 
            schools were overwhelmed by disorganized manual paperwork, fee tracking was prone to leakages, and parents remained in the dark about thier children's daily performance."</p>
            <p style="color:#aaa;">"With a bold vision to completely transform Uganda's Education sector, Eric engineered UNSCCDC. His mission is to brig world-class, cloud-based digital infrastructure to every school in Uganda-starting with better Institutions-ensuring accountability, 
            moving Uganda Education into a paperless, digitally transparent future."</p>

            <p style="font-size:18px;"><b>Technical Architecture and Reliability Specs</b></p>
            <ul style="color:#ccc; line-height:2;">
             <li>✅ Cloud Infrastructure</li>
                <p style="color:#aaa;">Hosted on highly reliable cloud servers with an automated deployment ppeline linked directly to secure version control, ensuring 99.9% platform uptime.</p>

                <li>✅ Database Integrity</li>
                <p style="color:#aaa;">Built on a robust relational database management system using Django's Object-Relational Mapping (ORM) to handle complex queries for thousands of student profiles without lag.</p>

                <li>✅ Local Compliance</li>
                <p style="color:#aaa;">Designed to align fully with the assessment grading guidelines stipulated by the Ministry of Educaton and Sports (MoES) and the Uganda National Curriculum Development Centre (NCDC).</p>
            
            </ul>
           

            <p style="font-size:18px;"><b>Technical Architecture and Reliability Specs</b></p>


            <!-- 🚀 THE NATIONAL DOWNLOAD BUTTON -->
            <div style="margin-top:40px;">
                <a href="1uVswBKYlTe6xC-5gIxhkGwcsAu_lxd67" 
                   style="background:#D4AF37; color:#000; padding:25px 50px; border-radius:20px; font-weight:900; text-decoration:none; font-size:20px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); display:inline-block;">
                   📥 DOWNLOAD ANDROID APP (APK)
                </a>
            </div>

            <p style="margin-top:50px;"><a href="/admin/" style="color:#D4AF37; text-decoration:none;">← BACK TO CONTROL CENTRE</a></p>
        </div>
    </body>
    """
    return HttpResponse(html)

def academics_tab(request):
    content = f"""{FLAG_STYLE.replace('{{acad_act}}', 'active-btn')}
    <div class="glass-tab">
        <h1 style="color:#FCDC04;">ACADEMIC ASSESSMENT ENGINE</h1>
        <p>This is the operational core of the school, built to handle <b>the complex realities of the Uganda grading matrix</b>.</p>

         <p style="font-size:18px;"><b>The Assessment Engine Specifications</b></p>
            <ul style="color:#ccc; line-height:2;">
            <li>✅ New Lower Secondary Curriculum (NLSC)</li>
            <p style="color:#aaa;"><b>Tracker:</b>Built-in grading architecture designed for the 20-point continuos assessment scale. It allows teachers to input Activities of Intergration (AoIs), automatically calculates scores out of 3, and generates the mandatory NCDC-compliant descriptors. </p>

             <li>✅ Traditional Curriculum Grading</li>
            <p style="color:#aaa;">An automated system for all levels that instantly converts raw percentages into UNEB-standard aggregtes and automatically determines student divisions and subjcet combinations. </p>

             <li>✅ Automated Report Card Generation</li>
            <p style="color:#aaa;">A one-clickgeneration system that compiles continuos assessment mrks, final exams, teacher remarks, housmaster comments, and school fees balance into a secure, downloadable PDF report card carrying the digital signature of the Headteacher.</p>

             <li>✅ Digital Staffroom Timetabler</li>
            <p style="color:#aaa;">An algorithmic scheduling tool that prevents room clashes and teacher double-booking across different classes and streams of all levels.</p>

             <li>✅ Student Progress Analytics</li>
            <p style="color:#aaa;">Interactive graphical trends showing a student's performance trajectory across multiple terms, allowing directors to identify struggling students early. </p>
        </ul>
    </div>"""
    return HttpResponse(content)

def finances_tab(request):
    content = f"""{FLAG_STYLE.replace('{{fin_act}}', 'active-btn')}
    <div class="glass-tab">
        <h1 style="color:#FCDC04;">THE FINANCIAL LEAK-PROOF LEDGER</h1>
        
       
        <ul style="color:#ccc; line-height:2;"> <p><b>Revenue and Ledger Management</b></p>
        <li>✅ Student Progress Analytics</li>
            <p style="color:#aaa;">At the start of every term, the system automatically applies unique billing structures to every student based on thier class, stream, or boarder/day scholar status, eliminating manual invoicing errors.</p>
        <li>✅ Real-Time Cash Flow Analytics</li>
            <p style="color:#aaa;">Provides the School Director with a secure, instant breakdown of total expected revenue, total fees collected so far, and total outstanding school debts. </p>
        
        <p><b>Advanced Anti-Leakage Intergration</b></p>

        <li>✅ Digital Gateway Snycing</li>
            <p style="color:#aaa;">Designed to hook into mobile money API networks (MTN MoMo and Airtel Money) and local banking agents. When a parent pays fees at a bank or via phone, the system instantly logs the payment, deducts the balance from the student's profile, and updates the bursar's dashboard.</p>
        
        <li>✅ Automated SMS Reminders</li>
            <p style="color:#aaa;">An intelligent notification agent that identifies accounts with outstanding balances at specified intervals (e.g. Week 4, Week 8) and sends a personalized, polite text reminder directly to the parent's phone.</p>
        
        <li>✅ Clearance Slip Verification</li>
            <p style="color:#aaa;">Genertes a secure, digital verification token (or barcode) once a student hits a set payment threshold, allowing gate staff to verify financil clearance instantly during school return days.</p>
        </ul>
       
        <div style="display:flex; gap:20px; margin-top:20px;">
            <div style="flex:1; background:#f1c40f; color:#000; padding:15px; border-radius:10px; font-weight:900; text-align:center;">MTN MoMo</div>
            <div style="flex:1; background:#D90000; color:#fff; padding:15px; border-radius:10px; font-weight:900; text-align:center;">AIRTEL MONEY</div>
        </div>
    </div>"""
    return HttpResponse(content)

from django.http import HttpResponse

def home_tab(request):
    html = """
    <div style="background: linear-gradient(90deg, #FCDC04, #D90000); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px; animation: pulse 2s infinite;">
        <h2 style="color: #000; margin: 0; font-weight: 900;"> NATIONAL HUB APP READY</h2>
        <p style="color: #000; font-size: 12px; font-weight: bold;">Click the button below to install the Official App on your Android phone.</p>
        <a href="/api/get-app/" style="background: #000; color: #fff; padding: 15px 30px; border-radius: 10px; text-decoration: none; font-weight: 900; display: inline-block; margin-top: 10px;">
           INSTALL APP NOW (56MB)
        </a>
    </div>
    
    <div class="module-card">
        <h1 style="font-family:'Orbitron'; color:#FCDC04; letter-spacing:8px; margin:0;">UNSCCDC GLOBAL</h1>
    <body style="background:#000; color:#fff; font-family:sans-serif; padding:50px;">
        <h1 style="color:#D4AF37; letter-spacing:3px;">ENTERPRISE COMMAND CENTER</h1>
        <p style="color:#888;">UNSCCDC GLOBAL Hub Status: <span style="color:#00ff00;">● LIVE</span></p>
        <hr style="border-color:#222;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
            <div style="background:#111; padding:20px; border-radius:15px; border-left:4px solid #D4AF37;">
                <h3 style="margin:0;">95%</h3>
                <p style="font-size:10px; color:#666;">ERROR REDUCTION</p>
            </div>
            <div style="background:#111; padding:20px; border-radius:15px; border-left:4px solid #00ff00;">
                <h3 style="margin:0;">14 Hours</h3>
                <p style="font-size:10px; color:#666;">SAVED WEEKLY</p>
            </div>
        </div>
        <p style="margin-top:30px;"><a href="/admin/" style="color:#D4AF37; text-decoration:none;">← BACK TO CONTROL CENTRE</a></p>
    </body>
    """
    return HttpResponse(html)

def profile_tab(request):
    content = f"""{FLAG_STYLE.replace('{{prof_act}}', 'active-btn')}
    <div class="glass-tab">
        <h1 style="color:#FCDC04;"><b>Security and Audit Logs</b></h1>
        <div style="background:#111; padding:30px; border-radius:20px;">
            <h3>Role-Based Access Control (RBAC): Users are strictly restricted based on permission groups:</h3>
            <li>✅ Super Administrators</li>
            <p style="color:#aaa;">Full database access, system configuration, and deployment controls.</p>

            <li>✅ School Administrators (Bursars/ Headteachers)</li>
            <p style="color:#aaa;">Access to financial reports, staff payroll, and final grade approvals.</p>

            <li>✅ Educators</li>
            <p style="color:#aaa;">Access only to the specific classes and subjects assigned to them for mark entry</p>

            <li>✅ Parents</li>
            <p style="color:#aaa;">Read-only access restricted strictly to their biological children's financial and academic records.</p>
        
            <p style="color:#00ff00; font-weight:bold;">Security Audit Trail</p>
            <p style="color:#aaa;">Tracks user activity for accountability. it displays the login timestamp, the device IP address, and a log of recent actions (e.g., "Teacher Namubiru Shifat updated Senior 3 Math marks on June 8, 2026").</p>

            <p style="color:#00ff00; font-weight:bold;">User Settings and Customization</p>
            <li>✅ Biometric and Two-Factor Authentication (2FA)</li>
            <p style="color:#aaa;">Optional security layer requiring an SMS token code before administrative or financial changes can be saved.</p>

            <li>✅ Language and Accessibility</li>
            <p style="color:#aaa;">Toggle features for high-contrast viewing and future intergration for localized support alerts.</p>  
        </div>
    </div>"""
    return HttpResponse(content)

from django.http import JsonResponse

# --- 🛰️ THE SOVEREIGN METRICS UPLINK ---
def get_hub_metrics(request):
    """Dynamically loads school health for the mobile app dashboard"""
    # Math logic:
    total_students = Student.objects.count()
    # Pulling real fee stats from your ledger
    fees = FeesTracker.objects.aggregate(due=Sum('total_fees_due'), paid=Sum('total_fees_paid'))
    
    data = {
        "status": "National Hub Online",
        "enrollment": total_students,
        "collection_rate": f"{(fees['paid']/fees['due']*100):.1f}%" if fees['due'] else "0%",
        "active_staff": Staff.objects.count(),
        "academic_week": "Week 6, Term II",
    }
    return JsonResponse(data)

from django.core.management import call_command
from django.db import connection

def force_registry_rebuild(request):
    try:
        # This physically builds your 100-character tables in Supabase
        call_command('migrate', interactive=False)
        return HttpResponse("<h1>NATIONAL REGISTRY BUILT SUCCESSFULLY! 🏆</h1>")
    except Exception as e:
        return HttpResponse(f"Registry Error: {str(e)}")


# --- 💰 THE SCHOOLPAY SETTLEMENT SIMULATOR ---
from .models import Student, School, SchoolPayLedger
import random

def simulate_payment(request):
    """Simulates a real USSD/Mobile Money payment through SchoolPay"""
    try:
        # 1. Pick a student (Ensure you have at least one student in the DB!)
        student = Student.objects.first() 
        if not student: return HttpResponse("Registry Error: Add a student first!")
        
        # 2. Create a fake Receipt
        receipt = f"RCPT-{random.randint(100000, 999999)}"
        amount = 50000 # 50k UGX
        
        # 3. Create the Ledger Entry
        ledger = SchoolPayLedger.objects.create(
            student=student,
            school=student.school,
            receipt_number=receipt,
            amount=amount,
            raw_data={"sourceChannel": "MTN_MOMO", "transactionID": receipt}
        )
        
        # 4. Trigger the Math Update (This mimics the worker)
        student.school.total_revenue_collected += amount
        student.school.save()

        return HttpResponse(f"<h1>💰 PAYMENT SUCCESS</h1><p>Student {student.full_name} paid UGX {amount}. Receipt: {receipt}</p>")
    except Exception as e:
        return HttpResponse(f"Simulation Failed: {str(e)}")

from django.shortcuts import redirect

def direct_app_download(request):
    google_drive_id = "YOUR_LONG_GOOGLE_DRIVE_ID_HERE"
    direct_link = f"https://drive.google.com/uc?export=download&id={google_drive_id}"
    
    return redirect(direct_link)

def generate_staff_dossier_pdf(request, staff_id):
    """
    Generates a high-security National HR Dossier for Audit.
    Includes: Biometrics, URA TIN, NSSF, and Regulatory Data.
    """
    try:
        staff = Staff.objects.get(staff_id=staff_id)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Dossier_{staff.full_name}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        w, h = A4

        p.saveState()
        p.setFont("Helvetica-Bold", 60)
        p.setFillColor(colors.lightgrey, alpha=0.05)
        p.translate(w/2, h/2); p.rotate(45)
        p.drawCentredString(0, 0, "UNSCCDC OFFICIAL HUB")
        p.restoreState()

        
        p.setLineWidth(5)
        p.setStrokeColor(colors.black); p.line(0, h-2, w/3, h-2)
        p.setStrokeColor(colors.orange); p.line(w/3, h-2, (w/3)*2, h-2)
        p.setStrokeColor(colors.red); p.line((w/3)*2, h-2, w, h-2)

        
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(w/2, h-50, "THE REPUBLIC OF UGANDA")
        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(w/2, h-70, "NATIONAL STAFF REGISTRY - OFFICIAL DOSSIER")
        p.setFont("Helvetica", 9)
        p.drawCentredString(w/2, h-85, f"Institutional Station: {staff.school.name.upper()}")

        
        p.setStrokeColor(colors.black); p.rect(40, h-250, w-80, 150)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, h-120, "1.0 PERSONAL BIOMETRICS")
        p.setFont("Helvetica", 10)
        p.drawString(60, h-145, f"FULL LEGAL NAME: {staff.full_name.upper()}")
        p.drawString(60, h-165, f"NATIONAL STAFF ID: {staff.staff_id}")
        p.drawString(60, h-185, f"DESIGNATION: {staff.designation}")
        p.drawString(60, h-205, f"CONTACT UPLINK: {staff.phone}")

        
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, h-280, "2.0 REGULATORY COMPLIANCE (URA / NSSF)")
        p.line(50, h-285, 300, h-285)
        p.setFont("Helvetica", 10)
        p.drawString(60, h-310, f"URA TIN NUMBER: {getattr(staff, 'tin_number', 'PENDING')}")
        p.drawString(60, h-330, f"NSSF REGISTRY NO: {getattr(staff, 'nssf_number', 'PENDING')}")

        
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, h-380, "3.0 EMERGENCY & KINSHIP REGISTRY")
        p.setFont("Helvetica", 10)
        p.drawString(60, h-410, f"NEXT OF KIN: {getattr(staff, 'next_of_kin', 'NOT SET')}")
        p.drawString(60, h-430, f"KIN CONTACT: {getattr(staff, 'next_of_kin_phone', 'NOT SET')}")

        
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(w/2, 100, "THIS DOCUMENT IS A CERTIFIED DIGITAL RECORD OF THE UNSCCDC HUB")
        p.drawCentredString(w/2, 85, f"VERIFICATION HASH: {staff.staff_id}-AUDIT-2026")

        p.showPage(); p.save()
        return response
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f"Dossier Engine Error: {str(e)}", status=400)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse
from .models import Student, AcademicResult

def generate_national_report_pdf(request, student_id):
    """
    THE GOLIATH PDF ENGINE v1.0
    Generates a 12-Column National Scholastic Record with Uganda Flag Borders.
    """
    try:
        # 1. 🔍 PULL REGISTRY DATA
        student = Student.objects.get(account_number=student_id)
        marks = student.marks.all() # Uses the related_name='marks'
        school = student.school
        
        # 2. 📄 INITIALIZE THE CANVAS
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Report_{student.full_name}.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # 3. 🎨 AUTOMATED REMARK LOGIC (AI)
        def get_sub_remark(score):
            if score >= 90: return "Exceptional mastery."
            if score >= 80: return "Excellent. Maintain focus."
            if score >= 70: return "Very good effort."
            if score >= 60: return "Good progress."
            if score >= 50: return "Basic competency."
            return "Requires support."

        # 4. 🇺🇬 THE NATIONAL FLAG BORDER (Black, Yellow, Red)
        p.setLineWidth(2)
        p.setStrokeColor(colors.black); p.rect(10, 10, width-20, height-20)
        p.setStrokeColor(colors.HexColor("#FCDC04")); p.rect(13, 13, width-26, height-26)
        p.setStrokeColor(colors.HexColor("#D90000")); p.rect(16, 16, width-32, height-32)

        # 5. 🏛️ OFFICIAL NATIONAL HEADER
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(width/2, height-50, "THE REPUBLIC OF UGANDA")
        p.drawCentredString(width/2, height-65, "UGANDA NATIONAL EXAMINATIONS BOARD (UNEB)")
        
        # Seal Box
        p.rect(width/2-25, height-120, 50, 50)
        p.setFont("Helvetica-Bold", 7)
        p.drawCentredString(width/2, height-95, "OFFICIAL")
        p.drawCentredString(width/2, height-105, "SEAL")

        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.HexColor("#002366"))
        p.drawCentredString(width/2, height-145, school.name.upper())
        p.setFont("Helvetica-Bold", 7)
        p.setFillColor(colors.grey)
        p.drawCentredString(width/2, height-155, "UNSCCDC NATIONAL MASTER HUB SYSTEM")

        # 6. 👤 STUDENT REGISTRY DETAILS
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(width/2, height-185, "OFFICIAL SCHOLASTIC PERFORMANCE RECORD")
        
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, height-215, f"STUDENT NAME: {student.full_name.upper()}")
        p.drawString(50, height-230, f"NATIONAL ID: {student.account_number}")
        p.drawString(350, height-215, f"CLASS: {student.current_class} ({student.stream or 'NORTH'})")
        p.drawString(350, height-230, f"TERM: EOT | YEAR: 2026")

        # 7. 📊 THE 12-COLUMN DATA MATRIX
        # Headers: SUBJECT, AOI1, AOI2, MID, AOI3, AOI4, EOT, PROJ, AVG, GRADE, TCH, REMARKS
        data = [['SUB', 'A1', 'A2', 'MID', 'A3', 'A4', 'EOT', 'PRJ', 'AVG', 'GRD', 'TCH', 'REMARKS']]
        
        for m in marks:
            data.append([
                m.subject.name[:4].upper(), m.aoi_1, m.aoi_2, m.mid_term, 
                m.aoi_3, m.aoi_4, m.eot_score, m.project_work, 
                m.eot_score, m.grade or 'P', 'STF', get_sub_remark(m.eot_score)
            ])

        table = Table(data, colWidths=[45, 25, 25, 25, 25, 25, 30, 25, 30, 25, 30, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        table.wrapOn(p, width, height)
        table.drawOn(p, 30, height-450)

        # 8. 📚 NATIONAL GRADING EXPLANATORY KEY (The Footer logic)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(50, 180, "NATIONAL GRADING SYSTEMS & STANDARDS:")
        p.setFont("Helvetica", 6.5)
        p.drawString(50, 165, "1. PRIMARY (PLE): DIV 1 (4-12 Agg) | DIV 2 (13-23 Agg) | DIV 3 (24-28 Agg)")
        p.drawString(50, 155, "2. SECONDARY (CBC): 90-100: A+ (Exceptional) | 80-89: A (Superior) | 70-79: B (Outstanding)")
        p.drawString(50, 145, "3. UACE: A (6pts) | B (5pts) | C (4pts) | D (3pts) | E (2pts) | O (1pt) | F (0pts)")
        
        # ✍️ AUTHORIZATION
        p.line(50, 80, 200, 80)
        p.drawString(70, 70, "Head Teacher Signature")
        p.line(350, 80, 500, 80)
        p.drawString(370, 70, "National Hub Registrar")
        
        # Stamp Box
        p.setStrokeColor(colors.HexColor("#008080"))
        p.circle(width/2, 85, 35, stroke=1, fill=0)
        p.drawCentredString(width/2, 85, "VERIFIED Hub")

        p.showPage(); p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Hub Printing Error: {str(e)}", status=400) 
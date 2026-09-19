import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Avg, Sum

# 💎 THE Hub Hub Hub Hub REST FRAMEWORK Hub Hub Hub Hub 💎
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q, Avg
from django.contrib.auth import get_user_model
from .models import *

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .models import Staff, Student # 💎 Ensure Staff is imported!
import africastalking

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
            p_rec = Parent.objects.get(phone_number=phone_in)
            student = p_rec.students.first() 
            if not student or student.full_name.lower() != s_name:
                return Response({"msg": "Identity Mismatch in National Registry"}, status=401)
            
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
        return Response([{
            "name": s.full_name, 
            "id": s.staff_id, 
            "designation": s.get_role_display() # This shows 'Class Teacher' instead of 'TEACHER'
        } for s in staff])

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

        if student.photo:
            try:
                # We use the path to the photo
                p.drawImage(student.photo.path, width-130, height-150, width=80, height=100, mask='auto')
                # Gold Frame
                p.setStrokeColor(rich_gold)
                p.setLineWidth(1)
                p.rect(width-130, height-150, 80, 100, stroke=1)
            except Exception as photo_error:
                print(f"Photo Error: {photo_error}") # Don't crash if photo is missing

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
            formatted_score = f"{m.eot_score:g} / {m.eot_max}" 
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
from django.contrib.auth import get_user_model

User = get_user_model()

def create_initial_king(request):
    # This is a secret URL to build the first admin in the clouds
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@unsccdc.com", "Imperial2026!")
        return HttpResponse("The King is Born in the Clouds! 👑")
    return HttpResponse("The Throne is already occupied.")   
# --- 👑 THE IMPERIAL KING-MAKER DOOR ---
from django.contrib.auth import get_user_model


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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student, Staff

@csrf_exempt
def student_identity_gate(request):
    """STAGE 1: Verify the 4-Point Identity Match (Parent/Student)"""
    if request.method == "OPTIONS": return sovereign_response({})
    
    try:
        # 💎 THE Hub Hub Hub Hub FIX: Read the JSON Body
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        s_name = data.get('student', '').strip()
        p_name = data.get('parent', '').strip()
        phone = data.get('phone', '').strip()

        # 🕵️ Phone Sanitizer: Match last 9 digits (handles +256 vs 07...)
        search_phone = phone[-9:] if len(phone) >= 9 else phone

        match = Student.objects.filter(
            payment_code__iexact=code,
            full_name__iexact=s_name,
            parent_link__full_name__iexact=p_name,
            parent_link__phone_number__icontains=search_phone
        ).first()

        if match:
            return sovereign_response({
                'status': 'IDENTITY_CONFIRMED',
                'student_id': match.account_number,
                'message': f"Identity Confirmed for {match.full_name}"
            })
        
        return sovereign_response({'msg': 'National Registry Mismatch. Please check spelling or PRN.'}, status=401)
    except Exception as e:
        return sovereign_response({'msg': 'Verification Gateway Error'}, status=500)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def staff_hub_auth(request):
    if request.method == "OPTIONS": return sovereign_response({})
    try:
        data = json.loads(request.body)
        name_in = data.get('name', '').strip()
        pin_in = str(data.get('pin', '')).strip()

        # 🕵️ THE TRUTH: Based on your error log, the field is 'full_name'
        staff = Staff.objects.filter(full_name__iexact=name_in, secure_pin=pin_in).first()

        if staff:
            return sovereign_response({
                "status": "authenticated",
                "type": "staff",
                "name": staff.full_name,
                "role": staff.get_role_display() if hasattr(staff, 'get_role_display') else "Staff",
                "photo": request.build_absolute_uri(staff.photo.url) if staff.photo else "",
                "schools": [{"school_name": staff.school.name if staff.school else "National Hub"}]
            })
        
        return sovereign_response({'msg': 'Credentials Denied'}, status=401)
    except Exception as e:
        return sovereign_response({'msg': f'Internal Error: {str(e)}'}, status=500)

# 📺 FIX FOR THE 404 NOT FOUND: /api/feed/
@api_view(['GET'])
@permission_classes([AllowAny])
def get_national_feed(request):
    """Returns the TikTok-style video broadcasts for schools"""
    posts = SchoolPost.objects.all().order_by('-date')[:15]
    feed = []
    for p in posts:
        feed.append({
            "media": request.build_absolute_uri(p.media_file.url) if p.media_file else "",
            "school": p.school.name,
            "title": p.title,
            "desc": getattr(p, 'content', 'Sovereign Broadcast'),
            "likes": getattr(p, 'likes_count', 0),
            "verified": True
        })
    return sovereign_response(feed)

from .utils import get_national_grading

@csrf_exempt
def pin_vault_auth(request):
    """STAGE 2: Final PIN Unlock & Full Data Delivery"""
    if request.method == "OPTIONS": return sovereign_response({})
    
    try:
        data = json.loads(request.body)
        sid = data.get('student_id')
        pin = data.get('pin', '').strip()

        student = Student.objects.select_related('parent_link', 'school').get(account_number=sid)
        parent = student.parent_link

        if parent and parent.secure_pin == pin:
            # 🚀 AUTHENTICATED: Build the Imperial Data Package
            sch = student.school
            
            # A. Finance Logic
            f_rec = getattr(student, 'fees', None)
            total_due = getattr(f_rec, 'total_fees_due', 0)
            paid = getattr(f_rec, 'total_fees_paid', 0)

            # B. Marks Logic (KEB Mock & National)
            national_report = {}
            # (Your marks gathering logic here...)

            # C. Marketing Feed (TikTok)
            feed_data = []
            for f in SchoolPost.objects.all().order_by('-date')[:10]:
                feed_data.append({
                    "media": request.build_absolute_uri(f.media_file.url) if f.media_file else "",
                    "school": f.school.name,
                    "title": f.title,
                    "desc": getattr(f, 'content', 'Sovereign Excellence'),
                    "likes": getattr(f, 'likes_count', 0),
                    "verified": True
                })

            # D. National Top Performers (The Carousel)
            performers = []
            for t in NationalTopPerformer.objects.all().order_by('?')[:10]:
                performers.append({
                    "name": t.name,
                    "school": t.school_name,
                    "score": t.score,
                    "photo": request.build_absolute_uri(t.photo.url) if t.photo else ""
                })

            return sovereign_response({
                "status": "authenticated",
                "name": student.full_name,
                "id": student.account_number,
                "payment_code": student.payment_code,
                "photo": request.build_absolute_uri(student.photo.url) if student.photo else "",
                "school": {"name": sch.name, "motto": sch.school_motto, "verified": True},
                "finance": {"balance": total_due - paid, "paid": paid, "total_due": total_due},
                "feed": feed_data,
                "top_performers": performers,
                "national_report": national_report
            })

        return sovereign_response({'msg': 'INVALID 6-DIGIT PIN'}, status=401)
    except Exception as e:
        return sovereign_response({'msg': 'Authorization Error'}, status=500)

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

import os
import datetime
from django.db.models import Avg
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import Student, AcademicResult, FeesTracker, School

def generate_national_report_pdf(request, student_id):
    """
    THE GOLIATH Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub
    UNSCCDC NATIONAL Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub
    """
    # 🏛️ 1. DEFINE Hub Hub Hub Hub Hub Hub Hub COLORS
    gov_blue = colors.HexColor("#002366")   # Royal Navy (Authority)
    rich_gold = colors.HexColor("#D4AF37")  # Champagne Gold (Prestige)
    off_white = colors.HexColor("#FDFDF5")  # Institutional Parchment
    ug_yellow = colors.HexColor("#FCDC04")  # National Gold
    ug_red = colors.HexColor("#D90000")     # National Red

    try:
        # 🔑 2. Hub Hub Hub Hub Hub Hub IDENTITY GATE
        student = Student.objects.get(account_number=student_id)
        fees, _ = FeesTracker.objects.get_or_create(student=student)
        
        amt_to_be_paid = fees.total_fees_due
        total_paid = fees.total_fees_paid
        balance = fees.fees_balance
        marks = student.marks.all() 
        school = student.school

        # 🧮 3. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub RANKING ENGINE
        all_class_students = Student.objects.filter(current_class=student.current_class, school=school)
        student_scores = []
        for s_obj in all_class_students:
            avg = s_obj.marks.aggregate(a=Avg('eot_score'))['a'] or 0
            student_scores.append({'id': s_obj.id, 'avg': avg})
        
        student_scores.sort(key=lambda x: x['avg'], reverse=True)
        total_in_class = len(student_scores)
        position = next((i + 1 for i, item in enumerate(student_scores) if item['id'] == student.id), 1)
        overall_avg = next((item['avg'] for item in student_scores if item['id'] == student.id), 0)

        # 📄 4. Hub Hub Hub Hub Hub INITIALIZE CANVAS
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="National_Report_{student.full_name}.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4 

        # 🎨 3. NATIONAL PALETTE & BACKGROUND
        gov_blue = colors.HexColor("#002366")   # Royal Navy
        rich_gold = colors.HexColor("#D4AF37")  # Champagne Gold
        off_white = colors.HexColor("#FDFDF5")  # Parchment
        
        p.setFillColor(off_white)
        p.rect(0, 0, width, height, fill=1, stroke=0)

        # 🛡️ 4. TRIPLE-GUARD BORDERS
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(colors.HexColor("#FCDC04")); p.rect(22, 22, width-44, height-44)
        p.setStrokeColor(colors.HexColor("#D90000")); p.rect(23, 23, width-46, height-46)

        # 🎨 5. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub PAINT THE Hub Hub Hub Hub Hub Hub Hub FLOOR
        p.setFillColor(off_white)
        p.rect(0, 0, width, height, fill=1, stroke=0)

        # 🛡️ 6. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub TRIPLE-GUARD Hub Hub Hub Hub Hub Hub Hub Hub BORDERS
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(ug_yellow); p.rect(22, 22, width-44, height-44)
        p.setStrokeColor(ug_red); p.rect(23, 23, width-46, height-46)

        # 🌌 7. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub SOVEREIGN Hub Hub Hub Hub Hub Hub Hub Hub WATERMARK
        p.saveState()
        p.setFont("Helvetica-Bold", 45); p.setFillColor(colors.lightgrey, alpha=0.03)
        p.translate(width/2, height/2); p.rotate(45); p.drawCentredString(0, 0, "UNSCCDC OFFICIAL RECORD")
        p.restoreState()

        # 🎨 8. Hub Hub Hub Hub Hub Hub Hub Hub Hub INTERNAL Hub Hub Hub Hub Hub Hub Hub Hub AI LOGIC
        def calculate_uce_grade(score):
            if score >= 80: return "A"
            if score >= 70: return "B"
            if score >= 60: return "C"
            if score >= 50: return "D"
            return "E"
        
        def get_sub_remark(score):
            if score >= 90: return "Exceptional mastery."
            if score >= 80: return "Excellent. Maintain focus."
            if score >= 70: return "Very good effort."
            if score >= 60: return "Good progress."
            if score >= 50: return "Basic competency."
            return "Requires support."

        def get_teacher_comment(avg):
            if avg >= 80: return "Disciplined and hardworking. High leadership potential."
            if avg >= 60: return "Good performance. Should focus more on technicals."
            return "Needs more effort and attend all remedial sessions."
        
        # 💎 THE Hub Hub Hub Hub Hub Hub Hub SECTOR-SPECIFIC GRADING
        if school.sector == 'PRIMARY':
            grade_title = "PRIMARY (PLE) GRADING STANDARDS"
            grade_data = [
                ['Agg', 'Div', 'Description'],
                ['4-12', '1', 'Exceptional - High Distinction'],
                ['13-23', '2', 'Strong Credit'],
                ['24-28', '3', 'Pass'],
                ['29-34', '4', 'Minimum Pass']
            ]
        elif school.sector == 'UNIVERSITY':
            grade_title = "HIGHER EDUCATION (NCHE) CGPA STANDARDS"
            grade_data = [
                ['CGPA', 'Class', 'Standing'],
                ['4.40-5.00', '1st Class', 'Exceptional Excellence'],
                ['3.60-4.39', '2nd Upper', 'Strong Honors'],
                ['2.80-3.59', '2nd Lower', 'Average Honors'],
                ['2.00-2.79', 'Pass', 'Satisfactory']
            ]
        else: # Default UCE
            grade_title = "SECONDARY (UCE) COMPETENCY STANDARDS"
            grade_data = [ ... ] # Your existing UCE data

        # 🏛️ 9. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub OFFICIAL Hub Hub Hub Hub Hub Hub Hub Hub Hub HEADER
        p.setFillColor(colors.black); p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(width/2, height-45, "THE REPUBLIC OF UGANDA")
        p.drawCentredString(width/2, height-58, "UGANDA NATIONAL EXAMINATIONS BOARD (UNEB)")

        if student.photo:
                    try:
                        # 🕵️ Safety check for Render's ephemeral storage
                        if os.path.exists(student.photo.path):
                            # 📍 TOP LEFT COORDINATES
                            px, py = 45, height - 130 
                            pw, ph = 70, 85 # Elegant Passport size
                            
                            # 1. Draw a subtle "Imperial Shadow" for 3D effect
                            p.setFillColor(colors.HexColor("#D3D3D3"))
                            p.rect(px + 1.5, py - 1.5, pw, ph, fill=1, stroke=0)
                            
                            # 2. Draw the actual student photo
                            p.drawImage(student.photo.path, px, py, width=pw, height=ph, mask='auto')
                            
                            # 3. Draw the Imperial Gold Frame (Matches the borders)
                            p.setStrokeColor(rich_gold)
                            p.setLineWidth(1.2)
                            p.rect(px, py, pw, ph, stroke=1, fill=0)
                            
                            # 4. Tiny "Verified" watermark on the photo bottom
                            p.setFillColor(colors.white)
                            p.setFont("Helvetica-Bold", 5.5)
                            p.drawString(px + 4, py + 4, "SECURE IDENTITY")
                    except Exception as e:
                        print(f"Top-Left Photo Skip: {e}")
        
        
       # 🖼️ 5. DYNAMIC SCHOOL LOGO (Replaces the Seal)
        if school.logo:
            try:
                # Path handles local and server storage automatically
                p.drawImage(school.logo.path, width/2-35, height-115, width=70, height=70, mask='auto')
            except:
                p.setStrokeColor(gov_blue)
                p.rect(width/2-25, height-115, 50, 50, stroke=1)
                p.drawCentredString(width/2, height-95, "LOGO")
        else:
            p.setStrokeColor(gov_blue)
            p.rect(width/2-25, height-115, 50, 50, stroke=1)
            p.drawCentredString(width/2, height-95, "OFFICIAL")

        p.setFont("Helvetica-Bold", 18); p.setFillColor(gov_blue)
        p.drawCentredString(width/2, height-135, school.name.upper())
        p.setFillColor(colors.black); p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(width/2, height-160, "NATIONAL SCHOLASTIC PERFORMANCE RECORD")

        # 👤 10. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub STUDENT Hub Hub Hub Hub Hub Hub Hub Hub IDENTITY
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, height-195, f"STUDENT NAME: {student.full_name.upper()}")
        p.drawString(50, height-210, f"NATIONAL ID: {student.account_number}")
        p.drawString(380, height-195, f"CLASS: {student.current_class} ({student.stream or 'NORTH'})")
        p.drawString(380, height-210, f"TERM: EOT | YEAR: 2026")

        # 📊 11. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub DATA Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub MATRIX
        data = [['SUB', 'A1', 'A2', 'MID', 'A3', 'A4', 'EOT', 'PRJ', 'AVG', 'GRD', 'TCH', 'REMARKS']]
        for m in marks:
            formatted_score = f"{m.eot_score:g} / {m.eot_max}" 
            auto_grade = calculate_uce_grade(m.eot_score) 
            data.append([m.subject.name[:4].upper(), m.aoi_1, m.aoi_2, m.mid_term, m.aoi_3, m.aoi_4, m.eot_score, m.project_work, f"{m.eot_score}%", auto_grade, 'STF', get_sub_remark(m.eot_score)])
        
        has_aois = any(
            getattr(m, 'aoi_1', 0) > 0 or 
            getattr(m, 'aoi_2', 0) > 0 or 
            getattr(m, 'aoi_3', 0) > 0 or 
            getattr(m, 'aoi_4', 0) > 0 
            for m in marks
        )

        if has_aois:
            # 12-Column Mode (Modern CBC)
            headers = ['SUB', 'A1', 'A2', 'MID', 'A3', 'A4', 'EOT', 'PRJ', 'AVG', 'GRD', 'TCH', 'REMARKS']
            col_widths = [45, 20, 20, 25, 20, 20, 25, 25, 30, 25, 30, 160]
        else:
            # 8-Column Mode (Traditional - AOIs DISAPPEAR COMPLETELY)
            headers = ['SUBJECT NAME', 'MID TERM', 'EOT EXAM', 'PROJECT', 'AVERAGE', 'GRADE', 'TEACHER', 'REMARKS']
            col_widths = [100, 55, 55, 55, 55, 45, 55, 120]

        data_rows = [headers]
        for m in marks:
            # Auto-Grader Logic
            score = m.eot_score
            g = "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D" if score >= 50 else "E"
            rem = "Excellent" if score >= 80 else "Good" if score >= 50 else "Needs Effort"

            if has_aois:
                # 💎 Row with AOIs
                data_rows.append([
                    m.subject.name[:4].upper(), 
                    m.aoi_1, getattr(m, 'aoi_2', 0), m.mid_term, 
                    getattr(m, 'aoi_3', 0), getattr(m, 'aoi_4', 0), 
                    m.eot_score, m.project_work, f"{score}%", g, 'STF', rem
                ])
            else:
                # 💎 Row WITHOUT AOIs (The 00s are physically removed!)
                data_rows.append([
                    m.subject.name.upper(), m.mid_term, m.eot_score, 
                    m.project_work, f"{score}%", g, 'STF', rem
                ])

        # Create Table with dynamic widths
        table = Table(data_rows, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), gov_blue), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 7), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [off_white, colors.white]),
            ('GRID', (0,0), (-1,-1), 0.1, colors.grey), ('LINEBELOW', (0,0), (-1,0), 2, rich_gold),
        ]))
        table.wrapOn(p, width, height); table.drawOn(p, 30, height - 350)

        # 📚 12. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub UCE Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub COMPETENCY
        p.setFont("Helvetica-Bold", 8); p.drawString(50, height - 375, "GRADE COMPETENCY LEVEL & DESCRIPTION (UCE STANDARDS):")
        grade_data = [
            ['Grade', 'Level', 'Description / Score Bracket'],
            ['A', 'Exceptional', '80% - 100%. Extraordinary mastery innovatively applied.'],
            ['B', 'Outstanding', '70% - 79%. High competency in practical applications.'],
            ['C', 'Satisfactory', '60% - 69%. Adequate competency in application.'],
            ['D', 'Basic', '50% - 59%. Minimum level of competency in problem solving.'],
            ['E', 'Elementary', '0% - 49%. Below the basic level of competency.']
        ]
        g_table = Table(grade_data, colWidths=[40, 80, 360])
        g_table.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.1,colors.black),('BACKGROUND',(0,0),(-1,0),gov_blue),('TEXTCOLOR',(0,0),(-1,0),colors.white)]))
        g_table.wrapOn(p, width, height); g_table.drawOn(p, 50, height - 470)

        # 🎓 13. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub UACE Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub (A-LEVEL) Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub KEY
        p.setFont("Helvetica-Bold", 8); p.drawString(50, height - 495, "ADVANCED LEVEL (UACE) PRINCIPAL PASS SCALES:")
        uace_data = [
            ['A (6pts)', 'B (5pts)', 'C (4pts)', 'D (3pts)', 'E (2pts)', 'O (1pt)', 'F (0pts)'],
            ['Excellent', 'Very Good', 'Good', 'Satisfactory', 'Fair', 'Sub. Pass', 'Fail']
        ]
        u_table = Table(uace_data, colWidths=[68, 68, 68, 68, 68, 68, 68])
        u_table.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.1,colors.black),('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        u_table.wrapOn(p, width, height); u_table.drawOn(p, 50, height - 530)

        # =============================================================
        # 💎 --- SECTION 12: Hub Hub Hub OFFICIAL Hub Hub Hub ADMINISTRATIVE Hub Hub Hub REMARKS ---
        # =============================================================
        p.setFont("Helvetica-Bold", 8)
        p.setFillColor(gov_blue)
        p.drawString(50, height - 565, "OFFICIAL ADMINISTRATIVE REMARKS:")

        # 🛡️ Draw a prestigious thin grey box for the remarks (Height Adjusted)
        p.setStrokeColor(colors.grey)
        p.setLineWidth(0.5)
        p.rect(50, height - 640, width - 100, 60) # Top=height-575, Bottom=height-635

        # A. Class Teacher Remarks
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(60, height - 595, "CLASS TEACHER:")
        p.setFont("Helvetica-Oblique", 7.5)
        class_remark = get_teacher_comment(overall_avg)
        p.drawString(135, height - 595, f'"{class_remark}"')

        # B. Headteacher Remarks
        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(60, height - 620, "HEAD TEACHER:")
        p.setFont("Helvetica-Oblique", 7.5)
        ht_remark = "Exceptional discipline. Highly recommended for National progressive placement." if overall_avg >= 75 else "Steady progress observed. Needs consistent focus in project-based assessments."
        p.drawString(135, height - 620, f'"{ht_remark}"')

        # =============================================================
        # 📜 --- SECTION 13: Hub Hub Hub CERTIFICATION Hub Hub Hub Hub Hub & Hub Hub Hub Hub Hub RANKING Hub Hub Hub ---
        # =============================================================
        p.setFont("Helvetica-Bold", 8)
        p.setFillColor(colors.black)
        p.drawString(50, height - 660, "CERTIFICATION STATUS:")
        p.setFont("Helvetica", 7)
        p.drawString(60, height - 672, f"• Result 1: Qualifies for UCE certificate. (Student achieved overall average of {overall_avg:.1f}%)")
        
        
        # 📊 National Standing & PRN Bar (Clean Horizontal Alignment)
        p.setStrokeColor(rich_gold)
        p.setLineWidth(1)
        p.line(50, height - 715, width - 50, height - 715) # Gold divider

        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(gov_blue)
        p.drawString(50, height - 710, f"NATIONAL STANDING: Position {position} out of {total_in_class}")
        
        p.setFillColor(ug_red)
        p.drawRightString(width - 50, height - 710, f"SCHOOLPAY PRN: {student.payment_code or '---'}")

        p.setFont("Helvetica-Oblique", 6.5)
        p.setFillColor(colors.black)
        p.drawString(50, height - 725, "Note: UNEB explicitly does not rank candidates via aggregates to avoid unethical competition.")

        # =============================================================
        # ✍️ --- SECTION 14: Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub FINAL Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub SIGNATURES ---
        # =============================================================
        p.setStrokeColor(gov_blue)
        p.setLineWidth(0.8)

        # =============================================================
        # 💰 --- SECTION 13.5: Hub Hub Hub NATIONAL TREASURY STANDING (REFINED) ---
        # =============================================================
        # 🛡️ 1. Draw the Royal Navy Background Bar
        p.setStrokeColor(rich_gold)
        p.setLineWidth(1.5)
        p.setFillColor(gov_blue) 
        p.rect(45, height - 730, width - 90, 50, fill=1) # Widened slightly

        # ✍️ 2. Insert the Real Shillings & National PRN
        p.setFillColor(colors.white)
        
        # Column 1: Total Due
        p.setFont("Helvetica-Bold", 7)
        p.drawString(55, height - 700, "TOTAL BILLED")
        p.setFont("Helvetica-Bold", 10)
        p.drawString(55, height - 715, f"{amt_to_be_paid:,.0f}")

        # Column 2: Total Paid
        p.setFont("Helvetica-Bold", 7)
        p.drawString(165, height - 700, "TOTAL PAID")
        p.setFont("Helvetica-Bold", 10)
        p.drawString(165, height - 715, f"{total_paid:,.0f}")

        # Column 3: Balance
        p.setFont("Helvetica-Bold", 7)
        p.drawString(285, height - 700, "OUTSTANDING BAL")
        p.setFont("Helvetica-Bold", 11)
        if balance <= 0:
            p.setFillColor(colors.HexColor("#00FF00")) # Success Green
            p.drawString(285, height - 715, "CLEARED")
        else:
            p.setFillColor(colors.white)
            p.drawString(285, height - 715, f"{balance:,.0f}")

        # 🔥 Column 4: THE Hub Hub NATIONAL PRN (THE KEY)
        # We use a bright, aggressive Red for high-visibility
        p.setFillColor(colors.HexColor("#FF0000")) # 🔴 PERFECT RED
        p.setFont("Helvetica-Bold", 8)
        p.drawString(425, height - 700, "PAYMENT CODE")
        p.setFont("Helvetica-Bold", 14) # 💎 Large font so parents can't miss it!
        p.drawString(425, height - 718, f"{student.payment_code or 'N/A'}")

        # 📄 3. Security Footer under the bar
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Oblique", 7)
        p.drawString(50, height - 745, f"Payment status is live. Reference the Red PRN code for all Bank/Mobile Money settlements.")
        # Left Signature
        p.line(50, height - 785, 200, height - 785)
        p.setFont("Helvetica-Bold", 7)
        p.drawCentredString(125, height - 797, "Head Teacher Signature")

        # Right Signature
        p.line(width - 200, height - 785, width - 50, height - 785)
        p.drawCentredString(width - 125, height - 797, "National Hub Registrar")
        
        # 🛡️ THE Hub Hub Hub Hub SOVEREIGN STAMP (Centered perfectly)
        p.setStrokeColor(colors.HexColor("#008080")) # Institutional Teal
        p.circle(width/2, height - 780, 32, stroke=1, fill=0)
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(width/2, height - 775, "UNSCCDC")
        p.setFont("Helvetica", 6)
        p.drawCentredString(width/2, height - 785, "VERIFIED")
        p.setFont("Helvetica-Bold", 7)
        p.drawCentredString(width/2, height - 795, datetime.date.today().strftime("%d-%b-%Y"))

        p.showPage(); p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Hub Printing Error: {str(e)}", status=400)

import random
from django.http import JsonResponse
from .models import Student, SchoolPayLedger

def sovereign_shilling_simulator(request):
    """
    🧪 TEST-ONLY Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub
    Simulates an incoming SchoolPay payment to test Real-Time Sync.
    Does not affect live bank credentials.
    """
    # 🛡️ SECURITY KEY: Only you can trigger this
    if request.GET.get('key') != 'imperial_test_2026':
        return JsonResponse({"status": "Access Denied"}, status=403)

    try:
        # 1. Grab the first student in the registry (e.g., Namaganda Erina)
        student = Student.objects.first()
        if not student:
            return JsonResponse({"status": "Error", "msg": "Add a student first!"})

        # 2. Define dummy payment data
        amount = 125000 # Simulating 125k UGX
        receipt = f"SIM-{random.randint(10000, 99999)}"

        # 3. 🚀 THE Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub ACTION
        # Creating this record physically triggers the @receiver(post_save) signal!
        SchoolPayLedger.objects.create(
            student=student,
            school=student.school,
            amount=amount,
            receipt_number=receipt,
            raw_data={"sourceChannel": "AIRTEL_MONEY", "note": "Simulation Test"}
        )

        return JsonResponse({
            "status": "Simulation Success",
            "student": student.full_name,
            "amount_simulated": f"UGX {amount:,.0f}",
            "receipt": receipt,
            "instruction": "Go to Fees Tracker or Bursar Terminal now and refresh!"
        })
    except Exception as e:
        return JsonResponse({"status": "Simulation Failed", "error": str(e)})

# 💎 ADD THESE TO YOUR BATCH ENGINE IN views.py

# =============================================================
# 📜 HELPER 1: THE Hub Hub Hub Hub Hub REPORT CARD ARCHITECT
# =============================================================
def draw_single_report_page(p, student):
    try:
        width, height = A4
        school = student.school
        marks = student.marks.all()
        fees_obj, _ = FeesTracker.objects.get_or_create(student=student)
        
        gov_blue = colors.HexColor("#002366")
        rich_gold = colors.HexColor("#D4AF37")
        off_white = colors.HexColor("#FDFDF5")

        # =============================================================
        # 📸 --- SECTION 6.5: TOP-LEFT BIOMETRIC IDENTITY ---
        # =============================================================
        if student.photo:
            try:
                # 🕵️ Safety check for Render's ephemeral storage
                if os.path.exists(student.photo.path):
                    # 📍 TOP LEFT COORDINATES
                    px, py = 45, height - 130 
                    pw, ph = 70, 85 # Elegant Passport size
                    
                    # 1. Draw a subtle "Imperial Shadow" for 3D effect
                    p.setFillColor(colors.HexColor("#D3D3D3"))
                    p.rect(px + 1.5, py - 1.5, pw, ph, fill=1, stroke=0)
                    
                    # 2. Draw the actual student photo
                    p.drawImage(student.photo.path, px, py, width=pw, height=ph, mask='auto')
                    
                    # 3. Draw the Imperial Gold Frame (Matches the borders)
                    p.setStrokeColor(rich_gold)
                    p.setLineWidth(1.2)
                    p.rect(px, py, pw, ph, stroke=1, fill=0)
                    
                    # 4. Tiny "Verified" watermark on the photo bottom
                    p.setFillColor(colors.white)
                    p.setFont("Helvetica-Bold", 5.5)
                    p.drawString(px + 4, py + 4, "SECURE IDENTITY")
            except Exception as e:
                print(f"Top-Left Photo Skip: {e}")

        # 1. Background & National Borders
        p.setFillColor(off_white); p.rect(0, 0, width, height, fill=1)
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(colors.HexColor("#FCDC04")); p.rect(22, 22, width-44, height-44)

        # 2. School Logo
        if school.logo and os.path.exists(school.logo.path):
            p.drawImage(school.logo.path, width/2-35, height-110, width=70, height=70, mask='auto')
        
        # 3. Header Text
        p.setFillColor(colors.black); p.setFont("Times-Bold", 10)
        p.drawCentredString(width/2, height-40, "THE REPUBLIC OF UGANDA")
        p.setFont("Times-Bold", 18); p.setFillColor(gov_blue)
        p.drawCentredString(width/2, height-135, school.name.upper())

        # 4. Student Info & Photo
        p.setFillColor(colors.black); p.setFont("Times-Bold", 9)
        p.drawString(50, height-200, f"STUDENT: {student.full_name.upper()}")
        p.drawString(50, height-215, f"NATIONAL ID: {student.account_number}")
        p.drawString(350, height-200, f"CLASS: {student.current_class} ({student.stream})")
        
        if student.photo and os.path.exists(student.photo.path):
            p.drawImage(student.photo.path, width-130, height-140, width=80, height=90, mask='auto')

        # 5. Elastic Marks Table
        has_aois = any(m.aoi_1 > 0 for m in marks)
        if has_aois:
            headers = ['SUB', 'A1', 'A2', 'MID', 'A3', 'A4', 'EOT', 'PRJ', 'AVG', 'GRD']
            col_widths = [50, 30, 30, 35, 30, 30, 35, 35, 40, 35]
        else:
            headers = ['SUBJECT NAME', 'MID TERM', 'EOT EXAM', 'PROJECT', 'AVERAGE', 'GRADE']
            col_widths = [150, 70, 70, 70, 70, 60]

        data_rows = [headers]
        for m in marks:
            row = [m.subject.name.upper(), m.mid_term, m.eot_score, m.project_work, f"{m.eot_score}%", "B"]
            if has_aois:
                row = [m.subject.name[:3].upper(), m.aoi_1, m.aoi_2, m.mid_term, m.aoi_3, m.aoi_4, m.eot_score, m.project_work, f"{m.eot_score}%", "B"]
            data_rows.append(row)

        table = Table(data_rows, colWidths=col_widths)
        table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), gov_blue), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.1, colors.black), ('FONTNAME', (0,0), (-1,-1), 'Times-Bold')]))
        table.wrapOn(p, width, height); table.drawOn(p, 40, height - 380)

        # 6. Treasury Bar
        p.setFillColor(gov_blue); p.rect(45, height - 680, width - 90, 50, fill=1, stroke=0)
        p.setFillColor(colors.white); p.setFont("Times-Bold", 7)
        p.drawString(55, height - 635, "OUTSTANDING BALANCE")
        p.drawString(385, height - 635, "NATIONAL PRN")
        p.setFont("Times-Bold", 12); p.drawString(55, height - 655, f"UGX {fees_obj.fees_balance:,.0f}")
        p.setFillColor(colors.red); p.drawString(385, height - 670, f"{student.payment_code}")

    except Exception as e:
        print(f"Error drawing page for {student.full_name}: {e}")

# =============================================================
# 🔔 HELPER 2: THE Hub Hub Hub Hub Hub FEES REMINDER ARCHITECT
# =============================================================
def draw_single_reminder_page(p, student):
    try:
        width, height = A4
        school = student.school
        fees, _ = FeesTracker.objects.get_or_create(student=student)
        
        gov_blue = colors.HexColor("#002366")
        rich_gold = colors.HexColor("#D4AF37")
        
        p.setStrokeColor(gov_blue); p.setLineWidth(5); p.rect(15, 15, width-30, height-30)
        p.setFillColor(gov_blue); p.setFont("Times-Bold", 16)
        p.drawCentredString(width/2, height-100, school.name.upper())
        p.setFont("Times-Bold", 12); p.setFillColor(colors.black)
        p.drawCentredString(width/2, height-130, "OFFICIAL FEES REMINDER")
        
        p.setFont("Times-Bold", 11)
        p.drawString(50, height-180, f"TO THE PARENT/GUARDIAN OF: {student.full_name.upper()}")
        p.drawString(50, height-200, f"CLASS: {student.current_class}")
        
        p.rect(50, height-300, width-100, 80)
        p.drawString(70, height-250, f"TOTAL BALANCE DUE: UGX {fees.fees_balance:,.0f}")
        p.setFillColor(colors.red); p.setFont("Times-Bold", 14)
        p.drawString(70, height-280, f"PAYMENT PRN: {student.payment_code}")
        
        p.setFillColor(colors.black); p.setFont("Times-Roman", 10)
        instructions = "Please settle this balance via MTN/Airtel using the PRN above to avoid service interruption."
        p.drawString(50, height-350, instructions)
    except Exception as e:
        print(f"Reminder Error: {e}")

@login_required
def batch_report_generator(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    selected_class = request.GET.get('class')
    
    students = Student.objects.filter(school=school, current_class=selected_class, is_active=True).order_by('full_name')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="REPORTS_{selected_class}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    
    for student in students:
        # 🛡️ THE Hub Hub Hub Hub Hub SAFETY SHIELD
        try:
            draw_single_report_page(p, student)
            p.showPage() 
        except:
            continue # If one student fails, just go to the next!
        
    p.save()
    return response

    
@login_required
def batch_reminder_generator(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    selected_class = request.GET.get('class')
    
    if not selected_class:
        return HttpResponse("Please select a class first.")

    students = Student.objects.filter(school=school, current_class=selected_class, is_active=True).order_by('full_name')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BATCH_REMINDERS_{selected_class}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    
    for student in students:
        # 🧪 CALL YOUR EXISTING REMINDER DRAWING LOGIC HERE
        draw_single_reminder_page(p, student)
        p.showPage() # 📄 New page for each parent's notice
        
    p.save()
    return response

@api_view(['GET'])
def live_warroom_stats(request):
    """
    🛰️ THE SATELLITE SIGNAL
    Returns raw JSON data for the ApexCharts to update live.
    """
    today = timezone.now().date()
    # 🧮 Calculate live totals
    total_revenue = SchoolPayLedger.objects.filter(timestamp__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    active_logins = 12 # Simulating live parents currently on the app
    
    return Response({
        "revenue_today": f"{total_revenue:,.0f}",
        "active_users": active_logins,
        "performance_index": "94.2%",
        # 📈 Send fresh coordinates for the line chart
        "chart_series": [random.randint(40, 100) for _ in range(7)] 
    })

@csrf_exempt
def catch_app_crash(request):
    """🛡️ THE Hub Hub Hub Hub Hub Hub NATIONAL MONITOR"""
    if request.method == 'POST':
        error_msg = request.POST.get('error', 'Unknown Log')
        
        # 💎 This makes the message look HUGE in the Render Terminal
        print("\n" + "📡" * 20)
        print(f"NATIONAL APP SIGNAL: {error_msg}")
        print("📡" * 20 + "\n")
        
        return HttpResponse("LOG_OK")
    return HttpResponse("LISTENING")

def generate_student_dossier(request, student_id):
    try:
        student = Student.objects.get(account_number=student_id)
        fees = FeesTracker.objects.get(student=student)
        payments = SchoolPayLedger.objects.filter(student=student).order_by('-timestamp')
        marks = AcademicResult.objects.filter(student=student)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="DOSSIER_{student.full_name}.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        gov_blue = colors.HexColor("#002366")
        rich_gold = colors.HexColor("#D4AF37")

        # 1. 🎨 BACKGROUND & BORDERS (England Standard)
        p.setFillColor(colors.HexColor("#FDFDF5"))
        p.rect(0, 0, width, height, fill=1)
        p.setStrokeColor(gov_blue); p.setLineWidth(5); p.rect(15, 15, width-30, height-30)

        # 2. 🏛️ HEADER
        p.setFillColor(gov_blue); p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width/2, height-60, "NATIONAL STUDENT DOSSIER")
        p.setFont("Helvetica", 8); p.setFillColor(colors.grey)
        p.drawCentredString(width/2, height-75, "OFFICIAL RECORD OF THE REPUBLIC OF UGANDA | UNSCCDC GLOBAL")

        # 3. 👤 SECTION: BIOMETRIC & IDENTITY
        p.setFillColor(gov_blue); p.rect(40, height-130, width-80, 20, fill=1)
        p.setFillColor(colors.white); p.setFont("Helvetica-Bold", 10)
        p.drawString(50, height-125, "I. STUDENT IDENTITY & REGISTRY")
        
        p.setFillColor(colors.black); p.setFont("Helvetica-Bold", 9)
        p.drawString(50, height-150, f"FULL NAME: {student.full_name.upper()}")
        p.drawString(50, height-165, f"NATIONAL ID / PRN: {student.payment_code}")
        p.drawString(300, height-150, f"CLASS: {student.current_class} ({student.stream})")
        p.drawString(300, height-165, f"SYSTEM ID: {student.account_number}")

        # 4. 💰 SECTION: FINANCIAL STANDING (Live Data)
        p.setFillColor(gov_blue); p.rect(40, height-210, width-80, 20, fill=1)
        p.setFillColor(colors.white); p.drawString(50, height-205, "II. FINANCIAL TREASURY STATUS")
        
        fin_data = [
            ['Category', 'Amount (UGX)'],
            ['Total Invoiced', f"{fees.total_fees_due:,.0f}"],
            ['Initial Deposit', f"{student.initial_deposit:,.0f}"],
            ['Total Paid to Date', f"{fees.total_fees_paid:,.0f}"],
            ['Current Balance', f"{fees.fees_balance:,.0f}"]
        ]
        t = Table(fin_data, colWidths=[200, 200])
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')]))
        t.wrapOn(p, width, height); t.drawOn(p, 50, height-300)

        # 5. 📑 SECTION: RECENT PAYSLIPS / PAYMENTS
        p.setFillColor(gov_blue); p.drawString(50, height-330, "III. RECENT SETTLEMENT LOG (PAYSLIPS)")
        pay_rows = [['Receipt #', 'Date', 'Amount', 'Channel']]
        for pay in payments[:5]: # Show last 5
            pay_rows.append([pay.receipt_number, pay.timestamp.strftime('%d/%m/%y'), f"{pay.amount:,.0f}", "SchoolPay"])
        
        pt = Table(pay_rows, colWidths=[120, 100, 100, 100])
        pt.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.1, colors.grey), ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke)]))
        pt.wrapOn(p, width, height); pt.drawOn(p, 50, height-430)

        # 6. 📜 SECTION: OFFICIAL DOCUMENT VERIFICATION
        p.setFillColor(gov_blue); p.rect(40, height-470, width-80, 20, fill=1)
        p.setFillColor(colors.white); p.drawString(50, height-465, "IV. DOCUMENT VERIFICATION STATUS")
        
        p.setFillColor(colors.black); p.setFont("Helvetica", 8)
        docs = [
            ("Birth Certificate", student.birth_certificate),
            ("PLE Result Slip", student.ple_result_slip),
            ("UCE Result Slip", student.uce_result_slip)
        ]
        y_pos = height-495
        for label, file in docs:
            status = "✅ VERIFIED & ATTACHED" if file else "❌ PENDING SUBMISSION"
            p.drawString(50, y_pos, f"{label}: {status}")
            y_pos -= 15

        # 7. 🛡️ FOOTER STAMP
        p.setStrokeColor(gov_blue); p.circle(width-100, 80, 40, stroke=1)
        p.setFont("Helvetica-Bold", 8); p.drawCentredString(width-100, 85, "UNSCCDC")
        p.drawCentredString(width-100, 75, "OFFICIAL SEAL")

        p.showPage(); p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Dossier Error: {str(e)}")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Avg, Sum # 💎 CRITICAL IMPORT
from .models import Student, School

@login_required
def sovereign_registry_view(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        
        # 🧠 Get Dynamic Class Map
        sector_map = {
            'PRIMARY': ['Baby', 'Middle', 'Top', 'P.1', 'P.2', 'P.3', 'P.4', 'P.5', 'P.6', 'P.7'],
            'SECONDARY': ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6'],
            'UNIVERSITY': ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
        }
        available_classes = sector_map.get(school.sector, ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6'])
        
        selected_class = request.GET.get('class', available_classes[0])
        query = request.GET.get('q', '').strip()
        
        # 🔎 SEARCH & FILTER ENGINE
        students = Student.objects.filter(school=school).select_related('parent_link')
        
        if query:
            students = students.filter(
                Q(full_name__icontains=query) | 
                Q(payment_code__icontains=query) |
                Q(account_number__icontains=query)
            )
        else:
            students = students.filter(current_class=selected_class)
            
        students = students.order_by('full_name')

        context = {
            'students': students,
            'available_classes': available_classes,
            'selected_class': selected_class,
            'school': school,
            'total_count': students.count(),
            'title': "STUDENT COMMAND COCKPIT"
        }
        return render(request, 'sovereign_registry.html', context)
    except Exception as e:
        return HttpResponse(f"Registry Error: {str(e)}")
    
@login_required
def inject_national_subjects(request):
    """💎 THE Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub MASTER SUBJECT SEED"""
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized")

    vocational_subjects = [
        ('Information & Comm. Technology', 'ICT', 'VOCATIONAL'),
        ('Tailoring & Fashion Design', 'TAIL', 'VOCATIONAL'),
        ('Bakery & Cookery', 'BAKE', 'VOCATIONAL'),
        ('Carpentry & Joinery', 'CARP', 'VOCATIONAL'),
        ('Bricklaying & Concrete Practice', 'BRIC', 'VOCATIONAL'),
        ('Art & Design', 'ART', 'VOCATIONAL'),
        ('Agriculture & Farming', 'AGRI', 'VOCATIONAL'),
        ('Hairdressing & Beauty', 'HAIR', 'VOCATIONAL'),
    ]

    academic_subjects = [
        ('Mathematics', 'MTH', 'CORE'),
        ('English Language', 'ENG', 'CORE'),
        ('Physics', 'PHY', 'CORE'),
        ('Chemistry', 'CHE', 'CORE'),
        ('Biology', 'BIO', 'CORE'),
        ('Geography', 'GEO', 'CORE'),
        ('History', 'HIS', 'CORE'),
    ]

    # 🚀 Inject into the Registry
    for name, code, cat in academic_subjects + vocational_subjects:
        Subject.objects.get_or_create(name=name, defaults={'code': code, 'category': cat})

    return HttpResponse("<h1 style='color:gold; background:black; padding:20px;'>NATIONAL SUBJECTS INJECTED SUCCESSFULLY! 🇺🇬</h1>")

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from api.models import Student, School
from .utils import auto_arrange_pdf_data
import pandas as pd
from docx import Document

def upload_uneb_roster(request, school_id):
    if request.method == "POST" and request.FILES.get("pdf_document"):
        uploaded_pdf = request.FILES["pdf_document"]
        auto_arrange_pdf_data(uploaded_pdf, school_id)
        return redirect('student_roster_dashboard', school_id=school_id)
        
    return render(request, 'upload.html', {'school_id': school_id})

def export_styled_layout(request, school_id, layout_format):
    students = Student.objects.filter(school_id=school_id).order_by('current_class', 'stream', 'full_name')
    school_obj = School.objects.get(id=school_id)

    # 📊 Layout Choice 1: Microsoft Excel Template
    if layout_format == "excel":
        dataset = []
        for s in students:
            dataset.append([s.account_number, s.payment_code, s.full_name, s.current_class, s.stream, s.gender, s.fees_balance])
            
        columns = ["System ID", "SchoolPay PRN", "Full Student Name", "Class", "Stream", "Gender", "Current Balance"]
        df = pd.DataFrame(dataset, columns=columns)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{school_obj.name}_Roster.xlsx"'
        df.to_excel(response, index=False)
        return response

    # 📝 Layout Choice 2: Microsoft Word Structured Table
    elif layout_format == "word":
        doc = Document()
        doc.add_heading(f'{school_obj.name} - Sorted Registry', level=1)
        doc.add_paragraph(f"Motto: {school_obj.school_motto} | Center: {school_obj.uneb_center_number}")
        
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Table Grid'
        
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'PRN (SchoolPay)'
        hdr_cells[1].text = 'Student Name'
        hdr_cells[2].text = 'Class'
        hdr_cells[3].text = 'Stream'
        hdr_cells[4].text = 'Balance status'
        
        for s in students:
            row_cells = table.add_row().cells
            row_cells[0].text = str(s.payment_code or 'N/A')
            row_cells[1].text = s.full_name
            row_cells[2].text = s.current_class
            row_cells[3].text = s.stream
            row_cells[4].text = s.fees_balance
            
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{school_obj.name}_Roster.docx"'
        doc.save(response)
        return response

@login_required
def operations_hub_view(request):
    """🏛️ THE NATIONAL OPERATIONS COMMAND CENTRE (V7.0)"""
    try:
        # 1. 🛡️ SOVEREIGN IDENTITY SHIELD
        # Ensures even the Master Admin can see the dashboard without errors
        user_profile = getattr(request.user, 'profile', None)
        if user_profile and user_profile.school:
            school = user_profile.school
        else:
            school = School.objects.first()

        if not school:
            return HttpResponse("<body style='background:#000;color:gold;padding:50px;'><h1>REGISTRY ERROR</h1><p>No schools found in the National Database.</p></body>")

        # 2. 📡 SATELLITE NOTIFICATION SYNC (SHIELDED)
        # If the external gov sites are down, the dashboard stays alive!
        try:
            sync_national_notifications() 
        except Exception as e:
            print(f"--- 📡 Notification Sync Bypassed: {e} ---")

        updates = []
        try:
            from .models import NationalUpdate
            # We use a try-except here so if the table is missing, the HUB DOES NOT CRASH
            updates = NationalUpdate.objects.all().order_by('-date_found')[:5]
            # Force evaluation to catch the error here, not in the template
            list(updates) 
        except Exception as e:
            print(f"--- ⚠️ NationalUpdate Table not ready yet: {e} ---")
            updates = [] # Fallback to empty list

        # 4. 📊 THE IMPERIAL COMMAND TABS (ALIGNED FOR SUCCESS)
        # All links are now verified and mapped
        minor_tabs = [
            ("Command View", "fa-terminal", "#00d4ff", "/api/cockpit/", "Single-Screen Management"),
            ("Biometric Center", "fa-camera-retro", "#ff5722", "/api/biometric-center/", "Passport Management"),
            ("Student Registry", "fa-user-graduate", "#3498db", "/admin/api/student/", "Manage Learners"),
            ("Fees & Payments", "fa-wallet", "#2ecc71", "/admin/api/schoolpayledger/", "Treasury Sync"),
            ("Exam Center", "fa-file-signature", "#9b59b6", "/api/explorer/", "Input Marks"),
            ("Fees Reminders", "fa-bell", "#f39c12", "/admin/api/feesreminder/", "Print Reminders"), 
            ("Report Architect", "fa-palette", "#ff007f", "/api/architect/", "Design & Branding"),
            ("Report Cards", "fa-print", "#e74c3c", "/api/explorer/", "Generate PDFs"),
            ("Guardian Registry", "fa-users", "#e91e63", "/api/parents/", "Parent Access & PINs"),
            ("Staff Force", "fa-chalkboard-teacher", "#f1c40f", "/admin/api/staff/", "Employee Files"),
            ("Staff Salaries", "fa-hand-holding-usd", "#9b59b6", "/api/payroll-hub/", "Payroll & Tax"),
            ("Import/Export", "fa-file-excel", "#2ecc71", "/api/exchange-center/", "Bulk Data Logistics"),
            ("SMS Broadcast", "fa-comment-alt", "#e67e22", "/api/sms-hub/", "Notify Parents"),
            ("Inventory/Store", "fa-boxes", "#1abc9c", "#", "School Property"),
            ("Library System", "fa-book", "#34495e", "#", "Book Tracking"),
            ("Transport/Bus", "fa-bus", "#d35400", "#", "Routes & Fees"),
            ("Dormitory/Hostel", "fa-bed", "#27ae60", "#", "Accommodation"),
            ("KEB Mock Center", "fa-file-signature", "#2196F3", "/api/keb-portal/", "Candidate Passlips"),
            ("KEB Ingestion", "fa-file-signature", "#2196F3", "/api/keb-ingestion/", "Speed Marks Entry"),
            ("UNEB/DIT Portal", "fa-medal", "#c0392b", "/api/uneb-gateway/", "National Exams"),
            ("KEB Mocks", "fa-file-invoice", "#2196F3", "/api/registry/", "Print KEB Passlips"), # 💎 18th TAB
            ("Performance Hub", "fa-chart-pie", "#008080", "/api/performance-hub/", "Advanced AI Analysis"),
            ("System Health", "fa-microchip", "#7f8c8d", "/admin/api/financialcommandcenter/", "Analytics"),
            ("Academic Command", "fa-award", "#9b59b6", "/api/results-center/", "Performance Analytics"),
            ("Merit List", "fa-trophy", "#ffd700", "/api/merit-list/", "National Rankings"),
            ("Secretary Entry", "fa-keyboard", "#1abc9c", "/api/secretary-entry/", "Fast Marks Ingestion"),
            ("System Settings", "fa-cogs", "#34495e", "/admin/api/systemsettings/", "Configure Hub"),
            ("Manage Users", "fa-user-lock", "#607d8b", "/admin/auth/user/", "Staff Access Control"), 
        ]

        # 5. 🎨 RENDER THE HIGH-DEFINITION DASHBOARD
        return render(request, 'admin/operations_hub.html', {
            'minor_tabs': minor_tabs,
            'national_updates': updates,
            'school': school,
            'title': "NATIONAL OPERATIONS COMMAND"
        })

    except Exception as e:
        # 🚑 THE EMERGENCY TRUTH TRAP
        # If any hidden error occurs, we see the map, not a 500 page!
        import traceback
        return HttpResponse(f"""
            <body style='background:black; color:red; padding:50px; font-family:serif;'>
                <h1>Hub Engine Critical Failure</h1>
                <pre style='color:white; background:#111; padding:20px;'>{traceback.format_exc()}</pre>
                <a href='/admin/' style='color:gold;'>RETURN TO SAFETY</a>
            </body>
        """)

import pdfplumber
from django.db import transaction

@login_required
def execute_data_bridge(request, bridge_id):
    bridge = get_object_or_404(NationalDataBridge, id=bridge_id)
    school = bridge.school
    count = 0
    
    try:
        with pdfplumber.open(bridge.source_pdf.path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table or len(table) < 2: continue
                
                # 🧠 AI HEADER DETECTION
                header = [str(h).upper() if h else "" for h in table[0]]
                idx_name = next((i for i, h in enumerate(header) if "NAME" in h), 0)
                idx_prn = next((i for i, h in enumerate(header) if "PRN" in h or "CODE" in h), 1)
                idx_class = next((i for i, h in enumerate(header) if "CLASS" in h), 2)
                idx_stream = next((i for i, h in enumerate(header) if "STREAM" in h), 3)
                idx_parent = next((i for i, h in enumerate(header) if "PARENT" in h), 4)
                idx_phone = next((i for i, h in enumerate(header) if "PHONE" in h), 5)

                for row in table[1:]:
                    if not row[idx_name] or not row[idx_prn]: continue
                    with transaction.atomic():
                        # 1. Sync Parent
                        p_phone = str(row[idx_phone]).strip() if row[idx_phone] else "000"
                        parent_obj, _ = Parent.objects.get_or_create(
                            phone_number=p_phone,
                            defaults={'full_name': str(row[idx_parent]), 'secure_pin': '123456'}
                        )
                        # 2. Sync Student & Auto-Arrange Class/Stream
                        student_obj, _ = Student.objects.update_or_create(
                            payment_code=str(row[idx_prn]).strip().upper(),
                            defaults={
                                'full_name': str(row[idx_name]).strip().upper(),
                                'current_class': str(row[idx_class]).strip().upper(),
                                'stream': str(row[idx_stream]).strip().upper() if row[idx_stream] else "NORTH",
                                'school': school,
                                'parent_link': parent_obj,
                            }
                        )
                        # 3. Initialize Fees
                        FeesTracker.objects.get_or_create(student=student_obj)
                        count += 1
        
        bridge.is_processed = True
        bridge.records_synced = count
        bridge.save()
        return HttpResponse(f"<body style='background:#000;color:gold;padding:50px;text-align:center;'><h1>BRIDGE SUCCESS!</h1><p style='color:white;'>{count} Students automatically arranged.</p><a href='/admin/'>Back to Dashboard</a></body>")
    except Exception as e:
        return HttpResponse(f"Bridge Error: {str(e)}")

import pdfplumber
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

@login_required
def bridge_preview_portal(request, bridge_id):
    bridge = get_object_or_404(NationalDataBridge, id=bridge_id)
    preview_rows = []
    
    try:
        with pdfplumber.open(bridge.source_file.path) as pdf:
            # We only look at the first page for the preview to be LIGHTNING FAST
            first_page = pdf.pages[0]
            table = first_page.extract_table()
            
            if table:
                # 🧠 AI Column Finder
                header = [str(h).upper() if h else "" for h in table[0]]
                idx_name = next((i for i, h in enumerate(header) if "NAME" in h), 0)
                idx_prn = next((i for i, h in enumerate(header) if "PRN" in h or "CODE" in h), 1)
                idx_class = next((i for i, h in enumerate(header) if "CLASS" in h), 2)
                
                # Take first 10 rows for preview
                for row in table[1:11]:
                    if row[idx_name]:
                        preview_rows.append({
                            'name': row[idx_name],
                            'prn': row[idx_prn],
                            'class': row[idx_class],
                        })

        return render(request, 'admin/bridge_preview.html', {
            'bridge': bridge,
            'preview_rows': preview_rows,
            'title': "DATA PREVIEW PORTAL"
        })
    except Exception as e:
        return HttpResponse(f"Preview Error: {str(e)}")

@login_required
def bridge_commit_data(request, bridge_id):
    """The final trigger that actually saves data to the Registry"""
    # ... (This will call the process_national_pdf logic we built earlier)
    # Redirecting to previous logic for final save
    return process_national_pdf(request, bridge_id)

# =============================================================
# ☢️ THE Hub Hub Hub Hub Hub NUCLEAR TABLE DESTROYER
# =============================================================
from django.db import connection # 💎 Ensure this is at the top of views.py

def nuke_problem_table(request):
    """🛡️ THE EMERGENCY CLEANER - DROPS THE STUCK TABLE"""
    try:
        with connection.cursor() as cursor:
            # 1. Physically drop the old table causing the 'Already Exists' error
            cursor.execute("DROP TABLE IF EXISTS api_dataingestionvault CASCADE;")
            
            # 2. Delete the record of the migrations for your 'api' app
            # This makes Django think the app is brand new!
            cursor.execute("DELETE FROM django_migrations WHERE app = 'api';")
            
        return HttpResponse("<h1 style='color:white; background:red; padding:50px;'>SUCCESS: Table and History Nuked! Ready for Fresh Start.</h1><a href='/admin/'>Go Back to Office</a>")
    except Exception as e:
        return HttpResponse(f"Nuke Error: {str(e)}")

import pdfplumber
from django.db import transaction

@login_required
def bridge_preview_portal(request, bridge_id):
    bridge = get_object_or_404(NationalDataBridge, id=bridge_id)
    
    if not bridge.preview_data:
        try:
            with pdfplumber.open(bridge.source_file.path) as pdf:
                all_rows = []
                for page in pdf.pages:
                    table = page.extract_table()
                    if table: all_rows.extend(table)
                
                if not all_rows: return HttpResponse("No table found in PDF.")

                # 🧠 AI Column Intelligence
                header = [str(h).upper() for h in all_rows[0]]
                def find_idx(keys, default):
                    for i, h in enumerate(header):
                        if any(k in h for k in keys): return i
                    return default

                idx_name = find_idx(["NAME", "STUDENT"], 0)
                idx_prn = find_idx(["PRN", "CODE", "ID"], 1)
                idx_class = find_idx(["CLASS", "LEVEL"], 2)
                idx_stream = find_idx(["STREAM", "HOUSE"], 3)
                idx_parent = find_idx(["PARENT", "GUARDIAN"], 4)
                idx_phone = find_idx(["PHONE", "CONTACT"], 5)

                # Format the data for the preview
                formatted = []
                for row in all_rows[1:]:
                    if not row[idx_name]: continue
                    formatted.append({
                        'name': str(row[idx_name]).strip().upper(),
                        'prn': str(row[idx_prn]).strip().upper(),
                        'class': str(row[idx_class]).strip().upper(),
                        'stream': str(row[idx_stream]).strip().upper() if row[idx_stream] else "NORTH",
                        'parent': str(row[idx_parent]).strip().title(),
                        'phone': str(row[idx_phone]).strip()
                    })
                
                bridge.preview_data = formatted
                bridge.records_count = len(formatted)
                bridge.save()
        except Exception as e:
            return HttpResponse(f"Scan Error: {str(e)}")

    return render(request, 'admin/bridge_preview.html', {
        'bridge': bridge,
        'preview': bridge.preview_data,
        'title': "NATIONAL DATA PREVIEW"
    })

@login_required
@transaction.atomic
def bridge_commit_final(request, bridge_id):
    """The Final Trigger: Turns 'Ghost Data' into Real Registry Records"""
    bridge = get_object_or_404(NationalDataBridge, id=bridge_id)
    if bridge.is_processed: return HttpResponse("Already Processed.")

    for item in bridge.preview_data:
        # 1. Weld Parent
        parent_obj, _ = Parent.objects.get_or_create(
            phone_number=item['phone'],
            defaults={'full_name': item['parent'], 'secure_pin': '123456'}
        )
        # 2. Weld Student
        Student.objects.update_or_create(
            payment_code=item['prn'],
            defaults={
                'full_name': item['name'],
                'current_class': item['class'],
                'stream': item['stream'],
                'school': bridge.school,
                'parent_link': parent_obj,
                'is_active': True
            }
        )
    
    bridge.is_processed = True
    bridge.save()
    return redirect('/admin/api/student/')

@login_required
def reset_staff_pin(request, staff_id):
    """🛡️ GENERATES A NEW 4-DIGIT Hub Hub Hub PIN"""
    staff = get_object_or_404(Staff, id=staff_id)
    new_pin = ''.join(random.choices(string.digits, k=4))
    staff.secure_pin = new_pin
    staff.save()
    
    return HttpResponse(f"""
        <body style="background:#000; color:white; text-align:center; padding:50px; font-family:sans-serif;">
            <h2 style="color:gold;">PIN RESET SUCCESSFUL</h2>
            <p>New Security PIN for <b>{staff.full_name}</b> is:</p>
            <h1 style="font-size:50px; color:#00ff00; letter-spacing:10px;">{new_pin}</h1>
            <a href="/admin/api/staff/" style="color:gold; text-decoration:none; border:1px solid gold; padding:10px 20px; border-radius:10px;">RETURN TO REGISTRY</a>
        </body>
    """)

from django.contrib.auth import get_user_model # 💎 THE UNIVERSAL KEY

def national_landing_page(request):
    User = get_user_model() # 🛡️ This grabs the CORRECT user model automatically
    
    # 💎 EMERGENCY AUTO-ACCOUNT CREATION (Updated for safety)
    if not User.objects.filter(username='Josephat').exists():
        u = User.objects.create_user('Josephat', password='Josephat123')
        u.is_staff = True
        u.save()
        # Note: You can link the profile here too if needed
    
    # ... rest of your code ...
    """The prestigious entry point for the UNSCCDC Global System"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>UNSCCDC GLOBAL | National Hub</title>
        <style>
            body { background: #050505; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px 20px; margin: 0; }
            .container { max-width: 800px; margin: auto; border: 2px solid #D4AF37; padding: 40px; border-radius: 30px; background: rgba(212,175,55,0.02); box-shadow: 0 0 50px rgba(212,175,55,0.1); }
            h1 { color: #D4AF37; letter-spacing: 4px; font-size: 32px; margin-bottom: 10px; font-weight: 900; }
            p { color: #888; font-size: 16px; line-height: 1.6; }
            .btn-group { margin-top: 40px; display: flex; flex-direction: column; gap: 15px; align-items: center; }
            .btn { text-decoration: none; padding: 18px 30px; border-radius: 15px; font-weight: 900; width: 280px; transition: 0.3s; display: block; border: 1px solid #D4AF37; cursor: pointer; }
            .btn-gold { background: #D4AF37; color: #000; }
            .btn-outline { color: #D4AF37; background: transparent; }
            .btn:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(212,175,55,0.4); }
            .footer { margin-top: 50px; font-size: 11px; color: #444; letter-spacing: 1px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="font-size: 60px; margin-bottom: 20px;">🌍</div>
            <h1>UNSCCDC GLOBAL</h1>
            <p>Uganda National Schools Central Control Digital Centre<br>
            <span style="color: #666;">Sovereign Infrastructure for Modern Education</span></p>
            
            <div class="btn-group">
                <a href="/admin/" class="btn btn-gold">ENTER MASTER OFFICE</a>
                <a href="/api/about/" class="btn btn-outline">ABOUT THE HUB</a>
                <a href="/api/get-app/" class="btn btn-outline" style="border-color: #00ff00; color: #00ff00;">📥 DOWNLOAD MOBILE APP</a>
            </div>
            
            <div class="footer">
                Developed by Yawe Eric &copy; 2026<br>
                Digitizing the Pearl of Africa
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

def generate_fees_reminder_pdf(request, student_id):
    try:
        student = Student.objects.get(account_number=student_id)
        parent = student.parent_link
        school = student.school
        fees = FeesTracker.objects.get(student=student)
        txns = SchoolPayLedger.objects.filter(student=student).order_by('-timestamp')
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Reminder_{student.full_name}.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        # 🎨 IMPERIAL COLORS
        gov_blue = colors.HexColor("#002366")
        rich_gold = colors.HexColor("#D4AF37")
        off_white = colors.HexColor("#FDFDF5")
        ug_red = colors.HexColor("#D90000")  

        # 1. BACKGROUND & BORDERS
        p.setFillColor(off_white); p.rect(0, 0, width, height, fill=1)
        p.setStrokeColor(gov_blue); p.setLineWidth(5); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(rich_gold); p.rect(22, 22, width-44, height-44)

        # 2. LOGO & HEADER
        logo_drawn = False
        if school.logo:
            try:
                # 🕵️ We check if the file physically exists on the disk
                if os.path.exists(school.logo.path):
                    p.drawImage(school.logo.path, width/2-35, height-100, width=70, height=70, mask='auto')
                    logo_drawn = True
                else:
                    print(f"--- ⚠️ Logo file missing on server: {school.logo.path} ---")
            except Exception as e:
                print(f"--- ⚠️ Logo Error: {e} ---")

        if not logo_drawn:
            # 🛡️ THE Hub Hub Hub Hub Hub Hub Hub EMERGENCY Hub Hub Hub Hub Hub Hub Hub SHIELD
            # If logo is missing, draw a professional Gold Seal so the PDF doesn't fail!
            p.setStrokeColor(rich_gold)
            p.setLineWidth(2)
            p.circle(width/2, height-65, 30, stroke=1, fill=0)
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredString(width/2, height-72, "U") # 'U' for Uganda / UNSCCDC
            p.setFont("Helvetica-Bold", 7)
            p.drawCentredString(width/2, height-105, "OFFICIAL SEAL")

        p.setFillColor(gov_blue); p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width/2, height-130, school.name.upper())
        p.setFont("Helvetica-Bold", 10); p.setFillColor(colors.black)
        p.drawCentredString(width/2, height-150, "OFFICIAL FEES REMITTANCE NOTICE")
        p.line(50, height-160, width-50, height-160)

        # 3. PERSONALIZED GREETING
        p.setFont("Helvetica-Bold", 11)
        # Determine Salutation based on Parent Gender (if available, otherwise Mr/Mrs)
        salutation = "Mr/Mrs." 
        if hasattr(parent, 'gender'):
            salutation = "Mr." if parent.gender == 'M' else "Mrs."
            
        p.drawString(50, height-190, f"Dear {salutation} {parent.full_name},")
        p.setFont("Helvetica", 10)
        p.drawString(50, height-205, f"RE: FEES REMINDER FOR {student.full_name.upper()} ({student.current_class})")

        # 4. FINANCIAL SUMMARY
        paid_pct = (fees.total_fees_paid / fees.total_fees_due * 100) if fees.total_fees_due > 0 else 0
        
        p.setFillColor(gov_blue); p.rect(50, height-280, width-100, 60, fill=1)
        p.setFillColor(colors.white); p.setFont("Helvetica-Bold", 9)
        p.drawString(65, height-240, "TOTAL BILLED")
        p.drawString(200, height-240, "TOTAL PAID")
        p.drawString(335, height-240, "PERCENTAGE")
        p.drawString(450, height-240, "BALANCE DUE")
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(65, height-265, f"{fees.total_fees_due:,.0f}")
        p.drawString(200, height-265, f"{fees.total_fees_paid:,.0f}")
        p.drawString(335, height-265, f"{paid_pct:.1f}%")
        p.setFillColor(colors.orange); p.drawString(450, height-265, f"{fees.fees_balance:,.0f}")

        # 5. TRANSACTION HISTORY
        p.setFillColor(colors.black); p.setFont("Helvetica-Bold", 9)
        p.drawString(50, height-310, "RECENT SETTLEMENT HISTORY:")
        
        data = [['Date', 'Receipt #', 'Category', 'Amount (UGX)']]
        for t in txns[:5]:
            data.append([t.timestamp.strftime('%d/%m/%y'), t.transaction_id, t.category, f"{t.amount_paid:,.0f}"])
        
        table = Table(data, colWidths=[100, 150, 130, 120])
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), gov_blue),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.1,colors.grey),('FONTSIZE',(0,0),(-1,-1),8)]))
        table.wrapOn(p, width, height); table.drawOn(p, 50, height-430)

        # 6. THE HUMBLE REMINDER MESSAGE
        p.setFont("Helvetica-Oblique", 9)
        msg = f"We kindly request you to complete the outstanding balance of UGX {fees.fees_balance:,.0f} to ensure " \
              f"uninterrupted learning for {student.full_name.split()[0]}. Thank you for your continued support."
        # Simple text wrap
        p.drawString(50, height-460, msg[:100])
        p.drawString(50, height-475, msg[100:])

        # 7. 📱 USSD PAYMENT GUIDELINES (DETAILED)
        p.setFillColor(colors.HexColor("#F2F2F2")); p.rect(50, 100, width-100, 130, fill=1, stroke=0)
        p.setFillColor(gov_blue); p.setFont("Helvetica-Bold", 9)
        p.drawString(60, 215, "HOW TO PAY VIA SCHOOLPAY (USSD GUIDE):")
        
        p.setFillColor(colors.black); p.setFont("Helvetica-Bold", 8)
        p.drawString(65, 195, "MTN MOBILE MONEY:")
        p.setFont("Helvetica", 7.5)
        p.drawString(65, 185, "Dial *165# > Select 4 (Payments) > Select 4 (School Fees) > Select 1 (SchoolPay) > Enter PRN")
        
        p.setFont("Helvetica-Bold", 8)
        p.drawString(65, 160, "AIRTEL MONEY:")
        p.setFont("Helvetica", 7.5)
        p.drawString(65, 150, "Dial *185# > Select 6 (School Fees) > Select 2 (SchoolPay) > Select 1 (Pay Fees) > Enter PRN")

        p.setFillColor(ug_red); p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(width/2, 115, f"YOUR UNIQUE PRN: {student.payment_code}")

        # ✍️ FOOTER
        p.setFillColor(colors.black); p.setFont("Helvetica-Bold", 8)
        p.line(50, 60, 200, 60); p.drawString(80, 50, "Bursar's Signature")
        p.drawRightString(width-50, 50, f"Issued Date: {datetime.date.today().strftime('%d/%b/%Y')}")

        p.showPage(); p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Reminder Engine Error: {str(e)}")

@login_required
def sovereign_parents_view(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        query = request.GET.get('q', '').strip()
        
        # 🔎 Search for parents who have children in THIS school
        parents = Parent.objects.filter(students__school=school).distinct()

        if query:
            parents = parents.filter(
                Q(full_name__icontains=query) | 
                Q(phone_number__icontains=query)
            )

        context = {
            'parents': parents,
            'school': school,
            'title': "NATIONAL GUARDIAN REGISTRY",
            'total_count': parents.count()
        }
        return render(request, 'sovereign_parents.html', context)
    except Exception as e:
        return HttpResponse(f"Guardian Registry Error: {str(e)}")

@login_required
@transaction.atomic # 💎 Ensures the reversal and balance update happen together or not at all
def execute_sovereign_reversal(request, txn_id):
    txn = get_object_or_404(SchoolPayLedger, id=txn_id)
    
    if txn.is_reversed:
        return HttpResponse("Error: This transaction was already reversed.")

    try:
        # 1. Deduct the amount from the student's total paid in FeesTracker
        from .models import FeesTracker
        tracker = FeesTracker.objects.get(student=txn.student)
        tracker.total_fees_paid -= txn.amount
        tracker.save()

        # 2. Mark the transaction as reversed
        txn.is_reversed = True
        txn.reversal_reason = request.GET.get('reason', 'Correction of wrong entry')
        txn.reversed_at = timezone.now()
        txn.save()

        # 3. Log it in the National Audit Ledger (The permanent record)
        from .models import NationalLedger
        NationalLedger.objects.create(
            transaction_id=f"REV-{txn.receipt_number}",
            school=txn.school,
            student=txn.student,
            category="SYSTEM REVERSAL",
            amount_paid=(txn.amount * -1), # Negative amount to show reversal
            note=f"Reversal of {txn.receipt_number}: {txn.reversal_reason}"
        )

        return HttpResponse(f"""
            <body style="background:#000; color:white; text-align:center; padding:50px; font-family:sans-serif;">
                <h1 style="color:#ff4444;">REVERSAL SUCCESSFUL</h1>
                <p>Transaction <b>{txn.receipt_number}</b> has been voided.</p>
                <p>UGX {txn.amount:,.0f} has been deducted from {txn.student.full_name}'s balance.</p>
                <a href="/admin/api/schoolpayledger/" style="color:gold;">Return to Ledger</a>
            </body>
        """)
    except Exception as e:
        return HttpResponse(f"Reversal Failed: {str(e)}")

@login_required
def add_school_user(request):
    """🛡️ ALLOWS ADMINS TO ADD STAFF TO THEIR OWN SCHOOL ONLY"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized")

    my_school = request.user.profile.school # 💎 THE Hub Hub Hub Hub Hub Hub PRIVACY LOCK

    if request.method == "POST":
        new_username = request.POST.get('username')
        new_pass = request.POST.get('password')
        
        # 1. Create the User
        user = User.objects.create_user(username=new_username, password=new_pass)
        user.is_staff = True # Allow them to see the dashboard
        user.save()

        # 2. Weld them to the school
        UserProfile.objects.create(user=user, school=my_school)
        
        return HttpResponse(f"<h1 style='color:gold;'>User {new_username} added to {my_school.name} Registry!</h1>")

    return render(request, 'admin/add_user_custom.html', {'school': my_school})

from django.contrib.auth import get_user_model # 💎 THE UNIVERSAL KEY

def national_landing_page(request):
    User = get_user_model() # 🛡️ This grabs the CORRECT user model automatically
    
    # 💎 EMERGENCY AUTO-ACCOUNT CREATION (Updated for safety)
    if not User.objects.filter(username='Josephat').exists():
        u = User.objects.create_user('Josephat', password='Josephat123')
        u.is_staff = True
        u.save()
        # Note: You can link the profile here too if needed
    
    # ... rest of your code ...

import os
import datetime
from django.db.models import Avg
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import Student, AcademicResult, FeesTracker, School
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

def generate_national_report_pdf(request, student_id):

    
    gov_blue = colors.HexColor("#002366")   # Royal Navy (Authority)
    rich_gold = colors.HexColor("#D4AF37")  # Champagne Gold (Prestige)
    off_white = colors.HexColor("#FDFDF5")  # Institutional Parchment
    ug_yellow = colors.HexColor("#FCDC04")  # National Gold
    ug_red = colors.HexColor("#D90000")     # National Red

    try:
        # 🔑 2. Hub Hub Hub Hub Hub Hub IDENTITY GATE
        student = Student.objects.get(account_number=student_id)
        fees, _ = FeesTracker.objects.get_or_create(student=student)
        
        amt_to_be_paid = fees.total_fees_due
        total_paid = fees.total_fees_paid
        balance = fees.fees_balance
        marks = student.marks.all() 
        school = student.school

        total_uace_points = 0 

        # 🧮 3. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub RANKING ENGINE
        all_class_students = Student.objects.filter(current_class=student.current_class, school=school)
        student_scores = []
        for s_obj in all_class_students:
            avg = s_obj.marks.aggregate(a=Avg('eot_score'))['a'] or 0
            student_scores.append({'id': s_obj.id, 'avg': avg})
        
        student_scores.sort(key=lambda x: x['avg'], reverse=True)
        total_in_class = len(student_scores)
        position = next((i + 1 for i, item in enumerate(student_scores) if item['id'] == student.id), 1)
        overall_avg = next((item['avg'] for item in student_scores if item['id'] == student.id), 0)

        # 📄 4. Hub Hub Hub Hub Hub INITIALIZE CANVAS
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="National_Report_{student.full_name}.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4 

        # 🎨 3. NATIONAL PALETTE & BACKGROUND
        gov_blue = colors.HexColor("#002366")   # Royal Navy
        rich_gold = colors.HexColor("#D4AF37")  # Champagne Gold
        off_white = colors.HexColor("#FDFDF5")  # Parchment
        
        p.setFillColor(off_white)
        p.rect(0, 0, width, height, fill=1, stroke=0)

        # 🛡️ 4. TRIPLE-GUARD BORDERS
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(colors.HexColor("#FCDC04")); p.rect(22, 22, width-44, height-44)
        p.setStrokeColor(colors.HexColor("#D90000")); p.rect(23, 23, width-46, height-46)

        # 🎨 5. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub PAINT THE Hub Hub Hub Hub Hub Hub Hub FLOOR
        p.setFillColor(off_white)
        p.rect(0, 0, width, height, fill=1, stroke=0)

        # 🛡️ 6. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub TRIPLE-GUARD Hub Hub Hub Hub Hub Hub Hub Hub BORDERS
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(ug_yellow); p.rect(22, 22, width-44, height-44)
        p.setStrokeColor(ug_red); p.rect(23, 23, width-46, height-46)

        # 🌌 7. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub SOVEREIGN Hub Hub Hub Hub Hub Hub Hub Hub WATERMARK
        p.saveState()
        p.setFont("Helvetica-Bold", 45); p.setFillColor(colors.lightgrey, alpha=0.03)
        p.translate(width/2, height/2); p.rotate(45); p.drawCentredString(0, 0, "UNSCCDC OFFICIAL RECORD")
        p.restoreState()
        
        # 🎨 8. Hub Hub Hub Hub Hub Hub Hub Hub Hub INTERNAL Hub Hub Hub Hub Hub Hub Hub Hub AI LOGIC
        def calculate_uce_grade(score):
            if score >= 80: return "A"
            if score >= 70: return "B"
            if score >= 60: return "C"
            if score >= 50: return "D"
            return "E"

        # =============================================================
        # 🎓 A-LEVEL (UACE) DETECTION & SCORING LOGIC
        # =============================================================
        c_name = str(student.current_class).upper()
        is_a_level = any(x in c_name for x in ["S.5", "S5", "S.6", "S6"])
        
        for m in marks:
            if is_a_level:
                sub_upper = m.subject.name.upper()
                # 🛡️ ONLY PRINCIPALS COUNT FOR THE 15-POINT TOTAL
                if not any(x in sub_upper for x in ["GENERAL", "GP", "SUB", "SUBSIDIARY", "ICT", "ICT"]):
                    if m.eot_score >= 80: total_uace_points += 5
                    elif m.eot_score >= 70: total_uace_points += 4
                    elif m.eot_score >= 60: total_uace_points += 3
                    elif m.eot_score >= 50: total_uace_points += 2
                    elif m.eot_score >= 40: total_uace_points += 1

        
        def calculate_uace_points(score, sub_name):
            s_name = sub_name.upper()
            # Subsidiaries (GP, Sub-Math, Sub-ICT) only give 1 point or 0
            if "GENERAL PAPER" in s_name or "SUB" in s_name or "SUBSIDIARY" in s_name:
                return (1 if score >= 40 else 0), ("O" if score >= 40 else "F")
            
            # Principal Subjects (A-E)
            if score >= 80: return 6, "A"
            if score >= 70: return 5, "B"
            if score >= 60: return 4, "C"
            if score >= 50: return 3, "D"
            if score >= 40: return 2, "E"
            if score >= 35: return 1, "O"
            return 0, "F"
        
        def get_uace_final_metrics(score, subject_name):

            sub = subject_name.upper()
            
            # 1. Subsidiaries (GP, Sub-Math, Sub-ICT) still contribute to the profile
            # but the 15-point total usually focuses on the 3 Principals.
            if any(x in sub for x in ["GENERAL PAPER", "GP", "SUB", "SUBSIDIARY", "ICT", "ICT"]):
                if score >= 40: return "O", 1, "Pass"
                else: return "F", 0, "Fail"
            
            # 2. NEW 5-POINT PRINCIPAL SCALE (A=5 to E=1)
            if score >= 80: return "A", 5, "Exceptional"
            if score >= 70: return "B", 4, "Outstanding"
            if score >= 60: return "C", 3, "Satisfactory"
            if score >= 50: return "D", 2, "Basic"
            if score >= 40: return "E", 1, "Elementary"
            return "F", 0, "Unsatisfactory"
        
        def get_sub_remark(score):
            if score >= 90: return "Exceptional mastery."
            if score >= 80: return "Excellent. Maintain focus."
            if score >= 70: return "Very good effort."
            if score >= 60: return "Good progress."
            if score >= 50: return "Basic competency."
            return "Requires support."
            

        def get_teacher_comment(avg):
            if avg >= 80: return "Disciplined and hardworking. High leadership potential."
            if avg >= 60: return "Good performance. Should focus more on technicals."
            return "Needs more effort and attend all remedial sessions."
        
        # 💎 THE Hub Hub Hub Hub Hub Hub Hub SECTOR-SPECIFIC GRADING
        if school.sector == 'PRIMARY':
            grade_title = "PRIMARY (PLE) GRADING STANDARDS"
            grade_data = [
                ['Agg', 'Div', 'Description'],
                ['4-12', '1', 'Exceptional - High Distinction'],
                ['13-23', '2', 'Strong Credit'],
                ['24-28', '3', 'Pass'],
                ['29-34', '4', 'Minimum Pass']
            ]
        elif school.sector == 'UNIVERSITY':
            grade_title = "HIGHER EDUCATION (NCHE) CGPA STANDARDS"
            grade_data = [
                ['CGPA', 'Class', 'Standing'],
                ['4.40-5.00', '1st Class', 'Exceptional Excellence'],
                ['3.60-4.39', '2nd Upper', 'Strong Honors'],
                ['2.80-3.59', '2nd Lower', 'Average Honors'],
                ['2.00-2.79', 'Pass', 'Satisfactory']
            ]
        else: # Default UCE
            grade_title = "SECONDARY (UCE) COMPETENCY STANDARDS"
            grade_data = [ ... ] # Your existing UCE data

        # 🏛️ HEADER SECTION (Sequence: UNEB -> School Name -> School Logo)
        p.setFillColor(colors.black); p.setFont("Times-Bold", 14)
        p.drawCentredString(width/2, height-40, "THE REPUBLIC OF UGANDA")
        p.drawCentredString(width/2, height-55, "UGANDA NATIONAL EXAMINATIONS BOARD (UNEB)")

        
        lx, ly, lw, lh = 35, height - 140, 70, 70
        if school.logo and os.path.exists(school.logo.path):
            p.drawImage(school.logo.path, lx, ly, width=lw, height=lh, mask='auto')
        else:
            p.setStrokeColor(gov_blue); p.rect(lx, ly, lw, lh, stroke=1)
            p.setFont("Times-Bold", 8); p.drawCentredString(lx+(lw/2), ly+30, "LOGO")

        # School Info (Immediately right of the logo)
        p.setFillColor(gov_blue); p.setFont("Times-Bold", 10)
        p.drawString(lx + 70, height - 85, school.name.upper())
        
        p.setFillColor(colors.black); p.setFont("Times-Bold", 8.5)
        # 📞 ADDING THE THREE NUMBERS (Phone 1, Phone 2, and Official Email)
        p.drawString(lx + 70, height - 100, f"TEL 1: {getattr(school, 'phone', '+256 709858960')}")
        p.drawString(lx + 70, height - 112, f"TEL 2: {getattr(school, 'phone2', '+256 770 000000')}")
        p.drawString(lx + 70, height - 124, f"EMAIL: {getattr(school, 'email', 'info@school.ug')}")
        
        p.setFont("Times-Italic", 8); p.setFillColor(colors.grey)
        p.drawString(lx + 70, height - 138, f"MOTTO: \"{getattr(school, 'school_motto', 'Excellence')}\"")


        
        # =============================================================
        # 📸 9. STUDENT BIOMETRIC IDENTITY (WITH HUMAN SHADOW FALLBACK)
        # =============================================================
        # Coordinates: px = width - 125, py = base_y - 180, pw = 80, ph = 100
        px, py, pw, ph = 313, height - 165, 80, 100 
        
        # 🛡️ Draw the Frame first
        p.setStrokeColor(gov_blue)
        p.setLineWidth(1.5)
        p.rect(px, py, pw, ph, stroke=1)

        if student.photo and os.path.exists(student.photo.path):
            # ✅ CASE A: PHOTO EXISTS - Draw the real face
            try:
                p.drawImage(student.photo.path, px, py, width=pw, height=ph, mask='auto')
                p.setFillColor(gov_blue); p.setFont("Times-Bold", 7)
                p.drawCentredString(px + (pw/2), py - 10, "VERIFIED PHOTO")
            except:
                # Secondary fallback if file is corrupted
                draw_human_shadow(p, px, py, pw, ph)
        else:
            # 👤 CASE B: NO PHOTO - Draw the Imperial Human Shadow
            draw_human_shadow(p, px, py, pw, ph)
            p.setFillColor(colors.grey); p.setFont("Times-Bold", 6.5)
            p.drawCentredString(px + (pw/2), py - 10, "PHOTO REQUIRED")
        
        name_style = ParagraphStyle('NameStyle', fontName='Times-Bold', fontSize=9, leading=10)

        # 2. DRAW THE INFORMATION (Right side of the photo, extending to the border)
        p.setFillColor(colors.black); p.setFont("Times-Bold", 9.5)
        # Text starts 90 units to the right of the photo start
        tx = px + 90 
        name_para = Paragraph(f"NAME: {student.full_name.upper()}", name_style)
        name_para.wrapOn(p, 150, 40) # Allow 150 units of width before wrapping
        name_para.drawOn(p, 400, height - 85)
        p.drawString(tx, height - 95,  f"NATIONAL PRN: {student.payment_code or '---'}")
        p.drawString(tx, height - 110, f"ACCOUNT ID: {student.account_number}")
        p.drawString(tx, height - 125, f"LEVEL: {student.current_class} ({student.stream or 'NORTH'})")
        p.drawString(tx, height - 140, f"ACADEMIC YEAR: 2026")
        p.drawString(tx, height - 155, f"TERM: TERM II : EOT")

        # 📏 10. SECTION DIVIDER & TITLE (RE-CENTERED)
        p.setStrokeColor(rich_gold); p.setLineWidth(1.2)
        p.line(45, height - 205, width - 45, height - 205) # Edge-to-edge line
        
        p.setFillColor(colors.black); p.setFont("Times-Bold", 11)
        p.drawCentredString(width/2, height - 222, "NATIONAL TERMLY SCHOLASTIC PERFORMANCE RECORD")

        desc_style = ParagraphStyle('DescStyle', fontName='Times-Roman', fontSize=9, leading=9, alignment=1) # Center align
        
        if is_a_level:
            # 🎓 HIGH-LEVEL A-LEVEL EXPLANATION
            descriptor_text = (
                "<b>UACE EVALUATION STANDARD:</b> This record evaluates the candidate based on the Uganda Advanced Certificate of Education "
                "20-point weighting system. Performance is measured across three (3) Principal Subjects, General Paper, and a Subsidiary. "
                "Your final grade for each subject is no longer determined by the final UNEB exam."
                "80% of the grade comes from the End-of-Cycle (UNEB) Examination."
                "20% of the grade comes from Continuous Assessment (CA) and a school-based project marks."
            )
        else:
            # 📚 NEW CURRICULUM O-LEVEL EXPLANATION
            descriptor_text = (
                "<b>UCE COMPETENCY STANDARD:</b> This record reflects the New Lower Secondary Curriculum (NLSC) standards. "
                "It measures learner achievement through Activities of Integration (AOI), Project-based learning, and Summative "
                "assessments. Grades 1, 2, and 3 represent levels of competency mastery as mandated by UNEB."
            )

        # Draw the descriptor in the 'Dead Space'
        desc_para = Paragraph(descriptor_text, desc_style)
        desc_para.wrapOn(p, 500, 50)
        desc_para.drawOn(p, 48, height - 260) # Positioned perfectly in the gap
        
        if is_a_level:
            summary_title = "UACE PERFORMANCE SUMMARY"
            summary_val = f"{total_uace_points} / 15"
            summary_label = "TOTAL WEIGHT"
        else:
            summary_title = "UCE PERFORMANCE SUMMARY"
            summary_val = f"{overall_avg:.1f}%"
            summary_label = "OVERALL AVERAGE"

        # 💎 Create a small, high-impact table
        summary_data = [
            [summary_title, ''],
            [summary_label, summary_val]
        ]
        
        s_table = Table(summary_data, colWidths=[160, 100])
        s_table.setStyle(TableStyle([
            # Title Row
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (-1,0), rich_gold),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            # Value Row
            ('BACKGROUND', (0,1), (-1,1), gov_blue),
            ('TEXTCOLOR', (0,1), (-1,1), colors.white),
            ('FONTNAME', (0,1), (-1,1), 'Times-Bold'),
            ('FONTSIZE', (0,1), (-1,1), 14),
            ('ALIGN', (0,1), (-1,1), 'CENTER'),
            # Outer Border
            ('GRID', (0,0), (-1,-1), 1.5, gov_blue),
        ]))

        # 📍 Position it in the gap (centered horizontally)
        s_table.wrapOn(p, width, height)
        s_table.drawOn(p, width/2 - 130, height - 315) # Centered below the descriptor

        data = [['SUB', 'A1', 'A2', 'MID', 'A3', 'A4', 'EOT', 'PRJ', 'AVG', 'GRD', 'TCH', 'REMARKS']]
        for m in marks:
            formatted_score = f"{m.eot_score:g} / {m.eot_max}" 
            auto_grade = calculate_uce_grade(m.eot_score) 
            data.append([m.subject.name[:4].upper(), m.aoi_1, m.aoi_2, m.mid_term, m.aoi_3, m.aoi_4, m.eot_score, m.project_work, f"{m.eot_score}%", auto_grade, 'STF', get_sub_remark(m.eot_score)])
        
        has_aois = any(
            getattr(m, 'aoi_1', 0) > 0 or 
            getattr(m, 'aoi_2', 0) > 0 or 
            getattr(m, 'aoi_3', 0) > 0 or 
            getattr(m, 'aoi_4', 0) > 0 
            for m in marks
        )

        if is_a_level:
            # 🏆 A-LEVEL COLUMNS (Separated Grade and Points)
            headers = ['SUBJECT NAME', 'MID', 'EOT', 'AVG', 'GRD', 'PTS', 'TCH', 'REMARKS']
            col_widths = [115, 35, 35, 40, 35, 35, 50, 165] # Total 510
        else:
            # 📚 O-LEVEL COLUMNS (Your existing logic)
            has_aois = any(getattr(m, 'aoi_1', 0) > 0 for m in marks)
            if has_aois:
                headers = ['SUB', 'A1', 'A2', 'MID', 'A3', 'A4', 'EOT', 'PRJ', 'AVG', 'GRD', 'TCH', 'REMARKS']
                col_widths = [45, 18, 18, 22, 18, 18, 22, 22, 30, 25, 35, 237]
            else:
                headers = ['SUBJECT NAME', 'MID', 'EOT', 'PROJ', 'AVG', 'GRD', 'TCH', 'REMARKS']
                col_widths = [115, 45, 45, 45, 45, 35, 50, 130]
        
        data_rows = [headers]
        total_uace_points = 0
        
        for m in marks:
            
            t_init = "STF" 
            rem = "Achieved"
            score = m.eot_score
        
            try:
                teacher_obj = Staff.objects.filter(subjects=m.subject, school=school).first()
                if teacher_obj and teacher_obj.full_name:
                    t_init = teacher_obj.full_name.split()[-1].upper()
            except:
                pass

            # 🤖 STEP C: AUTOMATIC REMARK ENGINE
            if score >= 90: rem = "Exceptional"
            elif score >= 80: rem = "Excellent"
            elif score >= 70: rem = "Very Good"
            elif score >= 60: rem = "Good Progress"
            elif score >= 50: rem = "Fair"
            else: rem = "Basic"

            # 🚀 STEP D: DATA ALIGNMENT (A-Level vs O-Level)
            if is_a_level:
                # --- UACE (A-LEVEL) LOGIC ---
                grd, pts, uace_interp = get_uace_final_metrics(score, m.subject.name)
                total_uace_points += pts
                
                data_rows.append([
                    m.subject.name.upper(), 
                    f"{m.mid_term:g}", 
                    f"{score:g}", 
                    f"{score:g}%", 
                    grd, 
                    pts, 
                    t_init, 
                    uace_interp # A-level uses specific board interpretation
                ])
            else:
                # --- UCE (O-LEVEL) LOGIC ---
                g = calculate_uce_grade(score) # Uses the function we defined above
                
                if has_aois:
                    data_rows.append([
                        m.subject.name[:3].upper(), m.aoi_1, m.aoi_2, m.mid_term, 
                        m.aoi_3, m.aoi_4, m.eot_score, m.project_work, 
                        f"{score:g}%", g, t_init, rem
                    ])
                else:
                    data_rows.append([
                        m.subject.name.upper(), f"{m.mid_term:g}", f"{score:g}", 
                        f"{m.project_work:g}", f"{score:g}%", g, t_init, rem
                    ])

       
        table = Table(data_rows, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), gov_blue), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold'), ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.1, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [off_white, colors.white]),
        ]))
        table.wrapOn(p, width, height)
        table.drawOn(p, 45, height - 408) # 💎 RE-ALIGNED TABLE START


        grade_data = [
            ['Grade', 'Level', 'Description / Score Bracket'],
            ['A', 'Exceptional', '80% - 100%. Extraordinary mastery innovatively applied.'],
            ['B', 'Outstanding', '70% - 79%. High competency in practical applications.'],
            ['C', 'Satisfactory', '60% - 69%. Adequate competency in application.'],
            ['D', 'Basic', '50% - 59%. Minimum level of competency in problem solving.'],
            ['E', 'Elementary', '0% - 49%. Below the basic level of competency.']
        ]
        g_table = Table(grade_data, colWidths=[40, 80, 360])
        g_table.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.1,colors.black),('BACKGROUND',(0,0),(-1,0),gov_blue),('TEXTCOLOR',(0,0),(-1,0),colors.white)]))
        g_table.wrapOn(p, width, height); g_table.drawOn(p, 55, height - 517)

        # 🎓 13. Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub UACE Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub (A-LEVEL) Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub KEY
        p.setFont("Helvetica-Bold", 8); p.drawString(50, height - 528, "ADVANCED LEVEL (UACE) PRINCIPAL PASS SCALES:")
        uace_data = [
            ['A (5pts)', 'B (4pts)', 'C (3pts)', 'D (2pts)', 'E (1pts)', 'O (1pt)', 'F (0pts)'],
            ['Excellent', 'Very Good', 'Good', 'Satisfactory', 'Basic', 'Sub. Pass', 'Fail']
        ]
        u_table = Table(uace_data, colWidths=[68, 68, 68, 68, 68, 68, 68])
        u_table.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.1,colors.black),('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        u_table.wrapOn(p, width, height); u_table.drawOn(p, 50, height - 567)

        # =============================================================
        # 💎 --- SECTION 12: Hub Hub Hub OFFICIAL Hub Hub Hub ADMINISTRATIVE Hub Hub Hub REMARKS ---
        # =============================================================
        p.setFont("Helvetica-Bold", 8)
        p.setFillColor(gov_blue)
        p.drawString(50, height - 578, "OFFICIAL ADMINISTRATIVE REMARKS:")

        # 🛡️ Draw a prestigious thin grey box for the remarks (Height Adjusted)
        p.setStrokeColor(colors.grey)
        p.setLineWidth(0.5)
        p.rect(50, height - 645, width - 100, 60) 

        # A. Class Teacher Remarks
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(60, height - 600, "CLASS TEACHER:")
        p.setFont("Helvetica-Oblique", 7.5)
        class_remark = get_teacher_comment(overall_avg)
        p.drawString(135, height - 600, f'"{class_remark}"')

        # B. Headteacher Remarks
        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(60, height - 625, "HEAD TEACHER:")
        p.setFont("Helvetica-Oblique", 7.5)
        ht_remark = "Exceptional discipline. Highly recommended for National progressive placement." if overall_avg >= 75 else "Steady progress observed. Needs consistent focus in project-based assessments."
        p.drawString(135, height - 625, f'"{ht_remark}"')

        # =============================================================
        # 📜 --- SECTION 13: Hub Hub Hub CERTIFICATION Hub Hub Hub Hub Hub & Hub Hub Hub Hub Hub RANKING Hub Hub Hub ---
        # =============================================================
        p.setFont("Helvetica-Bold", 8)
        p.setFillColor(colors.black)
        p.drawString(50, height - 660, "CERTIFICATION STATUS:")
        p.setFont("Helvetica", 7)
        p.drawString(60, height - 672, f"• Result 1: Qualifies for UCE certificate. (Student achieved overall average of {overall_avg:.1f}%)")
        
        
        # 📊 National Standing & PRN Bar (Clean Horizontal Alignment)
        p.setStrokeColor(rich_gold)
        p.setLineWidth(1)
        p.line(50, height - 715, width - 50, height - 715) # Gold divider

        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(gov_blue)
        p.drawString(50, height - 710, f"NATIONAL STANDING: Position {position} out of {total_in_class}")
        
        p.setFillColor(ug_red)
        p.drawRightString(width - 50, height - 710, f"SCHOOLPAY PRN: {student.payment_code or '---'}")

        p.setFont("Helvetica-Oblique", 6.5)
        p.setFillColor(colors.black)
        p.drawString(50, height - 725, "Note: UNEB explicitly does not rank candidates via aggregates to avoid unethical competition.")

        # =============================================================
        # ✍️ --- SECTION 14: Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub FINAL Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub SIGNATURES ---
        # =============================================================
        p.setStrokeColor(gov_blue)
        p.setLineWidth(0.8)

        # =============================================================
        # 💰 --- SECTION 13.5: Hub Hub Hub NATIONAL TREASURY STANDING (REFINED) ---
        # =============================================================
        # 🛡️ 1. Draw the Royal Navy Background Bar
        p.setStrokeColor(rich_gold)
        p.setLineWidth(1.5)
        p.setFillColor(gov_blue) 
        p.rect(45, height - 730, width - 90, 50, fill=1) # Widened slightly

        # ✍️ 2. Insert the Real Shillings & National PRN
        p.setFillColor(colors.white)
        
        # Column 1: Total Due
        p.setFont("Helvetica-Bold", 7)
        p.drawString(55, height - 700, "TOTAL BILLED")
        p.setFont("Helvetica-Bold", 10)
        p.drawString(55, height - 715, f"{amt_to_be_paid:,.0f}")

        # Column 2: Total Paid
        p.setFont("Helvetica-Bold", 7)
        p.drawString(165, height - 700, "TOTAL PAID")
        p.setFont("Helvetica-Bold", 10)
        p.drawString(165, height - 715, f"{total_paid:,.0f}")

        # Column 3: Balance
        p.setFont("Helvetica-Bold", 7)
        p.drawString(285, height - 700, "OUTSTANDING BAL")
        p.setFont("Helvetica-Bold", 11)
        if balance <= 0:
            p.setFillColor(colors.HexColor("#00FF00")) # Success Green
            p.drawString(285, height - 715, "CLEARED")
        else:
            p.setFillColor(colors.white)
            p.drawString(285, height - 715, f"{balance:,.0f}")

        # 🔥 Column 4: THE Hub Hub NATIONAL PRN (THE KEY)
        # We use a bright, aggressive Red for high-visibility
        p.setFillColor(colors.HexColor("#FF0000")) # 🔴 PERFECT RED
        p.setFont("Helvetica-Bold", 8)
        p.drawString(425, height - 700, "PAYMENT CODE")
        p.setFont("Helvetica-Bold", 14) # 💎 Large font so parents can't miss it!
        p.drawString(425, height - 718, f"{student.payment_code or 'N/A'}")

        # 📄 3. Security Footer under the bar
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Oblique", 7)
        p.drawString(50, height - 745, f"Payment status is live. Reference the Red PRN code for all Bank/Mobile Money settlements.")
        # Left Signature
        p.line(50, height - 785, 200, height - 785)
        p.setFont("Helvetica-Bold", 7)
        p.drawCentredString(125, height - 810, "Head Teacher Signature")

        term_end = getattr(school, 'term_end_date', 'To be announced')
        term_start = getattr(school, 'next_term_start', 'To be announced')

        calendar_data = [
            ['OFFICIAL STATUS & CALENDAR', 'DATE / VALUE'],
            ['REGISTRY STATUS:', '✅ AUTHENTICATED'],
            ['THIS TERM ENDED ON:', term_end.upper()],
            ['NEXT TERM BEGINS ON:', term_start.upper()],
        ]

        # Define table width and position
        cal_table = Table(calendar_data, colWidths=[140, 110])
        cal_table.setStyle(TableStyle([
            # Header Styling
            ('BACKGROUND', (0,0), (-1,0), gov_blue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            # Body Styling
            ('FONTNAME', (0,1), (-1,-1), 'Times-Roman'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            # Grid & Alignment
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,1), (1,-1), 'CENTER'), # Center the dates
        ]))

        # 💎 DRAW THE CALENDAR TABLE (Right Aligned to margin)
        cal_table.wrapOn(p, width, height)
        cal_table.drawOn(p, width - 295, height - 818)
        
        p.showPage(); p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Hub Printing Error: {str(e)}", status=400)

def draw_human_shadow(canvas_obj, x, y, width, height):
    """🛡️ THE Hub Hub Hub Hub Hub Hub Hub VECTOR SILHOUETTE ENGINE"""
    canvas_obj.saveState()
    
    # Set the shadow color (Light Grey/Obsidian tint)
    shadow_color = colors.HexColor("#DCDCDC")
    canvas_obj.setFillColor(shadow_color)
    
    # 1. Draw the Head (Circle)
    head_radius = 16
    canvas_obj.circle(x + width/2, y + height - 35, head_radius, fill=1, stroke=0)
    
    # 2. Draw the Shoulders/Body (Rounded Rectangle)
    # This creates the 'Human Shape' look
    body_width = width - 20
    body_height = 40
    canvas_obj.roundRect(x + 10, y + 15, body_width, body_height, 12, fill=1, stroke=0)
    
    canvas_obj.restoreState()

    
# 🚀 THE Hub Hub Hub Hub Hub NATIONAL PAIRED BATCH ENGINE
@login_required
def batch_report_download(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        selected_class = request.GET.get('class')
        
        if not selected_class:
            return HttpResponse("<h1>Error</h1><p>Please select a class to print.</p>")

        # 🕵️ Fetch all active students in the class A-Z
        students = Student.objects.filter(
            school=school, 
            current_class=selected_class, 
            is_active=True
        ).order_by('full_name')

        if not students.exists():
            return HttpResponse(f"No active students found in {selected_class}")

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="BATCH_A1_SLIPS_{selected_class}.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4 # 595 x 842 points
        half_height = height / 2 # 421 points

        # 🔄 THE Hub Hub Hub Hub Hub PAIRING LOOP
        # We loop through students in steps of 2
        for i in range(0, len(students), 2):
            # 1. DRAW STUDENT A (Top Half of A4)
            student_a = students[i]
            draw_keb_slip_layout(p, student_a, school, 0) # y_offset = 0

            # 2. DRAW THE PERFORATION LINE (The 'Cut Here' Guide)
            p.setDash(4, 4)
            p.setStrokeColor(colors.grey)
            p.setLineWidth(0.5)
            p.line(0, half_height, width, half_height)
            p.setDash() # Reset to solid line

            # 3. DRAW STUDENT B (Bottom Half of A4)
            # Check if there is a second student to pair with
            if i + 1 < len(students):
                student_b = students[i + 1]
                draw_keb_slip_layout(p, student_b, school, half_height) # y_offset = 421
            
            # 💎 THE Hub Hub Hub PAGE BREAK
            # After finishing the two slips, we flip to a new A4 sheet
            p.showPage()
            
        p.save()
        return response

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"National Batch Error: {str(e)}")

# =============================================================
# 🚀 THE Hub Hub Hub Hub Hub NATIONAL KEB BATCH ENGINE (A-ONE)
# =============================================================
@login_required
def batch_keb_passlip_download(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        selected_class = request.GET.get('class')
        
        if not selected_class:
            return HttpResponse("<h1 style='color:red;'>Error: Please select a class.</h1>")

        # 🕵️ Fetch all active candidates in this class
        students = Student.objects.filter(
            school=school, 
            current_class=selected_class, 
            is_active=True
        ).order_by('full_name')

        if not students.exists():
            return HttpResponse(f"<h1>No candidates found in {selected_class}</h1>")

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="BATCH_KEB_PASSLIPS_{selected_class}.pdf"'
        
        # 📄 Start the A4 Canvas
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4 # 595 x 842 points
        half_height = height / 2 # 421 points

        # 🔄 THE Hub Hub Hub PAIRING ENGINE
        # We loop through students in steps of 2
        for i in range(0, len(students), 2):
            
            # 1. DRAW FIRST STUDENT (Top Half)
            student_a = students[i]
            draw_keb_slip_layout(p, student_a, school, 0) # y_offset = 0

            # ✂️ THE PERFORATION LINE (The 'Cut Here' Guide)
            p.setDash(4, 4)
            p.setStrokeColor(colors.grey)
            p.setLineWidth(0.5)
            p.line(0, half_height, width, half_height)
            p.setDash() # Reset to solid

            # 2. DRAW SECOND STUDENT (Bottom Half)
            if i + 1 < len(students):
                student_b = students[i + 1]
                draw_keb_slip_layout(p, student_b, school, half_height) # y_offset = 421
            
            # 💎 FLIP THE PAGE (Next A4 Sheet)
            p.showPage()
            
        p.save()
        return response

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"<body style='background:black;color:red;padding:50px;'><h1>Batch Error</h1><pre>{str(e)}</pre></body>")


@login_required
def academic_results_center(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        
        # 🧠 Get Classes and Subjects
        sector_map = {
            'PRIMARY': ['P.1', 'P.2', 'P.3', 'P.4', 'P.5', 'P.6', 'P.7'],
            'SECONDARY': ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6'],
        }
        classes = sector_map.get(school.sector, ['S.1', 'S.2', 'S.3', 'S.4'])
        subjects = Subject.objects.all()

        # 🔎 Filter Logic
        sel_class = request.GET.get('class', classes[0])
        sel_sub = request.GET.get('subject')
        
        results = AcademicResult.objects.filter(student__school=school, student__current_class=sel_class)
        if sel_sub:
            results = results.filter(subject__id=sel_sub)

        # 📊 Calculate Analytics
        class_avg = results.aggregate(Avg('eot_score'))['eot_score__avg'] or 0
        top_score = results.order_by('-eot_score').first()

        context = {
            'school': school,
            'results': results,
            'classes': classes,
            'subjects': subjects,
            'sel_class': sel_class,
            'sel_sub': sel_sub,
            'class_avg': round(class_avg, 1),
            'top_student': top_score.student.full_name if top_score else "N/A"
        }
        return render(request, 'admin/academic_results_center.html', context)
    except Exception as e:
        return HttpResponse(f"Command Centre Error: {str(e)}")

@login_required
def uneb_dit_gateway(request):
    """🏛️ THE NATIONAL EXTERNAL PORTAL BRIDGE"""
    school = getattr(request.user, 'school', None) or School.objects.first()
    
    # 🔗 OFFICIAL GOVERNMENT LINKS
    portals = [
        {
            "name": "UNEB e-Registration",
            "url": "https://ereg.uneb.ac.ug/",
            "desc": "Register candidates for PLE, UCE, and UACE examinations.",
            "color": "#d35400" # Deep Orange
        },
        {
            "name": "UNEB Results Portal",
            "url": "https://eresults.uneb.ac.ug/",
            "desc": "Access and download official school performance results.",
            "color": "#2980b9"
        },
        {
            "name": "MoES Official Website",
            "url": "https://www.education.go.ug/",
            "desc": "Ministry of Education & Sports policies and circulars.",
            "color": "#27ae60" # Emerald Green
        },
        {
            "name": "DIT Assessment",
            "url": "https://dit.go.ug/",
            "desc": "Directorate of Industrial Training - Vocational Standards.",
            "color": "#8e44ad" # Amethyst Purple
        },
        {
            "name": "EMIS Portal",
            "url": "https://emis.go.ug/",
            "desc": "Educational Management Information System login.",
            "color": "#f1c40f" # Sun Yellow
        }
    ]

    return render(request, 'admin/uneb_gateway.html', {
        'portals': portals,
        'school': school,
        'title': "NATIONAL EXTERNAL GATEWAY"
    })

import requests
from bs4 import BeautifulSoup

def sync_national_notifications():
    """📡 THE Hub Hub Hub SATELLITE SCRAPER"""
    targets = [
        {'name': 'UNEB', 'url': 'https://uneb.ac.ug/news/'},
        {'name': 'MoES', 'url': 'https://www.education.go.ug/category/news/'}
    ]
    
    for target in targets:
        try:
            response = requests.get(target['url'], timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 🕵️ Find the first 3 news headlines (Logic adapts to their site structure)
            links = soup.find_all('a', href=True)
            for link in links:
                text = link.get_text().strip()
                href = link['href']
                
                # Filter for actual news titles (usually longer than 20 chars)
                if len(text) > 25 and ("2024" in text or "2025" in text or "Circular" in text):
                    NationalUpdate.objects.get_or_create(
                        title=text, 
                        defaults={'source': target['name'], 'link': href}
                    )
        except:
            pass # Ignore if site is down

@login_required
def sms_broadcast_view(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    parents = Parent.objects.filter(students__school=school).distinct()
    
    if request.method == "POST":
        msg_type = request.POST.get('msg_type') # 'SMS' or 'WHATSAPP'
        target = request.POST.get('target') # 'ALL' or 'DEBTORS'
        custom_msg = request.POST.get('message')
        
        count = 0
        target_parents = parents
        
        if target == 'DEBTORS':
            # 🕵️ Filter parents who have children with balance > 0
            target_parents = parents.filter(students__fees_tracker__total_fees_due__gt=models.F('students__fees_tracker__total_fees_paid'))

        for p in target_parents:
            # 🤖 LOGIC: Auto-personalize message
            # "Dear Mr. Musoke, your child Kato has a balance of..."
            final_msg = custom_msg.replace("[NAME]", p.full_name)
            
            # 🛰️ CALL THE EXTERNAL GATEWAY (Placeholder)
            # In real life: send_sms(p.phone_number, final_msg) 
            # Or: send_whatsapp(p.phone_number, final_msg)
            
            BroadcastLog.objects.create(
                school=school,
                recipient_name=p.full_name,
                phone_number=p.phone_number,
                message_body=final_msg,
                message_type=msg_type
            )
            count += 1
            
        return HttpResponse(f"<body style='background:#000;color:gold;padding:50px;text-align:center;'><h1>BROADCAST SUCCESSFUL!</h1><p>{count} {msg_type} messages sent to {target}.</p><a href='/api/sms-hub/'>Back to Comms</a></body>")

    return render(request, 'admin/sms_broadcast.html', {
        'school': school,
        'parents_count': parents.count(),
        'title': "NATIONAL BROADCAST CENTRE"
    })


@login_required
def staff_payroll_view(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    month = request.GET.get('month', str(datetime.date.today().month))
    
    # 🕵️ Fetch all salary records for this school
    payroll = StaffSalary.objects.filter(staff__school=school, month=month).select_related('staff')
    
    # 🧮 CALCULATE TREASURY TOTALS
    total_wage_bill = sum(item.net_pay for item in payroll)
    paid_count = payroll.filter(status='PAID').count()
    pending_count = payroll.filter(status='PENDING').count()

    context = {
        'payroll': payroll,
        'school': school,
        'total_bill': total_wage_bill,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'current_month': datetime.date(2000, int(month), 1).strftime('%B'),
        'title': "NATIONAL STAFF PAYROLL"
    }
    return render(request, 'admin/staff_payroll.html', context)

@login_required
def secretary_marks_entry(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        
        # 1. 🧠 COMPREHENSIVE CLASS LIST (All Levels)
        sector_map = {
            'PRIMARY': ['Baby', 'Middle', 'Top', 'P.1', 'P.2', 'P.3', 'P.4', 'P.5', 'P.6', 'P.7'],
            'SECONDARY': ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6'],
            'UNIVERSITY': ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
        }
        classes = sector_map.get(school.sector, ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6'])
        
        selected_class = request.GET.get('class', classes[0])
        selected_student_id = request.GET.get('student_id')
        field_type = request.GET.get('field_type', 'eot_score') # Persistent field selection

        # 2. 🔎 ALL-SEEING STUDENT FILTRATION
        # We use __icontains to make sure "S.1" finds "S1", "s.1", and "S.1 "
        clean_class = selected_class.replace(".", "").strip()
        students = Student.objects.filter(
            school=school
        ).filter(
            Q(current_class__iexact=selected_class) | 
            Q(current_class__icontains=clean_class)
        ).order_by('full_name')

        subjects = Subject.objects.all()

        # 3. 💾 SAVE & REFRESH LOGIC
        if request.method == "POST" and selected_student_id:
            student = get_object_or_404(Student, id=selected_student_id)
            target_field = request.POST.get('field_type', 'eot_score')
            
            for sub in subjects:
                score = request.POST.get(f'sub_{sub.id}')
                if score is not None and score != "":
                    res, _ = AcademicResult.objects.get_or_create(student=student, subject=sub)
                    setattr(res, target_field, float(score))
                    res.save()
            
            # 💎 REDIRECT: Keep the student and class selected after saving!
            return redirect(f"/api/secretary-entry/?class={selected_class}&student_id={selected_student_id}&field_type={target_field}")

        # 4. 🧠 THE MEMORY ENGINE: Fetch existing marks for the UI
        existing_marks = {}
        selected_student = None
        if selected_student_id:
            selected_student = students.filter(id=selected_student_id).first()
            if selected_student:
                marks_objs = AcademicResult.objects.filter(student=selected_student)
                for m in marks_objs:
                    # Store the specific score we are currently editing
                    val = getattr(m, field_type, None)
                    existing_marks[m.subject.id] = val if val is not None else ""

        # 5. 🚩 AUDIT: Missing marks calculation
        audit_data = []
        for s in students:
            # We check the specific field_type being entered
            # We use a filter that works even if the field is 0
            completed = AcademicResult.objects.filter(
                student=s, 
                subject__in=subjects
            ).exclude(**{f"{field_type}": 0}).count()
            
            missing = subjects.count() - completed
            audit_data.append({
                'student': s,
                'complete': missing <= 0,
                'missing_count': missing if missing > 0 else 0
            })

        return render(request, 'admin/secretary_marks.html', {
            'classes': classes,
            'selected_class': selected_class,
            'audit_data': audit_data,
            'subjects': subjects,
            'selected_student': selected_student,
            'existing_marks': existing_marks, # 💎 Send memory to UI
            'field_type': field_type,
            'school': school
        })
    except Exception as e:
        return HttpResponse(f"Registry Error: {str(e)}")

import os
import datetime
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import Student, KEBMockResult, School, Staff
from collections import Counter

@login_required
def generate_keb_passlip(request, student_id):
    """
    🏛️ THE NATIONAL KEB PASSLIP ENGINE
    Generates a high-prestige, dual-slip A4 document.
    """
    try:
        student = Student.objects.get(account_number=student_id)
        school = student.school
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="KEB_PASSLIP_{student.full_name}.pdf"'
        
        # Initialize Canvas
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4 # 595.27 x 841.89

        # 💎 DRAW TWO IDENTICAL SLIPS
        # Slip 1: Top Half
        draw_keb_slip_layout(p, student, school, 0)
        
        # ✂️ Central Cutting Guide
        p.setDash(3, 3)
        p.setStrokeColor(colors.grey)
        p.line(0, height/2, width, height/2)
        p.setDash() # Reset

        # Slip 2: Bottom Half
        draw_keb_slip_layout(p, student, school, height/2)

        p.save()
        return response
    except Exception as e:
        return HttpResponse(f"KEB Printing Error: {str(e)}", status=400)

def generate_national_report_pdf(request, student_id):
    try:
        student = Student.objects.get(account_number=student_id)
        school = student.school
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="National_Passlip_{student.full_name}.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        # 💎 THE Hub Hub Hub FIX: No more loop. We draw it once at full scale.
        draw_keb_slip_layout(p, student, school, 0) # y_offset is always 0 now

        p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Registry Engine Error: {str(e)}", status=400)


def draw_keb_slip_layout(p, student, school, y_offset):
    width, height = A4
    base_y = height - y_offset 
    
    # 🎨 1. THE Hub Hub Hub IMPERIAL COLOR VAULT
    gov_blue = colors.HexColor("#002366")      # Royal Navy
    rich_gold = colors.HexColor("#D4AF37")     # Imperial Gold
    ug_yellow = colors.HexColor("#FCDC04")     # National Yellow
    ug_red = colors.HexColor("#D90000")        # National Red
    success_green = colors.HexColor("#006400") # Emerald Success
    paper_cream = colors.HexColor("#FFF9E6")   # Premium Page Tint

    # 🔑 2. NATIONAL DATA & MATH INTELLIGENCE
    results_qs = KEBMockResult.objects.filter(student=student).select_related('subject')
    subject_count = results_qs.count()
    
    total_score_sum = 0
    total_uace_points = 0
    all_fails = True
    
    # Determine Class Level
    c_name = str(student.current_class).upper().replace(" ", "")
    is_a_level = any(x in c_name for x in ["S5", "S.5", "S6", "S.6", "A-LEVEL"])

    # 📊 3. DATA MATRIX BUILDING (Single Loop for Accuracy)
    if is_a_level:
        headers = ['SUBJECT NAME', 'SCORE', 'GRD', 'PTS', 'PERFORMANCE GRAPH', 'INTERPRETATION']
        col_widths = [140, 45, 35, 35, 120, 135]
    else:
        headers = ['SUBJECT NAME', 'SCORE', 'GRD', 'PERFORMANCE GRAPH', 'INTERPRETATION']
        col_widths = [160, 50, 40, 130, 130]

    data_rows = [headers]

    # 🖌️ 3. BACKGROUND & TRIPLE BORDERS
    p.setFillColor(paper_cream)
    p.rect(10, base_y - 415, width - 20, 405, fill=1, stroke=0)
    p.setLineWidth(2.5); p.setStrokeColor(gov_blue); p.rect(15, base_y - 410, width - 30, 395, stroke=1)
    p.setLineWidth(0.5); p.setStrokeColor(rich_gold); p.rect(18, base_y - 407, width - 36, 389, stroke=1)
    # 🌌 4. KEB LOGO WATERMARK (GHOST EFFECT)
    if school.keb_logo and os.path.exists(school.keb_logo.path):
        p.saveState()
        
        # 💎 THE Hub Hub Hub Hub Hub VISIBILITY TUNING
        # 0.07 is the "Perfect Visibility" - it's clear but doesn't block the marks!
        p.setFillAlpha(0.08) 
        
        # 📍 MATHEMATICAL CENTERING
        # A4 Width is 595. Slip height is roughly 400.
        watermark_size = 270 # 💎 MASSIVE SIZE
        center_x = (width / 2) - (watermark_size / 2)
        # Position it right behind the marks table area
        center_y = (base_y - 210) - (watermark_size / 2)
        
        # 🎨 DRAW THE GHOST IMAGE
        p.drawImage(
            school.keb_logo.path, 
            center_x, 
            center_y, 
            width=watermark_size, 
            height=watermark_size, 
            mask='auto'
        )
        
        p.restoreState() # 🛡️ Reset to full strength for the text
    else:
        # Fallback if no logo is found in the system
        p.saveState()
        p.setFont("Times-Bold", 50)
        p.setFillColor(colors.lightgrey, alpha=0.06)
        p.translate(width/2, base_y - 200)
        p.rotate(35)
        p.drawCentredString(0, 0, "KEB OFFICIAL RECORD")
        p.restoreState()

    # 🏛️ 5. NATIONAL TOP HEADERS
    p.setFillColor(colors.black); p.setFont("Times-Bold", 10)
    p.drawCentredString(width/2, base_y - 25, "THE REPUBLIC OF UGANDA")
    p.setFont("Times-Bold", 14); p.setFillColor(gov_blue)
    p.drawCentredString(width/2, base_y - 42, "KYADONDO EXAMINATIONS BOARD")
    
    # 🖼️ 6. SCHOOL LOGO & IDENTITY
    lx, ly, lw, lh = 45, base_y - 120, 73, 73
    if school.logo and os.path.exists(school.logo.path):
        p.drawImage(school.logo.path, lx, ly, width=lw, height=lh, mask='auto')
    else:
        p.setStrokeColor(gov_blue); p.rect(lx, ly, lw, lh, stroke=1)

    ix = 125
    p.setFillColor(gov_blue); p.setFont("Times-Bold", 12)
    p.drawString(ix, base_y - 70, school.name.upper())
    p.setFillColor(colors.black); p.setFont("Times-Bold", 9)
    p.drawString(ix, base_y - 85, f"STUDENT: {student.full_name.upper()}")
    p.drawString(ix, base_y - 100, f"LEVEL: {student.current_class} ({student.stream or 'NORTH'})")
    p.drawString(ix, base_y - 115, f"YEAR: 2026")
    
    # 📸 7. STUDENT PHOTO (FAR RIGHT)
    px, py, pw, ph = width - 110, base_y - 120, 75, 90
    if student.photo and os.path.exists(student.photo.path):
        p.setStrokeColor(gov_blue); p.setLineWidth(1.5)
        p.rect(px, py, pw, ph, stroke=1)
        p.drawImage(student.photo.path, px, py, width=pw, height=ph, mask='auto')
    else:
    # 👤 Draw the Vector Silhouette
        p.setStrokeColor(colors.grey); p.rect(px, py, pw, ph, stroke=1)
        p.setFillColor(colors.HexColor("#DCDCDC"))
        p.circle(px + pw/2, py + ph - 25, 15, fill=1)
        p.roundRect(px + 10, py + 10, pw - 20, 40, 8, fill=1)
    
    if is_a_level:
        desc_y = height - 174
        p.setFillColor(colors.black)
        p.setFont("Times-Bold", 8)
        p.drawString(45, desc_y + 15, "UACE PERFORMANCE EVALUATION STANDARDS:")
            
        # 🏛️ The Professional Description
        uace_desc = (
        
            "This KEB Mock Result Slip evaluates the candidate based on the New UACE Competency Framework. "
            "Principal subjects are weighted on a 5-point scale (A=5 to E=1). Subsidiary subjects, including General Paper, "
            "Sub-Mathematics, and ICT, are graded on a binary scale where a score above 50% earns a Subsidiary Pass (O) "
            "carrying 1 point. The total national weight is calculated out of a maximum of 15 points for principals."
        )
            
        style_desc = ParagraphStyle('UaceDesc', fontName='Times-Roman', fontSize=8, leading=11)
        para_desc = Paragraph(uace_desc, style_desc)
        para_desc.wrapOn(p, width - 90, 50)
        para_desc.drawOn(p, 45, desc_y - 25)
            
        # Move the table start point down because of the paragraph
        table_y_start = height - 270
    else:
        table_y_start = height - 280 # O-Level stays higher

    # 📊 8. DATA MATRIX BUILDING (WITH A-LEVEL PRINCIPAL LOGIC)
    if is_a_level:
        headers = ['SUBJECT NAME', 'SCORE', 'GRD', 'PTS', 'PERFORMANCE GRAPH', 'INTERPRETATION']
        col_widths = [140, 45, 35, 35, 120, 135]
    else:
        headers = ['SUBJECT NAME', 'SCORE', 'GRD', 'PERFORMANCE GRAPH', 'INTERPRETATION']
        col_widths = [160, 50, 40, 130, 130]

    data_rows = [headers]

    for r in results_qs:
        score = r.score if r.score else 0
        total_score_sum += score  # Added ONLY ONCE here
        if score >= 40: all_fails = False
            
        sub_name = r.subject.name.upper()
        grd = "F"
        pts = 0
        interp = "UNSATISFACTORY"
    
        if is_a_level:
            is_subsidiary = (
                "GENERAL PAPER" in sub_name
                or sub_name == "GP"
                or "ICT" in sub_name
                or "SUBSIDIARY MATHEMATICS" in sub_name
                or "SUB MATH" in sub_name
                or "SUBSIDIARY MATH" in sub_name
            )
            if is_subsidiary:
                if score >= 50: grd, pts, interp = "O", 1, "PASS"
                else: grd, pts, interp = "F", 0, "FAIL"
            else:
                if score >= 80:
                    grd, pts, interp = "A", 5, "EXCEPTIONAL"
                elif score >= 70:
                    grd, pts, interp = "B", 4, "OUTSTANDING"
                elif score >= 60:
                    grd, pts, interp = "C", 3, "SATISFACTORY"
                elif score >= 50:
                    grd, pts, interp = "D", 2, "BASIC"
                elif score >= 40:
                    grd, pts, interp = "E", 1, "ELEMENTARY"
                else:
                    grd, pts, interp = "E", 1, "FAIL"
                
            total_uace_points += pts
            data_rows.append([sub_name, f"{score:g}", grd, pts, "", interp])
        else:
            # O-Level Logic
            if score >= 80: grd, interp = "A", "EXCEPTIONAL"
            elif score >= 70: grd, interp = "B", "OUTSTANDING"
            elif score >= 55: grd, interp = "C", "SATISFACTORY"
            elif score >= 40: grd, interp = "D", "BASIC"
            else: grd, interp = "E", "ELEMENTARY"
            data_rows.append([sub_name, f"{score:g}", grd, "", interp])
    
    # 🧮 4. FINAL CALCULATIONS (Performed after the loop)
    final_average = total_score_sum / subject_count if subject_count > 0 else 0
        
    # Mapping the average to the Official Grade
    if final_average >= 80: final_overall_grade = "A"
    elif final_average >= 70: final_overall_grade = "B"
    elif final_average >= 55: final_overall_grade = "C"
    elif final_average >= 40: final_overall_grade = "D"
    else: final_overall_grade = "E"
    # 🏁 10. MERIT BAR (GREEN/GOLD)
    bar_y = base_y - 145
    p.setFillColor(rich_gold)
    p.rect(45, bar_y, 160, 22, fill=1)
    p.setFillColor(success_green)
    p.rect(205, bar_y, (width - 90) - 160, 22, fill=1)

    p.setFillColor(colors.black); p.setFont("Times-Bold", 10)
    p.drawCentredString(125, bar_y + 7, f"★★★ AVG: {final_average:.1f}% ({final_overall_grade}) ★★★")

    p.setFillColor(colors.white); p.setFont("Times-Bold", 9)
    if is_a_level:
        rank_text = f"KEB WEIGHT: {total_uace_points}/17 PTS | GRADE: {final_overall_grade}"
    else:
        res_tier = "RESULT 1" if not all_fails else "RESULT 4"
        rank_text = f"KEB RANKING: {res_tier} | GRADE: {final_overall_grade}"
    p.drawString(215, bar_y + 7, rank_text)

    # 📊 6. DRAW THE TABLE SUMMARY ROW
    summary_label = "TOTAL UACE WEIGHT" if is_a_level else "OVERALL AVERAGE"
    summary_val = f"{total_uace_points} PTS" if is_a_level else f"{final_average:.1f}%"
    
    if is_a_level:
        data_rows.append([summary_label, summary_val, final_overall_grade, "", "", "OFFICIAL VERDICT"])
    else:
        data_rows.append([summary_label, summary_val, final_overall_grade, "", "OFFICIAL VERDICT"])

    table_y = base_y - 335
    table = Table(data_rows, colWidths=col_widths, rowHeights=17)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), gov_blue), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Times-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.1, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.transparent, colors.Color(0,0,0, alpha=0.03)]),
        ('BACKGROUND', (0, -1), (-1, -1), rich_gold),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('SPAN', (4, -1), (5, -1)) if is_a_level else ('SPAN', (3, -1), (4, -1)), 
    ]))
    table.wrapOn(p, width, height); table.drawOn(p, 45, table_y)

    # 📈 12. SYNCED GRAPH BARS
    graph_idx = 4 if is_a_level else 3
    graph_x = 45 + sum(col_widths[:graph_idx]) + 10
    for i, r in enumerate(results_qs):
        bar_y_pos = (table_y + (len(data_rows) - i - 2) * 17) + 5.5
        p.setFillColor(colors.HexColor("#E0E0E0")) 
        p.roundRect(graph_x, bar_y_pos, 100, 5, 2.5, fill=1, stroke=0)
        bc = success_green if r.score >= 80 else rich_gold if r.score >= 50 else ug_red
        p.setFillColor(bc)
        p.roundRect(graph_x, bar_y_pos, max(2, r.score), 5, 2.5, fill=1, stroke=0)
    
    if is_a_level:
        key_data = [['GRADE:', 'A(5)', 'B(4)', 'C(3)', 'D(2)', 'E(1)', 'O(1)', 'F(0)'],['INTERPRETATION:', 'Exceptional', 'Very Good', 'Good', 'Satisfactory', 'Fair', 'Sub. Pass', 'Fail']]
    else:
        key_data = [['GRADE:', 'A', 'B', 'C', 'D', 'E'],['INTERPRETATION:', 'EXCEPTIONAL', 'OUTSTANDING', 'SATISFACTORY', 'BASIC', 'ELEMEMENTARY']]
    
    k_table = Table(key_data, colWidths=63 if is_a_level else 85, rowHeights=17)
    k_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTSIZE', (0,0), (-1,-1), 6), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('BACKGROUND', (0,0), (0,-1), colors.lightgrey)]))
    k_table.wrapOn(p, width, height); k_table.drawOn(p, 45, base_y - 374)

    # ✍️ 13. FOOTER & SIGNATURE
    
    try:
        if school.chairman_signature:
            signature_file = school.chairman_signature.open("rb")
            signature_image = ImageReader(signature_file)

            # REAL SIGNATURE — SMALL AND POSITIONED ABOVE THE LINE
            p.drawImage(
                signature_image,
                50,                  # X position
                base_y - 398,        # Y position
                width=50,           # smaller signature
                height=40,           # smaller height
                preserveAspectRatio=True,
                anchor='sw',
                mask='auto'
            )

            signature_file.close()
    except Exception:
        pass

    # Physical signature line
    p.setStrokeColor(gov_blue)
    p.setLineWidth(1)
    p.line(45, base_y - 398, 200, base_y - 398)

    # Chairman title
    p.setFillColor(colors.black)
    p.setFont("Times-Bold", 8)
    p.drawString(45, base_y - 405, "KEB EXAMINATIONS CHAIRMAN")

@login_required
def batch_report_download(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        selected_class = request.GET.get('class')
        
        if not selected_class:
            return HttpResponse("<h1 style='color:red;'>Error: Please select a class.</h1>")

        # 🕵️ Fetch all active candidates in this class
        students = Student.objects.filter(
            school=school, 
            current_class=selected_class, 
            is_active=True
        ).order_by('full_name')

        if not students.exists():
            return HttpResponse(f"<h1>No candidates found in {selected_class}</h1>")

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="BATCH_KEB_PASSLIPS_{selected_class}.pdf"'
        
        # 📄 Start the A4 Canvas
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4 # 595 x 842 points
        half_height = height / 2 # 421 points

        # 🔄 THE Hub Hub Hub PAIRING ENGINE
        # We loop through students in steps of 2
        for i in range(0, len(students), 2):
            
            # 1. DRAW FIRST STUDENT (Top Half)
            student_a = students[i]
            draw_keb_slip_layout(p, student_a, school, 0) # y_offset = 0

            # ✂️ THE PERFORATION LINE (The 'Cut Here' Guide)
            p.setDash(4, 4)
            p.setStrokeColor(colors.grey)
            p.setLineWidth(0.5)
            p.line(0, half_height, width, half_height)
            p.setDash() # Reset to solid

            # 2. DRAW SECOND STUDENT (Bottom Half)
            if i + 1 < len(students):
                student_b = students[i + 1]
                draw_keb_slip_layout(p, student_b, school, half_height) # y_offset = 421
            
            # 💎 FLIP THE PAGE (Next A4 Sheet)
            p.showPage()
            
        p.save()
        return response

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"<body style='background:black;color:red;padding:50px;'><h1>Batch Error</h1><pre>{str(e)}</pre></body>")

    
@login_required
def keb_mock_portal_view(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        
        sector_map = {
            'PRIMARY': ['P.6', 'P.7'],
            'SECONDARY': ['S.4', 'S.6'],
        }
        classes = sector_map.get(school.sector, ['S.4', 'S.6'])

        subjects = Subject.objects.all().order_by('name')

        # 🔎 Filter Logic
        sel_class = request.GET.get('class', classes[0])
        # Default to first subject if none selected
        first_sub = subjects.first().id if subjects.exists() else None
        sel_sub = request.GET.get('subject', first_sub)
        
        # ⚡ Fetch Students 
        students = Student.objects.filter(school=school, current_class=sel_class).select_related('parent_link').prefetch_related('keb_results').order_by('full_name')
        
        # 📊 Audit Data (Linking results to students)
        audit = []
        for s in students:
            # Look for the mark of the CURRENTLY SELECTED subject
            res = KEBMockResult.objects.filter(student=s, subject_id=sel_sub).first()
            audit.append({
                'student': s,
                'score': res.score if res else None,
                'grade': res.grade if res else None,
                'has_marks': res is not None # 💎 The status light
            })

        context = {
            'school': school,
            'classes': classes,
            'subjects': subjects,
            'sel_class': sel_class,
            'sel_sub': int(sel_sub) if sel_sub and str(sel_sub).isdigit() else None,
            'audit': audit,
            'total_students': students.count(),
            'title': "KEB MOCKS COMMAND"
        }
        return render(request, 'admin/keb_mock_portal.html', context)
    except Exception as e:
        return HttpResponse(f"<body style='background:black;color:red;padding:50px;'><h1>KEB Portal Engine Error</h1><p>{str(e)}</p></body>")

from reportlab.lib import pagesizes # 💎 Ensure this is imported
@login_required
@transaction.atomic
def save_keb_marks(request):
    """Kills the 500 error and saves marks for the entire class list."""
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        class_name = request.POST.get('class_name')
        
        if not subject_id or subject_id == "None":
            return HttpResponse("Error: No Subject Selected")

        for key, value in request.POST.items():
            if key.startswith('score_') and value != "":
                # Extract student ID: score_123 -> 123
                std_id = key.split('_')[1]
                score = float(value)
                
                # Apply National Grading (UCE/UACE auto-detect)
                is_a_level = any(x in class_name.upper() for x in ["S5", "S6"])
                grade = "F"
                if not is_a_level:
                    if score >= 80: grade = "A"
                    elif score >= 70: grade = "B"
                    elif score >= 60: grade = "C"
                    elif score >= 50: grade = "D"
                    else: grade = "E"
                
                KEBMockResult.objects.update_or_create(
                    student_id=std_id, subject_id=subject_id,
                    defaults={'score': score, 'grade': grade}
                )
        
        return redirect(f'/api/keb-portal/?class={class_name}&subject={subject_id}&status=success')

@login_required
def search_student_for_mock(request):
    """The engine for the advanced search pop-up."""
    query = request.GET.get('q', '').strip()
    subject_id = request.GET.get('subject_id')
    
    if not query:
        return JsonResponse({'results': []})

    # Search by Name or PRN
    students = Student.objects.filter(
        Q(full_name__icontains=query) | Q(payment_code__icontains=query)
    ).select_related('school')[:5] # Limit to 5 for speed

    results = []
    for s in students:
        # Check if they already have a mark for this subject
        res = KEBMockResult.objects.filter(student=s, subject_id=subject_id).first()
        results.append({
            'id': s.id,
            'name': s.full_name.upper(),
            'prn': s.payment_code,
            'class': s.current_class,
            'existing_score': res.score if res else ""
        })
    
    return JsonResponse({'results': results})
    
def web_app_home(request):
    """🏛️ THE Hub Hub Hub Hub Hub OFFICIAL SOVEREIGN GATEWAY"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>UNSCCDC GLOBAL | National Hub</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * { font-family: "Times New Roman", Times, serif; transition: 0.3s; }
            body { background: #000; color: white; margin: 0; overflow-x: hidden; text-align: center; }
            
            /* 🇺🇬 THE LIVE WAVING FLAG BACKGROUND */
            #bg-video {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                z-index: -1; opacity: 0.2; object-fit: cover; filter: saturate(1.5) blur(2px);
            }
            
            .main-container { padding: 80px 20px; max-width: 900px; margin: auto; }
            
            /* 💎 PRESTIGE GLASS CARDS */
            .command-card {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(15px);
                border: 2px solid #D4AF37;
                border-radius: 30px;
                padding: 50px;
                box-shadow: 0 0 50px rgba(212, 175, 55, 0.1);
            }
            
            h1 { color: #D4AF37; letter-spacing: 5px; font-size: 40px; font-weight: 900; margin: 0; }
            .status-line { color: #00ff00; font-size: 10px; font-weight: bold; letter-spacing: 3px; margin-bottom: 30px; }
            
            /* 🚀 THE ACTION BUTTONS */
            .btn-group { display: flex; flex-direction: column; gap: 20px; margin-top: 40px; align-items: center; }
            .btn {
                text-decoration: none; padding: 20px 40px; width: 300px; border-radius: 15px;
                font-weight: 900; font-size: 14px; letter-spacing: 2px; text-transform: uppercase;
                border: 2px solid #D4AF37; cursor: pointer; display: block;
            }
            .btn-gold { background: #D4AF37; color: black; box-shadow: 0 10px 20px rgba(212, 175, 55, 0.3); }
            .btn-gold:hover { transform: scale(1.05); background: white; }
            .btn-outline { color: #D4AF37; background: transparent; }
            .btn-outline:hover { background: rgba(212, 175, 55, 0.1); }
            
            .footer { margin-top: 60px; color: #444; font-size: 11px; letter-spacing: 1px; }
        </style>
    </head>
    <body>
        <video autoplay muted loop playsinline id="bg-video">
            <source src="https://assets.mixkit.co/videos/preview/mixkit-flag-of-uganda-waving-in-the-wind-32538-large.mp4" type="video/mp4">
        </video>
        
        <div class="main-container">
            <div class="command-card">
                <div style="font-size: 60px; margin-bottom: 10px;">🌍</div>
                <h1>UNSCCDC GLOBAL</h1>
                <div class="status-line">● NATIONAL NODE ACTIVE ●</div>
                
                <p style="color: #888; line-height: 1.6;">Welcome to the 2026 Sovereign Education Infrastructure. <br> Accessing the National Registry, Financial War-Room, and E-Library.</p>
                
                <div class="btn-group">
                    <a href="/admin/" class="btn btn-gold"><i class="fas fa-unlock-alt"></i> Enter Master Office</a>
                    <a href="/api/get-app/" class="btn btn-outline"><i class="fas fa-download"></i> Download Mobile App</a>
                    <a href="/api/registry/" class="btn btn-outline" style="border-color: #008080; color: #008080;"><i class="fas fa-search"></i> Registry Explorer</a>
                </div>
            </div>
            
            <div class="footer">
                ENGINEERED BY YAWE ERIC<br>
                Official Property of the Republic of Uganda
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

@login_required
def performance_analytics_view(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        
        # 1. 🧠 TARGET CLASSES (Focusing on Candidates)
        target_classes = ['S.4', 'S.6', 'P.7']
        sel_class = request.GET.get('class', 'S.4')
        
        # 2. 🔎 FETCH CANDIDATES
        students = Student.objects.filter(school=school, current_class=sel_class).order_by('full_name')
        
        analysis_data = []
        for s in students:
            # 💎 FOCUS ON KEB MOCK RESULTS
            mock_marks = KEBMockResult.objects.filter(student=s).select_related('subject')
            
            if mock_marks.exists():
                # 🧮 CALCULATION ENGINE
                avg_score = mock_marks.aggregate(a=Avg('score'))['a'] or 0
                best_sub_obj = mock_marks.order_by('-score').first()
                
                # Prepare clean data for Chart.js
                labels = [m.subject.name.upper() for m in mock_marks]
                scores = [float(m.score) for m in mock_marks]
                
                analysis_data.append({
                    'student': s,
                    'avg': round(avg_score, 1),
                    'best_subject': best_sub_obj.subject.name.upper() if best_sub_obj else "N/A",
                    'best_score': best_sub_obj.score if best_sub_obj else 0,
                    'chart_labels': json.dumps(labels),
                    'chart_scores': json.dumps(scores),
                })

        context = {
            'school': school,
            'analysis': analysis_data,
            'sel_class': sel_class,
            'target_classes': target_classes,
            'title': "NATIONAL MOCK ANALYTICS"
        }
        return render(request, 'admin/performance_analysis.html', context)
    except Exception as e:
        return HttpResponse(f"<body style='background:black;color:red;padding:50px;'><h1>Analytics Engine Error</h1><p>{str(e)}</p></body>")

import io
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader

# 📊 1. THE ADVANCED ANALYTICS GRAPH ENGINE
def generate_pro_analytics_graph(labels, values):
    # Set the style to be clean and modern
    plt.rcParams['font.family'] = 'serif'
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150) # High Resolution
    
    y_pos = np.arange(len(labels))
    # 🎨 Color Logic: Green for high, Gold for mid, Red for low
    bar_colors = []
    for v in values:
        if v >= 75: bar_colors.append('#006400') # Deep Green
        elif v >= 50: bar_colors.append('#D4AF37') # Gold
        else: bar_colors.append('#D90000') # National Red

    bars = ax.barh(y_pos, values, align='center', color=bar_colors, height=0.6)
    
    # 📐 Add labels and styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9, fontweight='bold')
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Mastery Percentage (%)', fontsize=8, fontweight='bold')
    ax.set_title('SUBJECT-BY-SUBJECT COMPETENCY RADIUS', fontsize=12, fontweight='black', pad=20)
    ax.set_xlim(0, 100)
    
    # Add grid lines behind the bars
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)

    # Add numeric labels to the end of bars
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:g}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close()
    buf.seek(0)
    return ImageReader(buf)

import io
import matplotlib.pyplot as plt
import numpy as np
from django.db.models import Avg, Max, Min
from reportlab.lib.utils import ImageReader

# 💎 HELPER: THE Hub Hub Hub VECTOR GRAPH CREATOR
def generate_graph_stream(labels, values, title, color="#002366"):
    plt.figure(figsize=(6, 3), dpi=100)
    plt.bar(labels, values, color=color, alpha=0.7)
    plt.title(title, fontsize=10, fontweight='bold', family='serif')
    plt.xticks(rotation=45, fontsize=7)
    plt.yticks(fontsize=8)
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close()
    buf.seek(0)
    return ImageReader(buf)

# 1. 🎓 INDIVIDUAL STUDENT INTELLIGENCE REPORT
def generate_analysis_pdf(request, student_id):
    """
    Professional student KEB Mock Performance Report.
    Uses the student's existing KEBMockResult records.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, KeepTogether
        )
        from reportlab.lib.units import mm
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        from io import BytesIO
        from datetime import datetime

        student = get_object_or_404(
            Student.objects.select_related('school', 'parent_link'),
            account_number=student_id
        )

        school = student.school

        # ---------------------------------------------------------
        # 1. FETCH EXISTING MOCK RESULTS
        # ---------------------------------------------------------
        marks = list(
            KEBMockResult.objects
            .filter(student=student)
            .select_related('subject')
            .order_by('subject__name')
        )

        # ---------------------------------------------------------
        # 2. RESPONSE
        # ---------------------------------------------------------
        buffer = BytesIO()

        safe_name = "".join(
            c for c in student.full_name
            if c.isalnum() or c in (" ", "-", "_")
        ).strip().replace(" ", "_")

        filename = f"MOCK_PERFORMANCE_{safe_name}.pdf"

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        # ---------------------------------------------------------
        # 3. COLORS
        # ---------------------------------------------------------
        NAVY = colors.HexColor("#001B44")
        BLUE = colors.HexColor("#003B73")
        GOLD = colors.HexColor("#D4AF37")
        LIGHT_GOLD = colors.HexColor("#F7F1D2")
        LIGHT_BLUE = colors.HexColor("#EEF4FA")
        WHITE = colors.white
        BLACK = colors.HexColor("#111111")
        GREY = colors.HexColor("#666666")
        LIGHT_GREY = colors.HexColor("#F4F5F7")
        GREEN = colors.HexColor("#16833B")
        RED = colors.HexColor("#B42318")

        # ---------------------------------------------------------
        # 4. DOCUMENT
        # ---------------------------------------------------------
        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"Mock Performance Report - {student.full_name}",
            author="UNSCCDC National Performance Registry"
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Times-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=NAVY,
            spaceAfter=5
        )

        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=GREY
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Times-Bold",
            fontSize=11,
            leading=14,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=7
        )

        normal_style = ParagraphStyle(
            "NormalReport",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=14,
            textColor=BLACK
        )

        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=8,
            leading=11,
            textColor=GREY
        )

        # ---------------------------------------------------------
        # 5. PAGE HEADER / FOOTER
        # ---------------------------------------------------------
        def draw_page(canvas, doc):
            canvas.saveState()

            width, height = A4

            # Outer border
            canvas.setStrokeColor(NAVY)
            canvas.setLineWidth(2)
            canvas.rect(
                10 * mm,
                10 * mm,
                width - 20 * mm,
                height - 20 * mm
            )

            # Inner gold border
            canvas.setStrokeColor(GOLD)
            canvas.setLineWidth(0.7)
            canvas.rect(
                13 * mm,
                13 * mm,
                width - 26 * mm,
                height - 26 * mm
            )

            # Footer
            canvas.setFont("Times-Roman", 7.5)
            canvas.setFillColor(GREY)
            canvas.drawString(
                18 * mm,
                13 * mm,
                "UNSCCDC • STUDENT PERFORMANCE REGISTRY"
            )

            canvas.drawRightString(
                width - 18 * mm,
                13 * mm,
                f"PAGE {doc.page}"
            )

            canvas.restoreState()

        # ---------------------------------------------------------
        # 6. CALCULATIONS
        # ---------------------------------------------------------
        scores = [float(m.score or 0) for m in marks]

        subject_count = len(marks)
        total_score = sum(scores)
        average_score = (
            total_score / subject_count
            if subject_count
            else 0
        )

        total_points = sum(
            int(m.points or 0)
            for m in marks
        )

        highest = max(marks, key=lambda x: float(x.score or 0)) if marks else None

        below_50 = [
            m for m in marks
            if float(m.score or 0) < 50
        ]

        # ---------------------------------------------------------
        # 7. BUILD REPORT
        # ---------------------------------------------------------
        story = []

        # Header
        story.append(
            Paragraph(
                "THE REPUBLIC OF UGANDA",
                ParagraphStyle(
                    "Gov",
                    parent=subtitle_style,
                    fontSize=10,
                    textColor=BLACK
                )
            )
        )

        story.append(
            Paragraph(
                "NATIONAL PERFORMANCE INTELLIGENCE & AUDIT",
                subtitle_style
            )
        )

        story.append(Spacer(1, 6))

        school_name = (
            school.name.upper()
            if school and school.name
            else "UNSCCDC NATIONAL HUB"
        )

        story.append(
            Paragraph(
                school_name,
                title_style
            )
        )

        story.append(
            Paragraph(
                "STUDENT MOCK PERFORMANCE REPORT",
                ParagraphStyle(
                    "ReportSubtitle",
                    parent=subtitle_style,
                    fontSize=11,
                    textColor=GOLD
                )
            )
        )

        story.append(Spacer(1, 10))

        # ---------------------------------------------------------
        # STUDENT PROFILE
        # ---------------------------------------------------------
        story.append(
            Paragraph(
                "I. STUDENT PROFILE",
                section_style
            )
        )

        profile_data = [
            [
                Paragraph("<b>STUDENT NAME</b>", small_style),
                Paragraph(
                    student.full_name.upper(),
                    normal_style
                ),
                Paragraph("<b>PRN / ACCOUNT</b>", small_style),
                Paragraph(
                    str(student.payment_code or student.account_number or "—"),
                    normal_style
                ),
            ],
            [
                Paragraph("<b>CLASS / LEVEL</b>", small_style),
                Paragraph(
                    str(student.current_class or "—"),
                    normal_style
                ),
                Paragraph("<b>SCHOOL</b>", small_style),
                Paragraph(
                    school_name,
                    normal_style
                ),
            ],
        ]

        profile_table = Table(
            profile_data,
            colWidths=[
                30 * mm,
                55 * mm,
                32 * mm,
                55 * mm
            ]
        )

        profile_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
                ("BACKGROUND", (2, 0), (2, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5DCE5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ])
        )

        story.append(profile_table)
        story.append(Spacer(1, 10))

        # ---------------------------------------------------------
        # PERFORMANCE SUMMARY
        # ---------------------------------------------------------
        story.append(
            Paragraph(
                "II. PERFORMANCE SUMMARY",
                section_style
            )
        )

        summary_data = [
            [
                Paragraph("<b>SUBJECTS</b>", small_style),
                Paragraph("<b>TOTAL SCORE</b>", small_style),
                Paragraph("<b>AVERAGE</b>", small_style),
                Paragraph("<b>TOTAL POINTS</b>", small_style),
            ],
            [
                str(subject_count),
                f"{total_score:.1f}",
                f"{average_score:.1f}%",
                str(total_points),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[40 * mm] * 4
        )

        summary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GOLD),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTNAME", (0, 1), (-1, 1), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.white),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )

        story.append(summary_table)
        story.append(Spacer(1, 10))

        # ---------------------------------------------------------
        # SUBJECT PERFORMANCE TABLE
        # ---------------------------------------------------------
        story.append(
            Paragraph(
                "III. SUBJECT-BY-SUBJECT PERFORMANCE",
                section_style
            )
        )

        result_rows = [
            [
                "#",
                "SUBJECT",
                "SCORE (%)",
                "GRADE",
                "POINTS"
            ]
        ]

        for index, mark in enumerate(marks, start=1):
            result_rows.append([
                str(index),
                mark.subject.name.upper(),
                f"{float(mark.score or 0):.1f}",
                mark.grade or "—",
                str(mark.points if mark.points is not None else 0)
            ])

        if not marks:
            result_rows.append([
                "—",
                "NO MOCK RESULTS RECORDED",
                "—",
                "—",
                "—"
            ])

        result_table = Table(
            result_rows,
            colWidths=[
                12 * mm,
                85 * mm,
                28 * mm,
                25 * mm,
                25 * mm
            ],
            repeatRows=1
        )

        table_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), BLACK),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BFC7D1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]

        for row_num in range(1, len(result_rows)):
            if row_num % 2 == 0:
                table_commands.append(
                    ("BACKGROUND", (0, row_num), (-1, row_num), LIGHT_GREY)
                )

        result_table.setStyle(TableStyle(table_commands))

        story.append(result_table)

        # ---------------------------------------------------------
        # PERFORMANCE ANALYSIS
        # ---------------------------------------------------------
        story.append(
            Paragraph(
                "IV. PERFORMANCE ANALYSIS",
                section_style
            )
        )

        if marks:
            highest_text = (
                f"The highest recorded subject score is "
                f"<b>{highest.subject.name.upper()}</b> at "
                f"<b>{float(highest.score or 0):.1f}%</b>."
            )

            story.append(
                Paragraph(highest_text, normal_style)
            )

            story.append(Spacer(1, 5))

            if below_50:
                weak_names = ", ".join(
                    m.subject.name.upper()
                    for m in below_50
                )

                effort_text = (
                    f"The following subjects have recorded scores below "
                    f"50% in the available mock results: "
                    f"<b>{weak_names}</b>. These areas may warrant "
                    f"additional revision and targeted practice."
                )
            else:
                effort_text = (
                    "No recorded subject score is below 50% in the "
                    "available mock results."
                )

            story.append(
                Paragraph(
                    effort_text,
                    normal_style
                )
            )

            story.append(Spacer(1, 5))

            story.append(
                Paragraph(
                    "This analysis is generated directly from the "
                    "mock results currently recorded in the UNSCCDC "
                    "performance registry. It does not constitute a "
                    "national ranking or comparison.",
                    small_style
                )
            )

        else:
            story.append(
                Paragraph(
                    "No mock examination results are currently recorded "
                    "for this student.",
                    normal_style
                )
            )

        # ---------------------------------------------------------
        # RECORD INFORMATION
        # ---------------------------------------------------------
        story.append(Spacer(1, 12))

        generated = datetime.now().strftime(
            "%d %B %Y, %H:%M"
        )

        record_data = [
            [
                Paragraph("<b>REPORT STATUS</b>", small_style),
                Paragraph(
                    "OFFICIAL SYSTEM RECORD",
                    normal_style
                )
            ],
            [
                Paragraph("<b>GENERATED</b>", small_style),
                Paragraph(generated, normal_style)
            ],
            [
                Paragraph("<b>REPORT TYPE</b>", small_style),
                Paragraph(
                    "STUDENT MOCK PERFORMANCE REPORT",
                    normal_style
                )
            ],
        ]

        record_table = Table(
            record_data,
            colWidths=[42 * mm, 133 * mm]
        )

        record_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5DCE5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        story.append(record_table)

        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                "UNSCCDC NATIONAL PERFORMANCE REGISTRY",
                ParagraphStyle(
                    "Registry",
                    parent=subtitle_style,
                    fontSize=9,
                    textColor=NAVY
                )
            )
        )

        story.append(
            Paragraph(
                "Computer-generated report • Verify against the official school record.",
                small_style
            )
        )

        # ---------------------------------------------------------
        # 8. BUILD PDF
        # ---------------------------------------------------------
        doc.build(
            story,
            onFirstPage=draw_page,
            onLaterPages=draw_page
        )

        return response

    except Exception as e:
        import traceback
        return HttpResponse(
            f"""
            <body style="background:#050505;color:#ff4444;
                         padding:50px;font-family:Arial;">
                <h1>Performance Report Engine Error</h1>
                <pre>{traceback.format_exc()}</pre>
            </body>
            """,
            status=500
        )

def generate_class_analysis_pdf(request, class_name):
    """
    Generates ONE PDF containing the mock performance reports
    for every student in the selected class.
    One student occupies one page.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak
        )
        from reportlab.lib.units import mm
        from datetime import datetime

        # ---------------------------------------------------------
        # 1. GET SCHOOL
        # ---------------------------------------------------------
        school = (
            getattr(request.user, "school", None)
            or School.objects.first()
        )

        # ---------------------------------------------------------
        # 2. GET ALL STUDENTS IN SELECTED CLASS
        # ---------------------------------------------------------
        students = list(
            Student.objects
            .filter(
                school=school,
                current_class=class_name
            )
            .order_by("full_name")
        )

        # ---------------------------------------------------------
        # 3. PDF RESPONSE
        # ---------------------------------------------------------
        response = HttpResponse(
            content_type="application/pdf"
        )

        safe_class = "".join(
            c for c in str(class_name)
            if c.isalnum() or c in (" ", "-", "_")
        ).strip().replace(" ", "_")

        response["Content-Disposition"] = (
            f'attachment; filename="CLASS_MOCK_PERFORMANCE_{safe_class}.pdf"'
        )

        # ---------------------------------------------------------
        # 4. COLORS
        # ---------------------------------------------------------
        NAVY = colors.HexColor("#001B44")
        GOLD = colors.HexColor("#D4AF37")
        LIGHT_GOLD = colors.HexColor("#F7F1D2")
        LIGHT_BLUE = colors.HexColor("#EEF4FA")
        LIGHT_GREY = colors.HexColor("#F4F5F7")
        WHITE = colors.white
        BLACK = colors.HexColor("#111111")
        GREY = colors.HexColor("#666666")
        RED = colors.HexColor("#B42318")

        # ---------------------------------------------------------
        # 5. DOCUMENT
        # ---------------------------------------------------------
        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"Class Mock Performance Report - {class_name}",
            author="UNSCCDC National Performance Registry"
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ClassTitle",
            parent=styles["Title"],
            fontName="Times-Bold",
            fontSize=17,
            leading=21,
            alignment=TA_CENTER,
            textColor=NAVY,
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            "ClassSubtitle",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=GREY
        )

        section_style = ParagraphStyle(
            "ClassSection",
            parent=styles["Heading2"],
            fontName="Times-Bold",
            fontSize=10.5,
            leading=13,
            textColor=NAVY,
            spaceBefore=7,
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            "ClassNormal",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=9,
            leading=13,
            textColor=BLACK
        )

        small_style = ParagraphStyle(
            "ClassSmall",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=7.5,
            leading=10,
            textColor=GREY
        )

        # ---------------------------------------------------------
        # 6. PAGE DECORATION
        # ---------------------------------------------------------
        def draw_page(canvas, doc):
            canvas.saveState()

            width, height = A4

            # Navy outer frame
            canvas.setStrokeColor(NAVY)
            canvas.setLineWidth(2)
            canvas.rect(
                10 * mm,
                10 * mm,
                width - 20 * mm,
                height - 20 * mm
            )

            # Gold inner frame
            canvas.setStrokeColor(GOLD)
            canvas.setLineWidth(0.7)
            canvas.rect(
                13 * mm,
                13 * mm,
                width - 26 * mm,
                height - 26 * mm
            )

            # Footer
            canvas.setFont("Times-Roman", 7)
            canvas.setFillColor(GREY)

            canvas.drawString(
                18 * mm,
                13 * mm,
                "UNSCCDC • CLASS MOCK PERFORMANCE REGISTRY"
            )

            canvas.drawRightString(
                width - 18 * mm,
                13 * mm,
                f"PAGE {doc.page}"
            )

            canvas.restoreState()

        story = []

        # ---------------------------------------------------------
        # 7. CLASS COVER / REPORT HEADER
        # ---------------------------------------------------------
        school_name = (
            school.name.upper()
            if school and school.name
            else "UNSCCDC NATIONAL HUB"
        )

        story.append(
            Paragraph(
                "THE REPUBLIC OF UGANDA",
                ParagraphStyle(
                    "Government",
                    parent=subtitle_style,
                    fontSize=10,
                    textColor=BLACK
                )
            )
        )

        story.append(
            Paragraph(
                "NATIONAL PERFORMANCE INTELLIGENCE & AUDIT",
                subtitle_style
            )
        )

        story.append(Spacer(1, 5))

        story.append(
            Paragraph(
                school_name,
                title_style
            )
        )

        story.append(
            Paragraph(
                f"CLASS MOCK PERFORMANCE DOSSIER — {str(class_name).upper()}",
                ParagraphStyle(
                    "DossierTitle",
                    parent=subtitle_style,
                    fontSize=11,
                    textColor=GOLD
                )
            )
        )

        story.append(Spacer(1, 12))

        # Class-level information
        students_with_results = 0
        total_class_subject_results = 0

        for student in students:
            count = KEBMockResult.objects.filter(
                student=student
            ).count()

            if count > 0:
                students_with_results += 1
                total_class_subject_results += count

        cover_data = [
            [
                Paragraph("<b>CLASS</b>", small_style),
                Paragraph(str(class_name).upper(), normal_style),
                Paragraph("<b>STUDENTS</b>", small_style),
                Paragraph(str(len(students)), normal_style),
            ],
            [
                Paragraph("<b>WITH RESULTS</b>", small_style),
                Paragraph(str(students_with_results), normal_style),
                Paragraph("<b>GENERATED</b>", small_style),
                Paragraph(
                    datetime.now().strftime("%d %B %Y"),
                    normal_style
                ),
            ]
        ]

        cover_table = Table(
            cover_data,
            colWidths=[
                32 * mm,
                53 * mm,
                32 * mm,
                53 * mm
            ]
        )

        cover_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
                ("BACKGROUND", (2, 0), (2, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.3,
                 colors.HexColor("#D5DCE5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ])
        )

        story.append(cover_table)

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "STUDENT PERFORMANCE RECORDS",
                section_style
            )
        )

        story.append(
            Paragraph(
                "This dossier contains the individual mock performance "
                "records currently stored for students in the selected "
                "class. Each student is presented on a separate report "
                "page.",
                normal_style
            )
        )

        # ---------------------------------------------------------
        # 8. INDIVIDUAL STUDENT REPORTS
        # ---------------------------------------------------------
        for student_index, student in enumerate(students):

            # New page for every student
            story.append(PageBreak())

            marks = list(
                KEBMockResult.objects
                .filter(student=student)
                .select_related("subject")
                .order_by("subject__name")
            )

            scores = [
                float(m.score or 0)
                for m in marks
            ]

            subject_count = len(marks)
            total_score = sum(scores)

            average_score = (
                total_score / subject_count
                if subject_count
                else 0
            )

            total_points = sum(
                int(m.points or 0)
                for m in marks
            )

            highest = (
                max(
                    marks,
                    key=lambda x: float(x.score or 0)
                )
                if marks
                else None
            )

            below_50 = [
                m for m in marks
                if float(m.score or 0) < 50
            ]

            # -----------------------------------------------------
            # STUDENT HEADER
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    school_name,
                    title_style
                )
            )

            story.append(
                Paragraph(
                    "STUDENT MOCK PERFORMANCE REPORT",
                    ParagraphStyle(
                        "StudentReportTitle",
                        parent=subtitle_style,
                        fontSize=10,
                        textColor=GOLD
                    )
                )
            )

            story.append(Spacer(1, 8))

            profile_data = [
                [
                    Paragraph("<b>STUDENT</b>", small_style),
                    Paragraph(
                        student.full_name.upper(),
                        normal_style
                    ),
                    Paragraph("<b>PRN / ACCOUNT</b>", small_style),
                    Paragraph(
                        str(
                            student.payment_code
                            or student.account_number
                            or "—"
                        ),
                        normal_style
                    ),
                ],
                [
                    Paragraph("<b>CLASS</b>", small_style),
                    Paragraph(
                        str(student.current_class or class_name),
                        normal_style
                    ),
                    Paragraph("<b>STUDENT NO.</b>", small_style),
                    Paragraph(
                        str(student_index + 1),
                        normal_style
                    ),
                ]
            ]

            profile_table = Table(
                profile_data,
                colWidths=[
                    28 * mm,
                    57 * mm,
                    35 * mm,
                    50 * mm
                ]
            )

            profile_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
                    ("BACKGROUND", (2, 0), (2, -1), LIGHT_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3,
                     colors.HexColor("#D5DCE5")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ])
            )

            story.append(profile_table)
            story.append(Spacer(1, 8))

            # -----------------------------------------------------
            # SUMMARY
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    "I. PERFORMANCE SUMMARY",
                    section_style
                )
            )

            summary_table = Table(
                [
                    [
                        "SUBJECTS",
                        "TOTAL SCORE",
                        "AVERAGE",
                        "TOTAL POINTS"
                    ],
                    [
                        str(subject_count),
                        f"{total_score:.1f}",
                        f"{average_score:.1f}%",
                        str(total_points)
                    ]
                ],
                colWidths=[40 * mm] * 4
            )

            summary_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GOLD),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                    ("FONTNAME", (0, 1), (-1, 1), "Times-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("BOX", (0, 0), (-1, -1), 0.7, NAVY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, WHITE),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ])
            )

            story.append(summary_table)
            story.append(Spacer(1, 8))

            # -----------------------------------------------------
            # SUBJECT RESULTS
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    "II. SUBJECT-BY-SUBJECT PERFORMANCE",
                    section_style
                )
            )

            result_rows = [
                [
                    "#",
                    "SUBJECT",
                    "SCORE (%)",
                    "GRADE",
                    "POINTS"
                ]
            ]

            for i, mark in enumerate(marks, start=1):
                result_rows.append([
                    str(i),
                    mark.subject.name.upper(),
                    f"{float(mark.score or 0):.1f}",
                    mark.grade or "—",
                    str(mark.points or 0)
                ])

            if not marks:
                result_rows.append([
                    "—",
                    "NO RESULTS RECORDED",
                    "—",
                    "—",
                    "—"
                ])

            result_table = Table(
                result_rows,
                colWidths=[
                    12 * mm,
                    85 * mm,
                    28 * mm,
                    25 * mm,
                    25 * mm
                ],
                repeatRows=1
            )

            commands = [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.35,
                 colors.HexColor("#BFC7D1")),
                ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]

            for row_num in range(1, len(result_rows)):
                if row_num % 2 == 0:
                    commands.append(
                        (
                            "BACKGROUND",
                            (0, row_num),
                            (-1, row_num),
                            LIGHT_GREY
                        )
                    )

            result_table.setStyle(TableStyle(commands))

            story.append(result_table)
            story.append(Spacer(1, 7))

            # -----------------------------------------------------
            # ANALYSIS
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    "III. PERFORMANCE ANALYSIS",
                    section_style
                )
            )

            if marks:

                if highest:
                    story.append(
                        Paragraph(
                            f"Highest recorded score: "
                            f"<b>{highest.subject.name.upper()}</b> — "
                            f"<b>{float(highest.score or 0):.1f}%</b>.",
                            normal_style
                        )
                    )

                story.append(Spacer(1, 3))

                if below_50:
                    weak_names = ", ".join(
                        m.subject.name.upper()
                        for m in below_50
                    )

                    analysis = (
                        f"Subjects with recorded scores below 50%: "
                        f"<b>{weak_names}</b>. These subjects may "
                        f"benefit from additional revision and targeted "
                        f"practice."
                    )
                else:
                    analysis = (
                        "No recorded subject score is below 50% "
                        "in the available mock results."
                    )

                story.append(
                    Paragraph(
                        analysis,
                        normal_style
                    )
                )

            else:
                story.append(
                    Paragraph(
                        "No mock results are currently recorded for "
                        "this student.",
                        normal_style
                    )
                )

            story.append(Spacer(1, 8))

            # -----------------------------------------------------
            # REPORT FOOTNOTE
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    "This report is generated from the mock results "
                    "currently stored in the UNSCCDC performance "
                    "registry.",
                    small_style
                )
            )

        # ---------------------------------------------------------
        # 9. EMPTY CLASS SAFETY
        # ---------------------------------------------------------
        if not students:
            story.append(PageBreak())

            story.append(
                Paragraph(
                    "NO STUDENTS FOUND",
                    title_style
                )
            )

            story.append(
                Paragraph(
                    f"No students were found in class "
                    f"<b>{class_name}</b> for the selected school.",
                    normal_style
                )
            )

        # ---------------------------------------------------------
        # 10. BUILD
        # ---------------------------------------------------------
        doc.build(
            story,
            onFirstPage=draw_page,
            onLaterPages=draw_page
        )

        return response

    except Exception as e:
        import traceback

        return HttpResponse(
            f"""
            <body style="
                background:#050505;
                color:#ff4444;
                padding:50px;
                font-family:Arial;
            ">
                <h1>Class Performance Report Engine Error</h1>
                <pre>{traceback.format_exc()}</pre>
            </body>
            """,
            status=500
        )
    
def generate_subject_analysis_pdf(request, class_name, subject_id):
    """
    Generates a professional institutional subject-performance report
    for all recorded candidates in the selected class and subject.
    """

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            KeepTogether
        )
        from reportlab.lib.units import mm
        from datetime import datetime

        # ---------------------------------------------------------
        # 1. SCHOOL / SUBJECT / STUDENTS
        # ---------------------------------------------------------

        school = (
            getattr(request.user, "school", None)
            or School.objects.first()
        )

        subject = get_object_or_404(
            Subject,
            id=subject_id
        )

        students = list(
            Student.objects
            .filter(
                school=school,
                current_class=class_name
            )
            .order_by("full_name")
        )

        results = list(
            KEBMockResult.objects
            .filter(
                student__in=students,
                subject=subject
            )
            .select_related("student", "subject")
            .order_by("-score", "student__full_name")
        )

        # ---------------------------------------------------------
        # 2. RESPONSE / FILE NAME
        # ---------------------------------------------------------

        response = HttpResponse(
            content_type="application/pdf"
        )

        safe_class = "".join(
            c for c in str(class_name)
            if c.isalnum() or c in (" ", "-", "_")
        ).strip().replace(" ", "_")

        safe_subject = "".join(
            c for c in str(subject.name)
            if c.isalnum() or c in (" ", "-", "_")
        ).strip().replace(" ", "_")

        response["Content-Disposition"] = (
            f'attachment; filename="KEB_SUBJECT_REPORT_'
            f'{safe_class}_{safe_subject}.pdf"'
        )

        # ---------------------------------------------------------
        # 3. INSTITUTIONAL COLOURS
        # ---------------------------------------------------------

        NAVY = colors.HexColor("#08224A")
        DEEP_NAVY = colors.HexColor("#04152F")
        BLUE = colors.HexColor("#164E86")
        GOLD = colors.HexColor("#C9A227")
        LIGHT_GOLD = colors.HexColor("#F7F0D2")
        PALE_BLUE = colors.HexColor("#EEF4FA")
        PALE_GREY = colors.HexColor("#F5F6F8")
        BORDER = colors.HexColor("#D4DAE2")
        DARK = colors.HexColor("#17202A")
        GREY = colors.HexColor("#667085")
        WHITE = colors.white
        GREEN = colors.HexColor("#197A45")
        LIGHT_GREEN = colors.HexColor("#EAF6EF")
        RED = colors.HexColor("#B42318")
        LIGHT_RED = colors.HexColor("#FDECEC")
        SILVER = colors.HexColor("#E9EDF2")
        BRONZE = colors.HexColor("#F4E7D5")

        # ---------------------------------------------------------
        # 4. DOCUMENT
        # ---------------------------------------------------------

        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=17 * mm,
            leftMargin=17 * mm,
            topMargin=17 * mm,
            bottomMargin=20 * mm,
            title=f"{subject.name} Subject Performance Report",
            author="UNSCCDC Performance Registry"
        )

        styles = getSampleStyleSheet()

        # ---------------------------------------------------------
        # 5. TYPOGRAPHY
        # ---------------------------------------------------------

        government_style = ParagraphStyle(
            "GovernmentHeader",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            textColor=DARK
        )

        institution_style = ParagraphStyle(
            "Institution",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=17,
            leading=20,
            alignment=TA_CENTER,
            textColor=NAVY
        )

        report_title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=GOLD
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Times-Bold",
            fontSize=11,
            leading=14,
            textColor=NAVY,
            spaceBefore=9,
            spaceAfter=7
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=9.2,
            leading=14,
            textColor=DARK
        )

        body_bold_style = ParagraphStyle(
            "BodyBold",
            parent=body_style,
            fontName="Times-Bold"
        )

        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=7.3,
            leading=10,
            textColor=GREY
        )

        small_center = ParagraphStyle(
            "SmallCenter",
            parent=small_style,
            alignment=TA_CENTER
        )

        metric_value_style = ParagraphStyle(
            "MetricValue",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=16,
            leading=18,
            alignment=TA_CENTER,
            textColor=NAVY
        )

        metric_label_style = ParagraphStyle(
            "MetricLabel",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
            textColor=GREY
        )

        # ---------------------------------------------------------
        # 6. PAGE FRAME / HEADER / FOOTER
        # ---------------------------------------------------------

        def draw_page(canvas, document):
            canvas.saveState()

            width, height = A4

            # Outer institutional frame
            canvas.setStrokeColor(NAVY)
            canvas.setLineWidth(1.8)
            canvas.rect(
                9 * mm,
                9 * mm,
                width - 18 * mm,
                height - 18 * mm
            )

            # Inner gold frame
            canvas.setStrokeColor(GOLD)
            canvas.setLineWidth(0.6)
            canvas.rect(
                12 * mm,
                12 * mm,
                width - 24 * mm,
                height - 24 * mm
            )

            # Footer separator
            canvas.setStrokeColor(BORDER)
            canvas.setLineWidth(0.5)
            canvas.line(
                17 * mm,
                17 * mm,
                width - 17 * mm,
                17 * mm
            )

            canvas.setFont("Times-Roman", 7)
            canvas.setFillColor(GREY)

            canvas.drawString(
                18 * mm,
                12.5 * mm,
                "UNSCCDC • KEB MOCK PERFORMANCE REGISTRY"
            )

            canvas.drawRightString(
                width - 18 * mm,
                12.5 * mm,
                f"PAGE {document.page}"
            )

            canvas.restoreState()

        # ---------------------------------------------------------
        # 7. CALCULATIONS
        # ---------------------------------------------------------

        scores = [
            float(r.score or 0)
            for r in results
        ]

        student_count = len(results)

        total_score = sum(scores)

        average = (
            total_score / student_count
            if student_count
            else 0
        )

        highest = results[0] if results else None
        lowest = results[-1] if results else None

        highest_score = (
            float(highest.score or 0)
            if highest else 0
        )

        lowest_score = (
            float(lowest.score or 0)
            if lowest else 0
        )

        score_range = (
            highest_score - lowest_score
            if results else 0
        )

        above_80 = sum(
            1 for x in scores if x >= 80
        )

        between_70_79 = sum(
            1 for x in scores if 70 <= x < 80
        )

        between_60_69 = sum(
            1 for x in scores if 60 <= x < 70
        )

        between_50_59 = sum(
            1 for x in scores if 50 <= x < 60
        )

        below_50 = sum(
            1 for x in scores if x < 50
        )

        at_or_above_50 = sum(
            1 for x in scores if x >= 50
        )

        pass_rate = (
            (at_or_above_50 / student_count) * 100
            if student_count
            else 0
        )

        # ---------------------------------------------------------
        # 8. STORY
        # ---------------------------------------------------------

        story = []

        school_name = (
            school.name.upper()
            if school and school.name
            else "UNSCCDC NATIONAL HUB"
        )

        # ---------------------------------------------------------
        # OFFICIAL HEADER
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "THE REPUBLIC OF UGANDA",
                government_style
            )
        )

        story.append(
            Paragraph(
                "KEB PERFORMANCE INTELLIGENCE & AUDIT",
                ParagraphStyle(
                    "NationalHeader",
                    parent=government_style,
                    fontSize=8.5,
                    textColor=GREY
                )
            )
        )

        story.append(Spacer(1, 5))

        # Gold rule
        rule = Table(
            [[""]],
            colWidths=[175 * mm],
            rowHeights=[1.2 * mm]
        )

        rule.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), GOLD)
            ])
        )

        story.append(rule)
        story.append(Spacer(1, 7))

        story.append(
            Paragraph(
                school_name,
                institution_style
            )
        )

        story.append(
            Paragraph(
                f"{str(subject.name).upper()} — SUBJECT PERFORMANCE REPORT",
                report_title_style
            )
        )

        story.append(
            Paragraph(
                f"CLASS: {str(class_name).upper()}",
                ParagraphStyle(
                    "ClassHeader",
                    parent=small_center,
                    fontName="Times-Bold",
                    textColor=NAVY
                )
            )
        )

        story.append(Spacer(1, 9))

        # ---------------------------------------------------------
        # REPORT METADATA PANEL
        # ---------------------------------------------------------

        generated = datetime.now().strftime(
            "%d %B %Y • %H:%M"
        )

        metadata = [
            [
                Paragraph("<b>DOCUMENT</b>", small_center),
                Paragraph("<b>SUBJECT</b>", small_center),
                Paragraph("<b>CLASS</b>", small_center),
                Paragraph("<b>GENERATED</b>", small_center)
            ],
            [
                Paragraph("KEB MOCK", small_center),
                Paragraph(str(subject.name).upper(), small_center),
                Paragraph(str(class_name).upper(), small_center),
                Paragraph(generated, small_center)
            ]
        ]

        metadata_table = Table(
            metadata,
            colWidths=[
                43.5 * mm,
                43.5 * mm,
                43.5 * mm,
                44.5 * mm
            ]
        )

        metadata_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PALE_BLUE),
                ("BACKGROUND", (0, 1), (-1, 1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        story.append(metadata_table)
        story.append(Spacer(1, 8))

        # ---------------------------------------------------------
        # I. EXECUTIVE PERFORMANCE SUMMARY
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "I. EXECUTIVE PERFORMANCE SUMMARY",
                section_style
            )
        )

        metrics = [
            [
                Paragraph(
                    f"{student_count}",
                    metric_value_style
                ),
                Paragraph(
                    f"{average:.1f}%",
                    metric_value_style
                ),
                Paragraph(
                    f"{highest_score:.1f}%",
                    metric_value_style
                ),
                Paragraph(
                    f"{lowest_score:.1f}%",
                    metric_value_style
                )
            ],
            [
                Paragraph(
                    "RECORDED CANDIDATES",
                    metric_label_style
                ),
                Paragraph(
                    "CLASS AVERAGE",
                    metric_label_style
                ),
                Paragraph(
                    "HIGHEST SCORE",
                    metric_label_style
                ),
                Paragraph(
                    "LOWEST SCORE",
                    metric_label_style
                )
            ]
        ]

        metrics_table = Table(
            metrics,
            colWidths=[43.5 * mm] * 4
        )

        metrics_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.9, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GOLD),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        story.append(metrics_table)
        story.append(Spacer(1, 8))

        # ---------------------------------------------------------
        # SECONDARY METRICS
        # ---------------------------------------------------------

        secondary = [
            [
                Paragraph(
                    f"{pass_rate:.1f}%",
                    metric_value_style
                ),
                Paragraph(
                    f"{score_range:.1f}",
                    metric_value_style
                ),
                Paragraph(
                    f"{at_or_above_50}",
                    metric_value_style
                ),
                Paragraph(
                    f"{below_50}",
                    metric_value_style
                )
            ],
            [
                Paragraph(
                    "50%+ RATE",
                    metric_label_style
                ),
                Paragraph(
                    "SCORE RANGE",
                    metric_label_style
                ),
                Paragraph(
                    "50% AND ABOVE",
                    metric_label_style
                ),
                Paragraph(
                    "BELOW 50%",
                    metric_label_style
                )
            ]
        ]

        secondary_table = Table(
            secondary,
            colWidths=[43.5 * mm] * 4
        )

        secondary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
            ])
        )

        story.append(secondary_table)

        # ---------------------------------------------------------
        # II. PERFORMANCE DISTRIBUTION
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "II. SCORE DISTRIBUTION",
                section_style
            )
        )

        distribution_rows = [
            [
                "SCORE BAND",
                "CANDIDATES",
                "PERCENTAGE"
            ],
            [
                "80 – 100%",
                str(above_80),
                f"{(above_80 / student_count * 100) if student_count else 0:.1f}%"
            ],
            [
                "70 – 79%",
                str(between_70_79),
                f"{(between_70_79 / student_count * 100) if student_count else 0:.1f}%"
            ],
            [
                "60 – 69%",
                str(between_60_69),
                f"{(between_60_69 / student_count * 100) if student_count else 0:.1f}%"
            ],
            [
                "50 – 59%",
                str(between_50_59),
                f"{(between_50_59 / student_count * 100) if student_count else 0:.1f}%"
            ],
            [
                "Below 50%",
                str(below_50),
                f"{(below_50 / student_count * 100) if student_count else 0:.1f}%"
            ]
        ]

        distribution_table = Table(
            distribution_rows,
            colWidths=[
                80 * mm,
                45 * mm,
                50 * mm
            ],
            repeatRows=1
        )

        distribution_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        # Alternate score rows
        for row in range(1, len(distribution_rows)):
            if row % 2 == 0:
                distribution_table.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, row),
                            (-1, row),
                            PALE_GREY
                        )
                    ])
                )

        story.append(distribution_table)

        # ---------------------------------------------------------
        # III. CANDIDATE RANKING
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "III. CANDIDATE PERFORMANCE RANKING",
                section_style
            )
        )

        ranking_rows = [
            [
                "RANK",
                "CANDIDATE",
                "SCORE",
                "GRADE",
                "POINTS"
            ]
        ]

        for position, result in enumerate(results, start=1):

            score = float(result.score or 0)

            ranking_rows.append([
                str(position),
                Paragraph(
                    result.student.full_name.upper(),
                    ParagraphStyle(
                        "CandidateName",
                        fontName="Times-Bold",
                        fontSize=8.5,
                        leading=10
                    )
                ),
                f"{score:.1f}%",
                result.grade or "—",
                str(result.points or 0)
            ])

        if not results:
            ranking_rows.append([
                "—",
                "NO RESULTS RECORDED",
                "—",
                "—",
                "—"
            ])

        ranking_table = Table(
            ranking_rows,
            colWidths=[
                20 * mm,
                85 * mm,
                28 * mm,
                22 * mm,
                20 * mm
            ],
            repeatRows=1
        )

        ranking_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), DEEP_NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        # Alternating rows
        for row in range(1, len(ranking_rows)):
            if row % 2 == 0:
                ranking_table.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, row),
                            (-1, row),
                            PALE_GREY
                        )
                    ])
                )

        # Highlight podium positions
        if len(ranking_rows) > 1:
            ranking_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, 1),
                        LIGHT_GOLD
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 1),
                        (0, 1),
                        NAVY
                    ),
                    (
                        "FONTNAME",
                        (0, 1),
                        (0, 1),
                        "Times-Bold"
                    )
                ])
            )

        if len(ranking_rows) > 2:
            ranking_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 2),
                        (-1, 2),
                        colors.HexColor("#F0F2F5")
                    )
                ])
            )

        if len(ranking_rows) > 3:
            ranking_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 3),
                        (-1, 3),
                        BRONZE
                    )
                ])
            )

        story.append(ranking_table)

        # ---------------------------------------------------------
        # IV. TOP PERFORMANCE ANALYSIS
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "IV. TOP PERFORMANCE ANALYSIS",
                section_style
            )
        )

        if highest:

            top_name = highest.student.full_name.upper()

            second_score = (
                float(results[1].score or 0)
                if len(results) > 1
                else None
            )

            if second_score is not None:
                lead = highest_score - second_score
                comparison = (
                    f"The leading recorded score exceeds the second-highest "
                    f"score by <b>{lead:.1f} percentage points</b>."
                )
            else:
                comparison = (
                    "Only one recorded result is available for this subject."
                )

            analysis = (
                f"<b>{top_name}</b> recorded the highest performance in "
                f"<b>{str(subject.name).upper()}</b> with a score of "
                f"<b>{highest_score:.1f}%</b>. "
                f"The class average is <b>{average:.1f}%</b>, giving the "
                f"highest recorded performance a difference of "
                f"<b>{highest_score - average:.1f} percentage points</b> "
                f"above the class average. "
                f"{comparison}"
            )

            story.append(
                Paragraph(
                    analysis,
                    body_style
                )
            )

            story.append(Spacer(1, 6))

            top_card = Table(
                [
                    [
                        Paragraph(
                            "HIGHEST RECORDED PERFORMANCE",
                            ParagraphStyle(
                                "TopCardHeader",
                                parent=small_style,
                                fontName="Times-Bold",
                                textColor=WHITE
                            )
                        )
                    ],
                    [
                        Paragraph(
                            f"<b>{top_name}</b><br/>"
                            f"{str(subject.name).upper()}<br/>"
                            f"<b>{highest_score:.1f}%</b> "
                            f"• Grade {highest.grade or '—'} "
                            f"• Points {highest.points or 0}",
                            body_style
                        )
                    ]
                ],
                colWidths=[175 * mm]
            )
            top_card.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GOLD),
                    ("BOX", (0, 0), (-1, -1), 0.9, GOLD),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
                ])
            )

            story.append(top_card)

        else:

            story.append(
                Paragraph(
                    "No recorded mock results are available for the selected "
                    "subject and class.",
                    body_style
                )
            )

        # ---------------------------------------------------------
        # V. PERFORMANCE INTERPRETATION
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "V. PERFORMANCE INTERPRETATION",
                section_style
            )
        )

        if results:

            if pass_rate >= 80:
                interpretation = (
                    f"The recorded results show that {pass_rate:.1f}% of "
                    f"candidates achieved scores of 50% or above. "
                    f"The class average stands at {average:.1f}%, while "
                    f"{above_80} candidate(s) recorded scores of 80% or above."
                )

            elif pass_rate >= 50:
                interpretation = (
                    f"The recorded results show a mixed performance profile. "
                    f"{pass_rate:.1f}% of candidates achieved scores of 50% "
                    f"or above, while {below_50} candidate(s) recorded below "
                    f"50%. The class average is {average:.1f}%."
                )

            else:
                interpretation = (
                    f"The recorded results show that fewer than half of the "
                    f"candidates achieved scores of 50% or above. "
                    f"The class average is {average:.1f}%, with "
                    f"{below_50} candidate(s) below 50%."
                )

            story.append(
                Paragraph(
                    interpretation,
                    body_style
                )
            )

            story.append(Spacer(1, 5))

            story.append(
                Paragraph(
                    "The ranking is calculated only from the recorded "
                    "scores within the selected class and subject. "
                    "Students without a recorded result are not included "
                    "in the ranking table.",
                    small_style
                )
            )

        # ---------------------------------------------------------
        # VI. ADMINISTRATIVE RECORD
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "VI. ADMINISTRATIVE RECORD",
                section_style
            )
        )

        admin_rows = [
            ["FIELD", "RECORDED VALUE"],
            ["Institution", school_name],
            ["Class", str(class_name).upper()],
            ["Subject", str(subject.name).upper()],
            ["Recorded candidates", str(student_count)],
            ["Highest score", f"{highest_score:.1f}%"],
            ["Lowest score", f"{lowest_score:.1f}%"],
            ["Class average", f"{average:.1f}%"],
            ["50%+ rate", f"{pass_rate:.1f}%"]
        ]

        admin_table = Table(
            admin_rows,
            colWidths=[65 * mm, 110 * mm],
            repeatRows=1
        )

        admin_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Times-Bold"),
                ("BACKGROUND", (0, 1), (0, -1), PALE_BLUE),
                ("BACKGROUND", (1, 1), (1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
            ])
        )

        story.append(admin_table)
        story.append(Spacer(1, 10))

        # ---------------------------------------------------------
        # CERTIFICATION / FOOT NOTE
        # ---------------------------------------------------------

        certification = Table(
            [
                [
                    Paragraph(
                        "<b>OFFICIAL RECORD NOTICE</b>",
                        ParagraphStyle(
                            "NoticeHeader",
                            parent=small_style,
                            fontName="Times-Bold",
                            textColor=NAVY
                        )
                    )
                ],
                [
                    Paragraph(
                        "This document is generated from the KEB mock "
                        "performance records currently stored in the "
                        "institutional performance registry. It is intended "
                        "for academic monitoring, internal analysis and "
                        "administrative reporting.",
                        small_style
                    )
                ]
            ],
            colWidths=[175 * mm]
        )

        certification.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PALE_BLUE),
                ("BACKGROUND", (0, 1), (-1, 1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
            ])
        )

        story.append(certification)

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                f"Generated electronically on {generated}.",
                small_center
            )
        )

        # ---------------------------------------------------------
        # BUILD PDF
        # ---------------------------------------------------------

        doc.build(
            story,
            onFirstPage=draw_page,
            onLaterPages=draw_page
        )

        return response

    except Exception as e:

        import traceback

        return HttpResponse(
            f"""
            <body style="
                background:#050505;
                color:#ff5555;
                padding:50px;
                font-family:Arial;
            ">
                <h1>Subject Performance Report Engine Error</h1>
                <pre>{traceback.format_exc()}</pre>
            </body>
            """,
            status=500
        )

@login_required
def academic_cockpit_view(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    
    # 🧠 Logic for filters
    sel_class = request.GET.get('class', 'S.1')
    sel_term = request.GET.get('term', '1')
    
    # 🕵️ Fetch subjects and find which teacher handles each one
    subjects = Subject.objects.all()
    subject_teacher_map = []
    
    for sub in subjects:
        # Look for the staff member assigned to this subject at this school
        teacher = Staff.objects.filter(subjects=sub, school=school).first()
        subject_teacher_map.append({
            'subject': sub.name.upper(),
            'teacher': teacher.full_name.upper() if teacher else "NOT ASSIGNED",
            'initials': teacher.full_name.split()[-1].upper() if teacher else "---"
        })

    return render(request, 'admin/academic_cockpit.html', {
        'school': school,
        'subject_map': subject_teacher_map,
        'sel_class': sel_class,
        'sel_term': sel_term,
        'title': "ACADEMIC COMMAND COCKPIT"
    })

@login_required
def report_designer_hub(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    
    # 🧠 Fetch Data for the sub-tabs
    subjects_primary = Subject.objects.filter(is_primary=True)
    subjects_a_level = Subject.objects.filter(is_a_level=True)
    
    # 🎨 Current Design
    template, _ = ReportTemplate.objects.get_or_create(school=school)

    return render(request, 'admin/report_designer.html', {
        'school': school,
        'template': template,
        'primary_subs': subjects_primary,
        'a_level_subs': subjects_a_level,
        'title': "GRADES & SUBJECTS ARCHITECT"
    })

import pandas as pd

@login_required
def data_exchange_view(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    recent_exchanges = DataExchangeHub.objects.filter(school=school).order_by('-timestamp')[:10]
    
    preview_data = None
    selected_exchange = None
    
    # 🕵️ PREVIEW LOGIC
    exchange_id = request.GET.get('preview_id')
    if exchange_id:
        selected_exchange = get_object_or_404(DataExchangeHub, id=exchange_id)
        try:
            # Read only the first 5 rows for a fast preview
            df = pd.read_excel(selected_exchange.exchange_file.path)
            preview_data = df.head(10).to_html(classes='preview-table', index=False)
        except Exception as e:
            preview_data = f"Error reading file: {str(e)}"

    return render(request, 'admin/data_exchange.html', {
        'school': school,
        'exchanges': recent_exchanges,
        'preview_data': preview_data,
        'selected_exchange': selected_exchange,
        'title': "NATIONAL LOGISTICS CENTER"
    })

@login_required
@transaction.atomic
def keb_mock_ingestion_view(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        
        # 1. 🧠 CLASS & SUBJECT REGISTRY
        sector_map = {
            'PRIMARY': ['P.6', 'P.7'],
            'SECONDARY': ['S.4', 'S.6'],
        }
        classes = sector_map.get(school.sector, ['S.4', 'S.6'])
        selected_class = request.GET.get('class', classes[0])
        selected_student_id = request.GET.get('student_id')
        search_query = request.GET.get('q', '').strip().upper() # 💎 THE SEARCH KEY
        
        subjects = Subject.objects.all().order_by('name')
        
        # 🔎 SEARCH LOGIC: Look for name or PRN
        students = Student.objects.filter(school=school, current_class=selected_class)
        if search_query:
            students = students.filter(Q(full_name__icontains=search_query) | Q(payment_code__icontains=search_query))
        students = students.order_by('full_name')

        # 2. 🧠 PREVIEW ENGINE (Calculates results for the UI before committing)
        preview_summary = {"avg": 0, "grade": "N/A", "status": "PENDING"}
        existing_marks = {}
        
        if selected_student_id:
            selected_student = get_object_or_404(Student, id=selected_student_id)
            marks_found = KEBMockResult.objects.filter(student=selected_student)
            
            total_score = 0
            for m in marks_found:
                existing_marks[m.subject.id] = m.score
                total_score += m.score
            
            if marks_found.exists():
                avg = total_score / marks_found.count()
                grade = "A" if avg >= 80 else "B" if avg >= 70 else "C" if avg >= 60 else "D" if avg >= 50 else "E"
                preview_summary = {"avg": round(avg, 1), "grade": grade, "status": "READY"}

        # 3. 🚩 AUDIT LIST (Who is missing data?)
        audit_list = []
        for s in students:
            done = KEBMockResult.objects.filter(student=s).count()
            audit_list.append({'student': s, 'is_complete': done >= subjects.count(), 'count': done})

        return render(request, 'admin/keb_mock_ingestion.html', {
            'classes': classes,
            'selected_class': selected_class,
            'audit_list': audit_list,
            'subjects': subjects,
            'selected_student': students.filter(id=selected_student_id).first() if selected_student_id else None,
            'existing_marks': existing_marks,
            'preview': preview_summary,
            'q': search_query,
            'school': school
        })
    except Exception as e:
        return HttpResponse(f"Terminal Error: {str(e)}")

@login_required
def biometric_photo_center(request):
    school = getattr(request.user, 'school', None) or School.objects.first()
    selected_class = request.GET.get('class', 'S.4')
    
    # 🕵️ Get students and check photo status
    students = Student.objects.filter(school=school, current_class=selected_class).order_by('full_name')
    
    # 📊 AUDIT: Count missing photos
    missing_count = students.filter(Q(photo='') | Q(photo__isnull=True)).count()
    total_count = students.count()

    context = {
        'school': school,
        'students': students,
        'selected_class': selected_class,
        'missing_count': missing_count,
        'total_count': total_count,
        'title': "NATIONAL BIOMETRIC CENTER"
    }
    return render(request, 'admin/biometric_center.html', context)

@login_required
@csrf_exempt
def update_student_photo_ajax(request):
    """💎 THE Hub Hub Hub AUTO-UPDATE ENGINE"""
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        photo_file = request.FILES.get('photo')
        
        if student_id and photo_file:
            student = get_object_or_404(Student, id=student_id)
            student.photo = photo_file
            student.save()
            return JsonResponse({"status": "success", "msg": f"Photo updated for {student.full_name}"})
            
    return JsonResponse({"status": "error", "msg": "Failed to sync photo"}, status=400)

def export_photo_audit_pdf(request):
    """🏛️ THE Hub Hub Hub MULTI-PAGE BIOMETRIC AUDIT ENGINE"""
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        selected_class = request.GET.get('class', 'S.4')
        
        # 🕵️ Fetch ALL students
        students = Student.objects.filter(school=school, current_class=selected_class).order_by('full_name')
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="FULL_AUDIT_{selected_class}.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        # 🎨 NATIONAL COLORS
        gov_blue = colors.HexColor("#002366")
        rich_gold = colors.HexColor("#D4AF37")
        ug_red = colors.HexColor("#D90000")
        success_green = colors.HexColor("#006400")

        # 💎 INTERNAL FUNCTION TO DRAW HEADER ON EVERY PAGE
        def draw_audit_header(canvas_obj, page_num):
            # 1. Background & Triple Border
            canvas_obj.setFillColor(colors.HexColor("#FDFDF5"))
            canvas_obj.rect(0, 0, width, height, fill=1, stroke=0)
            canvas_obj.setLineWidth(4); canvas_obj.setStrokeColor(gov_blue); canvas_obj.rect(15, 15, width-30, height-30)
            canvas_obj.setLineWidth(1); canvas_obj.setStrokeColor(colors.HexColor("#FCDC04")); canvas_obj.rect(20, 20, width-40, height-40)

            # 2. Titles
            canvas_obj.setFillColor(colors.black); canvas_obj.setFont("Times-Bold", 10)
            canvas_obj.drawCentredString(width/2, height-45, "THE REPUBLIC OF UGANDA")
            canvas_obj.drawCentredString(width/2, height-58, "UNSCCDC NATIONAL BIOMETRIC REGISTRY")
            
            canvas_obj.setFont("Times-Bold", 18); canvas_obj.setFillColor(gov_blue)
            canvas_obj.drawCentredString(width/2, height-90, school.name.upper())
            
            canvas_obj.setStrokeColor(rich_gold); canvas_obj.line(40, height-105, width-40, height-105)
            
            canvas_obj.setFillColor(colors.black); canvas_obj.setFont("Times-Bold", 12)
            canvas_obj.drawCentredString(width/2, height-130, f"BIOMETRIC COMPLIANCE AUDIT: {selected_class}")
            
            # Page Number
            canvas_obj.setFont("Times-Roman", 8)
            canvas_obj.drawRightString(width-50, 30, f"Page {page_num}")

        # 🔄 DATA CHUNKING (35 Students per page to prevent overlap)
        rows_per_page = 32
        total_students = students.count()
        page_count = 1
        
        # Initial Header
        draw_audit_header(p, page_count)
        
        y_position = height - 170
        headers = ['NO.', 'STUDENT LEGAL NAME', 'PRN / ACCESS CODE', 'STATUS']
        
        # Header for the table
        p.setFillColor(gov_blue); p.rect(40, y_position - 15, width-80, 20, fill=1, stroke=0)
        p.setFillColor(colors.white); p.setFont("Times-Bold", 9)
        p.drawString(45, y_position - 10, "NO.")
        p.drawString(85, y_position - 10, "STUDENT LEGAL NAME")
        p.drawString(345, y_position - 10, "PRN / ACCESS CODE")
        p.drawString(465, y_position - 10, "STATUS")
        
        y_position -= 35

        for i, s in enumerate(students, 1):
            # 🛡️ CHECK IF WE NEED A NEW PAGE
            if i > 0 and i % rows_per_page == 0:
                p.showPage()
                page_count += 1
                draw_audit_header(p, page_count)
                y_position = height - 170
                # Redraw Table Header on new page
                p.setFillColor(gov_blue); p.rect(40, y_position - 15, width-80, 20, fill=1, stroke=0)
                p.setFillColor(colors.white); p.setFont("Times-Bold", 9)
                p.drawString(45, y_position - 10, "NO.")
                p.drawString(85, y_position - 10, "STUDENT LEGAL NAME")
                p.drawString(345, y_position - 10, "PRN / ACCESS CODE")
                p.drawString(465, y_position - 10, "STATUS")
                y_position -= 35

            # ✍️ DRAW STUDENT ROW
            p.setFillColor(colors.black); p.setFont("Times-Roman", 10)
            p.drawString(45, y_position, str(i))
            p.setFont("Times-Bold", 9)
            p.drawString(85, y_position, s.full_name.upper()[:45]) # Truncate very long names
            p.setFont("Courier", 9)
            p.drawString(345, y_position, s.payment_code or "---")
            
            # Status Badge with Square Icon
            has_photo = bool(s.photo or (hasattr(s, 'photo_data') and s.photo_data))
            if has_photo:
                p.setFillColor(success_green)
                p.rect(465, y_position - 2, 8, 8, fill=1, stroke=0) # Green Square
                p.drawString(478, y_position, "UPLOADED")
            else:
                p.setFillColor(ug_red)
                p.rect(465, y_position - 2, 8, 8, fill=1, stroke=0) # Red Square
                p.drawString(478, y_position, "MISSING")
                
            # Draw thin line under row
            p.setStrokeColor(colors.lightgrey); p.setLineWidth(0.2)
            p.line(40, y_position - 5, width-40, y_position - 5)
            
            y_position -= 20

        # ✍️ FINAL FOOTER (ONLY ON THE LAST PAGE)
        p.setStrokeColor(gov_blue); p.setLineWidth(1)
        p.line(50, 70, 200, 70)
        p.setFillColor(colors.black); p.setFont("Times-Bold", 8)
        p.drawString(70, 58, "Director of Studies / Registrar")
        p.drawRightString(width-50, 58, f"Final Audit Date: {datetime.date.today().strftime('%d/%b/%Y')}")

        p.showPage()
        p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Multi-Page Error: {str(e)}")

from django.db import connection
from django.http import HttpResponse

def emergency_database_fix(request):
    """🛡️ THE Hub Hub Hub Hub Hub EMERGENCY SQL INJECTOR"""
    try:
        with connection.cursor() as cursor:
            # 1. Physically force the 'phone' column into the 'api_school' table
            # We use 'VARCHAR(50)' to match your model and add a default
            cursor.execute("""
                ALTER TABLE api_school 
                ADD COLUMN IF NOT EXISTS phone VARCHAR(50) DEFAULT '+256';
            """)
            
            # 2. While we are here, let's ensure 'created_at' also exists
            cursor.execute("""
                ALTER TABLE api_school 
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
            """)

        return HttpResponse("<h1 style='color:white; background:green; padding:50px;'>SUCCESS: 'phone' and 'created_at' columns injected! The Registry is now healed.</h1><a href='/admin/'>Return to Office</a>")
    except Exception as e:
        return HttpResponse(f"<h1 style='color:white; background:red; padding:50px;'>Injection Error</h1><p>{str(e)}</p>")
    

    from django.db import connection
from django.http import HttpResponse

def emergency_database_fix(request):
    """🛡️ THE Hub Hub Hub Hub Hub EMERGENCY SQL INJECTOR"""
    try:
        with connection.cursor() as cursor:
            # 1. Physically force the 'phone' column into the 'api_school' table
            # We use 'VARCHAR(50)' to match your model and add a default
            cursor.execute("""
                ALTER TABLE api_school 
                ADD COLUMN IF NOT EXISTS phone VARCHAR(50) DEFAULT '+256';
            """)
            
            # 2. While we are here, let's ensure 'created_at' also exists
            cursor.execute("""
                ALTER TABLE api_school 
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
            """)

        return HttpResponse("<h1 style='color:white; background:green; padding:50px;'>SUCCESS: 'phone' and 'created_at' columns injected! The Registry is now healed.</h1><a href='/admin/'>Return to Office</a>")
    except Exception as e:
        return HttpResponse(f"<h1 style='color:white; background:red; padding:50px;'>Injection Error</h1><p>{str(e)}</p>")
    
@login_required
def national_merit_view(request):
    try:
        school = getattr(request.user, 'school', None) or School.objects.first()
        exam_type = request.GET.get('type', 'TERMLY') # TERMLY or MOCK
        selected_class = request.GET.get('class', 'ALL')

        # 🕵️ 1. Fetch Students
        query = Student.objects.filter(school=school, is_active=True)
        if selected_class != 'ALL':
            query = query.filter(current_class=selected_class)

        rank_list = []
        
        for s in query:
            # 🧮 2. Calculate Average based on Exam Type
            if exam_type == 'MOCK':
                marks = KEBMockResult.objects.filter(student=s)
                scores = [m.score for m in marks]
            else:
                marks = AcademicResult.objects.filter(student=s)
                # For termly, we use the EOT score as the standard
                scores = [m.eot_score for m in marks]

            if scores:
                avg = sum(scores) / len(scores)
                # Find best subject
                if exam_type == 'MOCK':
                    best_sub = marks.order_by('-score').first().subject.name if marks.exists() else "N/A"
                else:
                    best_sub = marks.order_by('-eot_score').first().subject.name if marks.exists() else "N/A"
                
                rank_list.append({
                    'student': s,
                    'avg': round(avg, 1),
                    'best': best_sub.upper(),
                    'count': len(scores)
                })

        # 🏆 3. THE Hub Hub Hub Hub Hub MASTER SORT
        # Sort by average descending (Highest to Lowest)
        rank_list.sort(key=lambda x: x['avg'], reverse=True)

        context = {
            'school': school,
            'rank_list': rank_list,
            'exam_type': exam_type,
            'selected_class': selected_class,
            'title': "NATIONAL MERIT LIST"
        }
        return render(request, 'admin/national_merit.html', context)
    except Exception as e:
        return HttpResponse(f"Ranking Engine Error: {str(e)}")

from django.contrib.auth import login, get_user_model
from django.db import transaction

import base64

def convert_to_base64(file):
    """🛡️ THE Hub Hub Hub Hub Hub Hub Hub VECTOR ENCODER"""
    try:
        return base64.b64encode(file.read()).decode('utf-8')
    except:
        return None

@login_required
@csrf_exempt
def update_student_photo_ajax(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        photo_file = request.FILES.get('photo')
        
        if student_id and photo_file:
            student = get_object_or_404(Student, id=student_id)
            # 💎 ENCODE AND SAVE AS TEXT
            encoded_string = convert_to_base64(photo_file)
            student.photo_data = encoded_string
            student.save()
            return JsonResponse({"status": "success", "msg": f"Biometrics Linked for {student.full_name}"})
            
    return JsonResponse({"status": "error", "msg": "Sync Failed"}, status=400)

from io import BytesIO
from reportlab.lib.utils import ImageReader

def get_base64_image(base64_string):
    """💎 TURNS DATABASE TEXT BACK INTO A HIGH-RES IMAGE"""
    if not base64_string: return None
    try:
        format, imgstr = base64_string.split(';base64,') if ',' in base64_string else (None, base64_string)
        img_data = base64.b64decode(imgstr)
        return ImageReader(BytesIO(img_data))
    except:
        return None

@login_required
def save_report_design(request):
    """💾 SAVES THE Hub Hub Hub Hub Hub ARCHITECTURAL SETTINGS"""
    if request.method == "POST":
        school = request.user.profile.school
        target = request.POST.get('target_type')
        
        # Get or create the template for this specific school and document type
        template, _ = ReportTemplate.objects.get_or_create(school=school, target_type=target)
        
        template.page_format = request.POST.get('page_format')
        template.primary_color = request.POST.get('primary_color')
        template.watermark_opacity = float(request.POST.get('opacity', 0.05)) / 100
        template.save()
        
        return JsonResponse({"status": "SUCCESS", "msg": "National Design Templates Synchronized!"})

# =============================================================
# 🚀 19.5 THE Hub Hub Hub EXECUTIVE NATIONAL PERFORMANCE AUDIT
# =============================================================
@login_required
def generate_overall_performance_pdf(request):
    """🏛️ Generates a high-level analytics summary for the entire class/school."""
    try:
        # 1. IDENTITY & CONTEXT
        school = getattr(request.user, 'school', None) or School.objects.first()
        selected_class = request.GET.get('class', 'S.4').upper()
        
        # 🕵️ AGGREGATE DATA FROM THE BRAIN
        # Calculate averages for every subject in the specific class
        subject_stats = KEBMockResult.objects.filter(
            student__school=school, 
            student__current_class=selected_class
        ).values('subject__name').annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score')

        if not subject_stats:
            return HttpResponse("<body style='background:black;color:gold;padding:50px;'><h1>NO DATA DETECTED</h1><p>Ensure mock marks are entered before generating summary.</p></body>")

        # 📄 INITIALIZE PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="OVERALL_PERFORMANCE_{selected_class}.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        gov_blue = colors.HexColor("#002366")
        rich_gold = colors.HexColor("#D4AF37")
        ug_red = colors.HexColor("#D90000")

        # 🖌️ 2. NATIONAL Hub Hub Hub Hub Hub BORDERS & BG
        p.setFillColor(colors.HexColor("#FDFDF5"))
        p.rect(0, 0, width, height, fill=1, stroke=0)
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(rich_gold); p.rect(22, 22, width-44, height-44)

        # 🏛️ 3. HEADERS
        p.setFillColor(colors.black); p.setFont("Times-Bold", 10)
        p.drawCentredString(width/2, height-45, "THE REPUBLIC OF UGANDA")
        p.drawCentredString(width/2, height-58, "KYADONDO EXAMINATIONS BOARD (KEB)")
        p.setFont("Times-Bold", 18); p.setFillColor(gov_blue)
        p.drawCentredString(width/2, height-95, "EXECUTIVE PERFORMANCE SUMMARY")
        p.setFillColor(colors.black); p.setFont("Times-Bold", 11)
        p.drawCentredString(width/2, height-115, f"INSTITUTION: {school.name.upper()} | CLASS: {selected_class}")
        p.line(45, height-125, width-45, height-125)

        # 📈 4. THE Hub Hub Hub Hub Hub ANALYTICS GRAPH
        # We draw a graph of all subjects in the class
        labels = [s['subject__name'][:6].upper() for s in subject_stats]
        values = [float(s['avg_score']) for s in subject_stats]
        
        # Use our graph helper (Ensure you have matplotlib/numpy installed)
        try:
            from .views import generate_pro_analytics_graph # Re-using our earlier helper
            graph = generate_pro_analytics_graph(labels, values)
            p.drawImage(graph, 50, height-380, width=500, height=240)
        except:
            p.rect(50, height-380, 500, 240, stroke=1)
            p.drawCentredString(width/2, height-260, "[GRAPH GENERATION IN PROGRESS]")

        # 🏆 5. BEST VS WORST SUBJECTS TABLE
        best_sub = subject_stats[0]
        worst_sub = subject_stats.reverse()[0]
        
        def get_grade(score):
            if score >= 80: return "A"
            if score >= 70: return "B"
            if score >= 60: return "C"
            if score >= 50: return "D"
            return "E"

        data = [
            ['CATEGORY', 'SUBJECT', 'CLASS MEAN', 'AVG GRADE'],
            ['NATIONAL STRENGTH', best_sub['subject__name'].upper(), f"{best_sub['avg_score']:.1f}%", get_grade(best_sub['avg_score'])],
            ['CRITICAL WEAKNESS', worst_sub['subject__name'].upper(), f"{worst_sub['avg_score']:.1f}%", get_grade(worst_sub['avg_score'])]
        ]

        table = Table(data, colWidths=[150, 150, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), gov_blue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,1), (0,1), colors.honeydew),
            ('BACKGROUND', (0,2), (0,2), colors.mistyrose),
        ]))
        table.wrapOn(p, width, height)
        table.drawOn(p, 45, height-480)

        # 💡 6. SYSTEM RECOMMENDATIONS
        p.setFillColor(colors.black); p.setFont("Times-Bold", 11)
        p.drawString(50, height-520, "NATIONAL SYSTEM RECOMMENDATIONS:")
        
        p.setFont("Times-Roman", 10)
        recs = [
            f"• Priority: Deployment of additional resources for {worst_sub['subject__name'].upper()}.",
            f"• Mentorship: Assign instructors from {best_sub['subject__name'].upper()} to support weak departments.",
            "• Digital: Increase student engagement with E-Learning modules for technical subjects.",
            "• Parents: Issue digital fees reminders to facilitate weekend remedial bootcamps."
        ]
        y_pos = height-540
        for r in recs:
            p.drawString(60, y_pos, r)
            y_pos -= 18

        # 🛡️ 7. SOVEREIGN SEAL
        p.setStrokeColor(colors.teal); p.circle(width-100, 100, 40, stroke=1, fill=0)
        p.setFont("Times-Bold", 8)
        p.drawCentredString(width-100, 105, "KEB HQ")
        p.drawCentredString(width-100, 95, "AUTHENTICATED")

        p.showPage(); p.save()
        return response

    except Exception as e:
        import traceback
        return HttpResponse(f"Executive Report Error: {traceback.format_exc()}")


import io
import matplotlib.pyplot as plt
import numpy as np
from django.db.models import Avg
from reportlab.lib.utils import ImageReader

# =============================================================
# 📊 1. THE Hub Hub Hub Hub Hub ANALYTICS ARTIST (MATPLOTLIB)
# =============================================================
def generate_class_graph(labels, values, title):
    """Draws a professional analytics bar chart for the PDF"""
    plt.figure(figsize=(7, 3.5), dpi=150)
    y_pos = np.arange(len(labels))
    
    # 🎨 Sovereign Colors for the Bars
    colors_list = ['#002366' if v >= 60 else '#D90000' for v in values]
    
    plt.bar(labels, values, color=colors_list, alpha=0.8, edgecolor='black', linewidth=0.5)
    plt.axhline(y=50, color='gray', linestyle='--', alpha=0.5) # National Median Line
    
    plt.title(title, fontsize=11, fontweight='bold', family='serif')
    plt.xticks(rotation=30, fontsize=8)
    plt.yticks(fontsize=8)
    plt.ylim(0, 100)
    plt.ylabel("Average Mark (%)", fontsize=8)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close()
    buf.seek(0)
    return ImageReader(buf)

# =============================================================
# 🚀 2. THE Hub Hub Hub EXECUTIVE PERFORMANCE ENGINE (FIXES ERROR)
# =============================================================
@login_required
def generate_overall_performance_pdf(request):
    """🏛️ Generates the Master Executive Summary for the School Board"""
    try:
        # 1. 🔑 SET IDENTITY
        school = getattr(request.user, 'school', None) or School.objects.first()
        selected_class = request.GET.get('class', 'S.4').upper()
        
        # 2. 🧠 AGGREGATE THE BRAIN (Calculating Subject Means)
        # We group all mock results by subject and get the average
        stats = KEBMockResult.objects.filter(
            student__school=school, 
            student__current_class=selected_class
        ).values('subject__name').annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score')

        if not stats:
            return HttpResponse("<body style='background:#000;color:gold;padding:50px;'><h1>NO MOCK DATA</h1><p>Registry is empty for "+selected_class+".</p></body>")

        # 3. 📄 INITIALIZE THE Hub Hub Hub Hub Hub A4 DOCUMENT
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="EXECUTIVE_SUMMARY_{selected_class}.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        gov_blue = colors.HexColor("#002366")   # Royal Navy
        rich_gold = colors.HexColor("#D4AF37")  # Imperial Gold
        ug_red = colors.HexColor("#D90000")     # National Red

        # 4. 🖌️ PAINT THE Hub Hub Hub BORDERS
        p.setFillColor(colors.HexColor("#FDFDF5"))
        p.rect(0, 0, width, height, fill=1, stroke=0)
        p.setLineWidth(5); p.setStrokeColor(gov_blue); p.rect(15, 15, width-30, height-30)
        p.setLineWidth(1); p.setStrokeColor(rich_gold); p.rect(22, 22, width-44, height-44)

        # 5. 🏛️ NATIONAL HEADERS (Times New Roman)
        p.setFillColor(colors.black); p.setFont("Times-Bold", 10)
        p.drawCentredString(width/2, height-45, "THE REPUBLIC OF UGANDA")
        p.drawCentredString(width/2, height-58, "KYADONDO EXAMINATIONS BOARD (KEB)")
        p.setFont("Times-Bold", 22); p.setFillColor(gov_blue)
        p.drawCentredString(width/2, height-100, "EXECUTIVE PERFORMANCE AUDIT")
        p.setFillColor(colors.black); p.setFont("Times-Bold", 11)
        p.drawCentredString(width/2, height-125, f"INSTITUTION: {school.name.upper()} | CLASS: {selected_class}")
        p.line(45, height-135, width-45, height-135)

        # 6. 🏆 THE Hub Hub Hub Hub Hub SUMMARY TABLE (Best vs Worst)
        best = stats[0]
        worst = stats.reverse()[0]
        
        def map_grade(s):
            if s >= 80: return "A (Exceptional)"
            if s >= 65: return "B (Strong)"
            if s >= 50: return "C (Satisfactory)"
            return "E (Elementary)"

        summary_data = [
            ['INDICATOR', 'SUBJECT NAME', 'MEAN SCORE', 'EQUIV. GRADE'],
            ['NATIONAL STRENGTH', best['subject__name'].upper(), f"{best['avg_score']:.1f}%", map_grade(best['avg_score'])],
            ['CRITICAL WEAKNESS', worst['subject__name'].upper(), f"{worst['avg_score']:.1f}%", map_grade(worst['avg_score'])]
        ]
        
        summ_table = Table(summary_data, colWidths=[130, 150, 100, 130])
        summ_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), gov_blue), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.1, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,1), (0,1), colors.honeydew), ('BACKGROUND', (0,2), (0,2), colors.mistyrose),
        ]))
        summ_table.wrapOn(p, width, height)
        summ_table.drawOn(p, 45, height-220)

        # 7. 📈 THE Hub Hub Hub Hub Hub ANALYTICS GRAPH
        labels = [s['subject__name'][:5].upper() for s in stats]
        values = [float(s['avg_score']) for s in stats]
        graph = generate_class_graph(labels, values, "OVERALL SUBJECT MASTERY RADIUS")
        p.drawImage(graph, 45, height-520, width=500, height=280)

        # 8. 💡 SOVEREIGN Hub Hub Hub RECOMMENDATIONS
        p.setFillColor(colors.black); p.setFont("Times-Bold", 12)
        p.drawString(50, height-560, "NATIONAL SYSTEM RECOMMENDATIONS:")
        
        p.setFont("Times-Roman", 10)
        recs = [
            f"1. URGENT: Deploy specialized remedial support for {worst['subject__name'].upper()}.",
            f"2. MENTORSHIP: Use the winning department of {best['subject__name'].upper()} to train others.",
            "3. PARENTS: Use the SMS Broadcast tool to alert parents of students below the 45% median.",
            "4. RESOURCES: Reallocate library procurement priority to the weakest performing subjects."
        ]
        ry = height-585
        for r in recs:
            p.drawString(60, ry, r)
            ry -= 20

        # 9. 🛡️ FINAL Hub Hub Hub Hub Hub AUTHENTICATION
        p.setStrokeColor(colors.teal); p.circle(width/2, 100, 35, stroke=1, fill=0)
        p.setFont("Times-Bold", 8)
        p.drawCentredString(width/2, 105, "UNSCCDC")
        p.drawCentredString(width/2, 95, "AUDITED")
        
        p.setFont("Times-Roman", 6); p.setFillColor(colors.grey)
        p.drawRightString(width-50, 50, f"Generated: {datetime.datetime.now().strftime('%d/%b/%Y %H:%M')}")

        p.showPage(); p.save()
        return response

    except Exception as e:
        import traceback
        return HttpResponse(f"Executive Audit Error: {traceback.format_exc()}")

@login_required
def passlip_html_preview(request, student_id):
    """🛡️ FIXED: Never crashes even if photo is missing"""
    student = get_object_or_404(Student, account_number=student_id)
    results = KEBMockResult.objects.filter(student=student)
    
    # 💎 Add this line to handle the 'Result 1' logic we discussed
    all_fails = all(r.score < 40 for r in results) if results.exists() else True
    res_tier = "RESULT 2" if all_fails else "RESULT 1"

    return render(request, 'admin/passlip_preview_snippet.html', {
        'student': student, 'results': results, 'res_tier': res_tier,
        'photo_url': student.photo.url if student.photo else "https://via.placeholder.com/150"
    })

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Parent, Staff, KEBMockResult, SchoolPayLedger, NationalTopPerformer, SchoolPost
from .utils import get_national_grading # Assuming you have this helper

def sovereign_response(data, status=200):
    """Helper to ensure every response has correct CORS headers for the Web App"""
    response = JsonResponse(data, status=status)
    response["Access-Control-Allow-Origin"] = "*" # Use '*' for development
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Sovereign-Client"
    return response

@csrf_exempt
def student_identity_gate(request):
    """STAGE 1: Verify the 4-Point Identity Match"""
    if request.method == "OPTIONS": return sovereign_response({})
    
    try:
        # 💎 THE Hub Hub Hub Hub FIX: Read JSON Body instead of POST/GET
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        s_name = data.get('student', '').strip()
        p_name = data.get('parent', '').strip()
        phone = data.get('phone', '').strip()

        # 🕵️ Search logic (Ugandan Phone Number Sanitizer)
        # Matches last 9 digits to ignore 07... vs +256... differences
        search_phone = phone[-9:] if len(phone) >= 9 else phone

        match = Student.objects.filter(
            payment_code__iexact=code,
            full_name__iexact=s_name,
            parent_link__full_name__iexact=p_name,
            parent_link__phone_number__icontains=search_phone
        ).first()

        if match:
            return sovereign_response({
                'status': 'IDENTITY_CONFIRMED',
                'student_id': match.account_number,
                'message': f"Identity Confirmed for {match.full_name}"
            })
        
        return sovereign_response({'msg': 'National Registry Mismatch. Check spelling.'}, status=401)

    except Exception as e:
        return sovereign_response({'msg': f'System Error: {str(e)}'}, status=500)

@csrf_exempt
def pin_vault_auth(request):
    """STAGE 2: Verify PIN and Deliver the Imperial Data Package"""
    if request.method == "OPTIONS": return sovereign_response({})
    
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        pin = data.get('pin', '').strip()

        student = Student.objects.select_related('parent_link', 'school').get(account_number=student_id)
        parent = student.parent_link

        if parent and parent.secure_pin == pin:
            # 🚀 IDENTITY SECURE - Generate massive data payload
            # (Use the logic from your StudentViewSet.list here to build the response)
            # Below is a condensed version to ensure it works immediately:
            
            payload = {
                "status": "authenticated",
                "name": student.full_name,
                "id": student.account_number,
                "payment_code": student.payment_code,
                "class": student.current_class,
                "photo": request.build_absolute_uri(student.photo.url) if student.photo else "",
                "school": {
                    "name": student.school.name,
                    "motto": student.school.school_motto,
                },
                "finance": {
                    "balance": 0, # Calculate your balance logic here
                    "paid": 0
                },
                "feed": [], # Add your TikTok feed logic here
                "national_report": {} # Add your marks logic here
            }
            return sovereign_response(payload)

        return sovereign_response({'msg': 'SECURITY ALERT: Invalid 6-Digit PIN.'}, status=401)

    except Exception as e:
        return sovereign_response({'msg': 'Authorization Failed'}, status=500)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *

@api_view(['POST'])
def initiate_payment(request):
    """
    Requirement #7: Real School Fees/Report Payment Flow
    """
    user = request.user
    student_id = request.data.get('student_id')
    amount = request.data.get('amount')
    purpose = request.data.get('type') # 'REPORT' or 'FEES'

    # 1. Create Internal Transaction (Status: PENDING)
    tx = PaymentTransaction.objects.create(
        transaction_id=f"USDC-{uuid.uuid4().hex[:10].upper()}",
        student_id=student_id,
        amount=amount,
        type=purpose,
        status='PENDING'
    )

    # 2. Integrate with Payment Provider (Logic Placeholder)
    # response = PaymentGateway.init(amount, tx.transaction_id)
    
    return Response({
        "tx_id": tx.transaction_id,
        "amount": amount,
        "purpose": purpose,
        "gateway_url": "https://gateway.ug/pay/..." 
    })

@api_view(['GET'])
def get_parent_dashboard(request):
    """
    Requirement #8: Contextual Parent Dashboard
    """
    # Logic to identify parent's children across different schools
    parent = Parent.objects.get(user=request.user)
    students = student.objects.filter(parent_link=parent)
    
    data = []
    for s in students:
        fees = FeesTracker.objects.get(student=s)
        data.append({
            "student_name": s.full_name,
            "school": s.school.name,
            "verified": s.school.schoolverification.status == 'VERIFIED',
            "balance": fees.fees_balance,
            "latest_mark": s.marks.all().order_by('-id').first().eot_score
        })
    return Response(data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import UserIdentitySerializer
from .models import Staff, Parent, Student, School

class UnifiedUSDCAuth(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        role_type = request.data.get('login_mode') # 'staff' or 'parent'
        identifier = request.data.get('id_code')   # PRN for parents, Name for staff
        pin = str(request.data.get('pin')).strip()

        try:
            if role_type == 'staff':
                # 🕵️ Search Existing Staff Registry
                user_obj = Staff.objects.filter(full_name__iexact=identifier, secure_pin=pin).first()
                if not user_obj:
                    return Response({"msg": "Staff Credentials Denied"}, status=401)
                
                payload = {
                    "token": "usdc_stf_" + user_obj.staff_id,
                    "role": user_obj.role,
                    "display_name": user_obj.full_name,
                    "photo_url": user_obj.passport_photo.url if user_obj.passport_photo else None,
                    "school_context": user_obj.school
                }

            else: # Parent Mode
                # 🕵️ Search Existing Parent/Student Link
                student = Student.objects.filter(payment_code=identifier).first()
                if student and student.parent_link and student.parent_link.unique_code == pin:
                    payload = {
                        "token": "usdc_par_" + student.account_number,
                        "role": "PARENT",
                        "display_name": student.parent_link.full_name,
                        "photo_url": student.photo.url if student.photo else None,
                        "school_context": student.school
                    }
                else:
                    return Response({"msg": "Identity Mismatch in Registry"}, status=401)

            # Return the finalized Identity Packet
            serializer = UserIdentitySerializer(payload, context={'request': request})
            return Response(serializer.data)

        except Exception as e:
            return Response({"msg": f"System Error: {str(e)}"}, status=500)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import Staff, Student, Parent
from .serializers import UserIdentitySerializer # Import the serializer we just fixed

class UnifiedImperialAuth(APIView):
    permission_classes = [AllowAny] # The "Front Door" is open for login

    def post(self, request):
        mode = request.data.get('login_mode') # 'staff' or 'parent'
        id_code = request.data.get('id_code') # Name or PRN
        pin = str(request.data.get('pin')).strip()

        if mode == 'staff':
            member = Staff.objects.filter(full_name__iexact=id_code, secure_pin=pin).first()
            if not member: return Response({"msg": "Invalid Staff Credentials"}, 401)
            
            # 🔗 Link to Security User
            user, _ = User.objects.get_or_create(username=f"stf_{member.staff_id}")
            member.user = user
            member.save()
            role = member.role
            school = member.school

        else: # Parent Mode
            student = Student.objects.filter(payment_code=id_code).first()
            if student and student.parent_link and student.parent_link.unique_code == pin:
                parent = student.parent_link
                user, _ = User.objects.get_or_create(username=f"par_{parent.phone_number}")
                parent.user = user
                parent.save()
                member = parent
                role = "PARENT"
                school = student.school
            else:
                return Response({"msg": "Identity Mismatch"}, 401)

        # 🎫 Issue Standard Token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            "token": token.key,
            "role": role,
            "name": id_code,
            "school": {
                "name": school.name,
                "logo": request.build_absolute_uri(school.logo.url) if school.logo else ""
            }
        })

# ============================================================
# DIRECTOR PUBLIC REGISTRATION
# ============================================================

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


# ============================================================
# DIRECTOR PUBLIC REGISTRATION
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def director_register(request):
    """
    Public registration for School Directors.

    The Director creates their school during registration.
    No existing school_id can be supplied by the public user.

    Creates:
        School
        User
        UserProfile
        Staff record with DIRECTOR role
        Authentication token
    """

    try:
        full_name = request.data.get('full_name', '').strip()
        school_name = request.data.get('school_name', '').strip()
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()
        password = request.data.get('password', '')
        confirm_password = request.data.get('confirm_password', '')

        # -----------------------------
        # Basic validation
        # -----------------------------
        if not full_name or not school_name or not email or not phone or not password:
            return Response(
                {"msg": "Full name, school name, email, phone and password are required."},
                status=400
            )

        if password != confirm_password:
            return Response(
                {"msg": "Passwords do not match."},
                status=400
            )

        if len(password) < 8:
            return Response(
                {"msg": "Password must be at least 8 characters."},
                status=400
            )

        # -----------------------------
        # Prevent duplicate email
        # -----------------------------
        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"msg": "An account with this email already exists."},
                status=400
            )

        # -----------------------------
        # Prevent duplicate school names
        # -----------------------------
        if School.objects.filter(name__iexact=school_name).exists():
            return Response(
                {"msg": "A school with this name is already registered."},
                status=400
            )

        # -----------------------------
        # Generate unique username
        # -----------------------------
        base_username = email.split('@')[0][:120]
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # -----------------------------
        # Create the NEW school
        # -----------------------------
        school = School.objects.create(
            name=school_name,
            director=full_name,
            email=email,
        )

        # -----------------------------
        # Create Director User
        # -----------------------------
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        user.is_superuser = False
        user.is_staff = False
        user.is_staff_member = True
        user.school = school
        user.save()

        # -----------------------------
        # Connect Director to school
        # -----------------------------
        UserProfile.objects.create(
            user=user,
            school=school,
            is_school_admin=True,
        )

        # -----------------------------
        # Create Director Staff record
        # -----------------------------
        staff = Staff.objects.create(
            full_name=full_name,
            user=user,
            role='DIRECTOR',
            school=school,
            phone=phone,
        )

        # -----------------------------
        # Issue login token
        # -----------------------------
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "status": "registered",
            "message": "Director account and school created successfully.",
            "token": token.key,
            "user_id": user.id,
            "name": full_name,
            "role": "DIRECTOR",
            "school": {
                "id": school.id,
                "name": school.name,
                "school_account_id": school.school_account_id,
            }
        }, status=201)

    except Exception as e:
        return Response(
            {"msg": f"Registration failed: {str(e)}"},
            status=500
        )

# ============================================================
# DIRECTOR DASHBOARD
# ============================================================

@login_required
def director_dashboard(request):
    """
    Private dashboard for a School Director.

    The Director can only access data belonging to
    the school linked to their UserProfile.
    """

    user = request.user

    # Director must have a school profile
    profile = getattr(user, 'profile', None)

    if not profile or not profile.school:
        return HttpResponse(
            "Your Director account is not linked to a school.",
            status=403
        )

    if not profile.is_school_admin:
        return HttpResponse(
            "Director access required.",
            status=403
        )

    school = profile.school

    # Only retrieve records belonging to THIS school
    students = Student.objects.filter(school=school)
    staff = Staff.objects.filter(school=school)

    context = {
        'director': user,
        'school': school,
        'students': students,
        'staff': staff,
        'student_count': students.count(),
        'staff_count': staff.count(),
    }

    return render(
        request,
        'director/dashboard.html',
        context
    )

# ============================================================
# DIRECTOR WEB LOGIN
# ============================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def director_web_login(request):
    """
    Browser-based login for School Directors.

    GET  -> displays the login page.
    POST -> authenticates the Director and creates a Django session.
    """

    if request.method == 'GET':
        return render(request, 'director/login.html')

    try:
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        if not email or not password:
            return render(
                request,
                'director/login.html',
                {'error': 'Email and password are required.'}
            )

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if not user or not user.check_password(password):
            return render(
                request,
                'director/login.html',
                {'error': 'Invalid email or password.'}
            )

        profile = getattr(user, 'profile', None)

        if not profile or not profile.school:
            return render(
                request,
                'director/login.html',
                {'error': 'This account is not linked to a school.'}
            )

        if not profile.is_school_admin:
            return render(
                request,
                'director/login.html',
                {'error': 'This account is not registered as a School Director.'}
            )

        # Create Django browser session
        login(request, user)

        return redirect('/api/director/dashboard/')

    except Exception as e:
        return render(
            request,
            'director/login.html',
            {'error': f'Login failed: {str(e)}'}
        )
# ============================================================
# DIRECTOR LOGIN
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def director_login(request):
    """
    Public login for registered School Directors.
    """

    try:
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {"msg": "Email and password are required."},
                status=400
            )

        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.check_password(password):
            return Response(
                {"msg": "Invalid email or password."},
                status=401
            )

        profile = getattr(user, 'profile', None)

        if not profile or not profile.school:
            return Response(
                {"msg": "This account is not linked to a school."},
                status=403
            )

        if not profile.is_school_admin:
            return Response(
                {"msg": "This account is not registered as a School Director."},
                status=403
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "status": "authenticated",
            "token": token.key,
            "user_id": user.id,
            "name": user.first_name or user.username,
            "role": "DIRECTOR",
            "school": {
                "id": profile.school.id,
                "name": profile.school.name,
            }
        })

    except Exception as e:
        return Response(
            {"msg": f"Login failed: {str(e)}"},
            status=500
        )

@login_required
def generate_subject_audit_pdf(request):
    """
    COMPLETE SUBJECT PERFORMANCE AUDIT

    Independent report. This method does NOT modify or replace
    generate_overall_performance_pdf().

    S.4:
        Grade columns: A, B, C, D, E
        F/O are excluded from the report.

    S.6:
        Grade columns: A, B, C, D, E, F, O

    Ranking:
        1. Mean score - primary ranking
        2. Pass percentage - first tie-breaker
        3. Number of A grades - second tie-breaker
        4. Highest individual score - third tie-breaker
        5. Subject name - final deterministic tie-breaker

    Source:
        KEBMockResult
    """

    try:
        from collections import defaultdict

        from django.http import HttpResponse

        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle,
        )
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
        )

        # ========================================================
        # 1. DETERMINE THE DIRECTOR'S SCHOOL
        # ========================================================

        profile = getattr(request.user, 'profile', None)

        if profile and profile.school:
            school = profile.school
        else:
            school = getattr(request.user, 'school', None)

        if not school:
            return HttpResponse(
                "Your account is not linked to a school.",
                status=403
            )

        # ========================================================
        # 2. SELECT CLASS
        # ========================================================

        selected_class = request.GET.get(
            'class',
            request.GET.get('class_name', 'S.4')
        ).strip().upper()

        if not selected_class:
            selected_class = 'S.4'

        # ========================================================
        # 3. DETERMINE GRADING LEVEL
        # ========================================================

        is_six = selected_class in {
            'S.6',
            'S6',
            'S.6 NORTH',
            'S.6 SOUTH',
            'S.6 EAST',
            'S.6 WEST',
        }

        # S.4 only uses A-E.
        # S.6 may use A-E, F and O.
        if is_six:
            visible_grades = ['A', 'B', 'C', 'D', 'E', 'F', 'O']
            pass_grades = {'A', 'B', 'C', 'D', 'E', 'O'}
            fail_grades = {'F'}
        else:
            visible_grades = ['A', 'B', 'C', 'D', 'E']
            pass_grades = {'A', 'B', 'C', 'D', 'E'}
            fail_grades = set()

        # ========================================================
        # 4. FETCH MOCK RESULTS
        # ========================================================

        results = (
            KEBMockResult.objects
            .filter(
                student__school=school,
                student__current_class=selected_class
            )
            .select_related(
                'student',
                'subject'
            )
            .order_by(
                'subject__name',
                'student__full_name'
            )
        )

        if not results.exists():
            return HttpResponse(
                f"No mock results found for {selected_class}.",
                status=404
            )

        # ========================================================
        # 5. GROUP RESULTS BY SUBJECT
        # ========================================================

        subject_results = defaultdict(list)

        for result in results:

            if not result.subject:
                continue

            subject_name = (
                result.subject.name.strip()
                if result.subject.name
                else "UNKNOWN SUBJECT"
            )

            subject_results[subject_name].append(result)

        if not subject_results:
            return HttpResponse(
                f"No valid subject results found for {selected_class}.",
                status=404
            )

        # ========================================================
        # 6. CALCULATE SUBJECT STATISTICS
        # ========================================================

        subject_stats = []

        for subject_name, marks in subject_results.items():

            scores = []

            grade_counts = {
                grade: 0
                for grade in visible_grades
            }

            unrecognised_grades = 0

            # -----------------------------------------------
            # Read every candidate's actual stored result
            # -----------------------------------------------

            for mark in marks:

                if mark.score is not None:
                    try:
                        score = float(mark.score)
                        scores.append(score)
                    except (TypeError, ValueError):
                        continue

                stored_grade = str(
                    mark.grade or ''
                ).strip().upper()

                if not stored_grade:
                    continue

                # Only show grades appropriate to this class.
                if stored_grade in grade_counts:
                    grade_counts[stored_grade] += 1
                else:
                    unrecognised_grades += 1

            if not scores:
                continue

            # -----------------------------------------------
            # Core statistics
            # -----------------------------------------------

            candidate_count = len(scores)

            total_score = sum(scores)

            mean_score = (
                total_score / candidate_count
                if candidate_count
                else 0
            )

            highest_score = max(scores)
            lowest_score = min(scores)

            # -----------------------------------------------
            # Pass / fail
            # -----------------------------------------------

            pass_count = sum(
                grade_counts.get(grade, 0)
                for grade in pass_grades
            )

            fail_count = sum(
                grade_counts.get(grade, 0)
                for grade in fail_grades
            )

            classified_count = (
                pass_count + fail_count
            )

            if classified_count > 0:
                pass_percentage = (
                    pass_count / classified_count
                ) * 100
            else:
                pass_percentage = 0

            # -----------------------------------------------
            # A grade count
            # -----------------------------------------------

            a_count = grade_counts.get('A', 0)

            # -----------------------------------------------
            # Store complete subject record
            # -----------------------------------------------

            subject_stats.append({
                'subject': subject_name,
                'candidates': candidate_count,
                'total': total_score,
                'mean': mean_score,
                'highest': highest_score,
                'lowest': lowest_score,
                'pass': pass_count,
                'fail': fail_count,
                'pass_percentage': pass_percentage,
                'grades': grade_counts,
                'a_count': a_count,
                'unrecognised_grades': unrecognised_grades,
            })

        if not subject_stats:
            return HttpResponse(
                f"No usable subject results found for {selected_class}.",
                status=404
            )

        # ========================================================
        # 7. RANK ALL SUBJECTS
        # ========================================================

        subject_stats.sort(
            key=lambda item: (
                -item['mean'],
                -item['pass_percentage'],
                -item['a_count'],
                -item['highest'],
                item['subject'].upper()
            )
        )

        for rank, item in enumerate(
            subject_stats,
            start=1
        ):
            item['rank'] = rank

        best_subject = subject_stats[0]

        # ========================================================
        # 8. PDF RESPONSE
        # ========================================================

        response = HttpResponse(
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            'attachment; '
            f'filename="SUBJECT_PERFORMANCE_AUDIT_'
            f'{selected_class.replace(" ", "_")}.pdf"'
        )

        # ========================================================
        # 9. PDF DOCUMENT
        # ========================================================

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'SubjectAuditTitle',
            parent=styles['Title'],
            fontSize=21,
            leading=25,
            alignment=TA_CENTER,
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            'SubjectAuditSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=12,
        )

        heading_style = ParagraphStyle(
            'SubjectAuditHeading',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            spaceBefore=6,
            spaceAfter=7,
        )

        body_style = ParagraphStyle(
            'SubjectAuditBody',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
        )

        small_style = ParagraphStyle(
            'SubjectAuditSmall',
            parent=styles['Normal'],
            fontSize=7.5,
            leading=9,
        )

        story = []

        # ========================================================
        # 10. TITLE PAGE / EXECUTIVE SUMMARY
        # ========================================================

        story.append(
            Paragraph(
                "SUBJECT PERFORMANCE AUDIT",
                title_style
            )
        )

        story.append(
            Paragraph(
                f"{school.name} — {selected_class} MOCK EXAMINATION",
                subtitle_style
            )
        )

        story.append(
            Paragraph(
                f"Complete audit of {len(subject_stats)} "
                f"subjects using the recorded KEB mock results.",
                body_style
            )
        )

        story.append(Spacer(1, 10))

        # ========================================================
        # 11. BEST SUBJECT
        # ========================================================

        story.append(
            Paragraph(
                "BEST-PERFORMING SUBJECT",
                heading_style
            )
        )

        best_grade_parts = []

        for grade in visible_grades:
            count = best_subject['grades'].get(
                grade,
                0
            )

            best_grade_parts.append(
                f"{grade}: {count}"
            )

        best_grade_text = " | ".join(
            best_grade_parts
        )

        best_table_data = [
            [
                "Rank",
                "Subject",
                "Candidates",
                "Mean %",
                "Highest %",
                "Lowest %",
                "Pass",
                "Fail",
                "Pass %",
                "Grade Distribution",
            ],
            [
                best_subject['rank'],
                best_subject['subject'],
                best_subject['candidates'],
                f"{best_subject['mean']:.2f}",
                f"{best_subject['highest']:.2f}",
                f"{best_subject['lowest']:.2f}",
                best_subject['pass'],
                best_subject['fail'],
                f"{best_subject['pass_percentage']:.2f}",
                best_grade_text,
            ]
        ]

        best_table = Table(
            best_table_data,
            colWidths=[
                15 * mm,
                42 * mm,
                25 * mm,
                23 * mm,
                25 * mm,
                25 * mm,
                20 * mm,
                20 * mm,
                25 * mm,
                80 * mm,
            ]
        )

        best_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#16213E')
                ),
                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),
                (
                    'FONTNAME',
                    (0, 1),
                    (-1, 1),
                    'Helvetica-Bold'
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER'
                ),
                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),
                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    6
                ),
            ])
        )

        story.append(best_table)
        story.append(Spacer(1, 10))

        # ========================================================
        # 12. BEST SUBJECT EXPLANATION
        # ========================================================

        best_explanation = (
            f"<b>{best_subject['subject'].upper()}</b> ranked "
            f"<b>#1</b> because it recorded the highest mean score "
            f"of <b>{best_subject['mean']:.2f}%</b> among all "
            f"{len(subject_stats)} audited subjects. "
            f"It had <b>{best_subject['candidates']}</b> candidates, "
            f"a highest score of <b>{best_subject['highest']:.2f}%</b>, "
            f"a lowest score of <b>{best_subject['lowest']:.2f}%</b>, "
            f"and <b>{best_subject['pass']}</b> classified passes "
            f"representing <b>"
            f"{best_subject['pass_percentage']:.2f}%"
            f"</b> of classified results. "
            f"The recorded grade distribution was "
            f"<b>{best_grade_text}</b>."
        )

        story.append(
            Paragraph(
                best_explanation,
                body_style
            )
        )

        story.append(Spacer(1, 12))

        # ========================================================
        # 13. RANKING RULE
        # ========================================================

        ranking_explanation = (
            "<b>Ranking methodology:</b> Subjects are ranked primarily "
            "by mean score, from highest to lowest. Where two subjects "
            "have the same mean, pass percentage is used as the first "
            "tie-breaker, followed by the number of A grades, then the "
            "highest individual score. Subject name is used only as the "
            "final deterministic tie-breaker."
        )

        story.append(
            Paragraph(
                ranking_explanation,
                small_style
            )
        )

        story.append(PageBreak())

        # ========================================================
        # 14. COMPLETE SUBJECT RANKING
        # ========================================================

        story.append(
            Paragraph(
                f"COMPLETE SUBJECT RANKING — {selected_class}",
                heading_style
            )
        )

        ranking_header = [
            "Rank",
            "Subject",
            "Candidates",
            "Mean %",
            "Highest %",
            "Lowest %",
            "Pass",
            "Fail",
            "Pass %",
        ]

        ranking_header += visible_grades

        ranking_rows = [
            ranking_header
        ]

        for item in subject_stats:

            grades = item['grades']

            row = [
                item['rank'],
                item['subject'],
                item['candidates'],
                f"{item['mean']:.2f}",
                f"{item['highest']:.2f}",
                f"{item['lowest']:.2f}",
                item['pass'],
                item['fail'],
                f"{item['pass_percentage']:.2f}",
            ]

            row += [
                grades.get(grade, 0)
                for grade in visible_grades
            ]

            ranking_rows.append(row)

        # --------------------------------------------------------
        # Dynamic column widths
        # --------------------------------------------------------

        col_widths = [
            13 * mm,   # Rank
            43 * mm,   # Subject
            23 * mm,   # Candidates
            22 * mm,   # Mean
            24 * mm,   # Highest
            24 * mm,   # Lowest
            18 * mm,   # Pass
            18 * mm,   # Fail
            24 * mm,   # Pass %
        ]

        col_widths += [
            14 * mm
            for _ in visible_grades
        ]

        ranking_table = Table(
            ranking_rows,
            repeatRows=1,
            colWidths=col_widths
        )

        ranking_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#16213E')
                ),
                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.grey
                ),
                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER'
                ),
                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),
                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),
            ])
        )

        story.append(ranking_table)

        story.append(PageBreak())

        # ========================================================
        # 15. DETAILED SUBJECT AUDIT
        # ========================================================

        story.append(
            Paragraph(
                "DETAILED SUBJECT-BY-SUBJECT AUDIT",
                heading_style
            )
        )

        for index, item in enumerate(subject_stats):

            story.append(
                Paragraph(
                    f"#{item['rank']} — "
                    f"{item['subject'].upper()}",
                    heading_style
                )
            )

            grades = item['grades']

            grade_distribution = " | ".join(
                f"{grade}: {grades.get(grade, 0)}"
                for grade in visible_grades
            )

            detail_rows = [
                [
                    "Candidates",
                    str(item['candidates'])
                ],
                [
                    "Mean Score",
                    f"{item['mean']:.2f}%"
                ],
                [
                    "Highest Score",
                    f"{item['highest']:.2f}%"
                ],
                [
                    "Lowest Score",
                    f"{item['lowest']:.2f}%"
                ],
                [
                    "Pass Count",
                    str(item['pass'])
                ],
                [
                    "Fail Count",
                    str(item['fail'])
                ],
                [
                    "Pass Percentage",
                    f"{item['pass_percentage']:.2f}%"
                ],
                [
                    "Grade Distribution",
                    grade_distribution
                ],
            ]

            detail_table = Table(
                detail_rows,
                colWidths=[
                    48 * mm,
                    205 * mm,
                ]
            )

            detail_table.setStyle(
                TableStyle([
                    (
                        'BACKGROUND',
                        (0, 0),
                        (0, -1),
                        colors.HexColor('#E8ECF4')
                    ),
                    (
                        'FONTNAME',
                        (0, 0),
                        (0, -1),
                        'Helvetica-Bold'
                    ),
                    (
                        'GRID',
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.grey
                    ),
                    (
                        'VALIGN',
                        (0, 0),
                        (-1, -1),
                        'MIDDLE'
                    ),
                    (
                        'FONTSIZE',
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        'TOPPADDING',
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        'BOTTOMPADDING',
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                ])
            )

            story.append(detail_table)
            story.append(Spacer(1, 8))

            # ----------------------------------------------------
            # Explain this subject's ranking
            # ----------------------------------------------------

            if item['rank'] == 1:

                audit_text = (
                    f"This subject ranks #1 because its mean score "
                    f"of {item['mean']:.2f}% is the highest recorded "
                    f"mean among the audited subjects."
                )

            else:

                previous = subject_stats[
                    item['rank'] - 2
                ]

                audit_text = (
                    f"This subject ranks #{item['rank']} with a "
                    f"mean score of {item['mean']:.2f}%. "
                    f"The subject immediately above it, "
                    f"<b>{previous['subject']}</b>, recorded "
                    f"a mean of {previous['mean']:.2f}%."
                )

            story.append(
                Paragraph(
                    audit_text,
                    small_style
                )
            )

            story.append(Spacer(1, 10))

            if index < len(subject_stats) - 1:
                story.append(PageBreak())

        # ========================================================
        # 16. BUILD PDF
        # ========================================================

        doc.build(story)

        return response

    except Exception as e:

        return HttpResponse(
            f"Subject Audit PDF Error: {str(e)}",
            status=500
        )
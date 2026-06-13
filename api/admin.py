import json 
from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models import Sum, Avg, F 
from datetime import timedelta
from .models import *


def dossier_button(obj):
    # 💎 THE MASTER URL: Points to the Brain's PDF generator
    # We use '/api/' because that is the gateway to the logic
    url = f"/api/staff-dossier/{obj.staff_id}/"
    
    return mark_safe(f'''
        <a href="{url}" 
           target="_blank" 
           style="background-color: #002366; 
                  color: white; 
                  padding: 8px 15px; 
                  border-radius: 8px; 
                  font-weight: bold; 
                  text-decoration: none;
                  border: 1px solid #D4AF37;">
           📂 OPEN DOSSIER
        </a>
    ''')
dossier_button.short_description = 'HR Archive'


class StaffAdmin(admin.ModelAdmin):
    # 💎 1. THE VIEW: Scannable columns in the list
    list_display = ('full_name', 'designation', 'school', 'staff_id', dossier_button)
    search_fields = ('full_name', 'staff_id', 'tin_number')
    list_filter = ('school', 'designation')

    # 💎 2. THE CATEGORIZED TABS (The 'Fieldsets' logic)
    # This physically separates CVs and IDs from basic names
    fieldsets = (
        ('👤 CORE IDENTITY', {
            'fields': ('full_name', 'designation', 'school', 'staff_id')
        }),
        ('📂 OFFICIAL DOCUMENTATION', {
            'description': "Legal bio-metrics and career documents",
            'classes': ('collapse',), # Collapsible for prestige
            'fields': ('passport_photo', 'national_id_copy', 'cv_pdf')
        }),
        ('🏛️ GOVT COMPLIANCE', {
            'description': "URA Tax and NSSF Regulatory info",
            'fields': ('tin_number', 'nssf_number')
        }),
        ('📞 CONTACT & SECURITY', {
            'fields': ('phone', 'momo_number', 'secure_pin', 'next_of_kin', 'next_of_kin_phone')
        }),
    )

    readonly_fields = ('staff_id',)

    # 📥 THE DOSSIER BUTTON (Inside the list)
    def dossier_button_link(self, obj):
        return mark_safe(f'<a href="/api/staff-dossier/{obj.staff_id}/" target="_blank" style="background-color: #002366; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; text-decoration: none;">Download Dossier</a>')
    dossier_button_link.short_description = 'HR Archive'


class SchoolIsolatedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: # 💎 THE KING SEES ALL
            return qs
        if request.user.school:
            return qs.filter(school=request.user.school)
        return qs.none() # 🛡️ Others see nothing

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and hasattr(request.user, 'school'):
            obj.school = request.user.school
        super().save_model(request, obj, form, change)

admin.site.site_header = "UNSCCDC NATIONAL HUB - COMMAND CENTER"

class ImperialAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        # We manually set these to zero so the system doesn't look at the database yet
        extra_context['enterprise_stats'] = {
            'enrollment': "0", 'attendance': "0%", 'collection': "0%", 'milestone': "Registry Offline"
        }
        return super().index(request, extra_context)

admin.site = ImperialAdminSite()

# --- 📊 1. ACADEMIC RESULTS --
@admin.register(AcademicResult)
class AcademicResultAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'subject', 'aoi_1', 'mid_term', 'eot_score', 'project_work')
    def student_name(self, obj): return obj.student.full_name

class MarksInline(admin.TabularInline):
    model = AcademicResult
    # 💎 THE POWER GRID: All assessment fields in one horizontal row!
    fields = ('subject', 'aoi_1', 'aoi_2', 'mid_term', 'aoi_3', 'aoi_4', 'project_work', 'eot_score', 'grade')
    extra = 1 # Shows one empty row for new subjects
    classes = ['collapse'] # Keeps it neat

# --- ⚡ 1. THE BULK DOWNLOAD TOOL ---
@admin.action(description='⚡ DOWNLOAD NATIONAL REPORTS (PDF)')
def export_as_pdf(modeladmin, request, queryset):
    from django.shortcuts import redirect
    if queryset.count() == 1:
        student = queryset.first()
        return redirect(f'/api/download-report/{student.account_number}/')
    else:
        from django.contrib import messages
        modeladmin.message_user(request, "Select one student for instant download.", level='ERROR')

def download_button(obj):
    return mark_safe(f'<a href="/api/download-report/{obj.account_number}/" target="_blank" style="background-color: #D4AF37; color: black; padding: 5px 10px; border-radius: 8px; font-weight: bold; text-decoration: none;">Download PDF</a>')

class MarksInline(admin.TabularInline):
    model = AcademicResult
    # 💎 THE MATRIX LOGIC: Shows all 7 assessment fields in a horizontal line
    fields = ('subject', 'aoi_1', 'aoi_2', 'mid_term', 'aoi_3', 'aoi_4', 'project_work', 'eot_score', 'grade')
    extra = 0 # Don't show empty rows by default
    classes = ['collapse'] # Only show when clicking 'Show'


class AcademicResultsHubAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'account_number', 'school', 'current_class', 'download_report_button')
    search_fields = ('full_name', 'account_number')
    inlines = [MarksInline] # 💎 THIS allows adding all marks at once!

    def download_report_button(self, obj):
        # 💎 FIXED URL: Ensuring it points to /api/
        return mark_safe(f'<a href="/api/download-report/{obj.account_number}/" target="_blank" style="background:#D4AF37; color:#000; padding:5px 12px; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD PDF</a>')
    download_report_button.short_description = "National Report"

admin.site.register(AcademicResultsCenter, AcademicResultsHubAdmin)

class NationalLedgerAdmin(SchoolIsolatedAdmin):
    # 💎 THE VIEW: Every name in this list MUST be a method or a model field
    list_display = (
        'txn_id_display', 
        'school', 
        'child_name', 
        'category', 
        'amount_paid', 
        'timestamp'
    )
    
    # 🛡️ THE AUDIT LOCK (Makes it uneditable)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
    
    # --- 🧮 LIVE ALIGNMENT METHODS ---

    def txn_id_display(self, obj):
        # 💎 THE KEY FIX: We check multiple possible names (transaction_id or receipt_number)
        # to ensure the error never returns!
        val = getattr(obj, 'transaction_id', None) or getattr(obj, 'receipt_number', None) or str(obj.id)
        return mark_safe(f'<b style="color:#D4AF37; font-family:monospace;">{val}</b>')
    txn_id_display.short_description = "Transaction ID"

    def child_name(self, obj):
        # Pulls the student name from the linked student record
        return obj.student.full_name.upper() if obj.student else "National Deposit"
    child_name.short_description = "Student"

    # Ensure this matches your model field (amount_paid)
    def amount_paid_display(self, obj):
        return f"UGX {obj.amount_paid:,.0f}"

@admin.register(CommissionAnalytics)
class CommissionAnalyticsAdmin(SchoolIsolatedAdmin):
    list_display = ('name', 'district', 'total_revenue', 'my_commission')
    def total_revenue(self, obj):
        rev = Transaction.objects.filter(school=obj).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        return f"UGX {rev:,}"
    def my_commission(self, obj):
        com = Transaction.objects.filter(school=obj).aggregate(Sum('system_tax'))['system_tax__sum'] or 0
        return f"UGX {com:,}"
    def changelist_view(self, request, extra_context=None):
        now = timezone.now(); today = now.date(); all_txns = Transaction.objects.all()
        extra_context = extra_context or {}
        extra_context['daily_comm'] = all_txns.filter(timestamp__date=today).aggregate(Sum('system_tax'))['system_tax__sum'] or 0
        extra_context['annual_comm'] = all_txns.filter(timestamp__date__year=today.year).aggregate(Sum('system_tax'))['system_tax__sum'] or 0
        return super().changelist_view(request, extra_context=extra_context)
    def has_add_permission(self, request): return False
    # --- ⚔️ THE TREASURY LOCKS: NO ONE CAN TOUCH YOUR MONEY ⚔️ ---
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(AttendanceHub)
class AttendanceHubAdmin(SchoolIsolatedAdmin):
    list_display = ('student', 'get_class', 'get_stream', 'date', 'status', 'remarks')
    list_filter = ('date', 'status', 'student__school', 'student__current_class')
    search_fields = ('student__full_name', 'student__account_number')
    
    # 💎 THE POWER FEATURE: Teachers can mark 'Present/Absent' with one click here!
    list_editable = ('status', 'remarks') 
    
    def get_class(self, obj): return obj.student.current_class
    def get_stream(self, obj): return obj.student.stream
    get_class.short_description = "Class"
    get_stream.short_description = "Stream"


class FeesTrackerAdmin(admin.ModelAdmin):
    # 💎 THE VIEW: Scannable Financial Columns
    # We ensure every name here matches a method defined below
    list_display = (
        'student', 
        'total_invoiced', 
        'total_paid', 
        'remaining_balance', 
        'payment_percentage'
    )
    
    list_filter = ('student__school', 'student__current_class')
    search_fields = ('student__full_name', 'student__account_number')
    
    # 🛡️ THE AUDIT LOCK
    readonly_fields = ('remaining_balance', 'payment_percentage')

    # --- 🧮 LIVE FINANCIAL MATH ENGINES ---

    def total_invoiced(self, obj):
        # Format the Fees Due with UGX and commas
        return f"UGX {obj.total_fees_due:,.0f}"
    total_invoiced.short_description = "Invoiced"

    def total_paid(self, obj):
        # 💎 THE KEY FIX: Physically defining the 'total_paid' column
        # Using 'total_fees_paid' from your model
        return f"UGX {obj.total_fees_paid:,.0f}"
    total_paid.short_description = "Total Paid"

    def remaining_balance(self, obj):
        # Calculates the debt in real-time
        balance = obj.total_fees_due - obj.total_fees_paid
        color = "#D90000" if balance > 0 else "#00ff00"
        return mark_safe(f'<b style="color:{color};">UGX {balance:,.0f}</b>')
    remaining_balance.short_description = "Balance"

    def payment_percentage(self, obj):
        # Calculates the progress of the parent's payment
        if obj.total_fees_due > 0:
            percent = (obj.total_fees_paid / obj.total_fees_due) * 100
            return f"{percent:.1f}%"
        return "0%"
    payment_percentage.short_description = "Progress"
admin.site.register(FeesTracker, FeesTrackerAdmin)


@admin.register(SchoolPost)
class SchoolPostAdmin(SchoolIsolatedAdmin):
    list_display = ('title', 'school', 'likes_count', 'date')
    search_fields = ('title', 'description', 'school__name')

# --- 🏛️ 5. OTHER REGISTRIES ---
admin.site.register([
    Subject, 
    Parent,
    Student, 
    AcademicResult,
    AttendanceHub, 
    StaffPayroll,
    SchoolPost, 
    User,
    NationalTopPerformer, 
    BioAndCareer, 
    SovereignProfessionalInsights,
    CommissionAnalytics
    ])

admin.site.register(NationalLedger, NationalLedgerAdmin)
admin.site.register(Staff, StaffAdmin)

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_code', 'district', 'is_verified')
    
    # 💎 THE CATEGORIZED TABS (FIELDSETS)
    fieldsets = (
        ('🏢 INSTITUTIONAL PROFILE', {
            'fields': ('name', 'director', 'address', 'district', 'school_motto', 'uneb_center_number')
        }),
        ('📟 USSD GATEWAY INSTRUCTIONS', {
            'description': "What parents see when they dial *165#",
            'fields': ('ussd_instructions',)
        }),
        ('🔒 SCHOOLPAY HIGH-SECURITY API', {
            'description': "Bank-Level Gateway Credentials",
            'fields': ('school_code', 'api_password', 'total_revenue_collected', 'total_commission_earned')
        }),
    )
    readonly_fields = ('total_revenue_collected', 'total_commission_earned')
admin.site.register(School, SchoolAdmin)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'account_number', 'school', 'current_class', 'fee_status_badge')
    search_fields = ('full_name', 'account_number')
    
    # 💎 THE VAULT: Categorizing information
    fieldsets = (
        ('👤 STUDENT IDENTITY', {
            'fields': ('full_name', 'account_number', 'school', 'current_class', 'stream', 'gender')
        }),
        ('🎓 ACADEMIC TRACKING', {
            'fields': ('enrollment_status', 'academic_standing')
        }),
        # 🛡️ API Credentials are GONE from here!
    )

    def fee_status_badge(self, obj):
        # Shows a visual dot if they owe money
        return mark_safe('<span style="color:green;">● Cleared</span>')

def dossier_button(obj):
    # 💎 FIXED URL: Must start with /api/ to avoid 404
    url = f"/api/staff-dossier/{obj.staff_id}/"
    return mark_safe(f'<a href="{url}" target="_blank" style="background:#002366; color:#fff; padding:5px 12px; border-radius:10px; font-weight:bold; text-decoration:none;">📂 OPEN DOSSIER</a>')
    
def payslip_button(obj):
    url = f"/api/download-payslip/{obj.id}/"
    return mark_safe(f'''
        <a href="{url}" 
           target="_blank" 
           style="background-color: #D4AF37; 
                  color: black; 
                  padding: 6px 12px; 
                  border-radius: 6px; 
                  font-weight: bold; 
                  text-decoration: none;">
           📄 Download Slip
        </a>
    ''')
payslip_button.short_description = 'Finance Action'

# --- 🛰️ 1. THE ASSIGNMENT INLINE ---
class AssignmentInline(admin.TabularInline):
    model = SubjectAssignment
    extra = 1
    verbose_name = "Academic Workload"


@admin.register(StaffPayroll)
class StaffPayrollAdmin(SchoolIsolatedAdmin):
    list_display = ('staff', 'month', 'gross_salary', 'paye_tax', 'nssf_deduction', 'net_pay', 'status')
    list_filter = ('month', 'status', 'staff__school')
    
    # 💎 ADD ACTION TO DOWNLOAD SLIP
    actions = ['download_payslips']

    @admin.action(description='📄 Generate Digital Payslips')
    def download_payslips(self, request, queryset):
        # Logic to trigger PDF payslip generation
        pass


class SchoolPayLedgerAdmin(admin.ModelAdmin):
    # 💎 THE COLUMNS: Every detail you requested
    list_display = (
        'transaction_id_badge', 
        'student_name', 
        'code_number', 
        'reason_for_payment',
        'amount_paid', 
        'remaining_balance',
        'channel_badge', 
        'timestamp'
    )
    
    list_filter = ('school', 'timestamp')
    search_fields = ('receipt_number', 'student__full_name', 'student__payment_code')
    
    # 🛡️ THE SOVEREIGN LOCKDOWN (HARD-LOCK)
    # This physically removes all "Add", "Delete", and "Save" buttons
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
    
    # All fields become non-clickable "Read-Only" views
    readonly_fields = [f.name for f in SchoolPayLedger._meta.fields]

    # --- 🧮 LIVE CALCULATION METHODS ---

    def transaction_id_badge(self, obj):
        return mark_safe(f'<b style="color:#D4AF37; font-family:monospace;">{obj.receipt_number}</b>')
    transaction_id_badge.short_description = "TXN ID"

    def student_name(self, obj):
        return obj.student.full_name.upper()
    student_name.short_description = "Student Name"

    def code_number(self, obj):
        return mark_safe(f'<span style="color:#aaa;">{obj.student.payment_code}</span>')
    code_number.short_description = "Code (PRN)"

    def reason_for_payment(self, obj):
        # Dynamically extracts the reason from the bank metadata
        reason = obj.raw_data.get('narration', 'Tuition & Functional Fees')
        return reason.upper()
    reason_for_payment.short_description = "Reason"

    def amount_paid(self, obj):
        return mark_safe(f'<span style="color:#00ff00; font-weight:bold;">{obj.amount:,.0f} UGX</span>')
    amount_paid.short_description = "Paid"

    def remaining_balance(self, obj):
        # 💎 THE MATH: Finds the student's debt and subtracts what was paid
        try:
            tracker = obj.student.feestracker_set.first()
            if tracker:
                balance = tracker.total_fees_due - tracker.total_fees_paid
                color = "#D90000" if balance > 0 else "#00ff00"
                return mark_safe(f'<b style="color:{color};">{balance:,.0f} UGX</b>')
        except:
            pass
        return "0 UGX"
    remaining_balance.short_description = "Balance"

    def channel_badge(self, obj):
        channel = obj.raw_data.get('sourceChannel', 'BANK').upper()
        color = "#FCDC04" if "MTN" in channel else "#D90000"
        t_color = "#000" if "MTN" in channel else "#fff"
        return mark_safe(f'<span style="background:{color}; color:{t_color}; padding:2px 10px; border-radius:15px; font-size:9px; font-weight:900;">{channel}</span>')
    channel_badge.short_description = "Method"

admin.site.register(SchoolPayLedger, SchoolPayLedgerAdmin)


class FinancialCommandAdmin(admin.ModelAdmin):
    change_list_template = "admin/api/financialcommandcenter/change_list.html"
    
    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        today = now.date()
        three_days_ago = today - timedelta(days=3)
        
        # 1. ENROLLMENT & GENDER MATH
        total_students = Student.objects.count()
        males = Student.objects.filter(gender='M').count()
        females = Student.objects.filter(gender='F').count()
        
        # 2. FINANCIAL BEHAVIOR (Banking Logic)
        fees = FeesTracker.objects.all()
        # Elite Payers: Paid more than 80%
        elite_payers = fees.filter(total_fees_paid__gte=F('total_fees_due')*0.8).count()
        # Defaulters: Paid less than 20%
        defaulters = fees.filter(total_fees_paid__lt=F('total_fees_due')*0.2).count()

        # 3. PERFORMANCE TRENDS (Progressing vs Declining)
        # Average score this term vs target
        avg_data = AcademicResult.objects.aggregate(Avg('eot_score'))
        avg_score = avg_data['eot_score__avg'] if avg_data['eot_score__avg'] is not None else 0
        trend = "PROGRESSING ↑" if avg_score > 65 else "DECLINING ↓"

        # 4. STAFF ANALYTICS
        total_staff = Staff.objects.count()
        staff_male = Staff.objects.filter(gender='M').count()
        staff_female = Staff.objects.filter(gender='F').count()

        # 🛡️ 5. EMERGENCY ALERTS (Absent for 3 days)
        # Find students who have NO 'Present' records in the last 3 days
        from .models import Attendance
        present_recently = Attendance.objects.filter(date__gte=three_days_ago, status=True).values_list('student_id', flat=True)
        missing_students = Student.objects.exclude(id__in=present_recently)[:5] # Show top 5 missing

        # 🤖 6. SOVEREIGN SOLUTIONS (AI INSIGHTS)
        solutions = []
        if avg_score < 50: solutions.append("⚠️ ACADEMIC CRISIS: Initiate mandatory remedial hours.")
        if defaulters > (total_students * 0.3): solutions.append("💸 REVENUE LEAK: Deploy SMS Automated debt reminders.")
        if total_staff > (total_students / 10): solutions.append("💼 PAYROLL WARNING: High staff-to-student ratio detected.")

        extra_context = extra_context or {}
        extra_context['intel'] = {
            'total': total_students, 'm': males, 'f': females,
            'elite': elite_payers, 'defaulters': defaulters,
            'avg': f"{avg_score:.1f}%", 'trend': trend,
            'staff_total': total_staff, 'sm': staff_male, 'sf': staff_female,
            'missing': missing_students, 'solutions': solutions
        }
        
        # 7. CHART DATA (JSON)
        extra_context['gender_json'] = json.dumps([males, females])
        extra_context['pay_json'] = json.dumps([elite_payers, defaulters, (total_students - elite_payers - defaulters)])
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(FinancialCommandCenter, FinancialCommandAdmin)
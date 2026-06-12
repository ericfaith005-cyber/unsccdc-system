import json 
from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
from .models import *
from .models import (
    Student, School, Parent, FeesTracker, 
    SchoolPayLedger, AcademicResult, NationalTopPerformer, SchoolPost, BioAndCareer, Staff, StaffPayroll, 
    FinancialCommandCenter, AcademicResultsCenter, NationalLedger, CommissionAnalytics, 
    AttendanceHub, 
)
# --- 🛡️ SURGERY: THE INDESTRUCTIBLE SECURITY GUARD (api/admin.py) ---

class SchoolIsolatedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 👑 THE FIX: If it's YOU (Superuser), bypass all filters!
        if request.user.is_superuser:
            return qs
        # 🏢 If it's a regular admin, they MUST have a school
        if hasattr(request.user, 'school') and request.user.school:
            return qs.filter(school=request.user.school)
        # 🛡️ If they are not a superuser and have no school, show nothing
        return qs.none()

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
    fields = ('subject', 'aoi_1', 'aoi_2', 'mid_term', 'aoi_3', 'aoi_4', 'eot_score', 'project_work')
    extra = 1

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

@admin.register(AcademicResultsCenter)
class AcademicResultsHubAdmin(SchoolIsolatedAdmin):
    # 💎 Add the bulk action tool here
    actions = [export_as_pdf] 
    
    # 💎 Add 'download_button' to the end of this list
    list_display = ('full_name', 'account_number', 'school', 'current_class', 'stream', 'national_rank', download_button)
    
    search_fields = ('full_name', 'account_number')
    inlines = [MarksInline]

    def national_rank(self, obj):
        return mark_safe('<span style="color: #00ff00; font-weight:bold;">Top 5%</span>')
    

@admin.register(NationalLedger)
class NationalLedgerAdmin(SchoolIsolatedAdmin):
    list_display = ('transaction_id', 'school', 'child_name', 'category', 'amount_paid', 'system_tax', 'timestamp')
    readonly_fields = ('transaction_id', 'school', 'student', 'category', 'amount_paid', 'system_tax', 'timestamp')
    def child_name(self, obj): return obj.student.full_name if obj.student else "N/A"
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

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

# --- 📱 4. HD TIKTOK FEED (RESTORED) ---
@admin.register(SchoolPost)
class SchoolPostAdmin(SchoolIsolatedAdmin):
    list_display = ('title', 'school', 'likes_count', 'date')
    search_fields = ('title', 'description', 'school__name')

# --- 🏛️ 5. OTHER REGISTRIES ---
admin.site.register([
    Subject, 
    Parent,
    School,
    StaffAdmin, 
    Student, 
    AcademicResult,
    AttendanceHub, 
    StaffPayroll,
    SchoolPayLedger,
    AcademicResultsCenter,
    SchoolPost, 
    FeesTracker, 
    User,
    NationalTopPerformer, 
    BioAndCareer, 
    NationalLedger,
    SovereignProfessionalInsights,
    CommissionAnalytics,
    FinancialCommandCenter
    ])


# --- 🛡️ SURGERY: RESTORING ALL REGISTRY WINDOWS (api/admin.py) ---

@admin.register(School)
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

@admin.register(Student)
class StudentAdmin(SchoolIsolatedAdmin): # 💎 SHIELD ACTIVE
    
    list_display = ('full_name', 'account_number', 'payment_code', 'school', 'current_class')
    # Add PRN to the 'Edit' page
    fields = ('full_name', 'gender', 'age', 'current_class', 'school', 'level_category', 'payment_code', 'photo')
    readonly_fields = ('account_number',)

def dossier_button(obj):
    # We added 'http://127.0.0.1:8001' to force the computer to find the Brain
    url = f"/api/staff-dossier/{obj.staff_id}/"
    return mark_safe(f'''
        <a href="{url}" 
           target="_blank" 
           style="background-color: #002366; 
                  color: white; 
                  padding: 8px 15px; 
                  border-radius: 6px; 
                  font-weight: bold; 
                  text-decoration: none; 
                  display: inline-block;">
           📥 Download Dossier
        </a>
    ''')
dossier_button.short_description = 'HR ARCHIVE'

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

# =============================================================
# 👔 THE IMPERIAL HR COMMAND (STAFF DOSSIER REGISTRY)
# =============================================================
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    # 1. THE VIEW: High-level scannable columns
    list_display = ('full_name', 'designation', 'school', 'staff_id', 'tin_number')
    search_fields = ('full_name', 'staff_id', 'tin_number')
    list_filter = ('school', 'designation')

    # 💎 2. THE CATEGORIZED FIELDSETS (The Organize logic)
    fieldsets = (
        ('👤 CORE IDENTITY', {
            'description': "Basic profile and institutional designation",
            'fields': (('full_name', 'designation'), 'school', 'staff_id')
        }),
        ('📂 OFFICIAL DOCUMENTATION', {
            'description': "Legal bio-metrics and career documents",
            'fields': ('passport_photo', 'national_id_copy', 'cv_pdf')
        }),
        ('🏛️ GOVERNMENT COMPLIANCE', {
            'description': "URA Tax and NSSF Regulatory information",
            'fields': (('tin_number', 'nssf_number'),)
        }),
        ('📞 COMMUNICATION & KINSHIP', {
            'description': "Contact registry and emergency protocols",
            'fields': ('phone', 'next_of_kin', 'next_of_kin_phone')
        }),
        ('🔒 SECURITY & PAYMENTS', {
            'description': "Financial uplink and secure access credentials",
            'fields': (('momo_number', 'secure_pin'),)
        }),
    )

    # Make the ID and certain fields read-only to prevent accidental tampering
    readonly_fields = ('staff_id',)

    # 🛰️ Layout Trick: Grouping fields on the same line using tuples ( )

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

# =============================================================
# 💰 THE IMPERIAL NATIONAL AUDIT LEDGER (LEVEL 10,000)
# =============================================================
@admin.register(SchoolPayLedger)
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

@admin.register(FinancialCommandCenter)
class FinancialCommandAdmin(SchoolIsolatedAdmin):
    # This path must match your folder structure exactly!
    change_list_template = "admin/api/financialcommandcenter/change_list.html"
    
    list_display = ('name', 'district', 'current_term_subtotal', 'total_national_revenue')
    
    list_filter = ('district', 'school_type', 'is_verified') 
    search_fields = ('name', 'school_account_id', 'district')

    # =============================================================
    # 🧮 THE GOLIATH MATHEMATICAL FORMULAS (KILLS E108 ERRORS)
    # =============================================================
    
    def current_term_subtotal(self, obj):
        """Calculates rolling 120-day termly revenue for this specific school row"""
        term_start = timezone.now() - timedelta(days=120)
        # We look into the SchoolPayLedger to find payments for THIS school row
        total = SchoolPayLedger.objects.filter(
            school=obj, 
            timestamp__gte=term_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return f"UGX {total:,.0f}"
    
    # Tells the dashboard what name to show at the top of the column
    current_term_subtotal.short_description = "Termly Sub-Total"

    def total_national_revenue(self, obj):
        """Calculates total all-time collection for this specific school row"""
        total = SchoolPayLedger.objects.filter(
            school=obj
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return f"UGX {total:,.0f}"
    
    total_national_revenue.short_description = "Total Collected"

    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        today = now.date()
        txs = SchoolPayLedger.objects.all()
        
        extra_context = extra_context or {}

        # 1. 🧮 GOLIATH MATHEMATICS
        extra_context['daily_sub'] = txs.filter(timestamp__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        extra_context['weekly_sub'] = txs.filter(timestamp__date__gte=today - timedelta(days=7)).aggregate(Sum('amount'))['amount__sum'] or 0
        extra_context['monthly_sub'] = txs.filter(timestamp__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0
        extra_context['termly_sub'] = txs.filter(timestamp__date__gte=today - timedelta(days=120)).aggregate(Sum('amount'))['amount__sum'] or 0

        # 2. 📈 TREND CHART (7 DAYS)
        bar_data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            amt = txs.filter(timestamp__date=d).aggregate(Sum('amount'))['amount__sum'] or 0
            bar_data.append({"x": d.strftime('%a'), "y": float(amt)})
        extra_context['bar_json'] = json.dumps(bar_data)

        # 3. 📱 PIE CHART (NETWORK DISTRIBUTION)
        # Assuming SchoolPay sends 'MTN' or 'AIRTEL' in raw_data
        mtn = txs.filter(raw_data__sourceChannel__icontains="MTN").count()
        airtel = txs.filter(raw_data__sourceChannel__icontains="AIRTEL").count()
        other = max(0, txs.count() - (mtn + airtel))
        extra_context['pie_data_json'] = json.dumps([mtn, airtel, other])

        return super().changelist_view(request, extra_context=extra_context)
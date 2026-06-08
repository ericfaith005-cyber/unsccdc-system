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
# --- 🛡️ THE SOVEREIGN SECURITY GUARD (Base Class) ---
class SchoolIsolatedAdmin(admin.ModelAdmin):
    """
    This class ensures that users only see data belonging 
    to their assigned school. The King (Superuser) sees everything.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 1. If it's YOU (The King/Superuser), show the whole Nation
        if request.user.is_superuser:
            return qs
        # 2. If it's a School Director/Bursar, filter by THEIR school
        if request.user.school:
            return qs.filter(school=request.user.school)
        # 3. If they have no school assigned, show nothing (Security!)
        return qs.none()

    def save_model(self, request, obj, form, change):
        # Automatically attach the user's school to any new record they create
        if not request.user.is_superuser and request.user.school:
            obj.school = request.user.school
        super().save_model(request, obj, form, change)

admin.site.site_header = "UNSCCDC NATIONAL HUB - COMMAND CENTER"

class ImperialAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        # 🛡️ Comment these out for now so the migration can finish
        # total_students = Student.objects.count() 
        extra_context['enterprise_stats'] = {
            'enrollment': 0,
            'attendance': "0%",
            'collection': "0%",
            'milestone': "Initializing..."
        }
        return super().index(request, extra_context)

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
    """Adds a golden download button to the list view"""
    return mark_safe(f'<a href="/api/download-report/{obj.account_number}/" target="_blank" style="background-color: #D4AF37; color: black; padding: 6px 12px; border-radius: 8px; font-weight: bold; text-decoration: none;">Download PDF</a>')
download_button.short_description = 'Action'

@admin.register(AcademicResultsCenter)
class AcademicResultsHubAdmin(SchoolIsolatedAdmin):
    # 💎 Add the bulk action tool here
    actions = [export_as_pdf] 
    
    # 💎 Add 'download_button' to the end of this list
    list_display = ('full_name', 'account_number', 'school', 'current_class', download_button)
    
    search_fields = ('full_name', 'account_number')
    inlines = [MarksInline]

# --- 🛡️ 2. UNEDITABLE NATIONAL LEDGER ---
@admin.register(NationalLedger)
class NationalLedgerAdmin(SchoolIsolatedAdmin):
    list_display = ('transaction_id', 'school', 'child_name', 'category', 'amount_paid', 'system_tax', 'timestamp')
    readonly_fields = ('transaction_id', 'school', 'student', 'category', 'amount_paid', 'system_tax', 'timestamp')
    def child_name(self, obj): return obj.student.full_name if obj.student else "N/A"
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

# --- 💰 3. COMMISSION ANALYTICS DASHBOARD ---
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

# --- ✅ ADD TO api/admin.py ---

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
admin.site.register([Subject, Parent, FeesTracker, NationalTopPerformer, BioAndCareer, SovereignProfessionalInsights ])


# --- 🛡️ SURGERY: RESTORING ALL REGISTRY WINDOWS (api/admin.py) ---

@admin.register(School)
class SchoolAdmin(SchoolIsolatedAdmin):
    # What you see in the main list
    list_display = ('name', 'uneb_center_number', 'school_code', 'district', 'total_revenue_collected')
    
    # --- 🏗️ HOW THE EDIT PAGE IS ORGANIZED ---
    fieldsets = (
        ('CORE IDENTITY', {
            'fields': ('name', 'director', 'address', 'district', 'school_motto', 'uneb_center_number')
        }),
        ('PRESTIGE & BRANDING', {
            'fields': ('school_type', 'rating', 'mission', 'vision', 'core_values', 'is_verified', 'followers_count')
        }),
        ('USSD GATEWAY SETTINGS', {
            'fields': ('ussd_instructions',)
        }),
        ('SCHOOLPAY API CREDENTIALS', {
            'fields': ('school_code', 'api_password', 'total_revenue_collected', 'total_commission_earned')
        }),
    )
    readonly_fields = ('school_account_id', 'total_revenue_collected', 'total_commission_earned')
@admin.register(Student)
class StudentAdmin(SchoolIsolatedAdmin): # 💎 SHIELD ACTIVE
    
    list_display = ('full_name', 'account_number', 'payment_code', 'school', 'current_class')
    # Add PRN to the 'Edit' page
    fields = ('full_name', 'gender', 'age', 'current_class', 'school', 'level_category', 'payment_code', 'photo')
    readonly_fields = ('account_number',)

# --- 🛡️ SURGERY: HR MANAGER DASHBOARD (api/admin.py) ---
# --- 🛡️ SURGERY: HR DOSSIER DOWNLOAD BUTTON ---

# --- 🛡️ SURGERY: ABSOLUTE DOWNLOAD LINK ---
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

@admin.register(Staff)
class StaffAdmin(SchoolIsolatedAdmin):
    # The Executive View
    list_display = ('full_name', 'designation', 'school', dossier_button)
    list_display = ('full_name', 'designation', 'tin_number', 'nssf_number', 'school')
    search_fields = ('full_name', 'tin_number', 'nssf_number')
    
    # 📂 ORGANIZED HR TABS
    fieldsets = (
        ('PERSONAL BIOMETRICS', {
            'fields': ('full_name', 'passport_photo', 'national_id_copy', 'cv_pdf')
        }),
        ('GOVERNMENT REGISTRY', {
            'fields': ('tin_number', 'nssf_number', 'designation')
        }),
        ('SECURITY & CONTACT', {
            'fields': ('secure_pin', 'phone', 'momo_number', 'next_of_kin', 'next_of_kin_phone', 'school')
        }),
    )
# --- 🛡️ 1. THE PAYSLIP BUTTON WORKER (PASTE ABOVE THE CLASS) ---
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
@admin.register(SchoolPayLedger)
class SchoolPayLedgerAdmin(SchoolIsolatedAdmin):
    # What to show in the list view
    list_display = ('receipt_number', 'get_student_name', 'get_school_name', 'amount', 'timestamp')
    
    # Powerful filters for the Bursar/King
    list_filter = ('school', 'timestamp')
    search_fields = ('receipt_number', 'student__full_name', 'student__payment_code')
    
    # 💎 THE IMMUTABILITY SHIELD 💎
    # This prevents anyone (even staff) from adding, deleting, or editing SchoolPay records manually
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

    # Helpers to show names instead of IDs
    def get_student_name(self, obj):
        return obj.student.full_name
    get_student_name.short_description = "Student"

    def get_school_name(self, obj):
        return obj.school.name
    get_school_name.short_description = "School"

# --- 📊 THE REINFORCED FINANCIAL COMMAND ENGINE (api/admin.py) ---

# --- 🛡️ SURGERY: ALIGNING THE TEMPLATE PATH ---
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
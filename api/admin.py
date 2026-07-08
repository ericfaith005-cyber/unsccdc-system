import json 
from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models import Sum, Avg, F 
from django.db.models import Sum, Avg, Count
from django.db import connection 
from datetime import timedelta
from .models import *
from .models import SovereignRegistry


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
    list_display = ('full_name_styled', 'role_badge', 'school', 'display_subjects', 'staff_id', 'secure_pin_box', 'reset_pin_btn', dossier_button)
    search_fields = ('full_name', 'staff_id', 'tin_number')
    list_filter = ('role', 'school', 'subjects')
    filter_horizontal = ('subjects',) 

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

    def full_name_styled(self, obj):
        return mark_safe(f'<b style="color: #D4AF37;">{obj.full_name.upper()}</b>')
    full_name_styled.short_description = "Staff Name"

    def role_badge(self, obj):
        colors = {'TEACHER': '#3498db', 'BURSAR': '#2ecc71', 'HEADTEACHER': '#e74c3c', 'DIRECTOR': '#9b59b6'}
        color = colors.get(obj.role, '#7f8c8d')
        return mark_safe(f'<span style="background:{color}; color:white; padding:3px 10px; border-radius:12px; font-size:10px; font-weight:bold;">{obj.role}</span>')
    role_badge.short_description = "Position"

    def secure_pin_box(self, obj):
        return mark_safe(f'<code style="background:#222; color:#00ff00; padding:5px; border-radius:5px; font-weight:bold;">{obj.secure_pin}</code>')
    secure_pin_box.short_description = "Current PIN"

    def display_subjects(self, obj):
        try:
            # 🛡️ This safely joins names or returns 'None' if empty
            subs = obj.subjects.all()
            if subs:
                return ", ".join([s.name for s in subs])
            return mark_safe('<i style="color: #666;">No subjects assigned</i>')
        except:
            return "Syncing..."
    
    display_subjects.short_description = "Subjects Handled"

    # 💎 THE RESET BUTTON
    def reset_pin_btn(self, obj):
        url = f"/api/staff/reset-pin/{obj.id}/"
        return mark_safe(f'<a href="{url}" style="background:#444; color:white; padding:5px 8px; border-radius:5px; text-decoration:none; font-size:10px;">🔄 RESET PIN</a>')
    reset_pin_btn.short_description = "Action"


class SubjectAdmin(admin.ModelAdmin):
    # 💎 THE VIEW: Clean and Scannable
    list_display = ('name', 'level', 'code', 'is_core')
    list_filter = ('level', 'is_core')
    search_fields = ('name', 'code')
    ordering = ('level', 'name')

    def colored_category(self, obj):
        # 🎨 Advanced UI: Colors for different categories
        colors = {
            'CORE': '#002366', # Navy
            'VOCATIONAL': '#D4AF37', # Gold
            'ELECTIVE': '#008080', # Teal
        }
        color = colors.get(obj.category, '#666')
        return mark_safe(f'<b style="color:{color};">{obj.category}</b>')
    
    colored_category.short_description = "Classification"

    # 🚀 THE MASTER ACTIONS: Populate UNEB/NCDC Curriculum automatically
    actions = ['generate_uce_defaults', 'generate_ple_defaults']

    @admin.action(description="⚡ GENERATE UCE STANDARD (O-Level)")
    def generate_uce_defaults(self, request, queryset):
        core = ['English Language', 'Mathematics', 'Biology', 'Chemistry', 'Physics', 'Geography', 'History']
        for sub in core:
            Subject.objects.get_or_create(name=sub, level='UCE', is_core=True)
        self.message_user(request, "O-Level Registry Synced with National Standards! 📜")

    @admin.action(description="⚡ GENERATE PLE STANDARD (Primary)")
    def generate_ple_defaults(self, request, queryset):
        core = ['English', 'Mathematics', 'Social Studies', 'Integrated Science']
        for sub in core:
            Subject.objects.get_or_create(name=sub, level='PLE', is_core=True)
        self.message_user(request, "Primary Registry Synced with National Standards! 🎓")

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
    # 💎 1. THE VIEW: Match these names EXACTLY with the methods below
    list_display = (
        'full_name', 
        'account_number', 
        'school', 
        'current_class', 
        'national_standing', 
        'download_pdf'  # 👈 This name must match the function below!
    )
    
    inlines = [MarksInline]
    search_fields = ('full_name', 'account_number')
    list_filter = ('school', 'current_class')

    # 💎 2. THE MISSING METHOD: Physically drawing the button
    def download_pdf(self, obj):
        # This points to the National PDF Engine we built in views.py
        url = f"/api/download-report/{obj.account_number}/"
        return mark_safe(f'''
            <a href="{url}" target="_blank" 
               style="background:#D4AF37; color:#000; padding:6px 12px; border-radius:8px; font-weight:900; text-decoration:none; font-size:10px; border: 1px solid #000; display: inline-block;">
               📥 DOWNLOAD REPORT
            </a>
        ''')
    
    download_pdf.short_description = "National Record"

    # Ensure your national_standing method is also inside this class
    def national_standing(self, obj):
        c = str(obj.current_class).upper()
        if 'S.5' in c or 'S.6' in c:
            return mark_safe('<b style="color:#00ff00;">A-LEVEL COMBO</b>')
        return mark_safe(f'<span style="color:#aaa;">{c} Registry</span>')
    
    national_standing.short_description = "Status"


    
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
admin.site.register(AcademicResultsCenter, AcademicResultsHubAdmin)
admin.site.register(NationalLedger, NationalLedgerAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Subject, SubjectAdmin) 

admin.site.register([ 
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




class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_code', 'district', 'is_verified')
    readonly_fields = ('logo_preview',)
    
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" />')
        return "No Logo Uploaded"
    
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

from django.utils.safestring import mark_safe

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # 💎 1. Show the Dossier and Sector in the list
    list_display = ('full_name', 'current_class', 'payment_code', 'get_sector', 'view_dossier_btn')
    list_filter = ('school__sector', 'current_class', 'is_active')
    search_fields = ('full_name', 'account_number', 'payment_code')

    # 💎 2. THE Hub Hub Hub Hub Hub Hub DOSSIER BUTTON
    def view_dossier_btn(self, obj):
        url = f"/api/download-dossier/{obj.account_number}/"
        return mark_safe(f'''
            <a href="{url}" target="_blank" 
               style="background:#002366; color:white; padding:6px 12px; border-radius:8px; font-weight:900; text-decoration:none; border: 1px solid #D4AF37;">
               📄 PRINT DOSSIER
            </a>
        ''')
    view_dossier_btn.short_description = "National File"

    def get_sector(self, obj):
        return obj.school.get_sector_display()
    get_sector.short_description = "Education Sector"

    # 💎 2. THE FORM: Physically adding the Parent selector into the Student Profile
    fieldsets = (
        ('👤 STUDENT IDENTITY', {
            'fields': (
                'full_name', 
                'gender',
                'account_number', 
                'school', 
                'current_class', 
                'stream',
                'parent_link'  # 👈 THE Hub FIX: You can now select the Parent here!
            )
        }),
        ('🎓 ACADEMIC STANDING', {
            'fields': ('enrollment_status', 'academic_standing', 'payment_code')
        }),
        
    )

    # We keep the account number read-only so it's never accidentally changed
    readonly_fields = ('account_number',)

    def fee_status_badge(self, obj):
        # A nice visual indicator for your presentation
        return mark_safe('<span style="color: #00ff00; font-weight: bold;">● Active</span>')
    fee_status_badge.short_description = "Status"

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
        extra_context = extra_context or {}
        
        # 🛡️ SOVEREIGN DEFAULT DATA (What to show if DB is empty)
        intel_data = {
            'total': 0, 'm': 0, 'f': 0, 'avg': '0%', 
            'trend': 'INITIALIZING', 'missing': [], 
            'solutions': ["Awaiting National Data Registry..."]
        }
        gender_stats = [0, 0]
        pay_stats = [0, 0, 100] # 100% pending

        try:
            # 💎 1. TABLE CHECK: Only run if Student table physically exists
            if 'api_student' in connection.introspection.table_names():
                txs = SchoolPayLedger.objects.all()
                
                # Safe Sums (using 'or 0' is the secret!)
                extra_context['d_total'] = txs.filter(timestamp__date=timezone.now().date()).aggregate(s=Sum('amount'))['s'] or 0
                
                # Enrollment & Gender (Attribute safe)
                intel_data['total'] = Student.objects.count()
                if hasattr(Student, 'gender'):
                    intel_data['m'] = Student.objects.filter(gender='M').count()
                    intel_data['f'] = Student.objects.filter(gender='F').count()
                    gender_stats = [intel_data['m'], intel_data['f']]

                # Performance (Avoid division by zero)
                avg_res = AcademicResult.objects.aggregate(a=Avg('eot_score'))['a']
                if avg_res:
                    intel_data['avg'] = f"{avg_res:.1f}%"

        except Exception as e:
            print(f"Build-time shield active: {e}")

        # 🚀 Inject safe data into the dashboard
        extra_context['intel'] = intel_data
        extra_context['gender_json'] = json.dumps(gender_stats)
        extra_context['pay_json'] = json.dumps(pay_stats)
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(FinancialCommandCenter, FinancialCommandAdmin)

# =============================================================
# 🖨️ THE NATIONAL BURSAR Hub TERMINAL (LONDON BANK STANDARD)
# =============================================================
class BursarTerminalAdmin(admin.ModelAdmin):
    change_list_template = "admin/api/bursarterminal/change_list.html"

    def changelist_view(self, request, extra_context=None):
        school = request.user.school 
        if not school: school = School.objects.first() # God-mode fallback

        today = timezone.now().date()
        # 🕵️ CRITICAL: Get only TODAY'S transactions that are NOT YET PRINTED
        txs = SchoolPayLedger.objects.filter(school=school, timestamp__date=today).order_by('-timestamp')
        
        # 🧮 Hub Hub BANK MATH
        total_today = txs.aggregate(Sum('amount'))['amount__sum'] or 0
        pending_count = txs.filter(is_printed=False).count()
        
        # 🎓 Level-Aware Class List
        if school.school_type == 'SECONDARY':
            classes = ['S.1', 'S.2', 'S.3', 'S.4', 'S.5', 'S.6']
        else:
            classes = ['P.1', 'P.2', 'P.3', 'P.4', 'P.5', 'P.6', 'P.7']

        # Count per class
        class_stats = {cls: txs.filter(student__current_class=cls).count() for cls in classes}

        extra_context = extra_context or {}
        extra_context.update({
            'title': "NATIONAL Hub TERMINAL",
            'school': school,
            'txs': txs,
            'classes': classes,
            'stats': class_stats,
            'total_today': f"{total_today:,.0f}",
            'pending_count': pending_count,
            'today_date': today.strftime("%d %B %Y"),
        })
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(BursarTerminal, BursarTerminalAdmin)

import json
from django.contrib import admin
from django.db.models import Sum, Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import FinancialCommandCenter, Student, Staff, SchoolPayLedger, AcademicResult

# =============================================================
# 📊 THE Hub NATIONAL WAR-ROOM (COMMAND INTELLIGENCE)
# =============================================================

@admin.register(FinancialCommandCenter)
class FinancialWarRoomAdmin(admin.ModelAdmin):
    # 💎 THE MASTER Hub LINK
    # This tells Django: "Don't show a boring table, show my High-End Dashboard!"
    change_list_template = "admin/api/financialcommandcenter/change_list.html"

    def changelist_view(self, request, extra_context=None):
        # 🛡️ 1. IDENTITY Hub
        school = getattr(request.user, 'school', None)
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        extra_context = extra_context or {}

        # 💰 2. FINANCE Hub Hub (REAL-TIME CALCULATIONS)
        # Today's Cash Intake
        rev_today = SchoolPayLedger.objects.filter(timestamp__date=today).aggregate(s=Sum('amount'))['s'] or 0
        rev_yesterday = SchoolPayLedger.objects.filter(timestamp__date=yesterday).aggregate(s=Sum('amount'))['s'] or 0
        
        # Growth Logic for the Arrows ▲▼
        growth = 0
        if rev_yesterday > 0:
            growth = ((rev_today - rev_yesterday) / rev_yesterday) * 100

        # 👨‍🎓 3. ENROLLMENT Hub Hub (GENDER & CLASS)
        males = Student.objects.filter(gender='M').count()
        females = Student.objects.filter(gender='F').count()
        
        # Class Breakdown for the Bar Chart
        class_data = Student.objects.values('current_class').annotate(total=Count('id')).order_by('current_class')
        class_labels = [item['current_class'] for item in class_data]
        class_values = [item['total'] for item in class_data]

        # 🎓 4. ACADEMIC Hub Hub Hub (PERFORMANCE INDEX)
        avg_perf = AcademicResult.objects.aggregate(a=Avg('eot_score'))['a'] or 0

        # 📦 5. THE JSON DATA Hub (FOR APEXCHARTS)
        # We package this for the template to read instantly
        extra_context.update({
            'title': "NATIONAL WAR-ROOM",
            'revenue_today': f"UGX {rev_today:,.0f}",
            'revenue_growth': round(growth, 1),
            'total_students': Student.objects.count(),
            'total_staff': Staff.objects.count(),
            'avg_performance': f"{avg_perf:.1f}%",
            
            # Chart Data (Converted to JSON for JS)
            'gender_json': json.dumps([males, females]),
            'class_labels_json': json.dumps(class_labels),
            'class_values_json': json.dumps(class_values),
            'performance_trend_json': json.dumps([65, 72, 68, 74, 80, avg_perf]), # Simulating trend
        })

        return super().changelist_view(request, extra_context=extra_context)

from django.shortcuts import redirect

from .models import SovereignRegistry # 💎 Make sure you import it!

class SovereignRegistryAdmin(admin.ModelAdmin):
    # This is the "Magic Trick"
    def changelist_view(self, request, extra_context=None):
        return redirect('/api/registry/') # 💎 Make sure this matches your URL name!

    # 🛡️ Give it a dummy field so Django doesn't complain
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

admin.site.register(SovereignRegistry, SovereignRegistryAdmin)

from .models import OperationsHub # 💎 IMPORT IT
from django.shortcuts import redirect


class OperationsHubAdmin(admin.ModelAdmin):
    # 🎯 THE MAGIC REDIRECT
    def changelist_view(self, request, extra_context=None):
        return redirect('/api/ops-hub/') # 💎 This opens the 12 tabs!

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

admin.site.register(OperationsHub, OperationsHubAdmin)

from .models import NationalDataBridge # 💎 IMPORT IT

from django.contrib import admin
from django.utils.safestring import mark_safe # 💎 CRITICAL IMPORT
from django.shortcuts import redirect


class NationalDataBridgeAdmin(admin.ModelAdmin):
    list_display = ('school', 'records_count', 'is_processed', 'open_bridge')
    def open_bridge(self, obj):
        return mark_safe(f'<a href="/api/bridge-preview/{obj.id}/" style="background:gold; color:black; padding:5px 10px; border-radius:5px; font-weight:bold;">VIEW & SYNC</a>')
    
    # 💎 REDIRECT AFTER SAVE
    def response_add(self, request, obj, post_url_continue=None):
        return redirect(f'/api/bridge-preview/{obj.id}/')
    
admin.site.register(NationalDataBridge, NationalDataBridgeAdmin)
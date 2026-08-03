# --- 💎 SURGERY: RESTORING IMPERIAL IMPORTS 💎 ---
import random
import string
import datetime # 💎 CRITICAL: Needed for the Year in Staff ID
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from PIL import Image
import os
from django.contrib.auth.models import AbstractUser
from django.utils import timezone  # <--- THE FIX IS HERE!

# --- 🏛️ SURGERY: TETHERING USERS TO SCHOOLS ---
class User(AbstractUser):
    """Sovereign Identity tethered to a specific Institution"""
    is_staff_member = models.BooleanField(default=False)
    
    # 💎 THE MASTER KEY: Every Admin/Bursar belongs to ONE school
    school = models.ForeignKey(
        'School', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Which school does this administrator manage?"
    )

    objects = UserManager()

class School(models.Model):
    LEVEL_CHOICES = [
        ('KIND', 'Kindergarten (Baby, Middle, Top)'),
        ('PRIM', 'Primary (P.1 - P.7)'),
        ('SEC', 'Secondary (S.1 - S.6)'),
        ('INTL', 'International (Year 1 - Year 13)'),
        ('UNI', 'University (Year 1 - Year 5)'),
        ('VOC', 'Vocational/Technical'),
    ]

    SECTOR_CHOICES = [
        ('PRIMARY', 'Primary Level (PLE System)'),
        ('SECONDARY', 'Secondary Level (UCE/UACE System)'),
        ('VOCATIONAL', 'Vocational/Technical (DIT/BTVET)'),
        ('UNIVERSITY', 'Higher Education (NCHE/CGPA)'),
    ]
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default='SECONDARY')
    # ... rest of your fields
    school_type = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='SEC')
    stamp_color = models.CharField(max_length=20, default="#002366", help_text="Hex color for digital stamp")
    SCHOOL_TYPES = [('PRI', 'Primary (PLE)'), ('SEC', 'Secondary (UCE)'), ('ADV', 'Advanced (UACE)')]
    school_type = models.CharField(max_length=3, choices=SCHOOL_TYPES, default='SEC')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo:
            # 🛡️ THE Hub Hub Hub Hub AUTO-FORMATTER
            img = Image.open(self.logo.path)
            # Resize to high-res standard (300x300) while keeping quality
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size, Image.LANCZOS)
                img.save(self.logo.path, quality=95)

    # 💎 THE BRAIN: Automatically decides the National Grading Scale
    @property
    def grading_standard(self):
        if self.school_type == 'PRI': return "UNEB - PLE Standard"
        if self.school_type == 'SEC': return "NCDC - NLSC (20 Point Scale)"
        return "UNEB - UACE Standard"
        
    name = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100, default="Kampala")
    school_motto = models.CharField(max_length=255)
    school_account_id = models.CharField(max_length=100, unique=True, editable=False)
    
    # 💎 PRESTIGE REGISTRY DATA 💎
    uneb_center_number = models.CharField(max_length=20, default="U0000")
    school_type = models.CharField(max_length=100, default="Secondary / Boarding")
    rating = models.CharField(max_length=30, default="⭐⭐⭐⭐⭐")
    mission = models.TextField(default="To provide high-quality education.")
    vision = models.TextField(default="A lead institution of excellence.")
    core_values = models.TextField(default="Integrity, Excellence, Discipline")
    
    # 💎 USSD SETTINGS 💎
    ussd_instructions = models.TextField(
        default="1. Dial *165# (MTN) or *185# (Airtel)\n2. Select Fees & SchoolPay\n3. Select Pay Fees\n4. Enter PRN",
        help_text="Provide step-by-step dialing instructions for the Parent App"
    )

    # 💎 BANKING & API CREDENTIALS 💎
    school_code = models.CharField(max_length=100, blank=True)
    api_password = models.CharField(max_length=255, blank=True)
    total_revenue_collected = models.BigIntegerField(default=0)
    total_commission_earned = models.BigIntegerField(default=0)
    is_verified = models.BooleanField(default=True)
    followers_count = models.IntegerField(default=1500)

    def save(self, *args, **kwargs):
        if not self.school_account_id:
            import random, string
            self.school_account_id = "SCH" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        super().save(*args, **kwargs)

    def __str__(self): return self.name


# --- 🏛️ SURGERY: NATIONAL CURRICULUM REGISTRY ---

class Subject(models.Model):
    LEVEL_CHOICES = [
        ('PLE', 'Primary Level (PLE)'),
        ('UCE', 'Ordinary Level (UCE)'),
        ('UACE', 'Advanced Level (UACE)'),
        ('OTHER', 'Vocational/Other'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True) # e.g., 535 for Physics
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='UCE')
    is_core = models.BooleanField(default=True, help_text="Is this a compulsory subject?")
    
    # 💎 FOR A-LEVEL COMBINATIONS
    combination_category = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="e.g., Sciences, Humanities, Languages"
    )

    class Meta:
        verbose_name = "NATIONAL SUBJECT REGISTRY"
        ordering = ['level', 'name']

    def __str__(self):
        return f"[{self.level}] {self.name}"

class Student(models.Model):

    full_name = models.CharField(max_length=255, db_index=True) # 💎 Fast Search
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    age = models.IntegerField(default=15)
    current_class = models.CharField(max_length=50) # e.g., "S.1", "P.7"
    payment_code = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, help_text="Student's SchoolPay PRN")
    school_code = models.CharField(max_length=100, blank=True, help_text="Provided by SchoolPay")
    stream = models.CharField(max_length=50, default="North")
    account_number = models.CharField(max_length=30, unique=True, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='students_in_school')
    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)
    level_category = models.CharField(max_length=20, default='UCE_NEW')

    # OFFICIAL DOCUMENT VAULT
    birth_certificate = models.FileField(upload_to='docs/birth/', null=True, blank=True)
    ple_result_slip = models.FileField(upload_to='docs/ple/', null=True, blank=True)
    uce_result_slip = models.FileField(upload_to='docs/uce/', null=True, blank=True)
    admission_letter = models.FileField(upload_to='docs/admission/', null=True, blank=True)

    # INITIAL COMMITMENT
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, verbose_name="Active in Registry")
    
    parent_link = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = "UNS" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        super().save(*args, **kwargs)

    def __str__(self): 
        return self.full_name

    @property
    def national_category(self):
        c = str(self.current_class).upper()
        if c.startswith('P'): return 'PRIMARY'
        if c in ['S.1', 'S.2', 'S.3', 'S.4']: return 'O-LEVEL'
        if c in ['S.5', 'S.6']: return 'A-LEVEL'
        return 'OTHER'

    @property
    def fees_balance(self):
        from .models import FeesTracker
        tracker = FeesTracker.objects.filter(student=self).first()
        if tracker:
            bal = tracker.total_fees_due - tracker.total_fees_paid
            return f"UGX {bal:,.0f}"
        return "UGX 0"

    def __str__(self):
            # 🛡️ This prevents 500 error if name is missing during save
            return f"{self.full_name or 'NEW REGISTRATION'}"
        



# --- 📑 THE IMPERIAL SUBJECT ASSIGNMENT (FIXED) ---
class SubjectAssignment(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    target_class = models.CharField(max_length=50, help_text="e.g., S.1 North")
    school = models.ForeignKey('School', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Subject Assignment"
        # 💎 THE FIX: Add the missing 'l' to plural
        verbose_name_plural = "Subject Assignments" 

    def __str__(self):
        return f"{self.staff.full_name} - {self.subject.name} ({self.target_class})"

class AcademicResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    aoi_1 = models.FloatField(default=0); aoi_2 = models.FloatField(default=0)
    aoi_3 = models.FloatField(default=0); aoi_4 = models.FloatField(default=0)
    mid_term = models.FloatField(default=0); eot_score = models.FloatField(default=0)
    project_work = models.FloatField(default=0)

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='transactions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=100, default="Tuition")
    amount_paid = models.FloatField(default=0)
    system_tax = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

# --- 🛠️ SURGERY: AUTOMATIC STAFF REGISTRY (api/models.py) ---

# --- 🏛️ SURGERY: ADVANCED HR & AUDIT REGISTRY (api/models.py) ---

import random
import string
import datetime
from django.db import models

class Staff(models.Model):
    # CORE IDENTITY
    ROLE_CHOICES = [
        ('TEACHER', 'Class Teacher'),
        ('BURSAR', 'School Bursar'),
        ('HEADTEACHER', 'Head Teacher'),
        ('DIRECTOR', 'School Director'),
        ('SECRETARY', 'Front Desk/Secretary'),
        ('LIBRARIAN', 'Library Manager'),
    ]

    full_name = models.CharField(max_length=255)
    passport_photo = models.ImageField(upload_to='staff/photos/', null=True, blank=True)
    national_id_copy = models.ImageField(upload_to='staff/ids/', null=True, blank=True)
    cv_pdf = models.FileField(upload_to='staff/cvs/', null=True, blank=True)
    
    # SYSTEM ACCESS
    staff_id = models.CharField(max_length=50, unique=True, editable=False, blank=True)
    secure_pin = models.CharField(max_length=4, editable=False, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TEACHER')
    subjects = models.ManyToManyField('Subject', blank=True)
    
    
    # HR & AUDIT DATA
    tin_number = models.CharField(max_length=30, blank=True, verbose_name="URA TIN")
    nssf_number = models.CharField(max_length=30, blank=True, verbose_name="NSSF No.")
    next_of_kin = models.CharField(max_length=255, blank=True)
    next_of_kin_phone = models.CharField(max_length=30, blank=True)
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='staff_registry')
    designation = models.CharField(max_length=100, default="Instructor")
    phone = models.CharField(max_length=30)
    momo_number = models.CharField(max_length=30, blank=True, null=True)

    def save(self, *args, **kwargs):
        # 🤖 AUTO-GENERATE STAFF ID (Format: UNS/STF/Year/Random)
        if not self.staff_id:
            year = datetime.date.today().year
            rand = ''.join(random.choices(string.digits, k=4))
            self.staff_id = f"UNS/STF/{year}/{rand}"
        
        # 🤖 AUTO-GENERATE 4-DIGIT PIN
        if not self.secure_pin:
            self.secure_pin = ''.join(random.choices(string.digits, k=4))
            
        super().save(*args, **kwargs)

    def __str__(self):
        # 🛡️ This prevents the 500 error if a name is somehow empty
        name = self.full_name 


class Parent(models.Model):
    full_name = models.CharField(max_length=255); unique_code = models.CharField(max_length=50, unique=True); phone_number = models.CharField(max_length=15, unique=True) 
    
class BioAndCareer(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='bio'); future_career = models.CharField(max_length=255, default="Leader"); challenges_faced = models.TextField(default="None"); student_inspiration = models.TextField(default="Uganda")

class NationalTopPerformer(models.Model):
    name = models.CharField(max_length=255); school_name = models.CharField(max_length=255); score = models.CharField(max_length=50); photo = models.ImageField(upload_to='performers/')

class SchoolPost(models.Model):
    TYPES = [('PRIMARY', 'Primary School'), ('SECONDARY', 'Secondary School')]
    name = models.CharField(max_length=255)
    school_type = models.CharField(max_length=10, choices=TYPES, default='SECONDARY') 
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True) # FOR CLEAR TIKTOK HD
    media_file = models.FileField(upload_to='feed/')
    likes_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

# --- 📝 ADD TO api/models.py ---

class Attendance(models.Model):
    """Real-time Student Presence Registry"""
    STATUS_CHOICES = [('PRESENT', 'Present'), ('ABSENT', 'Absent'), ('LATE', 'Late'), ('SICK', 'Sick')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True, help_text="e.g. 'Arrived at 9AM'")

    class Meta:
        unique_together = ('student', 'date') # Prevents double marking on the same day
        verbose_name = "DAILY ATTENDANCE"
        verbose_name_plural = "DAILY ATTENDANCE"

    def __str__(self):
        return f"{self.student.full_name} - {self.date} ({self.status})"

class AttendanceHub(Attendance):
    """Proxy for a dedicated high-speed Attendance Tab"""
    class Meta:
        proxy = True
        verbose_name = "MARK DAILY ATTENDANCE"
        verbose_name_plural = "MARK DAILY ATTENDANCE"

class FeesTracker(models.Model):
    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='fees_tracker')
    total_fees_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_fees_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # 💎 THE Hub Hub Hub Hub Hub AUTOMATIC BALANCE FORMULA
    @property
    def fees_balance(self):
        return self.total_fees_due - self.total_fees_paid

    def __str__(self):
        return f"{self.student.full_name} - Balance: {self.fees_balance}"
    
class StaffPayroll(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=30)
    year = models.IntegerField(default=2026)
    
    # FINANCIALS
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    # 💎 THE AUDIT PILLARS (Calculated in Step 2)
    paye_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="PAYE (URA)")
    nssf_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="NSSF (5%)")
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=[('PAID', 'Paid'), ('PENDING', 'Pending')], default='PENDING')

    def save(self, *args, **kwargs):
        # 🧮 AUTOMATED UGANDAN TAX MATH
        # NSSF 5% Deduction
        self.nssf_deduction = float(self.gross_salary) * 0.05
        
        # Simple PAYE Logic (Over 235k)
        taxable = float(self.gross_salary) - 235000
        if taxable > 0:
            self.paye_tax = taxable * 0.10 # Basic 10% logic
        
        self.net_pay = float(self.gross_salary) - (float(self.paye_tax) + float(self.nssf_deduction) + float(self.other_deductions))
        super().save(*args, **kwargs)

# --- 👑 PROXY MODELS FOR COMMAND CENTER ---
class NationalLedger(Transaction):
    class Meta: proxy = True; verbose_name_plural = "NATIONAL UNEDITABLE LEDGER"
class CommissionAnalytics(School):
    class Meta: proxy = True; verbose_name_plural = "MY COMMISSION TRACKER"
class AcademicResultsCenter(Student):
    class Meta: proxy = True; verbose_name_plural = "ACADEMIC HUB (MASTER GRID)"
class SovereignProfessionalInsights(School):
    class Meta: proxy = True; verbose_name_plural = "SOVEREIGN ANALYTICS (PRO)"

class SchoolPayLedger(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_printed = models.BooleanField(default=False) 
    receipt_number = models.CharField(max_length=100, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # 💎 THE FIX: Add this specific line here! 💎
    raw_data = models.JSONField(default=dict, blank=True, null=True)
    is_reversed = models.BooleanField(default=False, verbose_name="Transaction Void")
    reversal_reason = models.TextField(blank=True, null=True, help_text="Why was this reversed?")
    reversed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "NATIONAL TREASURY LEDGER"
        verbose_name_plural = "NATIONAL TREASURY LEDGER"

    class Meta:
        verbose_name = "🛡️ SCHOOLPAY LEDGER"
    
class FinancialCommandCenter(School):
    """Proxy model for the Director's high-level dashboard"""
    class Meta:
        proxy = True
        verbose_name = "NATIONAL FINANCIAL COMMAND"
        verbose_name_plural = "NATIONAL FINANCIAL COMMAND"

# --- 🛰️ SURGERY: NATIONAL HUB INSTANT ALERTS ---
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=SchoolPayLedger)
def notify_king_of_payment(sender, instance, created, **kwargs):
    if created:
        # 💎 This prints to your cloud log immediately
        print(f"💰 NATIONAL HUB ALERT: {instance.student.full_name} paid {instance.amount} to {instance.school.name}")
        # Logic to send you an SMS via Africa's Talking can be added here!

# --- 🏛️ THE Hub Hub PROXY REGISTRY ---
# We make it a PROXY of School so it uses an existing table
class BursarTerminal(School):
    class Meta:
        proxy = True # 💎 THE Hub FIX: No new table needed!
        verbose_name = "NATIONAL BURSAR TERMINAL"
        verbose_name_plural = "NATIONAL BURSAR TERMINAL"

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from decimal import Decimal

@receiver(post_save, sender=SchoolPayLedger)
def imperial_real_time_settlement(sender, instance, created, **kwargs):
    """
    💎 THE Hub Hub Hub Hub Hub REAL-TIME Hub Hub Hub 💎
    Automated accounting logic for real money movement.
    """
    if created:
        # 1. Update the Student's Fees Tracker
        # This handles the 'Total Amount Completed' and 'Remaining Balance' logic
        tracker, _ = FeesTracker.objects.get_or_create(student=instance.student)
        
        # We use F expressions to prevent 'Race Conditions' (Standard Bank Logic)
        tracker.total_fees_paid = F('total_fees_paid') + Decimal(str(instance.amount))
        tracker.save()
        
        # 2. Update School Total Revenue
        school = instance.school
        school.total_revenue_collected = F('total_revenue_collected') + Decimal(str(instance.amount))
        school.save()

        # 3. Log to the Uneditable National Audit Ledger
        # This ensures the money is tracked even if the original ledger is tampered with
        from .models import NationalLedger
        NationalLedger.objects.create(
            transaction_id=instance.receipt_number,
            school=instance.school,
            student=instance.student,
            category=instance.category if hasattr(instance, 'category') else "General Fees",
            amount_paid=instance.amount,
            system_tax=Decimal(str(instance.amount)) * Decimal('0.01') # 1% Hub Fee
        )
        print(f"--- SETTLEMENT ---")
        print(f"Student: {instance.student.full_name} | Amount: {instance.amount} UGX | SYNCED!")
    
class SovereignRegistry(Student):
    class Meta:
        proxy = True
        # 💎 THE ONE TRUE NAME
        verbose_name = "SOVEREIGN NATIONAL REGISTRY"
        verbose_name_plural = "SOVEREIGN NATIONAL REGISTRY"

class OperationsHub(Student):
    class Meta:
        proxy = True
        verbose_name = "NATIONAL OPERATIONS HUB"
        verbose_name_plural = "NATIONAL OPERATIONS HUB"

class NationalDataBridge(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    source_file = models.FileField(upload_to='national_bridge/files/')
    # 💎 NEW: Stores the 'Ghost Data' for previewing
    preview_data = models.JSONField(null=True, blank=True) 
    is_processed = models.BooleanField(default=False)
    records_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NATIONAL DATA BRIDGE"
        verbose_name_plural = "NATIONAL DATA BRIDGE"

    def __str__(self):
        return f"Bridge Entry #{self.id} - {self.school.name}"

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    cover_image = models.ImageField(upload_to='books/')
    description = models.TextField()
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = "National Book Registry"

class BookOrder(models.Model):
    STATUS = [('PENDING', 'Pending'), ('DISPATCHED', 'Dispatched'), ('DELIVERED', 'Delivered')]
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    is_escrow_paid = models.BooleanField(default=False, help_text="10% commitment fee paid?")
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

class FeesReminder(Student):
    class Meta:
        proxy = True
        verbose_name = "NATIONAL FEES REMINDERS"
        verbose_name_plural = "NATIONAL FEES REMINDERS"

class SovereignParentRegistry(Parent):
    class Meta:
        proxy = True
        verbose_name = "SOVEREIGN PARENT REGISTRY"
        verbose_name_plural = "SOVEREIGN PARENT REGISTRY"

class SystemSettings(models.Model):
    academic_year = models.IntegerField(default=2026)
    current_term = models.CharField(max_length=10, choices=[('1','Term 1'),('2','Term 2'),('3','Term 3')])
    maintenance_mode = models.BooleanField(default=False)
    system_logo = models.ImageField(upload_to='system/')

    class Meta:
        verbose_name = "Global System Settings"

from django.conf import settings # 💎 THE KEY: Accesses the active User model
from django.db import models

# 🛡️ THE Hub Hub Hub Hub Hub USER ATTACHMENT
class UserProfile(models.Model):
    # 💎 FIX: Point to settings.AUTH_USER_MODEL instead of 'User'
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='user_profiles')
    is_school_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} @ {self.school.name}"

class NationalUpdate(models.Model):
    source = models.CharField(max_length=50) # e.g., UNEB, MoES
    title = models.CharField(max_length=500)
    link = models.URLField()
    date_found = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_found']
        verbose_name = "NATIONAL LIVE FEED"

class BroadcastLog(models.Model):
    MSG_TYPES = [('SMS', 'SMS Text'), ('WHATSAPP', 'WhatsApp Message')]
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    message_body = models.TextField()
    message_type = models.CharField(max_length=10, choices=MSG_TYPES, default='SMS')
    status = models.CharField(max_length=20, default='SENT')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "COMMUNICATION LOGS"
        ordering = ['-timestamp']
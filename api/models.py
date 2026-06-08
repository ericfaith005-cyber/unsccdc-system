# --- 💎 SURGERY: RESTORING IMPERIAL IMPORTS 💎 ---
import random
import string
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
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

class Subject(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default='ARTS')
    description = models.TextField(default="Detailed competencies.")
    level = models.CharField(max_length=20, default='ALL')
    def __str__(self): return self.name

class Student(models.Model):
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, default='M')
    age = models.IntegerField(default=15)
    current_class = models.CharField(max_length=50)
    # 💎 THE CORE FIX: This field MUST exist here for the Admin to see it!
    payment_code = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True, 
        help_text="Student's SchoolPay PRN"
    )
    school_code = models.CharField(max_length=30, blank=True, help_text="Provided by SchoolPay")
    api_password = models.CharField(max_length=255, blank=True, help_text="Secret password for API sync")
    stream = models.CharField(max_length=50, default="North")
    account_number = models.CharField(max_length=30, unique=True, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    photo = models.ImageField(upload_to='students/', null=True, blank=True)
    level_category = models.CharField(max_length=20, default='UCE_NEW')
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = "UNS" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        super().save(*args, **kwargs)
    def __str__(self): return self.full_name

class AcademicResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    aoi_1 = models.FloatField(default=0); aoi_2 = models.FloatField(default=0)
    aoi_3 = models.FloatField(default=0); aoi_4 = models.FloatField(default=0)
    mid_term = models.FloatField(default=0); eot_score = models.FloatField(default=0)
    project_work = models.FloatField(default=0)

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='transactions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=100, default="Tuition")
    amount_paid = models.FloatField(default=0)
    system_tax = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

# --- 🛠️ SURGERY: AUTOMATIC STAFF REGISTRY (api/models.py) ---

# --- 🏛️ SURGERY: ADVANCED HR & AUDIT REGISTRY (api/models.py) ---

class Staff(models.Model):
    # CORE IDENTITY
    full_name = models.CharField(max_length=255)
    passport_photo = models.ImageField(upload_to='staff/photos/', null=True, blank=True)
    national_id_copy = models.ImageField(upload_to='staff/ids/', null=True, blank=True)
    cv_pdf = models.FileField(upload_to='staff/cvs/', null=True, blank=True)
    
    # SYSTEM ACCESS
    staff_id = models.CharField(max_length=100, unique=True, editable=False)
    secure_pin = models.CharField(max_length=6, blank=True)
    
    # HR & AUDIT DATA
    tin_number = models.CharField(max_length=30, blank=True, verbose_name="URA TIN")
    nssf_number = models.CharField(max_length=30, blank=True, verbose_name="NSSF No.")
    next_of_kin = models.CharField(max_length=255, blank=True)
    next_of_kin_phone = models.CharField(max_length=30, blank=True)
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='staff_registry')
    designation = models.CharField(max_length=100, default="Instructor")
    phone = models.CharField(max_length=30)
    momo_number = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self): return f"{self.full_name} ({self.designation})"

class Parent(models.Model):
    full_name = models.CharField(max_length=255); unique_code = models.CharField(max_length=50, unique=True); phone_number = models.CharField(max_length=15, unique=True) 
    linked_student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='parent_link'); secure_pin = models.CharField(max_length=6, default="123456"); security_motto = models.CharField(max_length=100, default="Education is Light")

class BioAndCareer(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='bio'); future_career = models.CharField(max_length=255, default="Leader"); challenges_faced = models.TextField(default="None"); student_inspiration = models.TextField(default="Uganda")

class NationalTopPerformer(models.Model):
    name = models.CharField(max_length=255); school_name = models.CharField(max_length=255); score = models.CharField(max_length=50); photo = models.ImageField(upload_to='performers/')

class SchoolPost(models.Model):
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
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.CharField(max_length=255, blank=True, help_text="e.g. 'Arrived at 9AM'")

    class Meta:
        unique_together = ('student', 'date') # Prevents double marking on the same day
        verbose_name = "Daily Attendance"
        verbose_name_plural = "Daily Attendance"

    def __str__(self):
        return f"{self.student.full_name} - {self.date} ({self.status})"

class AttendanceHub(Attendance):
    """Proxy for a dedicated high-speed Attendance Tab"""
    class Meta:
        proxy = True
        verbose_name = "✅ MARK DAILY ATTENDANCE"
        verbose_name_plural = "✅ MARK DAILY ATTENDANCE"

class FeesTracker(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='fees'); total_fees_due = models.IntegerField(default=0); total_fees_paid = models.IntegerField(default=0)

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
    class Meta: proxy = True; verbose_name_plural = "🛡️ NATIONAL UNEDITABLE LEDGER"
class CommissionAnalytics(School):
    class Meta: proxy = True; verbose_name_plural = "💰 MY COMMISSION TRACKER"
class AcademicResultsCenter(Student):
    class Meta: proxy = True; verbose_name_plural = "📊 ACADEMIC HUB (MASTER GRID)"
class SovereignProfessionalInsights(School):
    class Meta: proxy = True; verbose_name_plural = "⭐ SOVEREIGN ANALYTICS (PRO)"

class SchoolPayLedger(models.Model):
    receipt_number = models.CharField(max_length=100, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # 💎 THE FIX: Add this specific line here! 💎
    raw_data = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "🛡️ SCHOOLPAY LEDGER"
    
class FinancialCommandCenter(School):
    """Proxy model for the Director's high-level dashboard"""
    class Meta:
        proxy = True
        verbose_name = "📊 NATIONAL FINANCIAL COMMAND"
        verbose_name_plural = "📊 NATIONAL FINANCIAL COMMAND"

# --- 🛰️ SURGERY: NATIONAL HUB INSTANT ALERTS ---
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=SchoolPayLedger)
def notify_king_of_payment(sender, instance, created, **kwargs):
    if created:
        # 💎 This prints to your cloud log immediately
        print(f"💰 NATIONAL HUB ALERT: {instance.student.full_name} paid {instance.amount} to {instance.school.name}")
        # Logic to send you an SMS via Africa's Talking can be added here!
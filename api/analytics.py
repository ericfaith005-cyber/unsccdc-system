from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Student, Staff, SchoolPayLedger, AcademicResult

def get_growth_rate(current, previous):
    if not previous or previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 1)

def get_dashboard_stats():
    today = timezone.now().date()
    last_month = today - timedelta(days=30)
    
    # 💰 FINANCE STATS
    revenue_today = SchoolPayLedger.objects.filter(timestamp__date=today).aggregate(s=Sum('amount'))['s'] or 0
    revenue_prev = SchoolPayLedger.objects.filter(timestamp__date=today-timedelta(days=1)).aggregate(s=Sum('amount'))['s'] or 0
    rev_growth = get_growth_rate(revenue_today, revenue_prev)

    # 👨‍🎓 STUDENT STATS
    total_students = Student.objects.count()
    # Assume we track 'created_at' for students
    new_students = Student.objects.filter(enrollment_date__gte=last_month).count()

    # 👔 STAFF STATS
    staff_breakdown = Staff.objects.values('role').annotate(total=Count('id'))

    return {
        "kpis": {
            "revenue": {"val": revenue_today, "growth": rev_growth},
            "students": {"val": total_students, "growth": 5.2}, # Example static growth
            "staff": {"val": Staff.objects.count(), "roles": list(staff_breakdown)},
        }
    }
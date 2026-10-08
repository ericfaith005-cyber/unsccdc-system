from decimal import Decimal

from django.db.models import Q

from api.models import FeesTracker, Parent, SchoolPayLedger, Student
from .models import SchoolConnectUser, StudentFeeQueryLog


PERMISSION_DENIED = "Permission denied: your account is not verified for this student."


def _authenticated(user):
    return bool(user and getattr(user, "is_authenticated", False))


def _find_student(identifier):
    normalized = str(identifier or "").strip()
    if not normalized:
        return None

    student = Student.objects.filter(
        Q(payment_code__iexact=normalized)
        | Q(account_number__iexact=normalized)
        | Q(parent_link__phone_number__iexact=normalized)
    ).select_related("school", "parent_link").first()
    if student:
        return student

    identity = SchoolConnectUser.objects.filter(
        Q(phone_number__iexact=normalized) | Q(student_prn__iexact=normalized)
    ).select_related("student").first()
    if identity and identity.student_id:
        return identity.student

    parent = Parent.objects.filter(phone_number__iexact=normalized).first()
    if parent:
        return Student.objects.filter(parent_link=parent).order_by("-id").first()

    if normalized.isdigit():
        return Student.objects.filter(pk=int(normalized)).first()
    return None


def _audit(user, identifier, decision, student=None, request_ip=None):
    StudentFeeQueryLog.objects.create(
        user=user if _authenticated(user) else None,
        student=student,
        requested_identifier=str(identifier or "")[:120],
        verified=decision == "ALLOWED",
        decision=decision,
        request_ip=request_ip,
    )


def _is_verified_parent(user, student):
    parent = student.parent_link
    if not parent or parent.user_id != user.pk:
        return False

    prn = (student.payment_code or "").strip().upper()
    if not prn:
        return False

    return SchoolConnectUser.objects.filter(
        user=user,
        student=student,
        student_prn=prn,
        is_prn_verified=True,
        is_active=True,
    ).exists()


def process_fee_inquiry(user, student_prn_or_id, request_ip=None):
    """Return fee details only for the authenticated, PRN-verified parent."""
    if not _authenticated(user):
        _audit(None, student_prn_or_id, "DENIED_UNAUTHENTICATED", request_ip=request_ip)
        return PERMISSION_DENIED

    student = _find_student(student_prn_or_id)
    if not student:
        _audit(user, student_prn_or_id, "DENIED_STUDENT_NOT_FOUND", request_ip=request_ip)
        return PERMISSION_DENIED

    if not _is_verified_parent(user, student):
        _audit(user, student_prn_or_id, "DENIED_PARENT_OR_PRN_LINK", student, request_ip)
        return PERMISSION_DENIED

    tracker = FeesTracker.objects.filter(student=student).first()
    due = tracker.total_fees_due if tracker else Decimal("0")
    paid = tracker.total_fees_paid if tracker else Decimal("0")
    balance = due - paid
    due_date = tracker.due_date if tracker else None

    recent_payments = SchoolPayLedger.objects.filter(
        student=student,
        school=student.school,
        is_reversed=False,
    ).order_by("-timestamp")[:5]

    lines = [
        f"Hello! Here is the fee breakdown for {student.full_name}.",
        f"Student PRN: {student.payment_code or 'Not recorded'}",
        f"School: {student.school.name}",
        f"Total fees due: UGX {due:,.0f}",
        f"Total paid to date: UGX {paid:,.0f}",
        f"Remaining balance: UGX {balance:,.0f}",
        f"Next due date: {due_date.strftime('%d %b %Y') if due_date else 'Not recorded'}",
        "Recent payments:",
    ]

    payments = list(recent_payments)
    if payments:
        lines.extend(
            f"- UGX {payment.amount:,.0f} on {payment.timestamp:%d %b %Y} "
            f"(receipt {payment.receipt_number})"
            for payment in payments
        )
    else:
        lines.append("- No recorded payments.")

    lines.append("Please contact your school bursar if you need help reviewing a payment or balance.")

    _audit(user, student_prn_or_id, "ALLOWED", student, request_ip)
    return "\n".join(lines)

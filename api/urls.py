from django.urls import path, include
from .views import generate_imperial_pdf
from .views import generate_imperial_pdf, generate_staff_dossier_pdf, generate_payslip_pdf
from rest_framework.routers import DefaultRouter
# --- 🛠️ SURGERY: IMPORTING THE STAFF KEY ---
from .views import StudentViewSet, StaffViewSet, UNSCCDC_Analytics, pay_fees, staff_hub_login
from .views import StudentViewSet, staff_hub_login, staff_marks_engine 
# --- 🛰️ SURGERY: ADDING THE MISSING NAME TO IMPORTS (api/urls.py) ---
from .views import (
    StudentViewSet, StaffViewSet, UNSCCDC_Analytics, pay_fees, 
    staff_hub_login, staff_marks_engine, sync_schoolpay_transaction,
    bursar_notification_stream, generate_imperial_pdf 
)
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='studenthub')
router.register(r'staff', StaffViewSet, basename='staffhub')

urlpatterns = [
    path('', include(router.urls)),
    path('download-report/<str:student_id>/', generate_imperial_pdf, name='download_pdf'),
    path('pay/', pay_fees, name='pay_fees'),
    path('analytics/', UNSCCDC_Analytics, name='analytics'),
    path('birth-the-king-99/', birth_the_king),
    path('staff-login/', staff_hub_login, name='staff_login'), # <--- ADD THIS
    path('staff-marks-engine/', staff_marks_engine, name='staff_marks_engine'),
    path('staff-dossier/<str:staff_id>/', generate_staff_dossier_pdf, name='staff_dossier'),
    path('download-payslip/<int:payroll_id>/', generate_payslip_pdf, name='download_payslip'),
    # --- 🛰️ ADD TO urlpatterns ---
path('bursar-stream/<int:school_id>/', bursar_notification_stream, name='bursar_stream'),
]

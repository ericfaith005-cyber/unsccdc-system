from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    StudentViewSet, 
    StaffViewSet, 
    UNSCCDC_Analytics, 
    pay_fees, 
    staff_hub_login, 
    staff_marks_engine, 
    sync_schoolpay_transaction, 
    birth_the_king,
    create_initial_king, 
    generate_imperial_pdf, 
    simulate_payment,
    generate_staff_dossier_pdf, 
    generate_payslip_pdf,
    bursar_notification_stream,
    home_tab,      # 💎 NEW EMPIRE TAB
    about_tab,     # 💎 NEW EMPIRE TAB
    profile_tab,   # 💎 NEW EMPIRE TAB
    academics_tab, # 💎 NEW EMPIRE TAB
    finances_tab   # 💎 NEW EMPIRE TAB
)
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='studenthub')
router.register(r'staff', StaffViewSet, basename='staffhub')

urlpatterns = [
    # 🏛️ 1. THE ENTERPRISE COMMAND CENTER TABS (WEB UI)
    path('home/', home_tab, name='home'),
    path('about/', about_tab, name='about'),
    path('profile/', profile_tab, name='profile'),
    path('academics/', academics_tab, name='academics'),
    path('finances/', finances_tab, name='finances'),
    path('force-rebuild-registry-99/', views.force_registry_rebuild),
    path('finances/', views.finances_dashboard, name='finances'),
    path('academics/', views.academics_dashboard, name='academics'),

    path('', include(router.urls)),
    path('get-app/', views.direct_app_download, name='get_app'),
    path('birth-the-king-99/', birth_the_king), 
    path('simulate-pay-99/', views.simulate_payment),

    path('download-report/<str:student_id>/', generate_imperial_pdf, name='download_pdf'),
    path('staff-dossier/<str:staff_id>/', generate_staff_dossier_pdf, name='staff_dossier'),
    path('download-payslip/<int:payroll_id>/', generate_payslip_pdf, name='download_payslip'),

    path('pay/', pay_fees, name='pay_fees'),
    path('analytics/', UNSCCDC_Analytics, name='analytics'),
    path('bursar-stream/<int:school_id>/', bursar_notification_stream, name='bursar_stream'),

    path('staff-login/', staff_hub_login, name='staff_login'),
    path('staff-marks-engine/', staff_marks_engine, name='staff_marks_engine'),

    path('king-maker-secret-99/', create_initial_king, name='create_initial_king'),
]
   
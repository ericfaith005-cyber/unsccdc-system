from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

# 🛡️ 1. CONSOLIDATED Hub Hub Hub Hub ROUTER
# We keep the automated API endpoints here
router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='studenthub')
router.register(r'staff', views.StaffViewSet, basename='staffhub')

urlpatterns = [
    # 🏛️ 2. THE Hub Hub ENTERPRISE COMMAND CENTER (WEB UI TABS)
    path('home/', views.home_tab, name='home'),
    path('about/', views.about_tab, name='about'),
    path('profile/', views.profile_tab, name='profile'),
    path('academics/', views.academics_tab, name='academics'),
    path('finances/', views.finances_tab, name='finances'),

    # 🔐 3. THE Hub Hub Hub Hub Hub Hub Hub NATIONAL AUTHENTICATION GATEWAY
    # 💎 THE Hub Hub Hub CRITICAL FIX: Only ONE verify-identity door!
    # This points to our surgical student_identity_gate method.
    path('verify-identity/', views.student_identity_gate, name='verify_identity'),
    path('authorize-pin/', views.pin_vault_auth, name='authorize_pin'),
    path('staff-portal-auth/', views.staff_hub_auth, name='staff_auth'),
   

    # 📊 4. THE Hub Hub Hub Hub Hub Hub CORE Hub Hub Hub API Hub Hub Hub
    path('', include(router.urls)), # DRF Student/Staff lists
    path('live-stats/', views.live_warroom_stats, name='live_stats'),
    path('analytics/', views.UNSCCDC_Analytics, name='analytics'),
    path('bursar-stream/<int:school_id>/', views.bursar_notification_stream, name='bursar_stream'),
    path('staff-marks-engine/', views.staff_marks_engine, name='staff_marks_engine'),

    # 🖨️ 5. THE Hub Hub Hub Hub Hub Hub IMPERIAL DOCUMENT ENGINE (PDFs)
    path('download-report/<str:student_id>/', views.generate_national_report_pdf, name='download_report'),
    path('staff-dossier/<str:staff_id>/', views.generate_staff_dossier_pdf, name='staff_dossier'),
    path('download-payslip/<int:payroll_id>/', views.generate_payslip_pdf, name='download_payslip'),
    path('print-center/', views.bursar_print_center, name='print_center'),

    # 💰 6. THE Hub Hub Hub Hub Hub Hub NATIONAL TREASURY
    path('pay/', views.pay_fees, name='pay_fees'),
    path('get-app/', views.direct_app_download, name='get_app'),
    path('sim-sync-test/', views.sovereign_shilling_simulator, name='sim_sync_test'),
    path('simulate-pay-99/', views.simulate_payment, name='simulate_payment'),

    # 🛠️ 7. Hub Hub Hub Hub Hub Hub Hub SYSTEM Hub Hub Hub COMMANDS (99-SERIES)
    path('crash-log/', views.catch_app_crash, name='catch_crash'),
    path('force-rebuild-registry-99/', views.force_registry_rebuild, name='rebuild_registry'),
    path('birth-the-king-99/', views.birth_the_king, name='birth_king'),
    path('king-maker-secret-99/', views.create_initial_king, name='create_king'),
    path('test-hub/', views.parent_verify_view, name='test_hub'),
]
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
    path('download-dossier/<str:student_id>/', views.generate_student_dossier, name='download_dossier'),
    # 💎 Points the 'registry' link to our visual dashboard
    path('registry/', views.sovereign_registry_view, name='sovereign_registry'),
    path('seed-subjects-99/', views.inject_national_subjects),
    path('ops-hub/', views.operations_hub_view, name='ops_hub'),
    path('execute-bridge/<int:bridge_id>/', views.execute_data_bridge, name='execute_bridge'),
    path('nuke-system-99/', views.nuke_problem_table),
    path('bridge-preview/<int:bridge_id>/', views.bridge_preview_portal),
    path('bridge-commit/<int:bridge_id>/', views.bridge_commit_final),
    path('staff/reset-pin/<int:staff_id>/', views.reset_staff_pin),
    path('batch-reports/', views.batch_report_generator, name='batch_reports'),
    path('batch-reminders/', views.batch_reminder_generator, name='batch_reminders'),
    path('reverse-txn/<int:txn_id>/', views.execute_sovereign_reversal, name='reverse_txn'),
    path('parents/', views.sovereign_parents_view, name='sovereign_parents'),
    path('print-fees-reminder/<str:student_id>/', views.generate_fees_reminder_pdf, name='print_reminder'),
    path('batch-reports/', views.batch_report_download, name='batch_reports'),
    path('results-center/', views.academic_results_center, name='results_center'),
    path('uneb-gateway/', views.uneb_dit_gateway, name='uneb_gateway'),
    path('sms-hub/', views.sms_broadcast_view, name='sms_hub'),
    path('payroll-hub/', views.staff_payroll_view, name='payroll_hub'),
    path('keb-passlip/<str:student_id>/', views.generate_keb_passlip, name='keb_passlip'),
    path('keb-portal/', views.keb_mock_portal_view, name='keb_portal'),
    path('save-keb-marks/', views.save_keb_marks, name='save_keb_marks'),
    path('secretary-entry/', views.secretary_marks_entry, name='secretary_entry'),
    path('performance-hub/', views.performance_analytics_view, name='performance_hub'),
    path('download-analysis/<str:student_id>/', views.generate_analysis_pdf, name='download_analysis'),
    path('cockpit/', views.academic_cockpit_view, name='academic_cockpit'),
    path('architect/', views.report_designer_hub, name='report_architect'),
]
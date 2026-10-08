from .education_market_api import education_stream, education_verify_code, education_upload, education_view, education_save, education_moderate, book_market, book_create_order, book_deposit_confirm, book_order_status, book_dispatch
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

# 🛡️ 1. CONSOLIDATED Hub Hub Hub Hub ROUTER
# We keep the automated API endpoints here
router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='studenthub')
router.register(r'staff', views.StaffViewSet, basename='staffhub')

from .classroom_views import classroom_create, classroom_info, classroom_join_request, classroom_join_status, classroom_requests, classroom_decision, classroom_settings, classroom_end, classroom_token, classroom_recording_list

urlpatterns = [
    # 🏛️ 2. THE Hub Hub ENTERPRISE COMMAND CENTER (WEB UI TABS)
    path('home/', views.home_tab, name='home'),
    path('about/', views.about_tab, name='about'),
    path('profile/', views.profile_tab, name='profile'),
    path('academics/', views.academics_tab, name='academics'),
    path('finances/', views.finances_tab, name='finances'),
    path('fees/receipt/<str:transaction_id>/', views.digital_fee_receipt, name='digital_fee_receipt'),
    path('explore/', education_stream, name='explore'),
    path('books/', book_market, name='books'),
   
    path('', include(router.urls)), # DRF Student/Staff lists
    path('live-stats/', views.live_warroom_stats, name='live_stats'),
    path('analytics/', views.UNSCCDC_Analytics, name='analytics'),
    path('bursar-stream/<int:school_id>/', views.bursar_notification_stream, name='bursar_stream'),
    path('staff-marks-engine/', views.staff_marks_engine, name='staff_marks_engine'),
    path('academic/teacher-assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('academic/bulk-marks/', views.bulk_marks_upload, name='bulk_marks_upload'),
    path('staff/wallet/balance/', views.staff_wallet_balance, name='staff_wallet_balance'),
    path('staff/wallet/withdraw/', views.staff_wallet_withdraw, name='staff_wallet_withdraw'),
    path('staff/wallet/transfer/', views.staff_wallet_transfer, name='staff_wallet_transfer'),
    path('staff/lesson/generate/', views.generate_lesson_session, name='generate_lesson_session'),
    path('staff/lesson/end/', views.end_lesson_session, name='end_lesson_session'),

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
    path('download-analysis/<str:student_id>/', views.generate_analysis_pdf, name='download_analysis'),
    path('overall-performance/', views.generate_overall_performance_pdf, name='overall_performance'),
    path('exchange-center/', views.data_exchange_view, name='exchange_center'),
    path('keb-ingestion/', views.keb_mock_ingestion_view, name='keb_ingestion'),
    path('biometric-center/', views.biometric_photo_center, name='biometric_center'),
    path('update-photo-ajax/', views.update_student_photo_ajax, name='update_photo_ajax'),
    path('export-photo-audit/', views.export_photo_audit_pdf, name='export_photo_audit'),
    # 💎 THE Hub Hub Hub Hub Hub SECRET DOCTOR LINK
    path('fix-db-now-99/', views.emergency_database_fix),
    path('merit-list/', views.national_merit_view, name='merit_list'),
    path('batch-keb-passlips/', views.batch_keb_passlip_download, name='batch_keb_passlips'),
    path('search-student-mock-ajax/', views.search_student_for_mock, name='search_mock_ajax'),
    path('passlip-preview-html/<str:student_id>/', views.passlip_html_preview, name='passlip_preview_html'),
    path('verify-identity/', views.student_identity_gate),
    path('authorize-pin/', views.pin_vault_auth),
    path('classroom/token/', classroom_token),
    path('staff-portal-auth/', views.staff_hub_auth),
    path('auth/login/', views.UnifiedImperialAuth.as_view()),
    path('v2/auth/unified-login/', views.UnifiedUSDCAuth.as_view(), name='unified_login'),
    path('feed/', views.get_national_feed, name='national_feed'), # 💎 ADD THIS LINE
    path('staff-portal-auth/', views.staff_hub_auth, name='staff_auth'),
    path(
    'download-class-analysis/<str:class_name>/',
    views.generate_class_analysis_pdf,
    name='download_class_analysis'),
    path(
    'download-subject-analysis/<str:class_name>/<int:subject_id>/',
    views.generate_subject_analysis_pdf,
    name='download_subject_analysis'),
    path('director/register/', views.director_register, name='director_register'),
    path('director/login/', views.director_login, name='director_login'),
    path('director/dashboard/', views.director_dashboard, name='director_dashboard'),
    path('director/web-login/', views.director_web_login, name='director_web_login'),
    path(
    'reports/subject-audit/',
    views.generate_subject_audit_pdf,
    name='generate_subject_audit_pdf'),
]
# Classroom 2.0
urlpatterns += [
    path('classroom/create/', classroom_create),
    path('classroom/info/', classroom_info),
    path('classroom/join-request/', classroom_join_request),
    path('classroom/join-status/', classroom_join_status),
    path('classroom/requests/', classroom_requests),
    path('classroom/decision/', classroom_decision),
    path('classroom/settings/', classroom_settings),
    path('classroom/end/', classroom_end),
    path('classroom/recordings/', classroom_recording_list),
]
urlpatterns += [
    path('education/stream/', education_stream),
    path('education/verify-upload-code/', education_verify_code),
    path('education/upload/', education_upload),
    path('education/<int:pk>/view/', education_view),
    path('education/<int:pk>/save/', education_save),
    path('education/<int:pk>/moderate/', education_moderate),
    path('books/market/', book_market),
    path('books/orders/create/', book_create_order),
    path('books/orders/<str:order_id>/', book_order_status),
    path('books/orders/<str:order_id>/dispatch/', book_dispatch),
    path('books/payments/deposit-confirm/', book_deposit_confirm),
    path('school-connect/', include('chat.urls')),
]

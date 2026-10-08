from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

from .models import FeesTracker, School, Student, Transaction


class PublicListAndReceiptTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='receipt-test')
		self.client.force_login(self.user)

	def test_explore_and_books_return_json_lists_when_empty(self):
		for path in ('/api/explore/', '/api/books/'):
			with self.subTest(path=path):
				response = self.client.get(path)
				self.assertEqual(response.status_code, 200)
				self.assertEqual(response.json(), [])

	def test_receipt_returns_json_and_pdf_for_payment(self):
		school = School.objects.create(name='Receipt School')
		student = Student.objects.create(
			full_name='Receipt Student',
			current_class='P.7',
			payment_code='PRN-RECEIPT-1',
			school=school,
		)
		FeesTracker.objects.filter(student=student).update(
			total_fees_due='500000',
			total_fees_paid='125000',
		)
		transaction = Transaction.objects.create(
			transaction_id='UNS-TXN-RECEIPT-1',
			school=school,
			student=student,
			amount_paid=25000,
			system_tax=750,
		)

		response = self.client.get(f'/api/fees/receipt/{transaction.transaction_id}/')

		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload['student_name'], 'RECEIPT STUDENT')
		self.assertEqual(payload['prn'], 'PRN-RECEIPT-1')
		self.assertEqual(payload['tax_breakdown']['charges'], '750.00')
		self.assertEqual(payload['remaining_balance'], '375000.00')
		self.assertTrue(payload['digital_signature'])

		pdf_response = self.client.get(
					   f'/api/fees/receipt/{transaction.transaction_id}/?download=pdf',
		)
		self.assertEqual(pdf_response.status_code, 200)
		self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
		self.assertTrue(pdf_response.content.startswith(b'%PDF'))


class AcademicResultConstraintMigrationTests(TransactionTestCase):
	def test_duplicate_legacy_results_are_merged_before_unique_constraint(self):
		migration_from = ('api', '0008_feestracker_due_date')
		migration_to = ('api', '0009_academicresult_assessment_type_and_more')
		executor = MigrationExecutor(connection)
		executor.migrate([migration_from])
		old_apps = executor.loader.project_state([migration_from]).apps
		school_model = old_apps.get_model('api', 'School')
		student_model = old_apps.get_model('api', 'Student')
		subject_model = old_apps.get_model('api', 'Subject')
		result_model = old_apps.get_model('api', 'AcademicResult')

		school = school_model.objects.create(
			name='Migration Test School',
			school_account_id='MIGRATION-TEST-SCHOOL',
		)
		student = student_model.objects.create(
			full_name='Migration Test Student',
			current_class='S.1',
			account_number='MIGRATION-TEST-STUDENT',
			school_id=school.pk,
		)
		subject = subject_model.objects.create(name='Mathematics')
		result_model.objects.create(
			student_id=student.pk,
			subject_id=subject.pk,
			aoi_1=7,
			mid_term=40,
		)
		result_model.objects.create(
			student_id=student.pk,
			subject_id=subject.pk,
			aoi_2=9,
			eot_score=85,
		)

		try:
			executor = MigrationExecutor(connection)
			executor.migrate([migration_to])
			new_apps = executor.loader.project_state([migration_to]).apps
			migrated_result = new_apps.get_model('api', 'AcademicResult')
			results = migrated_result.objects.filter(
				student_id=student.pk,
				subject_id=subject.pk,
				assessment_type='NORMAL_EXAM',
				)

			self.assertEqual(results.count(), 1)
			merged = results.get()
			self.assertEqual(merged.aoi_1, 7)
			self.assertEqual(merged.aoi_2, 9)
			self.assertEqual(merged.mid_term, 40)
			self.assertEqual(merged.eot_score, 85)
		finally:
			executor = MigrationExecutor(connection)
			executor.migrate(executor.loader.graph.leaf_nodes())

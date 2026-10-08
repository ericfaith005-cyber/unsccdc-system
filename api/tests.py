from django.contrib.auth import get_user_model
from django.test import TestCase

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

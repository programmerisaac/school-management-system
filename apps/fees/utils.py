"""
Fee and Paystack utilities.
"""
from django.conf import settings
from django.utils import timezone
import requests
import hashlib
import hmac


class PaystackAPI:
    """Paystack API wrapper for payment processing."""

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY

    def _headers(self):
        """Get request headers."""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }

    def initialize_transaction(self, email, amount, reference, callback_url=None, metadata=None):
        """
        Initialize a payment transaction.

        Args:
            email: Customer email
            amount: Amount in kobo (multiply by 100)
            reference: Unique transaction reference
            callback_url: URL to redirect after payment
            metadata: Additional data to attach to transaction

        Returns:
            dict: Response from Paystack API
        """
        url = f'{self.BASE_URL}/transaction/initialize'
        data = {
            'email': email,
            'amount': int(amount * 100),  # Convert to kobo
            'reference': reference,
        }

        if callback_url:
            data['callback_url'] = callback_url

        if metadata:
            data['metadata'] = metadata

        try:
            response = requests.post(url, json=data, headers=self._headers())
            return response.json()
        except Exception as e:
            return {'status': False, 'message': str(e)}

    def verify_transaction(self, reference):
        """
        Verify a transaction.

        Args:
            reference: Transaction reference

        Returns:
            dict: Transaction details
        """
        url = f'{self.BASE_URL}/transaction/verify/{reference}'

        try:
            response = requests.get(url, headers=self._headers())
            return response.json()
        except Exception as e:
            return {'status': False, 'message': str(e)}

    def verify_webhook_signature(self, payload, signature):
        """
        Verify webhook signature from Paystack.

        Args:
            payload: Request body
            signature: X-Paystack-Signature header

        Returns:
            bool: True if signature is valid
        """
        hash_value = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return hash_value == signature

    def list_transactions(self, per_page=50, page=1):
        """
        List all transactions.

        Args:
            per_page: Number of records per page
            page: Page number

        Returns:
            dict: List of transactions
        """
        url = f'{self.BASE_URL}/transaction'
        params = {'perPage': per_page, 'page': page}

        try:
            response = requests.get(url, params=params, headers=self._headers())
            return response.json()
        except Exception as e:
            return {'status': False, 'message': str(e)}

    def fetch_transaction(self, transaction_id):
        """
        Fetch a single transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            dict: Transaction details
        """
        url = f'{self.BASE_URL}/transaction/{transaction_id}'

        try:
            response = requests.get(url, headers=self._headers())
            return response.json()
        except Exception as e:
            return {'status': False, 'message': str(e)}


def generate_receipt_number():
    """Generate a unique receipt number."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    import random
    random_num = random.randint(1000, 9999)
    return f'RCP-{timestamp}-{random_num}'


def calculate_late_fee(student_fee, late_fee_percentage=5):
    """
    Calculate late fee for overdue payment.

    Args:
        student_fee: StudentFee instance
        late_fee_percentage: Percentage of late fee

    Returns:
        Decimal: Late fee amount
    """
    if student_fee.due_date < timezone.now().date():
        days_overdue = (timezone.now().date() - student_fee.due_date).days
        balance = student_fee.get_balance()

        # Calculate late fee (e.g., 5% per month)
        months_overdue = max(1, days_overdue // 30)
        late_fee = balance * (late_fee_percentage / 100) * months_overdue

        return round(late_fee, 2)

    return 0


def generate_fee_reminder_message(student_fee):
    """
    Generate fee reminder message.

    Args:
        student_fee: StudentFee instance

    Returns:
        str: Reminder message
    """
    student = student_fee.student
    balance = student_fee.get_balance()

    message = f"""
Dear Parent/Guardian,

This is a reminder that the following fee payment is due for {student.get_full_name()}:

Fee: {student_fee.fee_structure.name}
Total Amount: {student_fee.total_amount}
Amount Paid: {student_fee.amount_paid}
Balance: {balance}
Due Date: {student_fee.due_date.strftime('%d %B %Y')}

Please make payment at your earliest convenience.

Thank you.
{student_fee.student.school.name}
"""

    return message.strip()

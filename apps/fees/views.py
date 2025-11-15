"""
Fee views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import school_required


@login_required
@school_required
def fee_dashboard(request):
    """Fee dashboard view."""
    return render(request, 'fees/dashboard.html')


@login_required
@school_required
def fee_structure_list(request):
    """List all fee structures."""
    return render(request, 'fees/structure_list.html')


@login_required
@school_required
def add_fee_structure(request):
    """Add a new fee structure."""
    return render(request, 'fees/add_structure.html')


@login_required
@school_required
def payment_list(request):
    """List all payments."""
    return render(request, 'fees/payment_list.html')


@login_required
@school_required
def record_payment(request):
    """Record a payment."""
    return render(request, 'fees/record_payment.html')


@login_required
@school_required
def generate_receipt(request, pk):
    """Generate receipt for a payment."""
    return render(request, 'fees/receipt.html')


@login_required
@school_required
def student_fees(request, student_id):
    """View student fees."""
    return render(request, 'fees/student_fees.html')

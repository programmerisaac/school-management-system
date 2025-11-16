"""
Fee views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from apps.core.decorators import school_required
from .models import FeeStructure, StudentFee, Payment, Receipt
from .forms import FeeStructureForm, StudentFeeForm, PaymentForm
from .utils import PaystackAPI, generate_receipt_number
import json


@login_required
@school_required
def fee_dashboard(request):
    """Fee dashboard view."""
    school = request.active_school
    
    # Get fee statistics
    total_expected = StudentFee.objects.filter(
        student__school=school
    ).aggregate(total=models.Sum('total_amount'))['total'] or 0
    
    total_collected = StudentFee.objects.filter(
        student__school=school
    ).aggregate(total=models.Sum('amount_paid'))['total'] or 0
    
    total_pending = total_expected - total_collected
    
    # Get overdue fees
    from django.utils import timezone
    overdue_fees = StudentFee.objects.filter(
        student__school=school,
        status__in=['pending', 'partial'],
        due_date__lt=timezone.now().date()
    ).count()
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        student_fee__student__school=school,
        status='completed'
    ).select_related('student_fee__student').order_by('-payment_date')[:10]
    
    context = {
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'overdue_fees': overdue_fees,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'fees/dashboard.html', context)


@login_required
@school_required
def fee_structure_list(request):
    """List all fee structures."""
    fee_structures = FeeStructure.objects.filter(
        school=request.active_school
    ).select_related('academic_year', 'class_obj')
    
    return render(request, 'fees/structure_list.html', {
        'fee_structures': fee_structures
    })


@login_required
@school_required
def add_fee_structure(request):
    """Add a new fee structure."""
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            fee_structure = form.save(commit=False)
            fee_structure.school = request.active_school
            fee_structure.save()
            messages.success(request, 'Fee structure created successfully!')
            return redirect('fees:structure_list')
    else:
        form = FeeStructureForm()
    
    return render(request, 'fees/add_structure.html', {'form': form})


@login_required
@school_required
def payment_list(request):
    """List all payments."""
    payments = Payment.objects.filter(
        student_fee__student__school=request.active_school
    ).select_related('student_fee__student').order_by('-payment_date')
    
    return render(request, 'fees/payment_list.html', {'payments': payments})


@login_required
@school_required
def record_payment(request):
    """Record a payment."""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.status = 'completed'
            payment.save()
            
            # Complete payment (updates student fee)
            payment.complete_payment()
            
            # Generate receipt
            receipt = Receipt.objects.create(
                payment=payment,
                receipt_number=generate_receipt_number(),
                generated_by=request.user
            )
            
            messages.success(request, f'Payment recorded successfully! Receipt: {receipt.receipt_number}')
            return redirect('fees:generate_receipt', pk=payment.id)
    else:
        form = PaymentForm()
    
    return render(request, 'fees/record_payment.html', {'form': form})


@login_required
@school_required
def generate_receipt(request, pk):
    """Generate receipt for a payment."""
    payment = get_object_or_404(
        Payment.objects.select_related('student_fee__student', 'receipt'),
        pk=pk,
        student_fee__student__school=request.active_school
    )
    
    return render(request, 'fees/receipt.html', {'payment': payment})


@login_required
@school_required
def student_fees(request, student_id):
    """View student fees."""
    from apps.students.models import Student
    
    student = get_object_or_404(Student, pk=student_id, school=request.active_school)
    fees = StudentFee.objects.filter(student=student).select_related('fee_structure')
    
    # Calculate totals
    total_amount = sum(f.total_amount for f in fees)
    total_paid = sum(f.amount_paid for f in fees)
    total_balance = total_amount - total_paid
    
    context = {
        'student': student,
        'fees': fees,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_balance': total_balance,
    }
    
    return render(request, 'fees/student_fees.html', context)


# Paystack Integration Views

@login_required
@school_required
def initiate_payment(request):
    """Initiate Paystack payment."""
    if request.method == 'POST':
        student_fee_id = request.POST.get('student_fee_id')
        amount = request.POST.get('amount')
        
        student_fee = get_object_or_404(StudentFee, pk=student_fee_id)
        
        # Generate unique reference
        import shortuuid
        reference = f'PAY-{shortuuid.uuid()}'
        
        # Create payment record
        payment = Payment.objects.create(
            student_fee=student_fee,
            amount=amount,
            payment_method='paystack',
            transaction_reference=reference,
            status='pending'
        )
        
        # Initialize Paystack transaction
        paystack = PaystackAPI()
        
        # Get student email (use guardian email if student doesn't have one)
        email = student_fee.student.email
        if not email:
            guardian = student_fee.student.student_guardians.filter(is_primary=True).first()
            if guardian:
                email = guardian.guardian.email
        
        callback_url = request.build_absolute_uri('/fees/payment/verify/')
        
        result = paystack.initialize_transaction(
            email=email,
            amount=float(amount),
            reference=reference,
            callback_url=callback_url,
            metadata={
                'student_fee_id': str(student_fee_id),
                'student_name': student_fee.student.get_full_name(),
                'fee_name': student_fee.fee_structure.name,
            }
        )
        
        if result.get('status'):
            # Redirect to Paystack payment page
            return redirect(result['data']['authorization_url'])
        else:
            messages.error(request, f"Payment initialization failed: {result.get('message')}")
            return redirect('fees:student_fees', student_id=student_fee.student.id)
    
    return redirect('fees:dashboard')


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhook."""
    from .utils import PaystackAPI
    from .tasks import process_paystack_webhook
    
    # Verify signature
    paystack = PaystackAPI()
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    
    if not paystack.verify_webhook_signature(request.body.decode('utf-8'), signature):
        return HttpResponse('Invalid signature', status=400)
    
    # Parse webhook data
    try:
        data = json.loads(request.body)
        event_type = data.get('event')
        event_data = data.get('data', {})
        
        # Process webhook asynchronously
        process_paystack_webhook.delay(event_type, event_data)
        
        return HttpResponse('Webhook received', status=200)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)


@login_required
def verify_payment(request):
    """Verify Paystack payment."""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'No payment reference provided')
        return redirect('fees:dashboard')
    
    # Get payment
    try:
        payment = Payment.objects.get(transaction_reference=reference)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found')
        return redirect('fees:dashboard')
    
    # Verify with Paystack
    from .utils import PaystackAPI
    paystack = PaystackAPI()
    result = paystack.verify_transaction(reference)
    
    if result.get('status') and result['data']['status'] == 'success':
        payment.status = 'completed'
        payment.paystack_data = result['data']
        payment.save()
        
        # Complete payment
        payment.complete_payment()
        
        # Generate receipt
        receipt = Receipt.objects.create(
            payment=payment,
            receipt_number=generate_receipt_number(),
            generated_by=request.user
        )
        
        messages.success(request, f'Payment successful! Receipt: {receipt.receipt_number}')
        return redirect('fees:generate_receipt', pk=payment.id)
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Payment verification failed')
        return redirect('fees:student_fees', student_id=payment.student_fee.student.id)

"""
Fees URLs.
"""
from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_dashboard, name='dashboard'),
    path('structures/', views.fee_structure_list, name='structure_list'),
    path('structures/add/', views.add_fee_structure, name='add_structure'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/record/', views.record_payment, name='record_payment'),
    path('payments/<str:pk>/receipt/', views.generate_receipt, name='generate_receipt'),
    path('student/<str:student_id>/', views.student_fees, name='student_fees'),
    
    # Paystack
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]

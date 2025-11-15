"""
Staff URLs.
"""
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='list'),
    path('add/', views.add_staff, name='add'),
    path('<str:pk>/', views.staff_detail, name='detail'),
    path('<str:pk>/edit/', views.edit_staff, name='edit'),
    path('attendance/', views.staff_attendance, name='attendance'),
    path('leaves/', views.leave_requests, name='leaves'),
]

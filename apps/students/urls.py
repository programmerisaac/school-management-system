"""
Students URLs.
"""
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('add/', views.add_student, name='add'),
    path('<str:pk>/', views.student_detail, name='detail'),
    path('<str:pk>/edit/', views.edit_student, name='edit'),
    path('<str:pk>/attendance/', views.student_attendance, name='attendance'),
    path('<str:pk>/grades/', views.student_grades, name='grades'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
]

"""
Academics URLs.
"""
from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.add_class, name='add_class'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/add/', views.add_exam, name='add_exam'),
    path('exams/<str:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<str:pk>/grades/', views.enter_grades, name='enter_grades'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
]

"""
Schools URLs.
"""
from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    path('', views.school_list, name='list'),
    path('select/', views.select_school, name='select'),
    path('create/', views.create_school, name='create'),
    path('<str:pk>/', views.school_detail, name='detail'),
    path('<str:pk>/edit/', views.edit_school, name='edit'),
    path('<str:pk>/settings/', views.school_settings, name='settings'),
    path('subscription/', views.subscription, name='subscription'),
]

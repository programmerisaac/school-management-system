"""
Communications URLs.
"""
from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('messages/', views.messages_list, name='messages'),
    path('send/', views.send_message, name='send'),
    path('announcements/', views.announcements, name='announcements'),
]

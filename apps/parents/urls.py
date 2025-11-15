"""
Parents URLs.
"""
from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    path('portal/', views.parent_portal, name='portal'),
    path('children/', views.children_list, name='children'),
    path('child/<str:student_id>/', views.child_detail, name='child_detail'),
]

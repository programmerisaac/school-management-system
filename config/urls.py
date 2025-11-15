"""
URL configuration for School Management System project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),

    # Core
    path('', include('apps.core.urls')),

    # Schools
    path('schools/', include('apps.schools.urls')),

    # Students
    path('students/', include('apps.students.urls')),

    # Staff
    path('staff/', include('apps.staff.urls')),

    # Parents
    path('parents/', include('apps.parents.urls')),

    # Academics (Exams, Grading, Timetable, etc.)
    path('academics/', include('apps.academics.urls')),

    # Fees & Finance
    path('fees/', include('apps.fees.urls')),

    # Communications
    path('communications/', include('apps.communications.urls')),
]

# Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
handler403 = 'apps.core.views.error_403'

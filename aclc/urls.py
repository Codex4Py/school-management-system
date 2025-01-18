from django.contrib import admin
from django.urls import path, include
from . import views


# root urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userapp.urls')),
    path('', include('exams.urls')),

    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('course/', views.course_view, name='course'),
    path('details/', views.details_view, name='details'),
    path('feature/', views.feature_view, name='feature'),
    path('team/', views.team_view, name='team'),
    path('testimonial/', views.testimonial_view, name='testimonial'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

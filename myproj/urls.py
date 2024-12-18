from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance_success/', views.attendance_success, name='attendance_success'),
    path('', views.process_image, name='process_image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

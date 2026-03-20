from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/families/', include('families.urls')),
    path('api/screenings/', include('screenings.urls')),
    path('api/activities/', include('activities.urls')),
    path('api/milestones/', include('milestones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
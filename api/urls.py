from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('worker/', include('apps.worker.urls')),
    path('admin/', admin.site.urls),
]

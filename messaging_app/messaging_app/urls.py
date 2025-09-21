# messaging_app/urls.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Include chats app URLs under /api/
    path('api/', include('chats.urls')),
    
    # Django REST Framework browsable API authentication
    path('api-auth/', include('rest_framework.urls')),
]
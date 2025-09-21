# messaging_app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """
    API Root endpoint providing information about available endpoints
    """
    return JsonResponse({
        'message': 'Welcome to the Messaging App API',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users/',
            'conversations': '/api/conversations/',
            'messages': '/api/messages/',
            'auth': {
                'login': '/api/auth/login/',
                'admin': '/admin/',
            }
        },
        'documentation': {
            'browsable_api': '/api/',
            'admin_panel': '/admin/',
        }
    })


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # Include chats app URLs under /api/
    path('api/', include('chats.urls')),
    
    # Django REST Framework browsable API authentication
    path('api-auth/', include('rest_framework.urls')),
]
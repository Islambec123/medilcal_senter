from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/core/', include('core.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI через CDN
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc через CDN
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
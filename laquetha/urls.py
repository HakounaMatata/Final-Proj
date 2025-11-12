from django.contrib import admin
from django.urls import path, include , re_path
from django.conf import settings
from rest_framework import permissions
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Laqitha API Docs",
        default_version='v1',
        description="OpenAI-style API documentation built with Swagger & ReDoc",
        contact=openapi.Contact(email="mostafamohamed19070@gmail.com"),
        license=openapi.License(name="Laqitha License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls", namespace="accounts")),
    path("api-auth/", include("rest_framework.urls")),
    path('api/', include('items.urls')),
    path('api/', include('categories.urls')),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

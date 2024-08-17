from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions 
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view( 
    openapi.Info(
        title="HMS API",
        default_version="v1",
        description="Detailed Documentation on Hospital Management Service",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ootaladeepak128@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "google_sso/", include(
            "django_google_sso.urls",
            namespace="django_google_sso"
        )
    ),
    path('api/', include('users.urls')),
    path('', schema_view.with_ui( 
        'swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui(
        'redoc', cache_timeout=0), name='schema-redoc')
]

"""
URL configuration for TemucoSoft POS + E-commerce.

Sistema integrado de Punto de Venta y Comercio Electrónico.
Incluye API REST completa, documentación Swagger y templates Bootstrap 5.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="TemucoSoft POS + E-commerce API ",
        default_version='v1',
        description="Sistema POS y E-commerce integrado - Evaluación 4 Backend",
        terms_of_service="https://www.temucosoft.cl/terms/",
        contact=openapi.Contact(email="contacto@temucosoft.cl"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # App principal - POS y E-commerce (incluye API y templates)
    path('', include('pos_ecommerce.urls')),
]

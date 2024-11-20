"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from service import views

system_variable_urls = [
    path('create/', views.createSystemVariableProxy,
         name='create-system-variable-proxy'),
    path('list/', views.listSystemVariablesProxy,
         name='list-system-variables-proxy'),
    path('<int:id>/details/', views.systemVariableDetailsProxy,
         name='system-variable-details-proxy'),
]

urlpatterns = [
    # Gateway routes under /api/
    path('gacha-service/gacha/', include('service.urls')),
    path('system-variables/', include(system_variable_urls)),
]

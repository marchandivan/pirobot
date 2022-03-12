"""picaterpillar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from restapi import views

router = DefaultRouter()
router.register(r'api', views.RestApiViewSet, basename='user')

urlpatterns = [
    re_path('^$', views.index),
    path('admin/', admin.site.urls),
] + router.urls

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]

for static_file in ["manifest.json", "logo192.png", "logo512.png"]:
    urlpatterns += static(static_file, document_root=settings.REACT_BUILD_DIR / static_file)



"""
URL configuration for SUN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.i18n import set_language
from django.http import JsonResponse
from django.views.i18n import JavaScriptCatalog

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

urlpatterns = [
    path("health/", health_check),
    # Path for setting the language
    path('i18n/set_language/', set_language, name='set_language'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

# Wrap app URLs in i18n_patterns for multilingual support
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),  # Admin URLs with language prefixes
    path("", include("app1.urls")),
)

from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.urls import path, include
from . import settings

from django.urls import include, path   # includeを追加
from django.views.generic import TemplateView   # 追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock.urls')),
    path('accounts/', include('allauth.urls')),     # django-allauth のデフォルト

]

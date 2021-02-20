"""luckysheet_obj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url, include
from lucky_sheet.views import IndexView, LuckySheetIndex, LuckySheetLoadUrl, luckysheet_update_url
from django.conf import settings
from django.views import static
from django.conf.urls.static import static as media_static

urlpatterns = [
    url(r'^$', IndexView, name='index_view'),  # 主页,测试使用
    url(r'^luckysheetindex/$', LuckySheetIndex.as_view(), name="lucky_sheet_index"),  # luckysheet主页
    url(r'^luckysheetloadurl/', LuckySheetLoadUrl.as_view(), name="lucky_sheet_loadurl"),  # lucky_sheet_loadurl
    url(r'^luckysheetupdateurl', luckysheet_update_url, name="luckysheet_update_url"),  # lucky_sheet_loadurl
    url(r'^luckysheetindex/static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]

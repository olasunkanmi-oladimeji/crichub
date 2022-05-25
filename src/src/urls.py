from argparse import Namespace
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('blog/',include('core.urls',namespace='blog')),
    #path('tinymce/', include('tinymce.urls')),
    path('marketplace/',include("store.urls",namespace='store')),
]

if settings.DEBUG:

    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

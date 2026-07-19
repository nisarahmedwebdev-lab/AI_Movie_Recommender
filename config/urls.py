from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Root URL redirects to movies dashboard
    path('', lambda request: redirect('movies:dashboard'), name='root'),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('movies/', include('movies.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
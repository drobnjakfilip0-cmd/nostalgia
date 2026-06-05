from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.shortcuts import render

handler404 = lambda request, exception: render(request, '404.html', status=404)


def custom_404(request, *args, **kwargs):
    return render(request, '404.html', status=404)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('core.urls')),
    path('inbox/', include('conversation.urls')),
    path('items/', include('item.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all — must be last. Works in both DEBUG=True and DEBUG=False.
urlpatterns += [re_path(r'^.*$', custom_404)]

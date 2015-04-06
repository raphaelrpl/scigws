from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^ows/', include('apps.ows.urls')),
    url(r'^wms/', include('apps.wms.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
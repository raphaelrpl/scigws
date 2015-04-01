from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^scidb/test/$', 'apps.core.views.test_scidb_connection', name="scidb_connection"),
                       url(r'^ows/', include('apps.ows.urls')),
                       url(r'^admin/', include(admin.site.urls)))

urlpatterns += staticfiles_urlpatterns()
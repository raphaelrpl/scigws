from django.conf.urls import patterns, url

from views import OWSView

urlpatterns = patterns('',
    url(r'^$', OWSView.as_view()),
)
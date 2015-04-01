from django.conf.urls import patterns, url

from views import SimpleView

urlpatterns = patterns('',
    url(r'^$', SimpleView.as_view()),
)
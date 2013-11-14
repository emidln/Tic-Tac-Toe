""" The site urls.py including ttt and admin. """
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^tictactoe/', include('tictactoe.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )

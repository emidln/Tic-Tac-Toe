from django.conf.urls.defaults import *

urlpatterns = patterns('tictactoe.views',
    url(r'^$', 'index', name='tictactoe_index'),
    url(r'^(?P<board_id>\d+)/$', 'tictactoe', name='tictactoe'),
    url(r'^(?P<board_id>\d+)/update/$', 'board_update', name='board_update'),
)

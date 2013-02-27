from django.conf.urls import patterns, include, url
#from socialnetwork.weibo.views import *

urlpatterns = patterns('weibo.views',
        url(r'^home$', 'home'),
        url(r'^status_fans$', 'status_fans'),
        url(r'^management_fans$', 'management_fans'),
        url(r'^weibotools$', 'weibotools'),
        url(r'^scene_market$', 'scene_market'),
        url(r'^cut$', 'cut'),
        url(r'^own_fans_filter$', 'own_fans_filter'),
        url(r'^realtime_keyword_matching$', 'realtime_keyword_matching')
        )

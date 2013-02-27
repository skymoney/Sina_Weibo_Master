from django.conf.urls import patterns, include, url
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^weibo/', include('weibo.urls')),
    (r'^themes/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(os.path.abspath(__file__)) + '/themes/'}),
    # url(r'^$', 'socialnetwork.views.home', name='home'),
    # url(r'^socialnetwork/', include('socialnetwork.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

"""REDMUD URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

urlpatterns = [

    url(r'^main/$', 'sandbox.views.sandbox_main'),
    url(r'^posUpdate/$','sandbox.views.sandbox_pos_update'),
    url(r'^newInput/$', 'sandbox.views.sandbox_new_input'),
    url(r'^newOutput/$', 'sandbox.views.sandbox_new_output'),
    url(r'^deleteDatabaseItem/$', 'sandbox.views.sandbox_delete_item'),
    url(r'^newDatabaseItem/$', 'sandbox.views.sandbox_new_item'),
    url(r'^newConnection/$', 'sandbox.views.sandbox_new_connection'),
    url(r'^renameProcess/$', 'sandbox.views.sandbox_rename_process'),
    url(r'^editFlow/$', 'sandbox.views.sandbox_edit_quantity'),
    url(r'^removeLink/$', 'sandbox.views.sandbox_compute_link'),

    ]

from django.conf.urls import include, url
from .views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='audit_home'),
    url(r'^variables/$', AuditVariablesView.as_view(), name='audit_variables'),
    url(r'^variables/translate/source$', AuditVariablesSourceTranslationsView.as_view(), name='audit_variables_source_translations'),
]

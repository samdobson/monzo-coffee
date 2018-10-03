from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import hello.views
from password_required.views import login

urlpatterns = [
    path('', hello.views.index, name='index'),
    path('db', hello.views.db, name='db'),
    path('activate-webhook', hello.views.activate_webhook, name='activate-webhook'),
    path('deactivate-webhook', hello.views.deactivate_webhook, name='deactivate-webhook'),
    path('webhook/<str:account_id>', hello.views.webhook, name='webhook'),
    path('password_required/', login, name='password_required.views.login'),
    path('admin/', admin.site.urls),
]

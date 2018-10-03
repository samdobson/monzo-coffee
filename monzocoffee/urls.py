from django.conf import settings
from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

from hello import views
from password_required.views import login

urlpatterns = [
    path('', views.index, name='index'),
    
    path('connect-to-monzo', views.start_auth, name='start-auth'),
    path('auth-redirect', views.auth_redirect, name='auth-redirect'),

    path('tag-test/<str:account_id>', views.tag_test, name='tag-test'),

    path('tag/new', views.tag_new, name='tag-new'),
    path('tag/<str:pk>/edit/', views.tag_edit, name='tag-edit'),
    path('tag/<str:pk>/apply/<str:account_id>', views.tag_apply, name='tag-apply'),


    path('tag-by-time/<str:account_id>/<str:time_period>', views.tag_by_time, name='tag-by-time'),

    path('account/<str:account_id>', views.account, name='account'),
    
    path('webhook/<str:account_id>',views.webhook, name='webhook'),
    path('activate-webhook/<str:account_id>', views.activate_webhook, name='activate-webhook'),
    path('deactivate-webhook/<str:account_id>', views.deactivate_webhook, name='deactivate-webhook'),
    
    path('json-viewer', views.json_viewer, name='json-viewer'),
    path('transactions', views.transactions, name='transactions'),

    path('password_required/', login, name='password_required.views.login'),

]

if settings.ADMIN_ENABLED:
    urlpatterns += [path('admin/', admin.site.urls),]


from django.urls import path

from . import views

app_name = 'engagement'

urlpatterns = [
    path('contact/', views.contact,   name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
    # /book/ is removed — the booking concept has been replaced by the
    # workshop intake form on the unified /contact/ page.
]

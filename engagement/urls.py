from django.urls import path

from . import views

app_name = 'engagement'

urlpatterns = [
    path('book/', views.book, name='book'),
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
]

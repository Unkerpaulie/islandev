from django.urls import path

from . import views

app_name = 'engagement'

urlpatterns = [
    path('', views.BookView.as_view(), name='book'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]

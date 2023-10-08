from django.urls import path
from . import views
urlpatterns = [
    path('', views.messages_page, name='home'),
    path('get_latest_messages/', views.get_latest_messages, name='get_latest_messages'),

]
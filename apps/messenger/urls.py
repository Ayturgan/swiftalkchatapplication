from django.urls import path
from . import views
urlpatterns = [
    path('', views.combined_view, name='home'),
    path('get_latest_messages/', views.get_latest_messages, name='get_latest_messages'),
    path('upload_chat_file/', views.upload_chat_file, name='upload_chat_file'),

]
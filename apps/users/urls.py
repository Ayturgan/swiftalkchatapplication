from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='swiftalk/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-password/', views.reset_password, name='reset-password'),

    path('get_user_data/<int:user_id>/', views.get_user_data, name='get_user_data'),
    #
    # path('', views.update_profile, name='settings'),
]
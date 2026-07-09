from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name= 'index'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_email, name='verify'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
   
]
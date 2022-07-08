from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('dashboard/<int:user_id>/', views.dashboard, name="dashboard"),
    path('dashboard/<int:user_id>/transfer/', views.transfer, name="dashboard"),
    path('dashboard/<int:user_id>/deposit/', views.deposit, name="dashboard"),
    path('dashboard/<int:user_id>/withdraw/', views.withdraw, name="dashboard"),
    path('logout/', views.logout, name="logout")
]
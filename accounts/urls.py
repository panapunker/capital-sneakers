from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_cliente, name='login'),
    path('logout/', views.logout_cliente, name='logout'),
]
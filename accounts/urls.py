from django.urls import path
from .views import LoginAdminView, LoginClienteView, LogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginAdminView.as_view(), name='login_admin'),
    path('login/cliente/', LoginClienteView.as_view(), name='login_cliente'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
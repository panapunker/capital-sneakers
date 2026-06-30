from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View

from .forms import LoginAdminForm, LoginClienteForm
from .models import User


class LoginAdminView(View):
    template_name = 'accounts/login_admin.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.es_admin:
            return redirect('dashboard:admin_dashboard')
        form = LoginAdminForm(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginAdminForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.es_admin:
                login(request, user)
                return redirect('dashboard:admin_dashboard')
            else:
                messages.error(request, 'No tienes permisos de administrador.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
        return render(request, self.template_name, {'form': form})


class LoginClienteView(View):
    template_name = 'accounts/login_cliente.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.es_cliente:
            return redirect('dashboard:cliente_dashboard')
        form = LoginClienteForm(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginClienteForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.es_cliente:
                login(request, user)
                return redirect('dashboard:cliente_dashboard')
            else:
                messages.error(request, 'Accede desde el panel de administrador.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login_admin')
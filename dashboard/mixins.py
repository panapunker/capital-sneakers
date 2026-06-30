from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class AdminRequiredMixin(LoginRequiredMixin):
    """Solo permite acceso a usuarios con rol admin."""
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin:
            return redirect('dashboard:cliente_dashboard')
        return super().dispatch(request, *args, **kwargs)


class ClienteRequiredMixin(LoginRequiredMixin):
    """Solo permite acceso a usuarios con rol cliente."""
    login_url = '/login/cliente/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_cliente:
            return redirect('dashboard:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
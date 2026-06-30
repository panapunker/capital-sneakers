from django.db import models
from django.conf import settings


class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cliente'
    )
    nombre_completo = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    ciudad = models.CharField(max_length=100)
    direccion = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre_completo} ({self.documento})"

    def total_pedidos(self):
        if hasattr(self, 'pedidos'):
            return self.pedidos.count()
        return 0

    def balance(self):
        """
        Suma el total de todos los pedidos NO facturados.
        El balance desaparece cuando el admin factura el pedido.
        """
        if hasattr(self, 'pedidos'):
            from django.db.models import Sum
            total = self.pedidos.filter(
                facturado=False
            ).aggregate(total=Sum('total'))['total']
            return total or 0
        return 0

    def ultimo_pedido(self):
        if hasattr(self, 'pedidos'):
            return self.pedidos.order_by('-fecha').first()
        return None
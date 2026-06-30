from django.db import models
from django.conf import settings
from catalogo.models import Producto


TALLAS_CHOICES = [
    ('28', '28'), ('30', '30'), ('32', '32'), ('33', '33'),
    ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'),
    ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'),
    ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
]

TIPO_MOVIMIENTO_CHOICES = [
    ('entrada', 'Entrada'),
    ('salida', 'Salida'),
    ('ajuste', 'Ajuste'),
]


class Inventario(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='inventarios'
    )
    talla = models.CharField(max_length=5, choices=TALLAS_CHOICES)
    cantidad = models.PositiveIntegerField(default=0)
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('producto', 'talla')
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventario'
        ordering = ['producto', 'talla']

    def __str__(self):
        return f"{self.producto.nombre} - Talla {self.talla} ({self.cantidad} uds)"


class MovimientoInventario(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    talla = models.CharField(max_length=5, choices=TALLAS_CHOICES)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_inventario'
    )
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo.upper()} | {self.producto.nombre} T{self.talla} | {self.cantidad} uds"
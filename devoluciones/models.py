from django.db import models
from django.conf import settings
from pedidos.models import Pedido, DetallePedido
from clientes.models import Cliente
from catalogo.models import Producto
from inventario.models import TALLAS_CHOICES


TIPO_DEVOLUCION_CHOICES = [
    ('total', 'Devolucion Total'),
    ('parcial', 'Devolucion Parcial'),
    ('cambio_talla', 'Cambio por Talla'),
    ('cambio_producto', 'Cambio por Producto'),
    ('defectuoso', 'Producto Defectuoso'),
    ('garantia', 'Garantia'),
]

ESTADO_DEVOLUCION_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('aprobada', 'Aprobada'),
    ('rechazada', 'Rechazada'),
    ('finalizada', 'Finalizada'),
]

ESTADO_PRODUCTO_CHOICES = [
    ('nuevo', 'Nuevo'),
    ('usado', 'Usado'),
    ('defectuoso', 'Defectuoso'),
    ('danado', 'Danado'),
]


class Devolucion(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name='devoluciones'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='devoluciones'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devoluciones_registradas'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_DEVOLUCION_CHOICES)
    motivo = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=12,
        choices=ESTADO_DEVOLUCION_CHOICES,
        default='pendiente'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Devolucion'
        verbose_name_plural = 'Devoluciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"Devolucion #{self.id} - Pedido #{self.pedido_id}"

    def get_total_unidades(self):
        return sum(d.cantidad for d in self.detalles.all())

    def get_valor_devuelto(self):
        total = 0
        for d in self.detalles.select_related('detalle_pedido'):
            total += d.detalle_pedido.precio_unitario * d.cantidad
        return total

    def puede_aprobarse(self):
        return self.estado == 'pendiente'

    def puede_rechazarse(self):
        return self.estado == 'pendiente'

    def puede_finalizarse(self):
        return self.estado == 'aprobada'


class DetalleDevolucion(models.Model):
    devolucion = models.ForeignKey(
        Devolucion,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    detalle_pedido = models.ForeignKey(
        DetallePedido,
        on_delete=models.PROTECT,
        related_name='detalles_devolucion'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='devoluciones_detalle'
    )
    talla = models.CharField(max_length=5, choices=TALLAS_CHOICES)
    cantidad = models.PositiveIntegerField()
    motivo = models.TextField(blank=True, null=True)
    estado_producto = models.CharField(
        max_length=12,
        choices=ESTADO_PRODUCTO_CHOICES,
        default='nuevo'
    )
    vuelve_a_inventario = models.BooleanField(default=True)

    talla_nueva = models.CharField(
        max_length=5, choices=TALLAS_CHOICES, blank=True, null=True
    )

    producto_nuevo = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cambios_recibidos'
    )

    procesado = models.BooleanField(
        default=False,
        help_text='Indica si ya se aplicaron los efectos sobre inventario.'
    )

    class Meta:
        verbose_name = 'Detalle de Devolucion'
        verbose_name_plural = 'Detalles de Devolucion'

    def __str__(self):
        return f"{self.producto.nombre} T{self.talla} x{self.cantidad}"

    def es_cambio_talla(self):
        return bool(self.talla_nueva)

    def es_cambio_producto(self):
        return bool(self.producto_nuevo_id)


class MovimientoDevolucion(models.Model):
    devolucion = models.ForeignKey(
        Devolucion,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    detalle = models.ForeignKey(
        DetalleDevolucion,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos'
    )
    accion = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_devolucion'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Devolucion'
        verbose_name_plural = 'Movimientos de Devolucion'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} - Devolucion #{self.devolucion_id}"
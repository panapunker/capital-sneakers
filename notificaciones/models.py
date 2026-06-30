from django.db import models
from django.conf import settings


class Notificacion(models.Model):

    TIPO_NUEVO_PEDIDO      = 'nuevo_pedido'
    TIPO_STOCK_BAJO        = 'stock_bajo'
    TIPO_PRODUCTO_AGOTADO  = 'producto_agotado'
    TIPO_COMPRA_RECIBIDA   = 'compra_recibida'
    TIPO_COMPRA_CANCELADA  = 'compra_cancelada'
    TIPO_NUEVO_CLIENTE     = 'nuevo_cliente'
    TIPO_SISTEMA           = 'sistema'

    TIPO_CHOICES = [
        (TIPO_NUEVO_PEDIDO,     'Nuevo Pedido'),
        (TIPO_STOCK_BAJO,       'Stock Bajo'),
        (TIPO_PRODUCTO_AGOTADO, 'Producto Agotado'),
        (TIPO_COMPRA_RECIBIDA,  'Compra Recibida'),
        (TIPO_COMPRA_CANCELADA, 'Compra Cancelada'),
        (TIPO_NUEVO_CLIENTE,    'Nuevo Cliente'),
        (TIPO_SISTEMA,          'Sistema'),
    ]

    ICONO_MAP = {
        TIPO_NUEVO_PEDIDO:     'bi-bag-check-fill',
        TIPO_STOCK_BAJO:       'bi-exclamation-triangle-fill',
        TIPO_PRODUCTO_AGOTADO: 'bi-x-circle-fill',
        TIPO_COMPRA_RECIBIDA:  'bi-truck',
        TIPO_COMPRA_CANCELADA: 'bi-x-octagon-fill',
        TIPO_NUEVO_CLIENTE:    'bi-person-plus-fill',
        TIPO_SISTEMA:          'bi-gear-fill',
    }

    COLOR_MAP = {
        TIPO_NUEVO_PEDIDO:     'success',
        TIPO_STOCK_BAJO:       'warning',
        TIPO_PRODUCTO_AGOTADO: 'danger',
        TIPO_COMPRA_RECIBIDA:  'info',
        TIPO_COMPRA_CANCELADA: 'danger',
        TIPO_NUEVO_CLIENTE:    'primary',
        TIPO_SISTEMA:          'secondary',
    }

    tipo        = models.CharField(max_length=30, choices=TIPO_CHOICES)
    titulo      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    usuario     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notificaciones_recibidas',
    )
    # Relaciones opcionales para futura expansión
    pedido_id   = models.PositiveIntegerField(null=True, blank=True)
    compra_id   = models.PositiveIntegerField(null=True, blank=True)
    leida       = models.BooleanField(default=False)
    fecha       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering            = ['-fecha']

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.titulo}'

    @property
    def icono(self):
        return self.ICONO_MAP.get(self.tipo, 'bi-bell-fill')

    @property
    def color(self):
        return self.COLOR_MAP.get(self.tipo, 'secondary')

    @classmethod
    def crear(cls, tipo, titulo, descripcion='', usuario=None, pedido_id=None, compra_id=None):
        return cls.objects.create(
            tipo=tipo,
            titulo=titulo,
            descripcion=descripcion,
            usuario=usuario,
            pedido_id=pedido_id,
            compra_id=compra_id,
        )
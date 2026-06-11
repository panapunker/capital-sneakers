from django.db import models


class Producto(models.Model):

    nombre = models.CharField(max_length=200)

    marca = models.CharField(
        max_length=100,
        blank=True
    )

    referencia = models.CharField(
        max_length=100,
        unique=True
    )

    precio_compra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def ganancia(self):
        return self.precio - self.precio_compra

    @property
    def porcentaje_ganancia(self):

        if self.precio_compra <= 0:
            return 0

        return round(
            ((self.precio - self.precio_compra)
            / self.precio_compra) * 100,
            2
        )

    def __str__(self):
        return self.nombre
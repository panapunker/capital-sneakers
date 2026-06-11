from django.db import models

from catalogo.models import Producto


class Talla(models.Model):

    nombre = models.CharField(
        max_length=10,
        unique=True
    )

    def __str__(self):
        return self.nombre


class Inventario(models.Model):

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    talla = models.ForeignKey(
        Talla,
        on_delete=models.CASCADE
    )

    cantidad = models.IntegerField(
        default=0
    )

    class Meta:
        unique_together = (
            'producto',
            'talla'
        )

    def __str__(self):
        return (
            f"{self.producto} - "
            f"{self.talla} - "
            f"{self.cantidad}"
        )

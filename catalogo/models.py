from django.db import models


class Producto(models.Model):

    nombre = models.CharField(
        max_length=200
    )

    marca = models.CharField(
        max_length=100,
        blank=True
    )

    referencia = models.CharField(
        max_length=100,
        unique=True
    )

    codigo_barras = models.CharField(
        max_length=20,
        blank=True,
        null=True
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

    def save(self, *args, **kwargs):

        if not self.codigo_barras:

            ultimo = Producto.objects.order_by(
                '-id'
            ).first()

            siguiente = 100000

            if ultimo and ultimo.codigo_barras:

                try:

                    siguiente = (
                        int(
                            ultimo.codigo_barras.replace(
                                'CS',
                                ''
                            )
                        ) + 1
                    )

                except:

                    pass

            self.codigo_barras = f'CS{siguiente}'

        super().save(*args, **kwargs)

    @property
    def ganancia(self):

        return (
            self.precio -
            self.precio_compra
        )

    @property
    def porcentaje_ganancia(self):

        if self.precio_compra <= 0:
            return 0

        return round(
            (
                (
                    self.precio -
                    self.precio_compra
                )
                /
                self.precio_compra
            ) * 100,
            2
        )

    def __str__(self):

        return self.nombre
    
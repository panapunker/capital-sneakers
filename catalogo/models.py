from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    GENERO_CHOICES = [
        ('dama', 'Dama'),
        ('caballero', 'Caballero'),
        ('nino', 'Niño'),
        ('ambos', 'Ambos'),
    ]

    nombre = models.CharField(max_length=200)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    referencia = models.CharField(max_length=100, unique=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES)
    imagen_principal = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.nombre} - {self.referencia}'


class StockTalla(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stock_tallas')
    talla = models.CharField(max_length=10)
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Stock por Talla'
        verbose_name_plural = 'Stock por Tallas'
        unique_together = ('producto', 'talla')

    def __str__(self):
        return f'{self.producto} - Talla {self.talla}: {self.cantidad}'
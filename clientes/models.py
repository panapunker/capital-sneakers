from django.db import models


class Cliente(models.Model):

    nombre_negocio = models.CharField(max_length=150)

    propietario = models.CharField(max_length=150)

    telefono = models.CharField(max_length=20)

    whatsapp = models.CharField(max_length=20)

    correo = models.EmailField()

    ciudad = models.CharField(max_length=100)

    direccion = models.TextField()

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_negocio

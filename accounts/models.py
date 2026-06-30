from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROL_ADMIN = 'admin'
    ROL_CLIENTE = 'cliente'

    ROL_CHOICES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_CLIENTE, 'Cliente'),
    ]

    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        default=ROL_CLIENTE,
    )

    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'

    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    @property
    def es_cliente(self):
        return self.rol == self.ROL_CLIENTE
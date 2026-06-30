from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Crea un superusuario admin si no existe'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'CapitalSneakers2026!'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El usuario "{username}" ya existe.'))
            return

        User.objects.create_superuser(
            username=username,
            email='admin@capitalsneakers.com',
            password=password,
            rol='admin',
        )
        self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado correctamente.'))

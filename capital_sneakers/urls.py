from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación
    path('', include('accounts.urls')),

    # Módulos
    path('dashboard/',  include('dashboard.urls',   namespace='dashboard')),
    path('catalogo/',   include('catalogo.urls',    namespace='catalogo')),
    path('inventario/', include('inventario.urls',  namespace='inventario')),
    path('clientes/',   include('clientes.urls',    namespace='clientes')),
    path('pedidos/',    include('pedidos.urls',     namespace='pedidos')),
    path('carrito/',    include('carrito.urls',     namespace='carrito')),
    path('reportes/',        include('reportes.urls',        namespace='reportes')),
    path('notificaciones/',  include('notificaciones.urls',  namespace='notificaciones')),
    path('usuarios/',        include('usuarios.urls',        namespace='usuarios')),
    path('compras/', include('compras.urls', namespace='compras')),
    path('devoluciones/', include('devoluciones.urls', namespace='devoluciones')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
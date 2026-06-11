from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Producto
from inventario.models import Inventario


@login_required
def catalogo(request):

    productos = Producto.objects.filter(
        activo=True
    )

    buscar = request.GET.get('buscar')

    if buscar:

        productos = productos.filter(

            Q(nombre__icontains=buscar) |
            Q(marca__icontains=buscar) |
            Q(referencia__icontains=buscar)

        )

    return render(
        request,
        'catalogo/catalogo.html',
        {
            'productos': productos
        }
    )


@login_required
def detalle_producto(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id
    )

    inventario = Inventario.objects.filter(
        producto=producto
    )

    return render(
        request,
        'catalogo/detalle_producto.html',
        {
            'producto': producto,
            'inventario': inventario
        }
    )
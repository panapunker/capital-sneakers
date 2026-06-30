from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Categoria, Marca, Producto, StockTalla
from .forms import CategoriaForm, MarcaForm, ProductoForm
from .forms import TALLAS_POR_GENERO


# ==================== CATEGORÍAS ====================

@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'catalogo/categorias/lista.html', {'categorias': categorias})


@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('catalogo:lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'catalogo/categorias/form.html', {'form': form, 'titulo': 'Nueva Categoría'})


@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('catalogo:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'catalogo/categorias/form.html', {'form': form, 'titulo': 'Editar Categoría'})


@login_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
        return redirect('catalogo:lista_categorias')
    return render(request, 'catalogo/categorias/confirmar_eliminar.html', {'objeto': categoria, 'tipo': 'Categoría'})


# ==================== MARCAS ====================

@login_required
def lista_marcas(request):
    marcas = Marca.objects.all()
    return render(request, 'catalogo/marcas/lista.html', {'marcas': marcas})


@login_required
def crear_marca(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca creada exitosamente.')
            return redirect('catalogo:lista_marcas')
    else:
        form = MarcaForm()
    return render(request, 'catalogo/marcas/form.html', {'form': form, 'titulo': 'Nueva Marca'})


@login_required
def editar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada exitosamente.')
            return redirect('catalogo:lista_marcas')
    else:
        form = MarcaForm(instance=marca)
    return render(request, 'catalogo/marcas/form.html', {'form': form, 'titulo': 'Editar Marca'})


@login_required
def eliminar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        marca.delete()
        messages.success(request, 'Marca eliminada exitosamente.')
        return redirect('catalogo:lista_marcas')
    return render(request, 'catalogo/marcas/confirmar_eliminar.html', {'objeto': marca, 'tipo': 'Marca'})


# ==================== PRODUCTOS ====================

@login_required
def lista_productos(request):
    query = request.GET.get('q', '')
    genero = request.GET.get('genero', '')
    categoria = request.GET.get('categoria', '')
    marca = request.GET.get('marca', '')

    productos = Producto.objects.select_related('marca', 'categoria').all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(referencia__icontains=query)
        )
    if genero:
        productos = productos.filter(genero=genero)
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    if marca:
        productos = productos.filter(marca__id=marca)

    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)

    return render(request, 'catalogo/productos/lista.html', {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'query': query,
        'genero_sel': genero,
        'categoria_sel': categoria,
        'marca_sel': marca,
    })


@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            genero = producto.genero
            tallas = TALLAS_POR_GENERO.get(genero, [])

            for talla in tallas:
                cantidad = request.POST.get(f'talla_{talla}', 0)
                try:
                    cantidad = int(cantidad)
                except ValueError:
                    cantidad = 0
                if cantidad > 0:
                    # Guarda en StockTalla (catálogo)
                    StockTalla.objects.create(
                        producto=producto,
                        talla=talla,
                        cantidad=cantidad
                    )
                    # Sincroniza con Inventario (carrito/pedidos lo leen aquí)
                    from inventario.models import Inventario, MovimientoInventario
                    inv, creado = Inventario.objects.get_or_create(
                        producto=producto,
                        talla=talla,
                        defaults={'cantidad': cantidad}
                    )
                    if not creado:
                        inv.cantidad += cantidad
                        inv.save()
                    # Registra movimiento de entrada
                    MovimientoInventario.objects.create(
                        producto=producto,
                        talla=talla,
                        tipo='entrada',
                        cantidad=cantidad,
                        usuario=request.user,
                        observacion=f'Stock inicial al crear producto',
                    )

            messages.success(request, 'Producto creado exitosamente.')
            return redirect('catalogo:lista_productos')
    else:
        form = ProductoForm()

    return render(request, 'catalogo/productos/form.html', {
        'form': form,
        'titulo': 'Nuevo Producto',
        'tallas_json': TALLAS_POR_GENERO,
    })


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    stock_existente = {st.talla: st.cantidad for st in producto.stock_tallas.all()}

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            genero = producto.genero
            tallas = TALLAS_POR_GENERO.get(genero, [])

            # Elimina StockTalla anterior
            producto.stock_tallas.all().delete()

            # Elimina Inventario anterior y registra ajuste
            from inventario.models import Inventario, MovimientoInventario
            inventarios_anteriores = Inventario.objects.filter(producto=producto)
            for inv in inventarios_anteriores:
                if inv.cantidad > 0:
                    MovimientoInventario.objects.create(
                        producto=producto,
                        talla=inv.talla,
                        tipo='ajuste',
                        cantidad=inv.cantidad,
                        usuario=request.user,
                        observacion='Ajuste por edición de producto — stock reiniciado',
                    )
            inventarios_anteriores.delete()

            # Crea nuevo StockTalla e Inventario sincronizados
            for talla in tallas:
                cantidad = request.POST.get(f'talla_{talla}', 0)
                try:
                    cantidad = int(cantidad)
                except ValueError:
                    cantidad = 0
                if cantidad > 0:
                    # Guarda en StockTalla
                    StockTalla.objects.create(
                        producto=producto,
                        talla=talla,
                        cantidad=cantidad
                    )
                    # Sincroniza con Inventario
                    Inventario.objects.create(
                        producto=producto,
                        talla=talla,
                        cantidad=cantidad
                    )
                    # Registra movimiento de entrada
                    MovimientoInventario.objects.create(
                        producto=producto,
                        talla=talla,
                        tipo='entrada',
                        cantidad=cantidad,
                        usuario=request.user,
                        observacion='Stock actualizado por edición de producto',
                    )

            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('catalogo:lista_productos')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'catalogo/productos/form.html', {
        'form': form,
        'titulo': 'Editar Producto',
        'tallas_json': TALLAS_POR_GENERO,
        'stock_existente': stock_existente,
        'producto': producto,
    })


@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    stock_tallas = producto.stock_tallas.all().order_by('talla')
    stock_total = sum(st.cantidad for st in stock_tallas)
    return render(request, 'catalogo/productos/detalle.html', {
        'producto': producto,
        'stock_tallas': stock_tallas,
        'stock_total': stock_total,
    })


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('catalogo:lista_productos')
    return render(request, 'catalogo/productos/confirmar_eliminar.html', {'objeto': producto, 'tipo': 'Producto'})
# ── Vistas cliente (solo lectura) ─────────────────────────────────────────────

@login_required
def catalogo_cliente(request):
    query     = request.GET.get('q', '')
    genero    = request.GET.get('genero', '')
    categoria = request.GET.get('categoria', '')
    marca_id  = request.GET.get('marca', '')

    productos = Producto.objects.filter(activo=True).select_related('marca', 'categoria')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(referencia__icontains=query)
        )
    if genero:
        productos = productos.filter(genero=genero)
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    if marca_id:
        productos = productos.filter(marca__id=marca_id)

    categorias = Categoria.objects.filter(activo=True)
    marcas     = Marca.objects.filter(activo=True)

    return render(request, 'catalogo/cliente/catalogo.html', {
        'productos':     productos,
        'categorias':    categorias,
        'marcas':        marcas,
        'query':         query,
        'genero_sel':    genero,
        'categoria_sel': categoria,
        'marca_sel':     marca_id,
    })


@login_required
def producto_cliente_detalle(request, pk):
    from inventario.models import Inventario
    producto     = get_object_or_404(Producto, pk=pk, activo=True)
    stock_tallas = Inventario.objects.filter(
        producto=producto, cantidad__gt=0
    ).order_by('talla')
    return render(request, 'catalogo/cliente/detalle.html', {
        'producto':     producto,
        'stock_tallas': stock_tallas,
    })
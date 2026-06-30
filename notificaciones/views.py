from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notificacion

es_admin = lambda u: u.is_authenticated and u.es_admin


@login_required
@user_passes_test(es_admin)
def historial(request):
    tipo   = request.GET.get('tipo', '')
    leida  = request.GET.get('leida', '')

    qs = Notificacion.objects.select_related('usuario').all()

    if tipo:
        qs = qs.filter(tipo=tipo)
    if leida == '1':
        qs = qs.filter(leida=True)
    elif leida == '0':
        qs = qs.filter(leida=False)

    no_leidas = Notificacion.objects.filter(leida=False).count()

    return render(request, 'notificaciones/historial.html', {
        'notificaciones': qs[:100],
        'no_leidas':      no_leidas,
        'filtro_tipo':    tipo,
        'filtro_leida':   leida,
        'tipos':          Notificacion.TIPO_CHOICES,
    })


@login_required
@user_passes_test(es_admin)
def marcar_leida(request, pk):
    notif = get_object_or_404(Notificacion, pk=pk)
    notif.leida = True
    notif.save(update_fields=['leida'])
    return JsonResponse({'ok': True})


@login_required
@user_passes_test(es_admin)
def marcar_todas_leidas(request):
    Notificacion.objects.filter(leida=False).update(leida=True)
    return JsonResponse({'ok': True})


@login_required
@user_passes_test(es_admin)
def obtener_recientes(request):
    """
    Endpoint JSON para polling.
    Arquitectura preparada para WebSockets en el futuro.
    """
    desde_id = request.GET.get('desde_id', 0)
    try:
        desde_id = int(desde_id)
    except ValueError:
        desde_id = 0

    qs = (
        Notificacion.objects
        .filter(leida=False)
        .select_related('usuario')
        .order_by('-fecha')[:10]
    )

    data = []
    for n in qs:
        data.append({
            'id':          n.pk,
            'tipo':        n.tipo,
            'titulo':      n.titulo,
            'descripcion': n.descripcion,
            'icono':       n.icono,
            'color':       n.color,
            'fecha':       n.fecha.strftime('%d/%m/%Y'),
            'hora':        n.fecha.strftime('%H:%M'),
            'pedido_id':   n.pedido_id,
            'leida':       n.leida,
            'usuario':     n.usuario.get_full_name() or n.usuario.username if n.usuario else '',
        })

    no_leidas = Notificacion.objects.filter(leida=False).count()

    return JsonResponse({'notificaciones': data, 'no_leidas': no_leidas})
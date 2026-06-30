const NOTIF_URL    = document.getElementById('notif-config')?.dataset.url;
const MARCAR_TODAS = document.getElementById('notif-config')?.dataset.marcarTodas;
let ultimoId       = 0;
let primeraVez     = true;

function renderNotifDropdown(notifs) {
    const lista    = document.getElementById('listaNotifDropdown');
    const sinMsg   = document.getElementById('sinNotifMsg');
    const contador = document.getElementById('contadorCampana');
    const campana  = document.getElementById('campanaIcono');

    if (!lista) return;

    if (!notifs.length) {
        sinMsg.style.display  = 'block';
        contador.style.display = 'none';
        campana.classList.remove('text-danger');
        return;
    }

    sinMsg.style.display   = 'none';
    contador.style.display = 'inline-block';
    contador.textContent   = notifs.length > 9 ? '9+' : notifs.length;
    campana.classList.add('text-danger');

    lista.innerHTML = '';
    notifs.forEach(n => {
        const div = document.createElement('div');
        div.className = 'p-3 border-bottom d-flex align-items-start gap-2';
        div.innerHTML = `
            <span class="bg-${n.color} bg-opacity-15 rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                  style="width:36px;height:36px;">
                <i class="bi ${n.icono} text-${n.color} small"></i>
            </span>
            <div class="flex-grow-1">
                <div class="fw-semibold small">${n.titulo}</div>
                <div class="text-muted" style="font-size:0.75rem;">${n.descripcion}</div>
                <div class="text-muted" style="font-size:0.7rem;">${n.fecha} ${n.hora}</div>
                <div class="d-flex gap-1 mt-1">
                    ${n.pedido_id ? `<a href="/pedidos/${n.pedido_id}/" class="btn btn-outline-primary btn-sm py-0" style="font-size:0.7rem;">Ver pedido</a>` : ''}
                    <button class="btn btn-outline-secondary btn-sm py-0" style="font-size:0.7rem;"
                            onclick="marcarLeida(${n.id})">
                        <i class="bi bi-check"></i> Leída
                    </button>
                </div>
            </div>
        `;
        lista.appendChild(div);
    });
}

function mostrarToast(n) {
    const toast = document.createElement('div');
    toast.className = 'toast show align-items-center border-0 mb-2';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-start gap-2">
                <span class="bg-${n.color} bg-opacity-15 rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                      style="width:36px;height:36px;">
                    <i class="bi ${n.icono} text-${n.color}"></i>
                </span>
                <div>
                    <div class="fw-semibold small">${n.titulo}</div>
                    <div class="text-muted" style="font-size:0.78rem;">${n.descripcion}</div>
                    <div class="text-muted" style="font-size:0.7rem;">${n.fecha} ${n.hora}</div>
                    ${n.pedido_id ? `<a href="/pedidos/${n.pedido_id}/" class="btn btn-primary btn-sm mt-1 py-0" style="font-size:0.75rem;">Ver pedido</a>` : ''}
                </div>
            </div>
            <button type="button" class="btn-close me-2 m-auto" onclick="this.closest('.toast').remove()"></button>
        </div>
    `;
    document.getElementById('toastContainer')?.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
}

function marcarLeida(pk) {
    fetch(`/notificaciones/marcar/${pk}/`)
        .then(r => r.json())
        .then(() => pollNotificaciones());
}

function marcarTodasLeidas() {
    fetch(MARCAR_TODAS)
        .then(r => r.json())
        .then(() => pollNotificaciones());
}

function pollNotificaciones() {
    if (!NOTIF_URL) return;
    fetch(NOTIF_URL)
        .then(r => r.json())
        .then(data => {
            const notifs = data.notificaciones;
            renderNotifDropdown(notifs);

            if (!primeraVez && notifs.length > 0) {
                const nuevas = notifs.filter(n => n.id > ultimoId);
                nuevas.forEach(n => {
                    mostrarToast(n);
                    document.getElementById('sonidoNotif')?.play().catch(() => {});
                });
            }

            if (notifs.length > 0) {
                ultimoId = Math.max(...notifs.map(n => n.id));
            }
            primeraVez = false;
        })
        .catch(() => {});
}

// Polling cada 10 segundos
pollNotificaciones();
setInterval(pollNotificaciones, 10000);
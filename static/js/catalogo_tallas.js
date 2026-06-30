const TALLAS_POR_GENERO = {
    dama: ['36', '37', '38', '39'],
    caballero: ['40', '41', '42', '43', '44', '45'],
    nino: ['28', '30', '32', '33', '34', '35'],
    ambos: ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45'],
};

function cargarTallas(genero) {
    const contenedor = document.getElementById('contenedor-tallas');
    const stockTotalDiv = document.getElementById('stock-total');
    contenedor.innerHTML = '';

    if (!genero || !TALLAS_POR_GENERO[genero]) {
        stockTotalDiv.innerHTML = '';
        return;
    }

    const tallas = TALLAS_POR_GENERO[genero];

    tallas.forEach(talla => {
        const valorExistente = stockExistente[talla] || 0;
        const col = document.createElement('div');
        col.className = 'col-6 col-md-3 col-lg-2 mb-3';
        col.innerHTML = `
            <div class="card border-0 shadow-sm text-center p-2">
                <div class="fw-bold fs-5 mb-2">${talla}</div>
                <label class="form-label small text-muted">Cantidad</label>
                <input
                    type="number"
                    name="talla_${talla}"
                    class="form-control form-control-sm text-center talla-input"
                    min="0"
                    value="${valorExistente}"
                    oninput="calcularStockTotal()"
                >
            </div>
        `;
        contenedor.appendChild(col);
    });

    calcularStockTotal();
}

function calcularStockTotal() {
    const inputs = document.querySelectorAll('.talla-input');
    let total = 0;
    inputs.forEach(input => {
        const val = parseInt(input.value) || 0;
        total += val;
    });
    document.getElementById('stock-total').innerHTML = `
        <div class="alert alert-info mt-3 fw-bold fs-5">
            Stock Total: ${total} unidades
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', function () {
    const selectGenero = document.getElementById('id_genero');
    if (selectGenero && selectGenero.value) {
        cargarTallas(selectGenero.value);
    }
});
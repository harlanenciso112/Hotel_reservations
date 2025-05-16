// Initialize flatpickr with Spanish locale
flatpickr.localize(flatpickr.l10ns.es);

document.addEventListener('DOMContentLoaded', function() {
    // Obtener los elementos del DOM
    const fechaEntradaEl = document.getElementById('fecha-entrada');
    const fechaSalidaEl = document.getElementById('fecha-salida');
    const rangoFechasEl = document.getElementById('rango-fechas');
    const fechaDisplayEl = document.getElementById('fecha-display');
    const rangoMostradoEl = document.getElementById('rango-mostrado');
    
    // Verificar si los elementos existen en el DOM
    if (!rangoFechasEl) {
        console.error('Elemento #rango-fechas no encontrado');
        return;
    }
    
    // Obtener valores iniciales de fechas
    const entradaValue = fechaEntradaEl ? fechaEntradaEl.value : null;
    const salidaValue = fechaSalidaEl ? fechaSalidaEl.value : null;

    let defaultDates = [];
    if (entradaValue && salidaValue) {
        defaultDates = [entradaValue, salidaValue];
    }

    // Formatear fechas existentes al cargar la página
    if (entradaValue && salidaValue && rangoMostradoEl) {
        try {
            // Forzar la interpretación en la zona horaria local añadiendo 'T12:00:00'
            const entradaDate = new Date(`${entradaValue}T12:00:00`);
            const salidaDate = new Date(`${salidaValue}T12:00:00`);
            
            // Verificar que las fechas son válidas
            if (!isNaN(entradaDate.getTime()) && !isNaN(salidaDate.getTime())) {
                const entradaFormateada = entradaDate.toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                });
                const salidaFormateada = salidaDate.toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                });
                
                rangoMostradoEl.textContent = `${entradaFormateada} - ${salidaFormateada}`;
            }
        } catch (e) {
            console.error("Error al formatear fechas:", e);
        }
    }

    // Inicializar flatpickr
    const flatpickrInstance = flatpickr(rangoFechasEl, {
        mode: "range",
        minDate: "today",
        dateFormat: "Y-m-d",
        locale: "es",
        defaultDate: defaultDates,
        onChange: function(selectedDates, dateStr) {
            if (selectedDates.length === 2) {
                // Actualizar los campos ocultos con las nuevas fechas
                if (fechaEntradaEl) fechaEntradaEl.value = flatpickr.formatDate(selectedDates[0], "Y-m-d");
                if (fechaSalidaEl) fechaSalidaEl.value = flatpickr.formatDate(selectedDates[1], "Y-m-d");
                
                // Actualizar el texto mostrado
                if (rangoMostradoEl) {
                    // Usando el mismo truco para forzar la zona horaria correcta
                    const entradaDate = new Date(flatpickr.formatDate(selectedDates[0], "Y-m-d") + "T12:00:00");
                    const salidaDate = new Date(flatpickr.formatDate(selectedDates[1], "Y-m-d") + "T12:00:00");
                    
                    const entradaFormateada = entradaDate.toLocaleDateString('es-ES', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                    });
                    const salidaFormateada = salidaDate.toLocaleDateString('es-ES', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                    });
                    
                    rangoMostradoEl.textContent = `${entradaFormateada} - ${salidaFormateada}`;
                }
                
                // Calcular número de noches
                const noches = Math.ceil((selectedDates[1] - selectedDates[0]) / (1000 * 60 * 60 * 24));
                const nochesEl = document.getElementById("noches");
                if (nochesEl) {
                    nochesEl.textContent = `📅 ${noches} noche${noches > 1 ? 's' : ''}`;
                }
                
                // Enviar el formulario automáticamente cuando se seleccionan ambas fechas
                const form = document.getElementById('filtros-form');
                if (form) form.submit();
            }
        }
    });
    
    // Hacer que el selector de fechas se abra al hacer clic en el display
    if (fechaDisplayEl) {
        fechaDisplayEl.addEventListener("click", () => {
            flatpickrInstance.open();
        });
    }
    
    // También hacer que se abra cuando se hace clic en el input
    rangoFechasEl.addEventListener("click", () => {
        flatpickrInstance.open();
    });
});

// Función para limpiar filtros
function limpiarFiltros() {
    // Limpiar todos los checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Obtener los valores actuales de entrada y salida
    const fechaEntradaEl = document.getElementById('fecha-entrada');
    const fechaSalidaEl = document.getElementById('fecha-salida');
    
    const entradaValue = fechaEntradaEl ? fechaEntradaEl.value : null;
    const salidaValue = fechaSalidaEl ? fechaSalidaEl.value : null;
    
    // Construir la URL con solo las fechas más recientes
    let url = '/habitaciones';
    
    const params = new URLSearchParams();
    if (entradaValue) params.append('entrada', entradaValue);
    if (salidaValue) params.append('salida', salidaValue);
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    // Redirigir a la página con las fechas actualizadas
    window.location.href = url;
}

// Función para validar fechas antes de reservar
function validarFechasYReservar(url) {
    const fechaEntrada = document.getElementById('fecha-entrada');
    const fechaSalida = document.getElementById('fecha-salida');
    
    if (!fechaEntrada || !fechaSalida || !fechaEntrada.value || !fechaSalida.value) {
        alert('Por favor, selecciona las fechas de entrada y salida antes de realizar la reserva.');
        // Abrir el selector de fechas
        const flatpickrInstance = document.querySelector('#rango-fechas')._flatpickr;
        if (flatpickrInstance) {
            flatpickrInstance.open();
        }
        return false;
    }

    // Verificar que las fechas sean válidas
    const entrada = new Date(fechaEntrada.value);
    const salida = new Date(fechaSalida.value);
    
    if (isNaN(entrada.getTime()) || isNaN(salida.getTime())) {
        alert('Selecciona una fecha de entrada y salida.');
        return false;
    }

    
    window.location.href = url;
    return false; // Prevenir el comportamiento por defecto del enlace
}
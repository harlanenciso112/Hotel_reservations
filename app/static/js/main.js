flatpickr.localize(flatpickr.l10ns.es);

const flatpickrInstance = flatpickr("#rango-fechas", {
    mode: "range",
    dateFormat: "Y-m-d",
    minDate: "today",
    locale: "es",
    onChange: function (selectedDates) {
        const [entrada, salida] = selectedDates;
        const nochesEl = document.getElementById("noches");
        const rangoEl = document.getElementById("rango-mostrado");

        if (entrada && salida) {
            const options = { weekday: "short", day: "2-digit", month: "short" };
            const entradaStr = entrada.toLocaleDateString("es-ES", options);
            const salidaStr = salida.toLocaleDateString("es-ES", options);
            const noches = Math.ceil((salida - entrada) / (1000 * 60 * 60 * 24));
            nochesEl.textContent = `📅 ${noches} noche${noches > 1 ? 's' : ''}`;
            rangoEl.textContent = `${entradaStr} - ${salidaStr}`;
        } else {
            nochesEl.textContent = `📅 Selecciona fechas`;
            rangoEl.textContent = `Haz clic para elegir`;
        }
    }
});

document.getElementById("fecha-display").addEventListener("click", () => {
    flatpickrInstance.open();
});

document.getElementById("btn-reservar").addEventListener("click", () => {
    // Llamar a la función redirigirAReservas
    redirigirAReservas();
});

function redirigirAReservas() {
    const fechas = flatpickrInstance.selectedDates;
  
    // Verificar si las fechas son válidas (se seleccionaron 2 fechas)
    if (fechas.length !== 2) {
        alert("Selecciona una fecha de entrada y salida.");
        return;
    }

    const entrada = fechas[0].toISOString().split("T")[0]; // Formato YYYY-MM-DD
    const salida = fechas[1].toISOString().split("T")[0]; // Formato YYYY-MM-DD

    // Redirigir a la página de habitaciones con los parámetros de fechas
    window.location.href = `/habitaciones?entrada=${entrada}&salida=${salida}`;
}

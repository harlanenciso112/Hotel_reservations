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
    const fechas = flatpickrInstance.selectedDates;
    if (fechas.length !== 2) {
        alert("Selecciona una fecha de entrada y salida.");
        return;
    }
    const entrada = fechas[0].toISOString().split("T")[0];
    const salida = fechas[1].toISOString().split("T")[0];
    window.location.href = `habitaciones.html?entrada=${entrada}&salida=${salida}`;
});


function redirigirAReservas() {
    const fechaInicio = flatpickrInstance.selectedDates[0];
    const fechaFin = flatpickrInstance.selectedDates[1];
  
    if (fechaInicio && fechaFin) {
      const formatoFechaInicio = fechaInicio.toISOString().split('T')[0]; // Formato YYYY-MM-DD
      const formatoFechaFin = fechaFin.toISOString().split('T')[0]; // Formato YYYY-MM-DD
  
      // Redirigir a la página de reservas con los parámetros de fechas
      window.location.href = `/habitaciones?inicio=${formatoFechaInicio}&fin=${formatoFechaFin}`;
    } else {
      alert("Por favor, selecciona un rango de fechas.");
    }
  }
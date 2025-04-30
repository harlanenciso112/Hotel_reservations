// Initialize flatpickr with Spanish locale
flatpickr.localize(flatpickr.l10ns.es);

// Function to get URL parameters
function getUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        entrada: urlParams.get('entrada'),
        salida: urlParams.get('salida')
    };
}

// Get dates from URL if available
const { entrada, salida } = getUrlParams();
const defaultDates = [];

if (entrada) defaultDates.push(entrada);
if (salida) defaultDates.push(salida);

// Initialize flatpickr with configuration
const flatpickrInstance = flatpickr("#rango-fechas", {
    mode: "range",
    dateFormat: "Y-m-d",
    minDate: "today",
    locale: "es",
    defaultDate: defaultDates.length > 0 ? defaultDates : undefined,
    onChange: function (selectedDates) {
        updateDateDisplay(selectedDates);
    },
    onReady: function(selectedDates) {
        // Update display on initialization if dates are available
        if (selectedDates.length > 0) {
            updateDateDisplay(selectedDates);
        }
    }
});

// Function to update the date display
function updateDateDisplay(selectedDates) {
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
        nochesEl.textContent = "📅 Selecciona fechas";
        rangoEl.textContent = "Haz clic para elegir";
    }
}

// Make the calendar open when clicking on the display box
document.getElementById("fecha-display").addEventListener("click", () => {
    flatpickrInstance.open();
});

// Also make it open when clicking on the input
document.getElementById("rango-fechas").addEventListener("click", () => {
    flatpickrInstance.open();
});
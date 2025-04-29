document.addEventListener('DOMContentLoaded', function() {
    const btnReservar = document.querySelector('.btn-reservar');
    const calendarioContainer = document.querySelector('.calendario-container');
    const fechaSeleccionadaSpan = document.querySelector('.fecha-seleccionada');
    const numeroNochesSpan = document.querySelector('.noche'); // Seleccionamos el span de "1 noche"

    const fp = flatpickr(calendarioContainer, {
        mode: "range", // Permite seleccionar un rango de fechas
        inline: false, // El calendario no se muestra de forma predeterminada
        dateFormat: "D, d M", // Formato de la fecha
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length === 2) {
                const startDate = selectedDates[0];
                const endDate = selectedDates[1];
                const timeDifference = endDate.getTime() - startDate.getTime();
                const numberOfNights = Math.ceil(timeDifference / (1000 * 3600 * 24));
                numeroNochesSpan.textContent = `📅 ${numberOfNights} noche${numberOfNights > 1 ? 's' : ''}`;

                const startDateFormatted = instance.formatDate(startDate, "D, d M");
                const endDateFormatted = instance.formatDate(endDate, "D, d M");
                fechaSeleccionadaSpan.textContent = `${startDateFormatted} - ${endDateFormatted}`;
            } else if (selectedDates.length === 1) {
                const singleDateFormatted = instance.formatDate(selectedDates[0], "D, d M");
                fechaSeleccionadaSpan.textContent = singleDateFormatted;
                numeroNochesSpan.textContent = `📅 1 noche`; // Si solo hay una fecha seleccionada
            } else {
                fechaSeleccionadaSpan.textContent = "Seleccionar fechas";
                numeroNochesSpan.textContent = `📅 1 noche`; // Valor predeterminado
            }
        },
        onClose: function(selectedDates, dateStr, instance) {
            calendarioContainer.classList.remove('activo'); // Oculta el calendario al cerrar
        },
        onOpen: function() {
            calendarioContainer.classList.add('activo'); // Muestra el calendario al abrir
        }
    });

    btnReservar.addEventListener('click', function(e) {
        e.stopPropagation(); // Evita que el clic se propague al documento
        calendarioContainer.classList.toggle('activo');
        fp.toggle(); // Alterna la visibilidad del calendario de Flatpickr
    });

    document.addEventListener('click', function(e) {
        if (!calendarioContainer.contains(e.target) && e.target !== btnReservar) {
            calendarioContainer.classList.remove('activo');
            if (fp.isOpen) {
                fp.close();
            }
        }
    });
});
document.addEventListener("DOMContentLoaded", () => {

    /* FUNDADOR */

    const checkFundador =
        document.getElementById("esFundador");

    const seccionFundador =
        document.getElementById("seccionFundador");

    if (checkFundador && seccionFundador) {

        checkFundador.addEventListener("change", () => {

            if (checkFundador.checked) {

                seccionFundador.style.display = "block";

            } else {

                seccionFundador.style.display = "none";

            }

        });

    }

});


/* REPORTES */

function mostrarReporte(idReporte) {

    const reportes =
        document.querySelectorAll(".reporte-container");

    reportes.forEach(reporte => {

        reporte.classList.add("d-none");

    });

    const reporteSeleccionado =
        document.getElementById(idReporte);

    if (reporteSeleccionado) {

        reporteSeleccionado.classList.remove("d-none");

    }

}


/* CONFIRMACIONES */

function confirmarEliminacion() {

    return confirm(
        "¿Está seguro de realizar esta acción?"
    );

}
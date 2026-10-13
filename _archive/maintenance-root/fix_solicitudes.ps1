$root = "F:\edu_Final"
$file = "$root\templates\solicitudes\index.html"

if (!(Test-Path $file)) {
    Write-Host "NO EXISTE:"
    Write-Host $file
    exit
}

$backupDir = "$root\BACKUP_SOLICITUDES"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$backupFile = "$backupDir\index_antes_fix.html"
Copy-Item $file $backupFile -Force

$html = [System.IO.File]::ReadAllText(
    $file,
    [System.Text.Encoding]::UTF8
)

$fix = @'
<style id="EDUTURNOS-SOLICITUDES-FINAL">

.solicitudes-final-atras {
    margin-bottom: 20px !important;
}

.solicitudes-final-descripcion {
    margin-bottom: 24px !important;
}

.solicitudes-final-vacio {
    text-align: center !important;
    padding: 32px 20px !important;
}

.solicitudes-final-icono {
    font-size: 32px !important;
    margin-bottom: 14px !important;
}

.solicitudes-final-seguimiento {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: auto !important;
    min-width: 0 !important;
    min-height: 40px !important;
    padding: 9px 16px !important;
    font-size: 15px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
}

</style>

<script id="EDUTURNOS-SOLICITUDES-FINAL-JS">

(function () {

    "use strict";

    function repararTexto(texto) {

        var cambios = {
            "\u00c3\u00a1": "\u00e1",
            "\u00c3\u00a9": "\u00e9",
            "\u00c3\u00ad": "\u00ed",
            "\u00c3\u00b3": "\u00f3",
            "\u00c3\u00ba": "\u00fa",
            "\u00c3\u00b1": "\u00f1",
            "\u00c2\u00b7": "\u00b7",
            "\u00e2\u0086\u0090": "\u2190",
            "\u00e2\u0086\u0092": "\u2192",
            "\u00e2\u0080\u00b9": "\u2039",
            "\u00e2\u0080\u00ba": "\u203a",
            "\u00f0\u0178\u201c\u2039": "\ud83d\udccb"
        };

        Object.keys(cambios).forEach(function (incorrecto) {
            texto = texto.split(incorrecto).join(cambios[incorrecto]);
        });

        return texto;
    }

    function repararPagina() {

        var walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null
        );

        var nodos = [];
        var nodo;

        while ((nodo = walker.nextNode())) {
            nodos.push(nodo);
        }

        nodos.forEach(function (n) {

            var nuevo = repararTexto(n.nodeValue);

            if (nuevo !== n.nodeValue) {
                n.nodeValue = nuevo;
            }

        });

        var enlaces = document.querySelectorAll("a");

        enlaces.forEach(function (enlace) {

            var href = enlace.getAttribute("href") || "";
            var texto = (enlace.textContent || "").trim();

            if (href.indexOf("/auth/dashboard") >= 0) {

                if (
                    texto.indexOf("Atr") >= 0 ||
                    texto.indexOf("\u2190") >= 0
                ) {

                    enlace.innerHTML =
                        "&#8592; Atr&#225;s";

                    enlace.classList.add(
                        "solicitudes-final-atras"
                    );
                }
            }

            if (
                href.indexOf("/solicitudes/nueva/docente") >= 0
            ) {

                enlace.innerHTML =
                    "+ Solicitar seguimiento";

                enlace.classList.add(
                    "solicitudes-final-seguimiento"
                );
            }

        });

        var elementos = document.querySelectorAll("body *");

        elementos.forEach(function (elemento) {

            var texto = (elemento.textContent || "").trim();

            if (
                elemento.children.length === 0 &&
                texto.indexOf("Flujo formal de solicitud") >= 0
            ) {

                elemento.innerHTML =
                    "Flujo formal de solicitud, revisi&#243;n, propuesta y confirmaci&#243;n.";

                elemento.classList.add(
                    "solicitudes-final-descripcion"
                );
            }

            if (
                elemento.children.length === 0 &&
                texto.indexOf("Cuando se registre una solicitud") >= 0
            ) {

                elemento.innerHTML =
                    "Cuando se registre una solicitud, aparecer&#225; aqu&#237;.";
            }

            if (
                elemento.children.length === 0 &&
                (
                    texto.indexOf("\u00f0") >= 0 ||
                    texto.indexOf("\ud83d\udccb") >= 0
                )
            ) {

                elemento.innerHTML = "&#128203;";

                elemento.classList.add(
                    "solicitudes-final-icono"
                );
            }

        });

    }

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            repararPagina
        );

    } else {

        repararPagina();

    }

})();

</script>
'@

if (!$html.Contains("EDUTURNOS-SOLICITUDES-FINAL")) {

    if ($html.Contains("</body>")) {

        $html = $html.Replace(
            "</body>",
            $fix + "`r`n</body>"
        )

    } else {

        $html = $html + "`r`n" + $fix
    }

}

$utf8 = New-Object System.Text.UTF8Encoding($false)

[System.IO.File]::WriteAllText(
    $file,
    $html,
    $utf8
)

Write-Host ""
Write-Host "=========================================="
Write-Host " SOLICITUDES CORREGIDAS"
Write-Host "=========================================="
Write-Host ""
Write-Host "Archivo:"
Write-Host $file
Write-Host ""
Write-Host "Backup:"
Write-Host $backupFile
Write-Host ""
Write-Host "OK"
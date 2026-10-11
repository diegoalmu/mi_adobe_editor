"""Pruebas de app/formato_html.py para escribir en el PDF (Tarea 2 del diseno).

Se crea un PDF en memoria (sin archivos en disco) para probar
insertar_texto_con_formato y cabe_texto_con_formato.

El import va sin prefijo de paquete (from formato_html import ...) porque
asi corre el programa. Pyright no ve la ruta que agrega tests/conftest.py
en tiempo de ejecucion, por eso este archivo apaga reportMissingImports.
"""

# pyright: reportMissingImports=false

import fitz

from formato_html import (
    cabe_texto_con_formato,
    fragmentos_a_html,
    insertar_texto_con_formato,
)

# Bit de negrita en los flags de un span de get_text("dict")
# (TEXT_FONT_BOLD = 16 en PyMuPDF).
BIT_NEGRITA = 16


def _html_precio_actualizado():
    """HTML de 'Precio actualizado' con solo la segunda palabra en negrita."""
    return fragmentos_a_html([
        {"texto": "Precio ", "familia": "Arial", "tamano": 11.0,
         "negrita": False, "cursiva": False, "subrayado": False,
         "color": (0, 0, 0)},
        {"texto": "actualizado", "familia": "Arial", "tamano": 11.0,
         "negrita": True, "cursiva": False, "subrayado": False,
         "color": (0, 0, 0)},
    ])


def _spans_de_pagina(pagina):
    """Junta todos los spans de texto de la pagina en una sola lista."""
    spans = []
    for bloque in pagina.get_text("dict")["blocks"]:
        for linea in bloque.get("lines", []):
            spans.extend(linea["spans"])
    return spans


def test_inserta_negrita_solo_en_actualizado():
    """Inserta 'Precio actualizado' y solo 'actualizado' queda en negrita."""
    documento = fitz.open()
    try:
        pagina = documento.new_page(width=300, height=200)
        rect = fitz.Rect(20, 20, 280, 100)
        html = _html_precio_actualizado()

        assert cabe_texto_con_formato(rect, html, None, None)
        insertar_texto_con_formato(pagina, rect, html, None, None)

        spans = _spans_de_pagina(pagina)

        negritas = [s for s in spans if s["flags"] & BIT_NEGRITA]
        normales = [s for s in spans if not (s["flags"] & BIT_NEGRITA)]

        assert any("actualizado" in s["text"] for s in negritas)
        assert any("Precio" in s["text"] for s in normales)
        # la palabra en negrita NO aparece en un span sin negrita
        assert not any("actualizado" in s["text"] for s in normales)
    finally:
        documento.close()


def test_texto_enorme_no_cabe_y_no_modifica_el_documento():
    """Un texto enorme en un cuadro pequeno no cabe y el documento queda intacto."""
    documento = fitz.open()
    try:
        pagina = documento.new_page(width=300, height=200)
        texto_antes = pagina.get_text()
        rect_pequeno = fitz.Rect(20, 20, 60, 40)
        html_enorme = "palabra " * 500

        assert not cabe_texto_con_formato(rect_pequeno, html_enorme, None, None)
        # cabe_texto_con_formato trabaja en un documento temporal: el real
        # no se toca (ni siquiera se le escribe texto)
        assert pagina.get_text() == texto_antes
    finally:
        documento.close()

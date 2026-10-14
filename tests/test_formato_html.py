"""Pruebas de app/formato_html.py (Tarea 1 del diseno).

Se importan las funciones puras del modulo: no necesitan ventanas ni
PDFs reales, asi que corren sin Qt.

El import va sin prefijo de paquete (from formato_html import ...) porque
asi corre el programa. Pyright no ve la ruta que agrega tests/conftest.py
en tiempo de ejecucion, por eso este archivo apaga reportMissingImports.
"""


import tempfile
from pathlib import Path

from formato_html import css_tipografias, fragmentos_a_html, tipografias_disponibles


def _fragmento(texto, **cambios):
    """Crea un fragmento con los valores del diseno; `cambios` pisa lo que se quiera."""
    fragmento = {
        "texto": texto,
        "familia": "Arial",
        "tamano": 11.0,
        "negrita": False,
        "cursiva": False,
        "subrayado": False,
        "color": (0, 0, 0),
    }
    fragmento.update(cambios)
    return fragmento


def test_escapa_caracteres_especiales():
    """'<b>' escrito como texto debe quedar escapado, no como etiqueta HTML."""
    html = fragmentos_a_html([_fragmento("<b>")])
    assert "&lt;b&gt;" in html
    assert "<b>" not in html


def test_negrita_solo_en_su_span():
    """Un fragmento en negrita genera font-weight:bold solo en ese span."""
    html = fragmentos_a_html([
        _fragmento("Precio"),
        _fragmento("actualizado", negrita=True),
    ])
    assert "font-weight:bold" in html
    assert html.count("font-weight:bold") == 1
    assert "Precio" in html
    assert "actualizado" in html


def test_salto_de_linea_se_convierte_en_br():
    """Un '\\n' dentro del texto se convierte en <br>."""
    html = fragmentos_a_html([_fragmento("uno\ndos")])
    assert "<br>" in html
    assert "uno\ndos" not in html


def test_carpeta_vacia_no_hay_tipografias_ni_css():
    """Con una carpeta sin archivos no hay tipografias disponibles y el CSS queda vacio."""
    with tempfile.TemporaryDirectory() as carpeta:
        carpeta_vacia = Path(carpeta)
        assert tipografias_disponibles(carpeta_vacia) == []
        assert css_tipografias(carpeta_vacia) == ""

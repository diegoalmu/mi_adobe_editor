"""Prueba del flujo completo de edicion de texto en linea (Tarea 5).

Crea un PDF de verdad en un archivo temporal, abre la ventana principal,
detecta el parrafo, lo edita en linea (negrita a una palabra), acepta,
y comprueba que el PDF quedo cambiado y que la edicion se cerro sola.
"""

# pyright: reportMissingImports=false

import fitz
from PySide6.QtCore import QRect
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from main import EditorPDF

# QApplication unica para todas las pruebas (crear varias da error)
_aplicacion = QApplication.instance() or QApplication([])


def _crear_pdf_con_un_parrafo(ruta):
    """Crea un PDF de una pagina con la linea 'uno dos tres' a 12 puntos."""
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    pagina.insert_text((72, 100), "uno dos tres", fontsize=12, fontname="helv")
    documento.save(str(ruta))
    documento.close()


def _parrafo_unico(ventana, pagina):
    """Devuelve el unico parrafo de la pagina, con el bbox ensanchado.

    El bbox real del parrafo mide lo justo que ocupa el texto; se
    ensancha (+-10 en X, +-5 en Y) para que la prueba de 'si cabe el
    texto' pase siempre y no se abra un QMessageBox que bloquearia la
    ejecucion offscreen.
    """
    parrafos = ventana.obtener_todos_los_parrafos(pagina)
    assert len(parrafos) == 1
    parrafo = parrafos[0]
    bbox = parrafo["bbox"]
    parrafo = dict(parrafo)
    parrafo["bbox"] = fitz.Rect(bbox.x0 - 10, bbox.y0 - 5, bbox.x1 + 10, bbox.y1 + 5)
    return parrafo


def _span_con_negrita(pagina, palabra):
    """Busca en la pagina un span que contenga la palabra y tenga la marca de negrita."""
    for bloque in pagina.get_text("dict")["blocks"]:
        for linea in bloque.get("lines", []):
            for span in linea["spans"]:
                if palabra in span["text"] and span["flags"] & 16:
                    return span
    return None


def _texto_plano(pagina):
    """Texto de la pagina en una sola linea, con los espacios duros en normal.

    insert_htmlbox convierte los espacios normales en espacios duros
    (\xa0), asi que se unifican antes de comparar.
    """
    return str(pagina.get_text("text")).replace("\xa0", " ").replace("\n", " ").strip()


def test_editar_parrafo_en_linea_y_aceptar(tmp_path):
    ruta = tmp_path / "prueba.pdf"
    _crear_pdf_con_un_parrafo(ruta)

    ventana = EditorPDF()
    ventana.documento = fitz.open(str(ruta))
    ventana.ruta_actual = str(ruta)
    ventana.dibujar_todas_las_paginas()

    pagina = ventana.documento[0]
    parrafo = _parrafo_unico(ventana, pagina)

    # Abrir la edicion en linea sobre el parrafo
    ventana.editar_parrafo_encontrado(0, pagina, parrafo)
    assert ventana.editor_texto_inline is not None
    assert ventana.barra_formato is not None
    assert ventana.parrafo_editando is not None
    assert ventana.parrafo_editando["pagina"] == 0
    assert ventana.parrafo_editando["bbox"] == parrafo["bbox"]
    assert ventana.editor_texto_inline.toPlainText() == "uno dos tres"

    # Poner "dos" en negrita con el boton de la barra de formato
    cursor = ventana.editor_texto_inline.textCursor()
    cursor.setPosition(4)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    ventana.editor_texto_inline.setTextCursor(cursor)
    ventana.barra_formato.boton_negrita.toggle()

    # Aceptar: el texto se escribe en el PDF y la edicion se cierra
    ventana.aceptar_edicion_texto()
    assert ventana.editor_texto_inline is None
    assert ventana.barra_formato is None
    assert ventana.parrafo_editando is None

    # El PDF real ahora contiene la palabra "dos" con la marca de negrita
    span_negrita = _span_con_negrita(pagina, "dos")
    assert span_negrita is not None
    assert "dos" in span_negrita["text"]
    # Y el texto completo sigue siendo legible en la pagina
    assert _texto_plano(pagina) == "uno dos tres"

    # Guardar (sin dialogo: ruta_actual ya esta puesta) y reabrir el archivo
    ventana.guardar()
    ventana.documento.close()
    ventana.documento = fitz.open(str(ruta))
    assert _texto_plano(ventana.documento[0]) == "uno dos tres"
    assert _span_con_negrita(ventana.documento[0], "dos") is not None

    ventana.documento.close()
    ventana.close()


def test_editar_parrafo_y_cancelar_no_toca_el_pdf(tmp_path):
    ruta = tmp_path / "prueba_cancelar.pdf"
    _crear_pdf_con_un_parrafo(ruta)

    ventana = EditorPDF()
    ventana.documento = fitz.open(str(ruta))
    ventana.dibujar_todas_las_paginas()

    pagina = ventana.documento[0]
    parrafo = _parrafo_unico(ventana, pagina)
    texto_antes = str(pagina.get_text("text"))

    ventana.editar_parrafo_encontrado(0, pagina, parrafo)
    assert ventana.editor_texto_inline is not None

    # Cambiar el texto en el editor, pero CANCELAR: el PDF no debe cambiar
    ventana.editor_texto_inline.setPlainText("texto totalmente distinto")
    ventana.cancelar_edicion_texto()

    assert ventana.editor_texto_inline is None
    assert ventana.barra_formato is None
    assert ventana.parrafo_editando is None
    assert str(pagina.get_text("text")) == texto_antes

    ventana.documento.close()
    ventana.close()


def test_clic_en_otro_parrafo_acepta_y_abre_el_nuevo(tmp_path):
    """Como en Acrobat: con la edicion de A abierta, un clic en B
    acepta A (queda escrito en el PDF) y abre el editor en B."""
    ruta = tmp_path / "dos_parrafos.pdf"
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    pagina.insert_text((72, 100), "parrafo A", fontsize=12, fontname="helv")
    pagina.insert_text((72, 200), "parrafo B", fontsize=12, fontname="helv")
    documento.save(str(ruta))
    documento.close()

    ventana = EditorPDF()
    ventana.documento = fitz.open(str(ruta))
    ventana.dibujar_todas_las_paginas()

    pagina = ventana.documento[0]
    parrafos = ventana.obtener_todos_los_parrafos(pagina)
    assert len(parrafos) == 2
    parrafo_a = parrafos[0]  # el de mas arriba
    parrafo_b = parrafos[1]

    # Abrir la edicion del parrafo A y cambiarle el texto
    ventana.editar_parrafo_encontrado(0, pagina, parrafo_a)
    assert ventana.editor_texto_inline is not None
    ventana.editor_texto_inline.setPlainText("A editado")

    # Simular un clic en el centro del parrafo B, por el flujo real:
    # al_seleccionar_rectangulo recibe el rectangulo en PIXELES del
    # visor (por eso se multiplica por el zoom). La herramienta debe
    # seguir siendo "Editar contenido" (como en la app real).
    ventana.combo_herramienta.setCurrentText("Editar contenido (texto e imagenes)")
    centro_b = parrafo_b["bbox"]
    punto_x = int(((centro_b.x0 + centro_b.x1) / 2) * ventana.zoom)
    punto_y = int(((centro_b.y0 + centro_b.y1) / 2) * ventana.zoom)
    ventana.al_seleccionar_rectangulo(0, QRect(punto_x, punto_y, 1, 1))

    # El cambio de A quedo escrito en el PDF...
    assert "A editado" in _texto_plano(ventana.documento[0])
    # ...y hay un editor abierto ahora en el parrafo B
    assert ventana.editor_texto_inline is not None
    assert ventana.parrafo_editando is not None
    assert ventana.editor_texto_inline.toPlainText() == "parrafo B"
    assert ventana.parrafo_editando["pagina"] == 0
    assert ventana.parrafo_editando["bbox"] == parrafo_b["bbox"]

    ventana.cancelar_edicion_texto()
    ventana.documento.close()
    ventana.close()

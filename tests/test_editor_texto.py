"""Pruebas de app/editor_texto.py (Tareas 3, 4 y 5 del diseno).

La plataforma offscreen de Qt la fija tests/conftest.py antes de
importar los modulos de la aplicacion.
"""

# pyright: reportMissingImports=false

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QColor, QKeyEvent, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication

from editor_texto import (
    BarraFormato, EditorTextoInline, documento_a_fragmentos,
    tamano_editor_a_pdf, tamano_pdf_a_editor,
)
from formato_html import CARPETA_FUENTES_WINDOWS, tipografias_disponibles

# QApplication unica para todas las pruebas (crear varias da error)
_aplicacion = QApplication.instance() or QApplication([])


def test_documento_a_fragmentos_con_negrita_en_dos():
    editor = EditorTextoInline()
    editor.setPlainText("uno dos tres")

    # Seleccionar la palabra "dos" (posiciones 4 a 7)
    cursor = editor.textCursor()
    cursor.setPosition(4)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)

    formato_negrita = QTextCharFormat()
    formato_negrita.setFontWeight(QFont.Weight.Bold)
    cursor.mergeCharFormat(formato_negrita)

    fragmentos = documento_a_fragmentos(editor.document())

    con_dos = [f for f in fragmentos if "dos" in f["texto"]]
    assert len(con_dos) == 1
    assert con_dos[0]["negrita"] is True

    sin_negrita = [f for f in fragmentos if not f["negrita"]]
    assert any("uno" in f["texto"] for f in sin_negrita)
    assert any("tres" in f["texto"] for f in sin_negrita)


def test_esc_emite_cancelado():
    editor = EditorTextoInline()
    recibidos = []
    editor.cancelado.connect(lambda: recibidos.append("cancelado"))
    evento = QKeyEvent(
        QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier
    )
    editor.keyPressEvent(evento)
    assert recibidos == ["cancelado"]


def test_ctrl_enter_emite_aceptado():
    editor = EditorTextoInline()
    recibidos = []
    editor.aceptado.connect(lambda: recibidos.append("aceptado"))
    evento = QKeyEvent(
        QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier
    )
    editor.keyPressEvent(evento)
    assert recibidos == ["aceptado"]


def test_barra_negrita_aplica_solo_a_la_seleccion():
    editor = EditorTextoInline()
    editor.setPlainText("uno dos tres")
    barra = BarraFormato(editor)

    # Seleccionar la palabra "dos" (posiciones 4 a 7)
    cursor = editor.textCursor()
    cursor.setPosition(4)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)

    # Activar el boton Negrita de la barra
    barra.boton_negrita.toggle()

    fragmentos = documento_a_fragmentos(editor.document())
    con_dos = [f for f in fragmentos if "dos" in f["texto"]]
    assert len(con_dos) == 1
    assert con_dos[0]["negrita"] is True

    sin_negrita = [f for f in fragmentos if not f["negrita"]]
    assert any("uno" in f["texto"] for f in sin_negrita)
    assert any("tres" in f["texto"] for f in sin_negrita)


def test_barra_refleja_negrita_del_cursor():
    editor = EditorTextoInline()
    editor.setPlainText("uno dos tres")

    # Poner "dos" en negrita con un cursor de Qt directamente
    cursor = editor.textCursor()
    cursor.setPosition(4)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)
    formato = QTextCharFormat()
    formato.setFontWeight(QFont.Weight.Bold)
    cursor.mergeCharFormat(formato)

    # Dejar el cursor en "uno" (sin negrita) y recien ahi crear la barra
    cursor_uno = editor.textCursor()
    cursor_uno.setPosition(1)
    editor.setTextCursor(cursor_uno)

    barra = BarraFormato(editor)
    assert not barra.boton_negrita.isChecked()

    # Mover el cursor dentro de "dos": el boton debe marcarse solo
    cursor_dos = editor.textCursor()
    cursor_dos.setPosition(5)
    editor.setTextCursor(cursor_dos)
    assert barra.boton_negrita.isChecked()


def test_barra_aplicar_color_a_la_seleccion():
    editor = EditorTextoInline()
    editor.setPlainText("uno dos tres")
    barra = BarraFormato(editor)

    cursor = editor.textCursor()
    cursor.setPosition(4)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)

    # Las pruebas usan solo aplicar_color; el dialogo no se abre nunca
    barra.aplicar_color(QColor(200, 10, 50))

    fragmentos = documento_a_fragmentos(editor.document())
    con_dos = [f for f in fragmentos if "dos" in f["texto"]]
    assert con_dos[0]["color"] == (200, 10, 50)


def test_barra_tipografias_solo_las_disponibles():
    barra = BarraFormato(EditorTextoInline())
    esperadas = tipografias_disponibles(CARPETA_FUENTES_WINDOWS)
    assert barra.combo_tipografia.count() == len(esperadas)
    for indice, nombre in enumerate(esperadas):
        assert barra.combo_tipografia.itemText(indice) == nombre


def test_tamano_pdf_y_editor_ida_y_vuelta():
    for tamano_pdf in (8, 12, 24, 72):
        for zoom in (0.5, 1.0, 1.5, 2.0):
            editor = tamano_pdf_a_editor(tamano_pdf, zoom, 96.0)
            assert editor > 0
            # La conversion inversa debe devolver el mismo punto PDF
            assert abs(tamano_editor_a_pdf(editor, zoom, 96.0) - tamano_pdf) < 1e-9

    # A 96 DPI y zoom 1, 12 puntos PDF son 9 puntos de Qt (factor 0.75)
    assert abs(tamano_pdf_a_editor(12, 1.0, 96.0) - 9.0) < 1e-9

"""Pruebas de app/editor_texto.py (Tarea 3 del diseno).

La plataforma offscreen de Qt la fija tests/conftest.py antes de
importar los modulos de la aplicacion.
"""

# pyright: reportMissingImports=false

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication

from editor_texto import EditorTextoInline, documento_a_fragmentos

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

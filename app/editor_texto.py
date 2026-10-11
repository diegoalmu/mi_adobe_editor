"""
editor_texto.py - Cuadro editable del editor de texto inline
============================================================

Clase EditorTextoInline (un QTextEdit sin marco que se pone encima de un
parrafo del PDF, con fondo blanco semitransparente) y la funcion
documento_a_fragmentos, que convierte el contenido del QTextEdit en la
lista de fragmentos que consume formato_html.fragmentos_a_html.

El codigo usa nombres COMPLETOS de los enums de Qt (por ejemplo
Qt.Key.Key_Escape o QFont.Weight.Bold) para que pyright no reporte
errores por enums cortos.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import QFrame, QTextEdit


class EditorTextoInline(QTextEdit):
    """Cuadro editable que se coloca encima de un parrafo del PDF.

    Sin marco y con fondo blanco semitransparente, para que se vea el
    parrafo original debajo. Esc emite la senal `cancelado` y Ctrl+Enter
    emite la senal `aceptado`.
    """

    cancelado = Signal()
    aceptado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 200);")

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key.Key_Escape:
            self.cancelado.emit()
            return
        if (
            evento.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and evento.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.aceptado.emit()
            return
        super().keyPressEvent(evento)


# =========================================================================
# DOCUMENTO DE QT -> LISTA DE FRAGMENTOS
# =========================================================================

def documento_a_fragmentos(documento_qt):
    """Convierte el documento de un QTextEdit en la lista de fragmentos.

    Cada fragmento es un diccionario con las claves texto, familia,
    tamano, negrita, cursiva, subrayado y color (tupla rgb de 0 a 255),
    el mismo formato que consume formato_html.fragmentos_a_html. Entre
    bloques (parrafos) se agrega un "\\n" al final del ultimo fragmento
    del bloque, para que despues se convierta en <br>. Si un bloque esta
    vacio, se agrega un fragmento que solo contiene el "\\n".
    """
    fragmentos = []
    fuente_defecto = documento_qt.defaultFont()

    bloque = documento_qt.begin()
    while bloque.isValid():
        fragmentos_bloque = []

        iterador = bloque.begin()
        while not iterador.atEnd():
            fragmento = iterador.fragment()
            if fragmento.isValid() and fragmento.text():
                formato = fragmento.charFormat()
                familias = formato.fontFamilies()
                familia = familias[0] if familias else fuente_defecto.family()
                tamano = formato.fontPointSize() or fuente_defecto.pointSizeF()
                color_qt = formato.foreground().color()
                if color_qt.isValid():
                    tupla_color = (color_qt.red(), color_qt.green(), color_qt.blue())
                else:
                    tupla_color = (0, 0, 0)
                fragmentos_bloque.append({
                    "texto": fragmento.text(),
                    "familia": familia,
                    "tamano": tamano,
                    "negrita": formato.fontWeight() >= int(QFont.Weight.Bold),
                    "cursiva": formato.fontItalic(),
                    "subrayado": formato.fontUnderline(),
                    "color": tupla_color,
                })
            iterador += 1

        # Entre bloques se deja un salto de linea (despues sera <br>)
        if bloque.next().isValid():
            if fragmentos_bloque:
                fragmentos_bloque[-1]["texto"] += "\n"
            else:
                fragmentos_bloque.append({
                    "texto": "\n",
                    "familia": fuente_defecto.family(),
                    "tamano": fuente_defecto.pointSizeF(),
                    "negrita": False,
                    "cursiva": False,
                    "subrayado": False,
                    "color": (0, 0, 0),
                })

        fragmentos.extend(fragmentos_bloque)
        bloque = bloque.next()

    return fragmentos

"""
editor_texto.py - Cuadro editable y barra de formato del editor inline
======================================================================

Clase EditorTextoInline (un QTextEdit sin marco que se pone encima de un
parrafo del PDF, con fondo blanco semitransparente), clase BarraFormato
(el QToolBar con selector de tipografia y tamano, botones de Negrita,
Cursiva y Subrayado, boton de color, Aceptar y Cancelar), la funcion
documento_a_fragmentos, que convierte el contenido del QTextEdit en la
lista de fragmentos que consume formato_html.fragmentos_a_html, y las
funciones tamano_pdf_a_editor / tamano_editor_a_pdf, que convierten los
tamanos de puntos PDF (los del documento) a puntos de letra de Qt (los
del editor) segun el zoom del visor y el DPI logico de la pantalla.

El codigo usa nombres COMPLETOS de los enums de Qt (por ejemplo
Qt.Key.Key_Escape o QFont.Weight.Bold) para que pyright no reporte
errores por enums cortos.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QComboBox,
    QColorDialog,
    QFrame,
    QPushButton,
    QTextEdit,
    QToolBar,
    QToolButton,
)

from formato_html import CARPETA_FUENTES_WINDOWS, tipografias_disponibles


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
# BARRA DE FORMATO
# =========================================================================

# Tamanos de letra (en puntos) que ofrece la barra, como en un
# procesador de textos clasico. Son PUNTOS PDF (el PDF usa 72 puntos
# por pulgada); la barra los muestra tal cual y el PDF los recibe tal
# cual. Para mostrarlos en el editor Qt se convierten con las dos
# funciones de abajo.
TAMANOS = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]


# =========================================================================
# TAMANOS: PUNTOS PDF <-> PUNTOS DEL EDITOR (QT)
# =========================================================================

def tamano_pdf_a_editor(tamano_pdf, zoom, dpi_logica):
    """Convierte un tamano en puntos PDF al tamano en puntos de Qt.

    El visor dibuja la pagina con la matriz (zoom, zoom) y PyMuPDF usa
    72 puntos por pulgada al renderizar, asi que 1 punto PDF ocupa
    `zoom` pixeles en el visor. Qt, en cambio, usa el DPI logico de la
    pantalla (`dpi_logica`, 96 en Windows al 100%): 1 punto de letra Qt
    ocupa `dpi_logica / 72` pixeles. Igualando los dos tamaños para que
    el texto del editor se vea igual que en la página:

        punto_editor = punto_pdf * zoom * 72 / dpi_logica
    """
    return tamano_pdf * zoom * 72.0 / dpi_logica


def tamano_editor_a_pdf(tamano_editor, zoom, dpi_logica):
    """Convierte un tamano en puntos de Qt a puntos PDF (ida y vuelta
    exacto con tamano_pdf_a_editor)."""
    return tamano_editor * dpi_logica / (zoom * 72.0)


class BarraFormato(QToolBar):
    """Barra con los controles de formato del editor de texto inline.

    Contiene el selector de tipografia (solo las disponibles en el
    sistema), el de tamano, los botones activables de Negrita, Cursiva y
    Subrayado, el boton de color, y los botones Aceptar y Cancelar. Cada
    control aplica el formato solo a la seleccion del editor (o a lo que
    se escriba despues, si no hay seleccion, como en Word). Al mover el
    cursor del editor, la barra refleja el formato del texto donde esta.

    Los tamanos del selector son PUNTOS PDF (como los que recibe el
    PDF); `zoom` y `dpi_logica` son los del visor, y se usan para
    convertirlos al tamano de letra que el editor Qt necesita (ver
    tamano_pdf_a_editor). Senales: `aceptar` y `cancelar`.
    """

    aceptar = Signal()
    cancelar = Signal()

    def __init__(self, editor, zoom=1.0, dpi_logica=96.0, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.zoom = zoom
        self.dpi_logica = dpi_logica
        self._color_actual = QColor(0, 0, 0)

        # Selector de tipografia: solo las disponibles en el sistema
        self.combo_tipografia = QComboBox()
        self.combo_tipografia.addItems(
            tipografias_disponibles(CARPETA_FUENTES_WINDOWS)
        )
        self.combo_tipografia.currentTextChanged.connect(self.aplicar_tipografia)
        self.addWidget(self.combo_tipografia)

        # Selector de tamano
        self.combo_tamano = QComboBox()
        for tamano in TAMANOS:
            self.combo_tamano.addItem(str(tamano))
        self.combo_tamano.setCurrentIndex(TAMANOS.index(11))
        self.combo_tamano.currentTextChanged.connect(self.aplicar_tamano)
        self.addWidget(self.combo_tamano)

        # Botones activables: Negrita (N), Cursiva (C) y Subrayado (S)
        self.boton_negrita = QToolButton()
        self.boton_negrita.setText("N")
        self.boton_negrita.setCheckable(True)
        self.boton_negrita.toggled.connect(self.alternar_negrita)
        self.addWidget(self.boton_negrita)

        self.boton_cursiva = QToolButton()
        self.boton_cursiva.setText("C")
        self.boton_cursiva.setCheckable(True)
        self.boton_cursiva.toggled.connect(self.alternar_cursiva)
        self.addWidget(self.boton_cursiva)

        self.boton_subrayado = QToolButton()
        self.boton_subrayado.setText("S")
        self.boton_subrayado.setCheckable(True)
        self.boton_subrayado.toggled.connect(self.alternar_subrayado)
        self.addWidget(self.boton_subrayado)

        # Boton de color: elegir_color abre el dialogo de Windows y
        # aplicar_color hace el trabajo (las pruebas usan solo
        # aplicar_color, nunca abren el dialogo).
        self.boton_color = QPushButton("Color")
        self.boton_color.clicked.connect(self.elegir_color)
        self.addWidget(self.boton_color)

        # Aceptar y Cancelar
        self.boton_aceptar = QPushButton("Aceptar")
        self.boton_aceptar.clicked.connect(lambda: self.aceptar.emit())
        self.addWidget(self.boton_aceptar)

        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(lambda: self.cancelar.emit())
        self.addWidget(self.boton_cancelar)

        # Reflejar el formato del cursor y seguirlo cuando se mueva
        self.editor.cursorPositionChanged.connect(self.actualizar_desde_cursor)
        self.actualizar_desde_cursor()

    def aplicar_tipografia(self, nombre):
        """Aplica la tipografia elegida a la seleccion del editor."""
        if not nombre:
            return
        formato = QTextCharFormat()
        formato.setFontFamilies([nombre])
        self.editor.mergeCurrentCharFormat(formato)

    def aplicar_tamano(self, texto):
        """Aplica al editor el tamano elegido en la barra (puntos PDF)."""
        if not texto:
            return
        tamano_editor = tamano_pdf_a_editor(
            float(texto), self.zoom, self.dpi_logica
        )
        formato = QTextCharFormat()
        formato.setFontPointSize(tamano_editor)
        self.editor.mergeCurrentCharFormat(formato)

    def alternar_negrita(self, activo):
        """Pone o quita negrita en la seleccion del editor."""
        formato = QTextCharFormat()
        if activo:
            formato.setFontWeight(QFont.Weight.Bold)
        else:
            formato.setFontWeight(QFont.Weight.Normal)
        self.editor.mergeCurrentCharFormat(formato)

    def alternar_cursiva(self, activo):
        """Pone o quita cursiva en la seleccion del editor."""
        formato = QTextCharFormat()
        formato.setFontItalic(activo)
        self.editor.mergeCurrentCharFormat(formato)

    def alternar_subrayado(self, activo):
        """Pone o quita subrayado en la seleccion del editor."""
        formato = QTextCharFormat()
        formato.setFontUnderline(activo)
        self.editor.mergeCurrentCharFormat(formato)

    def elegir_color(self):
        """Abre el selector de color de Windows y aplica el elegido."""
        color = QColorDialog.getColor(initial=self._color_actual, parent=self)
        if color.isValid():
            self.aplicar_color(color)

    def aplicar_color(self, color):
        """Aplica el color dado (un QColor) a la seleccion del editor."""
        formato = QTextCharFormat()
        formato.setForeground(color)
        self.editor.mergeCurrentCharFormat(formato)
        self._color_actual = color
        self._pintar_boton_color(color)

    def _pintar_boton_color(self, color):
        """Pinta el boton de color con el color actual, como muestra."""
        self.boton_color.setStyleSheet(
            "background-color: rgb({}, {}, {});".format(
                color.red(), color.green(), color.blue()
            )
        )

    def actualizar_desde_cursor(self):
        """Refleja en la barra el formato del texto donde esta el cursor.

        Los controles bloquean sus senales mientras se actualizan
        (blockSignals), para que marcar un boton no vuelva a aplicar el
        formato al cursor ni dispare un bucle de senales.
        """
        formato = self.editor.textCursor().charFormat()

        controles = (
            self.combo_tipografia,
            self.combo_tamano,
            self.boton_negrita,
            self.boton_cursiva,
            self.boton_subrayado,
        )
        estados = [control.blockSignals(True) for control in controles]
        try:
            familias = formato.fontFamilies()
            if familias:
                indice = self.combo_tipografia.findText(familias[0])
                if indice >= 0:
                    self.combo_tipografia.setCurrentIndex(indice)

            tamano_editor = formato.fontPointSize()
            if tamano_editor:
                # El combo muestra puntos PDF; el editor guarda puntos Qt
                tamano_pdf = tamano_editor_a_pdf(
                    tamano_editor, self.zoom, self.dpi_logica
                )
                self.combo_tamano.setCurrentIndex(self._indice_de_tamano(tamano_pdf))

            self.boton_negrita.setChecked(
                formato.fontWeight() >= int(QFont.Weight.Bold)
            )
            self.boton_cursiva.setChecked(formato.fontItalic())
            self.boton_subrayado.setChecked(formato.fontUnderline())

            color = formato.foreground().color()
            if color.isValid():
                self._color_actual = color
                self._pintar_boton_color(color)
        finally:
            for control, estado in zip(controles, estados):
                control.blockSignals(estado)

    def _indice_de_tamano(self, tamano):
        """Indice del tamano de la lista mas cercano al valor dado."""
        return min(range(len(TAMANOS)), key=lambda i: abs(TAMANOS[i] - tamano))


# =========================================================================
# DOCUMENTO DE QT -> LISTA DE FRAGMENTOS
# =========================================================================

def documento_a_fragmentos(documento_qt, zoom=None, dpi_logica=None):
    """Convierte el documento de un QTextEdit en la lista de fragmentos.

    Cada fragmento es un diccionario con las claves texto, familia,
    tamano, negrita, cursiva, subrayado y color (tupla rgb de 0 a 255),
    el mismo formato que consume formato_html.fragmentos_a_html. Entre
    bloques (parrafos) se agrega un "\\n" al final del ultimo fragmento
    del bloque, para que despues se convierta en <br>. Si un bloque esta
    vacio, se agrega un fragmento que solo contiene el "\\n".

    El editor guarda los tamanos en puntos de Qt, pero el HTML del PDF
    necesita puntos PDF: si se pasan `zoom` y `dpi_logica` (los del
    visor), cada tamano se convierte con tamano_editor_a_pdf. Si no se
    pasan, se copia tal cual (util en pruebas).
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
                if zoom is not None and dpi_logica is not None:
                    tamano = tamano_editor_a_pdf(tamano, zoom, dpi_logica)
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

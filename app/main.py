"""
Mi-Adobe-PDF - Fase 2 (v2): Scroll continuo + indicador de pagina visible.
============================================================================

Cambios respecto a la version anterior:
    - Ya no se ve una pagina a la vez con botones "siguiente/anterior".
      Ahora TODAS las paginas se muestran apiladas, una debajo de otra,
      y te desplazas con la rueda del mouse / la barra de scroll,
      igual que en Adobe Reader o cualquier lector normal.
    - Los botones "<- Pagina" / "Pagina ->" siguen existiendo, pero ahora
      lo que hacen es saltar el scroll directo a esa pagina.
    - Se agrego una etiqueta fija en la barra de herramientas que siempre
      dice "Pagina X de Y", actualizandose sola mientras haces scroll.
    - Las herramientas de anotacion (resaltar, subrayar, etc.) ahora saben
      sobre CUAL pagina especifica estas dibujando, sin importar cual sea
      la "pagina actual" mostrada en el indicador.
"""

import sys
import os
import bisect
import tempfile
import fitz  # PyMuPDF

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea, QToolBar, QFileDialog,
    QMessageBox, QComboBox, QInputDialog, QLineEdit, QRubberBand, QStatusBar,
    QWidget, QVBoxLayout, QDialog, QListWidget, QListWidgetItem, QPushButton,
    QHBoxLayout, QAbstractItemView, QTextEdit, QDoubleSpinBox, QCheckBox,
    QColorDialog, QFormLayout,
)
from PySide6.QtGui import (
    QPixmap, QImage, QAction, QIcon, QColor, QPainter, QPen, QFont,
    QTextCharFormat, QTextCursor,
)
from PySide6.QtCore import Qt, QRect, QSize, Signal, QTranslator, QLibraryInfo, QLocale, QPoint


# =========================================================================
# DIALOGO PARA REORDENAR PAGINAS (arrastrar y soltar)
# =========================================================================

class DialogoReordenarPaginas(QDialog):
    """
    Ventana emergente con una CUADRICULA de miniaturas, una por pagina
    (igual que el panel de paginas de Adobe Acrobat). El usuario arrastra
    las miniaturas para cambiar el orden. Al aceptar, se devuelve la
    nueva lista de indices de pagina (en el orden nuevo).
    """

    def __init__(self, documento, zoom_miniatura=0.25, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reordenar paginas (arrastra para mover)")
        self.resize(950, 700)

        layout_principal = QVBoxLayout(self)

        ayuda = QLabel(
            "Intenta arrastrar las miniaturas para moverlas. Si tu sistema no lo permite "
            "bien (a veces pasa en Linux), selecciona una miniatura con un clic y usa los "
            "botones de abajo para moverla."
        )
        ayuda.setWordWrap(True)
        layout_principal.addWidget(ayuda)

        self.lista = QListWidget()
        # --- Esto es lo que convierte la lista en una CUADRICULA tipo Acrobat ---
        self.lista.setViewMode(QListWidget.IconMode)   # miniaturas en vez de filas de texto
        self.lista.setFlow(QListWidget.LeftToRight)     # se acomodan de izquierda a derecha
        self.lista.setWrapping(True)                    # y saltan de renglon automaticamente
        self.lista.setResizeMode(QListWidget.Adjust)     # se reacomoda si cambias el tamano de la ventana
        self.lista.setMovement(QListWidget.Static)       # evita mover "libre" (eso no reordena); asi el arrastre SI reordena la lista
        self.lista.setDragDropMode(QAbstractItemView.InternalMove)
        self.lista.setDragEnabled(True)
        self.lista.setAcceptDrops(True)
        self.lista.setDropIndicatorShown(True)
        self.lista.setDefaultDropAction(Qt.MoveAction)
        self.lista.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lista.setSpacing(12)
        self.lista.setIconSize(QSize(130, 170))
        self.lista.setUniformItemSizes(True)
        layout_principal.addWidget(self.lista)

        matriz = fitz.Matrix(zoom_miniatura, zoom_miniatura)
        for numero, pagina in enumerate(documento):
            pix = pagina.get_pixmap(matrix=matriz)
            imagen_qt = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            miniatura = QPixmap.fromImage(imagen_qt)

            item = QListWidgetItem(QIcon(miniatura), str(numero + 1))
            item.setTextAlignment(Qt.AlignHCenter)
            item.setData(Qt.UserRole, numero)  # guardamos el indice ORIGINAL de esta pagina
            item.setFlags(item.flags() | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.lista.addItem(item)

        fila_botones = QHBoxLayout()
        boton_mover_izq = QPushButton("<-- Mover")
        boton_mover_der = QPushButton("Mover -->")
        boton_mover_izq.clicked.connect(self.mover_izquierda)
        boton_mover_der.clicked.connect(self.mover_derecha)
        fila_botones.addWidget(QLabel("Selecciona una miniatura (clic sobre ella) y muevela:"))
        fila_botones.addWidget(boton_mover_izq)
        fila_botones.addWidget(boton_mover_der)
        layout_principal.addLayout(fila_botones)

        fila_botones_finales = QHBoxLayout()
        boton_aceptar = QPushButton("Aplicar nuevo orden")
        boton_cancelar = QPushButton("Cancelar")
        boton_aceptar.clicked.connect(self.accept)
        boton_cancelar.clicked.connect(self.reject)
        fila_botones_finales.addWidget(boton_cancelar)
        fila_botones_finales.addWidget(boton_aceptar)
        layout_principal.addLayout(fila_botones_finales)

    def mover_izquierda(self):
        """Mueve la miniatura seleccionada una posicion antes en el orden."""
        fila = self.lista.currentRow()
        if fila > 0:
            item = self.lista.takeItem(fila)
            self.lista.insertItem(fila - 1, item)
            self.lista.setCurrentRow(fila - 1)

    def mover_derecha(self):
        """Mueve la miniatura seleccionada una posicion despues en el orden."""
        fila = self.lista.currentRow()
        if 0 <= fila < self.lista.count() - 1:
            item = self.lista.takeItem(fila)
            self.lista.insertItem(fila + 1, item)
            self.lista.setCurrentRow(fila + 1)

    def obtener_nuevo_orden(self):
        """Devuelve la lista de indices originales, en el orden final que quedo tras arrastrar."""
        return [self.lista.item(i).data(Qt.UserRole) for i in range(self.lista.count())]


# =========================================================================
# DIALOGO PARA POSICIONAR/REDIMENSIONAR UNA IMAGEN
# =========================================================================

class DialogoPosicionarImagen(QDialog):
    """
    Deja elegir DONDE va la imagen (posicion X/Y) y que TAMANO tiene
    (ancho/alto, en puntos del PDF), en vez de forzarla siempre dentro
    del cuadro exacto de la imagen que se esta reemplazando.
    """

    def __init__(self, x, y, ancho, alto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Posicion y tamano de la imagen")
        self.resize(320, 260)

        layout_principal = QVBoxLayout(self)
        formulario = QFormLayout()

        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(0, 5000)
        self.spin_x.setValue(x)
        formulario.addRow("Posicion X:", self.spin_x)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(0, 5000)
        self.spin_y.setValue(y)
        formulario.addRow("Posicion Y:", self.spin_y)

        self.spin_ancho = QDoubleSpinBox()
        self.spin_ancho.setRange(1, 5000)
        self.spin_ancho.setValue(ancho)
        formulario.addRow("Ancho:", self.spin_ancho)

        self.spin_alto = QDoubleSpinBox()
        self.spin_alto.setRange(1, 5000)
        self.spin_alto.setValue(alto)
        formulario.addRow("Alto:", self.spin_alto)

        self.check_proporcion = QCheckBox("Mantener proporcion original de la imagen")
        self.check_proporcion.setChecked(True)
        formulario.addRow(self.check_proporcion)

        layout_principal.addLayout(formulario)

        self.usar_clic = False
        boton_usar_clic = QPushButton("📍 Usar clic en la pagina (mas facil)")
        boton_usar_clic.clicked.connect(self.al_elegir_con_clic)
        layout_principal.addWidget(boton_usar_clic)

        ayuda = QLabel(
            "Tip: 'Posicion X/Y' es la esquina superior izquierda, medida "
            "desde la esquina superior izquierda de la pagina. Si no quieres "
            "calcular numeros, usa el boton de arriba y luego da clic en la "
            "pagina donde quieras la imagen."
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: #666; font-style: italic;")
        layout_principal.addWidget(ayuda)

        fila_botones = QHBoxLayout()
        boton_cancelar = QPushButton("Cancelar")
        boton_aceptar = QPushButton("Colocar imagen")
        boton_cancelar.clicked.connect(self.reject)
        boton_aceptar.clicked.connect(self.accept)
        fila_botones.addWidget(boton_cancelar)
        fila_botones.addWidget(boton_aceptar)
        layout_principal.addLayout(fila_botones)

    def al_elegir_con_clic(self):
        self.usar_clic = True
        self.accept()

    def obtener_valores(self):
        return {
            "x": self.spin_x.value(),
            "y": self.spin_y.value(),
            "ancho": self.spin_ancho.value(),
            "alto": self.spin_alto.value(),
            "mantener_proporcion": self.check_proporcion.isChecked(),
            "usar_clic": self.usar_clic,
        }


# =========================================================================
# DIALOGO PARA EDITAR UN "CUADRO DE TEXTO" (texto que ya existia en el PDF)
# =========================================================================

class DialogoEditarCuadroDeTexto(QDialog):
    """
    Ventana tipo "cuadro de texto" de Adobe Acrobat: muestra el texto del
    parrafo detectado y deja cambiar texto, tamano de letra, color,
    negrita, cursiva, y el ancho/alto del cuadro (en puntos del PDF).
    """

    def __init__(self, texto, tamano, color_rgb_0_255, negrita, cursiva, x, y, ancho, alto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar cuadro de texto")
        self.resize(480, 460)
        self.color_actual = QColor(*[int(c) for c in color_rgb_0_255])

        layout_principal = QVBoxLayout(self)

        layout_principal.addWidget(QLabel("Texto:"))
        self.caja_texto = QTextEdit()
        self.caja_texto.setPlainText(texto)
        layout_principal.addWidget(self.caja_texto)

        formulario = QFormLayout()

        self.spin_tamano = QDoubleSpinBox()
        self.spin_tamano.setRange(1, 300)
        self.spin_tamano.setValue(tamano)
        formulario.addRow("Tamano de letra:", self.spin_tamano)

        self.boton_color = QPushButton()
        self.actualizar_boton_color()
        self.boton_color.clicked.connect(self.elegir_color)
        formulario.addRow("Color del texto:", self.boton_color)

        fila_estilo = QHBoxLayout()
        self.check_negrita = QCheckBox("Negrita")
        self.check_negrita.setChecked(negrita)
        self.check_cursiva = QCheckBox("Cursiva")
        self.check_cursiva.setChecked(cursiva)
        fila_estilo.addWidget(self.check_negrita)
        fila_estilo.addWidget(self.check_cursiva)
        formulario.addRow("Estilo:", fila_estilo)

        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(0, 5000)
        self.spin_x.setValue(x)
        formulario.addRow("Posicion X:", self.spin_x)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(0, 5000)
        self.spin_y.setValue(y)
        formulario.addRow("Posicion Y:", self.spin_y)

        self.spin_ancho = QDoubleSpinBox()
        self.spin_ancho.setRange(10, 2000)
        self.spin_ancho.setValue(ancho)
        formulario.addRow("Ancho del cuadro (puntos):", self.spin_ancho)

        self.spin_alto = QDoubleSpinBox()
        self.spin_alto.setRange(10, 2000)
        self.spin_alto.setValue(alto)
        formulario.addRow("Alto del cuadro (puntos):", self.spin_alto)

        layout_principal.addLayout(formulario)

        self.usar_clic = False
        boton_usar_clic = QPushButton("📍 Usar clic en la pagina (mas facil)")
        boton_usar_clic.clicked.connect(self.al_elegir_con_clic)
        layout_principal.addWidget(boton_usar_clic)

        ayuda = QLabel(
            "Tip: si el texto no cabe en el cuadro, agranda el ancho/alto o "
            "reduce el tamano de letra. Si no quieres calcular la Posicion "
            "X/Y a mano, usa el boton de arriba y luego da clic en la pagina "
            "donde quieras que quede el texto."
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: #666; font-style: italic;")
        layout_principal.addWidget(ayuda)

        fila_botones = QHBoxLayout()
        boton_cancelar = QPushButton("Cancelar")
        boton_aceptar = QPushButton("Aplicar cambios")
        boton_cancelar.clicked.connect(self.reject)
        boton_aceptar.clicked.connect(self.accept)
        fila_botones.addWidget(boton_cancelar)
        fila_botones.addWidget(boton_aceptar)
        layout_principal.addLayout(fila_botones)

    def al_elegir_con_clic(self):
        self.usar_clic = True
        self.accept()

    def actualizar_boton_color(self):
        self.boton_color.setText(self.color_actual.name())
        self.boton_color.setStyleSheet(
            f"background-color: {self.color_actual.name()}; "
            f"color: {'white' if self.color_actual.lightness() < 128 else 'black'};"
        )

    def elegir_color(self):
        color_elegido = QColorDialog.getColor(self.color_actual, self, "Elige el color del texto")
        if color_elegido.isValid():
            self.color_actual = color_elegido
            self.actualizar_boton_color()

    def obtener_valores(self):
        return {
            "texto": self.caja_texto.toPlainText(),
            "tamano": self.spin_tamano.value(),
            "color": (self.color_actual.red(), self.color_actual.green(), self.color_actual.blue()),
            "negrita": self.check_negrita.isChecked(),
            "cursiva": self.check_cursiva.isChecked(),
            "x": self.spin_x.value(),
            "y": self.spin_y.value(),
            "ancho": self.spin_ancho.value(),
            "alto": self.spin_alto.value(),
            "usar_clic": self.usar_clic,
        }


ESPACIO_ENTRE_PAGINAS = 15  # pixeles de separacion visual entre una pagina y la siguiente


# =========================================================================
# EDITOR DE TEXTO EN LINEA (estilo Acrobat / Word directamente sobre la hoja)
# =========================================================================

class EditorTextoInline(QTextEdit):
    """
    Editor de texto que se superpone directamente sobre la pagina del PDF
    en el lugar exacto del parrafo seleccionado, con un recuadro azul punteado
    (estilo Adobe Acrobat DC). Permite escribir y editar como en Word.
    """
    aplicar_solicitado = Signal()
    cancelar_solicitado = Signal()

    def __init__(self, es_una_sola_linea=True, parent=None):
        super().__init__(parent)
        self.es_una_sola_linea = es_una_sola_linea
        self.setFrameShape(QTextEdit.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textChanged.connect(self.ajustar_tamano_al_contenido)

    def ajustar_tamano_al_contenido(self):
        doc_height = int(self.document().size().height()) + 8
        if doc_height > self.height():
            self.setFixedHeight(doc_height)

    def keyPressEvent(self, evento):
        # Escape: cancela y descarta cambios
        if evento.key() == Qt.Key_Escape:
            self.cancelar_solicitado.emit()
            return

        # Ctrl+Enter: aplica los cambios
        if (evento.modifiers() & Qt.ControlModifier) and evento.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.aplicar_solicitado.emit()
            return

        # Enter en linea simple (sin Shift): aplica los cambios
        if self.es_una_sola_linea and evento.key() in (Qt.Key_Return, Qt.Key_Enter) and not (evento.modifiers() & Qt.ShiftModifier):
            self.aplicar_solicitado.emit()
            return

        super().keyPressEvent(evento)


# =========================================================================
# ETIQUETA_PDF: una instancia por cada pagina dibujada en pantalla.
# =========================================================================

class EtiquetaPDF(QLabel):
    """
    Muestra UNA pagina del PDF y detecta clics/arrastres de mouse sobre ELLA
    para colocar anotaciones. Cada instancia "sabe" su propio numero de
    pagina (self.numero_pagina), asi que no importa que haya muchas
    paginas en pantalla a la vez: siempre se anota la correcta.

    Tambien puede guardar una copia "limpia" de su imagen (sin cuadros
    dibujados encima) para poder mostrar/quitar los recuadros de texto
    detectados sin tener que volver a leer el PDF cada vez.
    """

    # Envia: (numero_de_pagina, rectangulo_en_pixeles_de_esa_pagina)
    seleccion_lista = Signal(int, QRect)

    def __init__(self, numero_pagina: int):
        super().__init__()
        self.numero_pagina = numero_pagina
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.punto_inicio = None
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.pixmap_limpio = None  # se llena cada vez que se dibuja la pagina normalmente

    def mousePressEvent(self, evento):
        self.punto_inicio = evento.position().toPoint()
        self.rubber_band.setGeometry(QRect(self.punto_inicio, QSize()))
        self.rubber_band.show()

    def mouseMoveEvent(self, evento):
        if self.punto_inicio is not None:
            rect = QRect(self.punto_inicio, evento.position().toPoint()).normalized()
            self.rubber_band.setGeometry(rect)

    def mouseReleaseEvent(self, evento):
        if self.punto_inicio is not None:
            rect = QRect(self.punto_inicio, evento.position().toPoint()).normalized()
            self.rubber_band.hide()
            self.punto_inicio = None
            # Ya no exigimos un tamano minimo: un simple CLIC (sin arrastrar)
            # tambien cuenta, para poder dar clic directo sobre un recuadro
            # de texto ya detectado, sin tener que arrastrar nada.
            self.seleccion_lista.emit(self.numero_pagina, rect)


# =========================================================================
# VENTANA PRINCIPAL
# =========================================================================

class EditorPDF(QMainWindow):

    HERRAMIENTAS = [
        "Ninguna (solo ver)",
        "Resaltar",
        "Subrayar",
        "Tachar",
        "Texto libre",
        "Rectangulo",
        "Linea",
        "Circulo",
        "Firma (imagen)",
        "Editar contenido (texto e imagenes)",
    ]

    def __init__(self):
        super().__init__()

        self.documento = None
        self.ruta_actual = None
        self.ruta_firma = None          # ruta a la imagen de firma cargada por el usuario
        self.accion_pendiente_por_clic = None  # si no es None, el PROXIMO clic en la pagina ejecuta esto
        self.zoom = 1.5
        self.pagina_actual = 0          # pagina que se considera "visible" ahora mismo
        self.etiquetas_paginas = []      # lista de EtiquetaPDF, una por pagina
        self.offsets_top = []            # posicion vertical (en pixeles) donde empieza cada pagina
        self.edicion_inline_activa = None  # referencia a la edicion de texto en curso sobre la hoja
        self.color_edicion_actual = (0, 0, 0)  # color RGB del texto actual para la barra de formato

        self.setWindowTitle("Mi Adobe PDF - Fase 2")
        self.resize(1100, 850)

        # --- Contenedor vertical donde se apilan TODAS las paginas ---
        self.contenedor = QWidget()
        self.layout_paginas = QVBoxLayout(self.contenedor)
        self.layout_paginas.setAlignment(Qt.AlignHCenter)
        self.layout_paginas.setSpacing(ESPACIO_ENTRE_PAGINAS)

        self.area_scroll = QScrollArea()
        self.area_scroll.setWidget(self.contenedor)
        self.area_scroll.setWidgetResizable(True)
        self.area_scroll.verticalScrollBar().valueChanged.connect(self.al_hacer_scroll)
        self.setCentralWidget(self.area_scroll)

        self.setStatusBar(QStatusBar())
        self.crear_menu_archivo()
        self.crear_menus_y_barras()
        self.actualizar_ayuda()
        self.actualizar_indicador_pagina()

        self.contenedor.setLayout(self.layout_paginas)
        etiqueta_vacia = QLabel("Abre un PDF con el boton 'Abrir PDF'")
        etiqueta_vacia.setAlignment(Qt.AlignCenter)
        self.layout_paginas.addWidget(etiqueta_vacia)

    # ---------------------------------------------------------------
    # MENU SUPERIOR (Archivo, Paginas, Herramientas, Seguridad)
    # ---------------------------------------------------------------

    def crear_menu_archivo(self):
        menu_archivo = self.menuBar().addMenu("Archivo")

        self.agregar_a_menu(menu_archivo, "Abrir PDF...", self.abrir_pdf)
        menu_archivo.addSeparator()
        self.agregar_a_menu(menu_archivo, "Guardar", self.guardar)
        self.agregar_a_menu(menu_archivo, "Guardar como...", self.guardar_como)
        menu_archivo.addSeparator()
        self.agregar_a_menu(menu_archivo, "Convertir a Word (.docx)...", self.convertir_a_word)
        self.agregar_a_menu(menu_archivo, "Hacer PDF buscable (OCR)...", self.hacer_ocr)
        menu_archivo.addSeparator()
        self.agregar_a_menu(menu_archivo, "Cerrar documento", self.cerrar_documento)
        menu_archivo.addSeparator()
        self.agregar_a_menu(menu_archivo, "Salir del programa", self.close)

        menu_paginas = self.menuBar().addMenu("Paginas")
        self.agregar_a_menu(menu_paginas, "Rotar pagina actual", self.rotar_pagina)
        self.agregar_a_menu(menu_paginas, "Eliminar pagina actual", self.eliminar_pagina)
        self.agregar_a_menu(menu_paginas, "Insertar pagina en blanco", self.insertar_pagina_blanco)
        menu_paginas.addSeparator()
        self.agregar_a_menu(menu_paginas, "Reordenar paginas...", self.reordenar_paginas)

        menu_herramientas = self.menuBar().addMenu("Herramientas")
        self.agregar_a_menu(menu_herramientas, "Unir PDFs...", self.unir_pdfs)
        self.agregar_a_menu(menu_herramientas, "Dividir PDF...", self.dividir_pdf)
        self.agregar_a_menu(menu_herramientas, "Exportar a imagenes...", self.exportar_imagenes)
        self.agregar_a_menu(menu_herramientas, "Comprimir PDF...", self.comprimir_pdf)
        menu_herramientas.addSeparator()
        self.agregar_a_menu(menu_herramientas, "Cargar imagen de firma...", self.cargar_firma)

        menu_seguridad = self.menuBar().addMenu("Seguridad")
        self.agregar_a_menu(menu_seguridad, "Agregar contrasena...", self.agregar_contrasena)
        self.agregar_a_menu(menu_seguridad, "Quitar contrasena...", self.quitar_contrasena)

    def agregar_a_menu(self, menu, texto, funcion):
        accion = QAction(texto, self)
        accion.triggered.connect(funcion)
        menu.addAction(accion)
        return accion

    # ---------------------------------------------------------------
    # BARRA DE HERRAMIENTAS (solo lo de uso constante: zoom, pagina, herramienta activa)
    # ---------------------------------------------------------------

    def crear_menus_y_barras(self):
        barra = QToolBar("Principal")
        barra.setMovable(False)
        self.addToolBar(barra)

        # --- Indicador de pagina, SIEMPRE visible en la barra (se actualiza con el scroll) ---
        self.etiqueta_indicador = QLabel("  Pagina 0 de 0  ")
        self.etiqueta_indicador.setStyleSheet(
            "font-weight: bold; padding: 2px 8px; background: #e0e0e0; border-radius: 4px;"
        )
        barra.addWidget(self.etiqueta_indicador)

        self.agregar_boton(barra, "Zoom -", self.zoom_menos)
        self.agregar_boton(barra, "Zoom +", self.zoom_mas)
        barra.addSeparator()

        barra.addWidget(QLabel(" Herramienta: "))
        self.combo_herramienta = QComboBox()
        self.combo_herramienta.addItems(self.HERRAMIENTAS)
        self.combo_herramienta.currentTextChanged.connect(self.al_cambiar_herramienta)
        barra.addWidget(self.combo_herramienta)

        # --- Barra de herramientas de formato de texto (estilo Word / Acrobat) ---
        self.barra_formato = QToolBar("Formato de Texto")
        self.barra_formato.setMovable(False)
        self.addToolBar(self.barra_formato)

        lbl_formato = QLabel("  Formato: ")
        lbl_formato.setStyleSheet("font-weight: bold; color: #333;")
        self.barra_formato.addWidget(lbl_formato)

        self.barra_formato.addWidget(QLabel(" Tamaño: "))
        self.spin_tamano = QDoubleSpinBox()
        self.spin_tamano.setRange(4.0, 144.0)
        self.spin_tamano.setSingleStep(1.0)
        self.spin_tamano.setValue(12.0)
        self.spin_tamano.setDecimals(1)
        self.spin_tamano.valueChanged.connect(self.al_cambiar_tamano_inline)
        self.barra_formato.addWidget(self.spin_tamano)

        self.btn_negrita = QPushButton(" N ")
        self.btn_negrita.setCheckable(True)
        self.btn_negrita.setFocusPolicy(Qt.NoFocus)
        self.btn_negrita.setToolTip("Negrita")
        self.btn_negrita.setStyleSheet("font-weight: bold; min-width: 26px; padding: 2px 4px;")
        self.btn_negrita.toggled.connect(self.al_cambiar_estilo_inline)
        self.barra_formato.addWidget(self.btn_negrita)

        self.btn_cursiva = QPushButton(" K ")
        self.btn_cursiva.setCheckable(True)
        self.btn_cursiva.setFocusPolicy(Qt.NoFocus)
        self.btn_cursiva.setToolTip("Cursiva")
        self.btn_cursiva.setStyleSheet("font-style: italic; font-weight: bold; min-width: 26px; padding: 2px 4px;")
        self.btn_cursiva.toggled.connect(self.al_cambiar_estilo_inline)
        self.barra_formato.addWidget(self.btn_cursiva)

        self.barra_formato.addWidget(QLabel(" Color: "))
        self.btn_color_texto = QPushButton()
        self.btn_color_texto.setFixedSize(26, 22)
        self.btn_color_texto.setFocusPolicy(Qt.NoFocus)
        self.btn_color_texto.setToolTip("Color de texto")
        self.actualizar_muestra_color_boton()
        self.btn_color_texto.clicked.connect(self.elegir_color_inline)
        self.barra_formato.addWidget(self.btn_color_texto)

        self.barra_formato.addSeparator()

        self.btn_aplicar_inline = QPushButton(" ✔ Guardar texto ")
        self.btn_aplicar_inline.setFocusPolicy(Qt.NoFocus)
        self.btn_aplicar_inline.setToolTip("Guardar cambios en el PDF (Ctrl+Enter)")
        self.btn_aplicar_inline.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; padding: 3px 10px; border-radius: 3px;"
        )
        self.btn_aplicar_inline.clicked.connect(self.aplicar_edicion_inline)
        self.barra_formato.addWidget(self.btn_aplicar_inline)

        self.btn_cancelar_inline = QPushButton(" ✖ Cancelar ")
        self.btn_cancelar_inline.setFocusPolicy(Qt.NoFocus)
        self.btn_cancelar_inline.setToolTip("Descartar cambios (Esc)")
        self.btn_cancelar_inline.setStyleSheet(
            "background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;"
        )
        self.btn_cancelar_inline.clicked.connect(self.cancelar_edicion_inline)
        self.barra_formato.addWidget(self.btn_cancelar_inline)

        self.barra_formato.setVisible(False)

    def agregar_boton(self, barra, texto, funcion):
        accion = QAction(texto, self)
        accion.triggered.connect(funcion)
        barra.addAction(accion)
        return accion

    def al_cambiar_herramienta(self, herramienta_nueva):
        """Se dispara cada vez que el usuario cambia la herramienta del desplegable."""
        self.actualizar_ayuda()
        es_modo_edicion = (herramienta_nueva == "Editar contenido (texto e imagenes)")
        self.barra_formato.setVisible(es_modo_edicion)
        if not es_modo_edicion and self.edicion_inline_activa is not None:
            self.aplicar_edicion_inline()
        self.alternar_cajas_de_texto(es_modo_edicion)

    def al_cambiar_tamano_inline(self, nuevo_tamano):
        if self.edicion_inline_activa is None:
            return
        editor = self.edicion_inline_activa["widget"]
        cursor = editor.textCursor()

        fmt = QTextCharFormat()
        fmt.setFontPointSize(nuevo_tamano)

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            cursor_todo = editor.textCursor()
            cursor_todo.select(QTextCursor.Document)
            cursor_todo.mergeCharFormat(fmt)

        editor.setFocus()
        editor.ajustar_tamano_al_contenido()

    def al_cambiar_estilo_inline(self, _=None):
        if self.edicion_inline_activa is None:
            return
        editor = self.edicion_inline_activa["widget"]
        cursor = editor.textCursor()
        negrita = self.btn_negrita.isChecked()
        cursiva = self.btn_cursiva.isChecked()

        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if negrita else QFont.Normal)
        fmt.setFontItalic(cursiva)

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            cursor_todo = editor.textCursor()
            cursor_todo.select(QTextCursor.Document)
            cursor_todo.mergeCharFormat(fmt)

        editor.setFocus()
        editor.ajustar_tamano_al_contenido()

    def elegir_color_inline(self):
        color_previo = QColor(*self.color_edicion_actual)
        color_nuevo = QColorDialog.getColor(color_previo, self, "Elige el color del texto")
        if color_nuevo.isValid():
            self.color_edicion_actual = (color_nuevo.red(), color_nuevo.green(), color_nuevo.blue())
            self.actualizar_muestra_color_boton()
            if self.edicion_inline_activa is not None:
                editor = self.edicion_inline_activa["widget"]
                cursor = editor.textCursor()
                fmt = QTextCharFormat()
                fmt.setForeground(color_nuevo)
                if cursor.hasSelection():
                    cursor.mergeCharFormat(fmt)
                else:
                    cursor_todo = editor.textCursor()
                    cursor_todo.select(QTextCursor.Document)
                    cursor_todo.mergeCharFormat(fmt)
                editor.setFocus()

    def al_cambiar_posicion_cursor(self):
        """Sincroniza los controles de la barra de formato con la palabra/letra bajo el cursor."""
        if self.edicion_inline_activa is None:
            return
        editor = self.edicion_inline_activa["widget"]
        cursor = editor.textCursor()
        fmt = cursor.charFormat()

        es_negrita = (fmt.fontWeight() >= QFont.Bold or fmt.font().bold())
        es_cursiva = (fmt.fontItalic() or fmt.font().italic())

        self.btn_negrita.blockSignals(True)
        self.btn_negrita.setChecked(es_negrita)
        self.btn_negrita.blockSignals(False)

        self.btn_cursiva.blockSignals(True)
        self.btn_cursiva.setChecked(es_cursiva)
        self.btn_cursiva.blockSignals(False)

        if fmt.fontPointSize() > 0:
            self.spin_tamano.blockSignals(True)
            self.spin_tamano.setValue(fmt.fontPointSize())
            self.spin_tamano.blockSignals(False)

        col = fmt.foreground().color()
        if col.isValid():
            self.color_edicion_actual = (col.red(), col.green(), col.blue())
            self.actualizar_muestra_color_boton()

    def actualizar_muestra_color_boton(self):
        if hasattr(self, "btn_color_texto"):
            r, g, b = self.color_edicion_actual
            self.btn_color_texto.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b}); border: 1px solid #555; border-radius: 2px;"
            )

    def configurar_fuente_inicial_editor(self, editor, tamano, negrita, cursiva, color_rgb):
        fuente_base = QFont("Helvetica", pointSize=int(tamano))
        fuente_base.setBold(negrita)
        fuente_base.setItalic(cursiva)
        editor.document().setDefaultFont(fuente_base)

        cursor = editor.textCursor()
        cursor.select(QTextCursor.Document)
        fmt = QTextCharFormat()
        fmt.setFont(fuente_base)
        fmt.setFontPointSize(tamano)
        fmt.setFontWeight(QFont.Bold if negrita else QFont.Normal)
        fmt.setFontItalic(cursiva)
        fmt.setForeground(QColor(*color_rgb))
        cursor.mergeCharFormat(fmt)
        cursor.clearSelection()
        editor.setTextCursor(cursor)

    def actualizar_fuente_editor_inline(self, editor, tamano, negrita, cursiva, color_rgb):
        """
        Aplica al editor en linea recien creado la fuente del parrafo que se
        va a editar (tamano, negrita, cursiva y color), para que el texto se
        muestre igual que en el PDF mientras se escribe, y deja sincronizado
        el color que muestra el boton de la barra de formato.
        """
        self.color_edicion_actual = color_rgb
        self.actualizar_muestra_color_boton()
        self.configurar_fuente_inicial_editor(editor, tamano, negrita, cursiva, color_rgb)

    def actualizar_ayuda(self, *_):
        herramienta = self.combo_herramienta.currentText() if hasattr(self, "combo_herramienta") else "Ninguna (solo ver)"
        mensajes = {
            "Ninguna (solo ver)": "Modo lectura: solo estas viendo el PDF.",
            "Resaltar": "Arrastra el mouse sobre el texto que quieras resaltar en amarillo.",
            "Subrayar": "Arrastra el mouse sobre el texto que quieras subrayar.",
            "Tachar": "Arrastra el mouse sobre el texto que quieras tachar.",
            "Texto libre": "Arrastra un cuadro donde quieras escribir texto nuevo.",
            "Rectangulo": "Arrastra para dibujar un rectangulo.",
            "Linea": "Arrastra desde el inicio hasta el final de la linea.",
            "Circulo": "Arrastra para dibujar un circulo/ovalo.",
            "Firma (imagen)": "Arrastra un cuadro donde quieras colocar tu firma (cargala antes con 'Cargar firma...').",
            "Editar contenido (texto e imagenes)": "Da clic directamente sobre cualquier texto azul para editarlo en la hoja con la barra de formato.",
        }
        self.statusBar().showMessage(mensajes.get(herramienta, ""))

    def cargar_firma(self):
        """Elige la imagen (PNG/JPG) que se usara como firma en la herramienta 'Firma (imagen)'."""
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Selecciona la imagen de tu firma", "",
            "Imagenes (*.png *.jpg *.jpeg)"
        )
        if ruta:
            self.ruta_firma = ruta
            self.statusBar().showMessage(f"Firma cargada: {os.path.basename(ruta)}", 5000)
            QMessageBox.information(
                self, "Firma cargada",
                "Listo. Ahora elige la herramienta 'Firma (imagen)' en el desplegable "
                "y arrastra un cuadro sobre el documento donde quieras colocarla."
            )

    def actualizar_indicador_pagina(self):
        total = len(self.documento) if self.documento else 0
        actual = (self.pagina_actual + 1) if total else 0
        self.etiqueta_indicador.setText(f"  Pagina {actual} de {total}  ")

    # ---------------------------------------------------------------
    # ABRIR Y DIBUJAR TODAS LAS PAGINAS (scroll continuo)
    # ---------------------------------------------------------------

    def abrir_pdf(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un archivo PDF", "", "Archivos PDF (*.pdf)"
        )
        if not ruta_archivo:
            return
        try:
            documento = fitz.open(ruta_archivo)

            if documento.needs_pass:
                contrasena, ok = QInputDialog.getText(
                    self, "PDF protegido",
                    "Este PDF tiene contrasena. Escribela para abrirlo:",
                    QLineEdit.Password,
                )
                if not ok or not documento.authenticate(contrasena):
                    QMessageBox.critical(self, "Error", "Contrasena incorrecta o cancelada.")
                    return

            self.documento = documento
            self.ruta_actual = ruta_archivo
            self.pagina_actual = 0
            self.dibujar_todas_las_paginas()
        except Exception as error:
            QMessageBox.critical(self, "Error al abrir el archivo", str(error))

    def dibujar_todas_las_paginas(self):
        """Borra lo que hubiera dibujado y vuelve a crear una EtiquetaPDF por cada pagina."""

        # Limpiar el contenedor
        while self.layout_paginas.count():
            item = self.layout_paginas.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.etiquetas_paginas = []
        self.offsets_top = []

        if self.documento is None or len(self.documento) == 0:
            return

        matriz_zoom = fitz.Matrix(self.zoom, self.zoom)
        posicion_y = 0

        for numero, pagina in enumerate(self.documento):
            try:
                pixmap_fitz = pagina.get_pixmap(matrix=matriz_zoom)
                imagen_qt = QImage(
                    pixmap_fitz.samples, pixmap_fitz.width, pixmap_fitz.height,
                    pixmap_fitz.stride, QImage.Format_RGB888,
                )
                pixmap_qt = QPixmap.fromImage(imagen_qt)

                etiqueta = EtiquetaPDF(numero)
                etiqueta.setPixmap(pixmap_qt)
                etiqueta.pixmap_limpio = pixmap_qt
                etiqueta.setFixedSize(pixmap_qt.size())
                etiqueta.seleccion_lista.connect(self.al_seleccionar_rectangulo)

                self.layout_paginas.addWidget(etiqueta)
                self.etiquetas_paginas.append(etiqueta)
                self.offsets_top.append(posicion_y)
                posicion_y += pixmap_qt.height() + ESPACIO_ENTRE_PAGINAS
            except Exception as error:
                # Si ESTA pagina en particular tiene algo corrupto/raro en el PDF,
                # no tumbamos todo el programa: mostramos un aviso solo en su lugar
                # y seguimos dibujando el resto de las paginas con normalidad.
                etiqueta_error = QLabel(
                    f"No se pudo dibujar la pagina {numero + 1}\n(el PDF tiene algo "
                    f"dañado en esta pagina)\n\nDetalle: {error}"
                )
                etiqueta_error.setAlignment(Qt.AlignCenter)
                etiqueta_error.setStyleSheet(
                    "background: #fff3cd; border: 1px solid #ffc107; padding: 20px;"
                )
                etiqueta_error.setFixedSize(400, 150)
                self.layout_paginas.addWidget(etiqueta_error)
                self.etiquetas_paginas.append(None)  # ocupa el lugar, pero no es una pagina real
                self.offsets_top.append(posicion_y)
                posicion_y += 150 + ESPACIO_ENTRE_PAGINAS

        self.pagina_actual = max(0, min(self.pagina_actual, len(self.documento) - 1))
        self.actualizar_indicador_pagina()
        self.setWindowTitle(f"Mi Adobe PDF - {len(self.documento)} paginas")

        # Si el usuario ya tenia activa la herramienta de editar texto,
        # dibujamos de una vez los recuadros sobre las paginas nuevas.
        if hasattr(self, "combo_herramienta") and self.combo_herramienta.currentText() == "Editar contenido (texto e imagenes)":
            self.alternar_cajas_de_texto(True)

    def al_hacer_scroll(self, valor_scroll):
        """Se dispara cada vez que el usuario mueve la barra de scroll (o hace scroll con la rueda)."""
        if not self.offsets_top:
            return
        # bisect encuentra, de forma eficiente, cual es la ultima pagina
        # cuyo offset_top es menor o igual al scroll actual = la pagina visible arriba.
        indice = bisect.bisect_right(self.offsets_top, valor_scroll) - 1
        indice = max(0, min(indice, len(self.offsets_top) - 1))
        if indice != self.pagina_actual:
            self.pagina_actual = indice
            self.actualizar_indicador_pagina()

    def ir_a_pagina(self, numero_pagina):
        if not self.offsets_top:
            return
        numero_pagina = max(0, min(numero_pagina, len(self.offsets_top) - 1))
        self.area_scroll.verticalScrollBar().setValue(self.offsets_top[numero_pagina])
        self.pagina_actual = numero_pagina
        self.actualizar_indicador_pagina()

    def zoom_mas(self):
        if self.edicion_inline_activa is not None:
            self.aplicar_edicion_inline()
        self.zoom += 0.2
        self.dibujar_todas_las_paginas()
        self.ir_a_pagina(self.pagina_actual)

    def zoom_menos(self):
        if self.zoom > 0.4:
            if self.edicion_inline_activa is not None:
                self.aplicar_edicion_inline()
            self.zoom -= 0.2
            self.dibujar_todas_las_paginas()
            self.ir_a_pagina(self.pagina_actual)

    # ---------------------------------------------------------------
    # ANOTACIONES
    # ---------------------------------------------------------------

    def al_seleccionar_rectangulo(self, numero_pagina: int, rect_pixeles: QRect):
        if self.documento is None:
            return

        # Si habia una edicion de texto inline activa y el usuario da clic en la hoja,
        # guardamos los cambios de esa edicion antes de procesar el nuevo clic.
        if self.edicion_inline_activa is not None:
            self.aplicar_edicion_inline()

        x0 = rect_pixeles.left() / self.zoom
        y0 = rect_pixeles.top() / self.zoom
        x1 = rect_pixeles.right() / self.zoom
        y1 = rect_pixeles.bottom() / self.zoom
        rect_pdf = fitz.Rect(x0, y0, x1, y1)

        # Si hay una accion esperando a que el usuario de clic en la pagina
        # (por ejemplo, "elige donde poner la imagen"), este es ESE clic:
        # ejecutamos la accion pendiente y no seguimos con el flujo normal.
        if self.accion_pendiente_por_clic is not None:
            accion = self.accion_pendiente_por_clic
            self.accion_pendiente_por_clic = None
            self.statusBar().clearMessage()
            accion(numero_pagina, rect_pdf.tl)
            return

        herramienta = self.combo_herramienta.currentText()
        if herramienta == "Ninguna (solo ver)":
            return

        pagina = self.documento[numero_pagina]

        try:
            if herramienta == "Resaltar":
                pagina.add_highlight_annot(rect_pdf)
            elif herramienta == "Subrayar":
                pagina.add_underline_annot(rect_pdf)
            elif herramienta == "Tachar":
                pagina.add_strikeout_annot(rect_pdf)
            elif herramienta == "Rectangulo":
                pagina.add_rect_annot(rect_pdf)
            elif herramienta == "Circulo":
                pagina.add_circle_annot(rect_pdf)
            elif herramienta == "Linea":
                pagina.add_line_annot(rect_pdf.top_left, rect_pdf.bottom_right)
            elif herramienta == "Texto libre":
                texto, ok = QInputDialog.getText(self, "Texto libre", "Escribe el texto:")
                if ok and texto:
                    pagina.add_freetext_annot(rect_pdf, texto, fontsize=12)
            elif herramienta == "Firma (imagen)":
                if not self.ruta_firma:
                    QMessageBox.information(
                        self, "Falta cargar la firma",
                        "Primero dale clic a 'Cargar firma...' y elige tu imagen."
                    )
                    return
                pagina.insert_image(rect_pdf, filename=self.ruta_firma)
            elif herramienta == "Editar contenido (texto e imagenes)":
                self.editar_contenido_en_punto(pagina, rect_pdf)
                return

            # Solo hace falta re-dibujar la pagina afectada, no todas (mas rapido)
            self.redibujar_pagina_individual(numero_pagina)

            # Si seguimos en modo "Editar contenido (texto e imagenes)", refrescamos los
            # recuadros azules de ESA pagina (las posiciones pudieron cambiar).
            if herramienta == "Editar contenido (texto e imagenes)":
                etiqueta = self.etiquetas_paginas[numero_pagina]
                if etiqueta is not None and etiqueta.pixmap_limpio is not None:
                    parrafos = self.obtener_todos_los_parrafos(pagina)
                    imagenes = self.obtener_todas_las_imagenes(pagina)
                    formas = self.obtener_formas_de_color(pagina)
                    etiqueta.setPixmap(self.dibujar_cajas_de_texto(etiqueta.pixmap_limpio, parrafos, imagenes, formas))
        except Exception as error:
            QMessageBox.critical(self, "No se pudo agregar la anotacion", str(error))

    def redibujar_pagina_individual(self, numero_pagina):
        if self.documento is None:
            return
        etiqueta_objetivo = self.etiquetas_paginas[numero_pagina]
        if etiqueta_objetivo is None:
            return  # esta pagina tuvo un error al dibujarse originalmente, no hay donde redibujar
        try:
            pagina = self.documento[numero_pagina]
            matriz_zoom = fitz.Matrix(self.zoom, self.zoom)
            pixmap_fitz = pagina.get_pixmap(matrix=matriz_zoom)
            imagen_qt = QImage(
                pixmap_fitz.samples, pixmap_fitz.width, pixmap_fitz.height,
                pixmap_fitz.stride, QImage.Format_RGB888,
            )
            pixmap_qt = QPixmap.fromImage(imagen_qt)
            etiqueta_objetivo.pixmap_limpio = pixmap_qt
            etiqueta_objetivo.setPixmap(pixmap_qt)
        except Exception as error:
            QMessageBox.warning(self, "No se pudo actualizar la vista", str(error))

    # ---------------------------------------------------------------
    # PAGINAS (rotar/eliminar/insertar actuan sobre self.pagina_actual,
    # la que este marcada en el indicador en ese momento)
    # ---------------------------------------------------------------

    def obtener_lineas_de_pagina(self, pagina):
        """Devuelve TODAS las lineas de texto de la pagina, ordenadas de arriba a abajo."""
        info = pagina.get_text("dict")
        lineas = []
        for bloque in info.get("blocks", []):
            if bloque.get("type") != 0:
                continue
            for linea in bloque.get("lines", []):
                texto = "".join(span["text"] for span in linea["spans"])
                if not texto.strip():
                    continue
                primer_span = linea["spans"][0]
                lineas.append({
                    "bbox": fitz.Rect(linea["bbox"]),
                    "texto": texto,
                    "size": primer_span["size"],
                    "color": primer_span["color"],
                    "font": primer_span.get("font", ""),
                    "origen": primer_span.get("origin"),  # punto EXACTO de la linea base original
                })
        lineas.sort(key=lambda l: l["bbox"].y0)
        return lineas

    # IMPORTANTE: este numero decide cuando dos lineas pegadas se consideran
    # "el mismo parrafo" vs "parrafos distintos". Se ajusto usando documentos
    # reales: un espacio normal ENTRE lineas de un mismo parrafo es muy chico
    # (2-3 puntos); el espacio ENTRE parrafos distintos suele ser bastante
    # mayor (8+ puntos). 0.5 veces la altura de la linea separa bien ambos casos
    # en la mayoria de documentos (Word, Canva, InDesign).
    # IMPORTANTE: estos ajustes deciden cuando dos lineas pegadas se consideran
    # "el mismo parrafo" vs "parrafos distintos".
    #
    # Aprendizaje real (con documentos reales del usuario): el ESPACIADO entre
    # lineas casi nunca sirve para detectar el fin de un parrafo, porque muchos
    # documentos (Word, InDesign) usan el MISMO interlineado entre parrafos que
    # dentro de un parrafo (sin renglon en blanco de por medio).
    #
    # La senal que SI funciona: en un parrafo normal, todas las lineas llegan
    # casi hasta el mismo margen derecho ("linea llena"), EXCEPTO la ULTIMA
    # linea del parrafo, que termina antes porque ahi se acaba el texto.
    # Por eso: si la linea anterior NO llego a su margen derecho tipico,
    # asumimos que ahi terminaba un parrafo, y la siguiente linea (aunque
    # tenga el mismo tamano/margen izquierdo) empieza uno nuevo.
    TOLERANCIA_MARGEN_IZQUIERDO = 40
    TOLERANCIA_MARGEN_DERECHO = 20
    MULTIPLICADOR_ESPACIO_MAXIMO = 1.8  # si el hueco es MUCHO mayor a una linea, sin duda es otro parrafo

    # Ancho minimo (en puntos) para que una linea pueda considerarse parte de
    # un PARRAFO que sigue en la siguiente linea. Evita el error de mezclar
    # etiquetas cortas sueltas (ej. "Terminado", "Pantalla" en una ficha
    # tecnica) que por casualidad comparten tamano/margen y estan cerca,
    # pero NO son continuacion la una de la otra.
    ANCHO_MINIMO_PARA_CONTINUAR = 120

    def lineas_son_compatibles(self, a, b):
        mismo_tamano = abs(a["size"] - b["size"]) < 1.0
        mismo_margen = abs(a["bbox"].x0 - b["bbox"].x0) < self.TOLERANCIA_MARGEN_IZQUIERDO
        return mismo_tamano and mismo_margen

    def combinar_lineas_en_parrafo(self, lineas_del_grupo):
        seleccionadas = sorted(lineas_del_grupo, key=lambda l: l["bbox"].y0)
        bbox_total = seleccionadas[0]["bbox"]
        for l in seleccionadas[1:]:
            bbox_total |= l["bbox"]
        return {
            "bbox": bbox_total,
            "texto": " ".join(l["texto"] for l in seleccionadas),
            "size": seleccionadas[0]["size"],
            "color": seleccionadas[0]["color"],
            "font": seleccionadas[0]["font"],
            "num_lineas": len(seleccionadas),
            "origen": seleccionadas[0]["origen"],  # solo se usa si num_lineas == 1
        }

    def obtener_todos_los_parrafos(self, pagina):
        """
        Recorre TODA la pagina de arriba a abajo y arma la lista de parrafos,
        uniendo lineas consecutivas mientras: tengan el mismo tamano/margen
        izquierdo, el espacio entre ellas sea normal, Y la linea anterior haya
        llegado hasta su margen derecho tipico (si no llego, ahi termino un parrafo).
        """
        lineas = self.obtener_lineas_de_pagina(pagina)
        if not lineas:
            return []

        grupos = [[lineas[0]]]
        ancho_tipico_grupo = lineas[0]["bbox"].x1

        for anterior, actual in zip(lineas, lineas[1:]):
            espacio = actual["bbox"].y0 - anterior["bbox"].y1
            espacio_normal = espacio < anterior["bbox"].height * self.MULTIPLICADOR_ESPACIO_MAXIMO
            linea_anterior_llego_al_margen = (
                ancho_tipico_grupo - anterior["bbox"].x1
            ) < self.TOLERANCIA_MARGEN_DERECHO
            # La linea anterior debe ser "larga" de verdad para confiar en que
            # es texto corrido (evita mezclar etiquetas cortas sueltas).
            linea_anterior_es_larga = anterior["bbox"].width >= self.ANCHO_MINIMO_PARA_CONTINUAR

            if (
                self.lineas_son_compatibles(anterior, actual)
                and espacio_normal
                and linea_anterior_llego_al_margen
                and linea_anterior_es_larga
            ):
                grupos[-1].append(actual)
                ancho_tipico_grupo = max(ancho_tipico_grupo, actual["bbox"].x1)
            else:
                grupos.append([actual])
                ancho_tipico_grupo = actual["bbox"].x1

        return [self.combinar_lineas_en_parrafo(grupo) for grupo in grupos]

    def encontrar_parrafo_en_punto(self, pagina, punto):
        """Encuentra, dentro de todos los parrafos de la pagina, el que contiene ese punto."""
        for parrafo in self.obtener_todos_los_parrafos(pagina):
            bbox = parrafo["bbox"]
            if bbox.x0 - 2 <= punto.x <= bbox.x1 + 2 and bbox.y0 - 2 <= punto.y <= bbox.y1 + 2:
                return parrafo
        return None

    def obtener_todas_las_imagenes(self, pagina):
        """Devuelve una lista de {'bbox': fitz.Rect, 'xref': int} por cada imagen de la pagina."""
        imagenes = []
        for info in pagina.get_image_info(xrefs=True):
            if info.get("xref"):  # 0 significa que no se pudo identificar el objeto
                imagenes.append({"bbox": fitz.Rect(info["bbox"]), "xref": info["xref"]})
        return imagenes

    # Una pagina puede tener CIENTOS de formas vectoriales chiquitas (las
    # lineas de una grafica, por ejemplo). Solo nos interesan los RELLENOS
    # DE COLOR grandes (banners, fondos), no cada segmento de linea suelto.
    ANCHO_MINIMO_FORMA = 15
    ALTO_MINIMO_FORMA = 15

    def obtener_formas_de_color(self, pagina):
        """
        Devuelve los RECTANGULOS DE COLOR (rellenos solidos, sin contar lineas
        ni bordes) que sean lo bastante grandes como para ser un "banner" o
        "fondo" editable de verdad, con su color de relleno actual.
        """
        formas = []
        for dibujo in pagina.get_drawings():
            if dibujo.get("type") != "f" or dibujo.get("fill") is None:
                continue
            rect = fitz.Rect(dibujo["rect"])
            if rect.width >= self.ANCHO_MINIMO_FORMA and rect.height >= self.ALTO_MINIMO_FORMA:
                formas.append({"bbox": rect, "color": dibujo["fill"]})
        return formas

    def dibujar_cajas_de_texto(self, pixmap_base, parrafos, imagenes=None, formas=None):
        """
        Devuelve una COPIA del pixmap con un recuadro AZUL alrededor de cada
        parrafo de texto, VERDE alrededor de cada imagen, y NARANJA alrededor
        de cada forma/rectangulo de color grande (banners, fondos) - igual
        que el modo "Editar PDF" de Acrobat marca cada elemento seleccionable.
        """
        resultado = QPixmap(pixmap_base)
        pintor = QPainter(resultado)

        if formas:
            lapiz_forma = QPen(QColor(255, 127, 39))  # naranja
            lapiz_forma.setWidth(2)
            pintor.setPen(lapiz_forma)
            for forma in formas:
                bbox = forma["bbox"]
                rect_pixeles = QRect(
                    int(bbox.x0 * self.zoom), int(bbox.y0 * self.zoom),
                    int(bbox.width * self.zoom), int(bbox.height * self.zoom),
                )
                pintor.drawRect(rect_pixeles)

        lapiz_texto = QPen(QColor(30, 144, 255))  # azul
        lapiz_texto.setWidth(2)
        pintor.setPen(lapiz_texto)
        for parrafo in parrafos:
            bbox = parrafo["bbox"]
            rect_pixeles = QRect(
                int(bbox.x0 * self.zoom), int(bbox.y0 * self.zoom),
                int(bbox.width * self.zoom), int(bbox.height * self.zoom),
            )
            pintor.drawRect(rect_pixeles)

        if imagenes:
            lapiz_imagen = QPen(QColor(34, 177, 76))  # verde
            lapiz_imagen.setWidth(2)
            pintor.setPen(lapiz_imagen)
            for imagen in imagenes:
                bbox = imagen["bbox"]
                rect_pixeles = QRect(
                    int(bbox.x0 * self.zoom), int(bbox.y0 * self.zoom),
                    int(bbox.width * self.zoom), int(bbox.height * self.zoom),
                )
                pintor.drawRect(rect_pixeles)

        pintor.end()
        return resultado

    def alternar_cajas_de_texto(self, activar):
        """
        Se llama cuando el usuario elige (o deja de elegir) la herramienta
        "Editar contenido (texto e imagenes)". Si se activa, dibuja
        automaticamente un recuadro azul sobre cada parrafo de texto, uno
        verde sobre cada imagen, y uno naranja sobre cada forma/banner de
        color, en todas las paginas visibles. Si se desactiva, regresa las
        paginas a su vista normal.
        """
        if self.documento is None:
            return
        for numero, etiqueta in enumerate(self.etiquetas_paginas):
            if etiqueta is None or etiqueta.pixmap_limpio is None:
                continue
            if activar:
                pagina = self.documento[numero]
                parrafos = self.obtener_todos_los_parrafos(pagina)
                imagenes = self.obtener_todas_las_imagenes(pagina)
                formas = self.obtener_formas_de_color(pagina)
                etiqueta.setPixmap(self.dibujar_cajas_de_texto(etiqueta.pixmap_limpio, parrafos, imagenes, formas))
            else:
                etiqueta.setPixmap(etiqueta.pixmap_limpio)

    def muestrear_color_de_fondo(self, pagina, bbox):
        """
        En vez de asumir que el fondo detras del texto siempre es blanco
        (que rompia titulos con fondo de color, como banners azules),
        tomamos una "foto" chiquita justo a los lados del texto y leemos
        de que color es el fondo ahi de verdad.
        """
        try:
            margen = 6
            clip = fitz.Rect(
                max(0, bbox.x0 - margen), bbox.y0,
                min(pagina.rect.width, bbox.x1 + margen), bbox.y1,
            )
            if clip.width <= 0 or clip.height <= 0:
                return (1, 1, 1)
            pix = pagina.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
            y_medio = max(0, min(pix.height - 1, pix.height // 2))
            color_izquierda = pix.pixel(1, y_medio)
            color_derecha = pix.pixel(max(0, pix.width - 2), y_medio)

            # Nos quedamos con el que este MAS LEJOS de blanco puro, porque
            # si uno de los dos lados cayo fuera del banner/fondo de color
            # (por accidente) va a salir blanco y no nos sirve.
            def distancia_a_blanco(c):
                return sum(255 - v for v in c[:3])

            elegido = color_izquierda if distancia_a_blanco(color_izquierda) >= distancia_a_blanco(color_derecha) else color_derecha
            return tuple(v / 255 for v in elegido[:3])
        except Exception:
            return (1, 1, 1)  # si algo falla, blanco es el valor seguro de siempre

    def texto_cabe_en_cuadro(self, texto, rect, tamano, fuente):
        """
        Prueba si un texto cabe en un rectangulo dado, con cierto tamano y
        fuente, PERO haciendolo en un documento PDF temporal descartable,
        para no arriesgar el documento real del usuario. Devuelve True/False.
        """
        documento_prueba = fitz.open()
        try:
            pagina_prueba = documento_prueba.new_page(
                width=max(rect.width, 10) + 20, height=max(rect.height, 10) + 20
            )
            rect_prueba = fitz.Rect(0, 0, rect.width, rect.height)
            resultado = pagina_prueba.insert_textbox(
                rect_prueba, texto, fontsize=tamano, fontname=fuente, align=0,
            )
            return resultado >= 0
        finally:
            documento_prueba.close()

    def calcular_espacio_disponible_vertical(self, pagina, bbox_objetivo):
        """
        Mide cuanto espacio libre hay ARRIBA y ABAJO de un bbox, antes de
        chocar con la linea de texto mas cercana en esa direccion (que no
        sea parte del propio parrafo). Sirve para nunca invadir texto vecino
        al agregar margen de seguridad.
        """
        espacio_arriba = None
        espacio_abajo = None
        for linea in self.obtener_lineas_de_pagina(pagina):
            b = linea["bbox"]
            if b.y1 <= bbox_objetivo.y0 + 0.5:
                hueco = bbox_objetivo.y0 - b.y1
                if espacio_arriba is None or hueco < espacio_arriba:
                    espacio_arriba = hueco
            elif b.y0 >= bbox_objetivo.y1 - 0.5:
                hueco = b.y0 - bbox_objetivo.y1
                if espacio_abajo is None or hueco < espacio_abajo:
                    espacio_abajo = hueco
        return espacio_arriba, espacio_abajo

    def editar_contenido_en_punto(self, pagina, rect_pdf):
        """
        Punto de entrada unico para la herramienta "Editar contenido": decide
        si el clic cayo sobre una IMAGEN, un PARRAFO DE TEXTO, o una FORMA/
        BANNER DE COLOR, y manda a la funcion correspondiente. Asi el usuario
        no tiene que elegir un modo distinto para cada cosa, como en Acrobat.
        """
        punto = rect_pdf.tl + (rect_pdf.br - rect_pdf.tl) * 0.5

        for imagen in self.obtener_todas_las_imagenes(pagina):
            if imagen["bbox"].contains(punto):
                self.editar_imagen(pagina, imagen)
                return

        parrafo = self.encontrar_parrafo_en_punto(pagina, punto)
        if parrafo is not None:
            self.editar_parrafo_encontrado(pagina, parrafo, punto_clic=punto)
            return

        for forma in self.obtener_formas_de_color(pagina):
            if forma["bbox"].contains(punto):
                self.editar_forma(pagina, forma)
                return

        QMessageBox.information(
            self, "No se encontro nada editable ahi",
            "Ahi no hay texto, imagen, ni forma de color detectados (fijate "
            "en los recuadros: AZUL=texto, VERDE=imagen, NARANJA=forma de "
            "color; da clic DENTRO de alguno).\n\n"
            "(Si el PDF es una imagen escaneada, primero usa Archivo -> "
            "Hacer PDF buscable (OCR), y guarda ese resultado antes de editarlo)."
        )

    def editar_forma(self, pagina, forma):
        """
        Cambia el color de relleno de una forma/banner, PRESERVANDO cualquier
        texto que estuviera dibujado encima (se guarda antes de borrar, y se
        vuelve a escribir despues, en su mismo lugar exacto).
        """
        bbox = forma["bbox"]
        color_actual = QColor(*[int(c * 255) for c in forma["color"]])

        color_nuevo = QColorDialog.getColor(color_actual, self, "Elige el nuevo color de la forma")
        if not color_nuevo.isValid():
            return

        try:
            # Guardamos cualquier texto que este ENCIMA de esta forma, para
            # poder volver a escribirlo despues (si no, se perderia).
            texto_encima = [
                linea for linea in self.obtener_lineas_de_pagina(pagina)
                if bbox.intersects(linea["bbox"])
            ]

            color_normalizado = (color_nuevo.redF(), color_nuevo.greenF(), color_nuevo.blueF())
            pagina.add_redact_annot(bbox, fill=color_normalizado)
            pagina.apply_redactions()
            pagina.clean_contents()  # evita referencias colgando tras editar

            for linea in texto_encima:
                codigo_color = linea["color"]
                color_texto = (
                    ((codigo_color >> 16) & 255) / 255,
                    ((codigo_color >> 8) & 255) / 255,
                    (codigo_color & 255) / 255,
                )
                nombre_fuente = linea["font"].lower()
                if "bold" in nombre_fuente and ("italic" in nombre_fuente or "oblique" in nombre_fuente):
                    fuente = "hebi"
                elif "bold" in nombre_fuente:
                    fuente = "hebo"
                elif "italic" in nombre_fuente or "oblique" in nombre_fuente:
                    fuente = "heit"
                else:
                    fuente = "helv"
                pagina.insert_text(
                    linea["origen"], linea["texto"], fontsize=linea["size"],
                    fontname=fuente, color=color_texto,
                )
        except Exception as error:
            QMessageBox.critical(self, "Error al cambiar el color", str(error))

    def editar_parrafo_encontrado(self, pagina, parrafo, punto_clic=None):
        """
        Inicia la edicion DIRECTA sobre la hoja (inline) para el parrafo detectado,
        colocando un editor estilo Acrobat/Word con recuadro azul sobre el PDF.

        punto_clic: coordenada (en puntos del PDF) dentro del parrafo donde el
        usuario hizo clic. Hoy solo se recibe y se guarda por si en el futuro
        queremos colocar el cursor del editor en esa posicion exacta.
        """
        numero_pagina = pagina.number
        if numero_pagina >= len(self.etiquetas_paginas):
            return

        etiqueta = self.etiquetas_paginas[numero_pagina]
        if etiqueta is None:
            return

        # Si ya habia una edicion activa previa, guardamos sus cambios primero
        if self.edicion_inline_activa is not None:
            self.aplicar_edicion_inline()

        bbox_detectado = parrafo["bbox"]
        es_una_sola_linea = parrafo["num_lineas"] == 1

        # Coordenadas en pixeles directamente sobre la EtiquetaPDF
        x_px = max(0, int(bbox_detectado.x0 * self.zoom) - 4)
        y_px = max(0, int(bbox_detectado.y0 * self.zoom) - 3)
        w_px = max(int(bbox_detectado.width * self.zoom) + 16, 90)
        h_px = max(int(bbox_detectado.height * self.zoom) + 6, 26)

        texto_actual = parrafo["texto"]
        tamano_actual = parrafo["size"]
        codigo_color = parrafo["color"]
        color_actual = (
            (codigo_color >> 16) & 255, (codigo_color >> 8) & 255, codigo_color & 255,
        )
        nombre_fuente = parrafo["font"].lower()
        negrita_actual = "bold" in nombre_fuente
        cursiva_actual = "italic" in nombre_fuente or "oblique" in nombre_fuente

        # Actualizamos la barra de formato superior
        self.spin_tamano.blockSignals(True)
        self.spin_tamano.setValue(tamano_actual)
        self.spin_tamano.blockSignals(False)

        self.btn_negrita.blockSignals(True)
        self.btn_negrita.setChecked(negrita_actual)
        self.btn_negrita.blockSignals(False)

        self.btn_cursiva.blockSignals(True)
        self.btn_cursiva.setChecked(cursiva_actual)
        self.btn_cursiva.blockSignals(False)

        self.color_edicion_actual = color_actual
        self.actualizar_muestra_color_boton()

        # Creamos el editor de texto superpuesto en la hoja
        editor = EditorTextoInline(es_una_sola_linea=es_una_sola_linea, parent=etiqueta)
        editor.setGeometry(x_px, y_px, w_px, h_px)
        editor.setPlainText(texto_actual)
        self.actualizar_fuente_editor_inline(editor, tamano_actual, negrita_actual, cursiva_actual, color_actual)

        editor.aplicar_solicitado.connect(self.aplicar_edicion_inline)
        editor.cancelar_solicitado.connect(self.cancelar_edicion_inline)

        self.edicion_inline_activa = {
            "numero_pagina": numero_pagina,
            "pagina": pagina,
            "parrafo": parrafo,
            "widget": editor,
            "texto_original": texto_actual,
            "tamano_original": tamano_actual,
            "negrita_original": negrita_actual,
            "cursiva_original": cursiva_actual,
            "color_original": color_actual,
            "es_una_sola_linea": es_una_sola_linea,
            "bbox": bbox_detectado,
        }

        editor.show()
        editor.setFocus()
        editor.selectAll()
        self.statusBar().showMessage(
            "Edita el texto directamente en la hoja. Usa la barra superior para cambiar formato y presiona '✔ Guardar texto' (o Ctrl+Enter)."
        )

    def aplicar_edicion_inline(self):
        """Aplica la edicion de texto activa directamente sobre el documento PDF."""
        if self.edicion_inline_activa is None:
            return

        info = self.edicion_inline_activa
        editor = info["widget"]
        texto_nuevo = editor.toPlainText().strip()

        tamano_nuevo = self.spin_tamano.value()
        negrita = self.btn_negrita.isChecked()
        cursiva = self.btn_cursiva.isChecked()
        color_nuevo = self.color_edicion_actual
        color_normalizado = tuple(c / 255 for c in color_nuevo)

        # Si el texto y formato no cambiaron en absoluto, no tocamos el PDF
        if (
            texto_nuevo == info["texto_original"]
            and abs(tamano_nuevo - info["tamano_original"]) < 0.1
            and negrita == info["negrita_original"]
            and cursiva == info["cursiva_original"]
            and color_nuevo == info["color_original"]
        ):
            self.cancelar_edicion_inline()
            return

        numero_pagina = info["numero_pagina"]
        pagina = info["pagina"]
        parrafo = info["parrafo"]
        bbox_detectado = info["bbox"]
        es_una_sola_linea = info["es_una_sola_linea"]

        if negrita and cursiva:
            fuente = "hebi"
        elif negrita:
            fuente = "hebo"
        elif cursiva:
            fuente = "heit"
        else:
            fuente = "helv"

        color_de_fondo = self.muestrear_color_de_fondo(pagina, bbox_detectado)

        try:
            if es_una_sola_linea and "\n" not in texto_nuevo:
                pagina.add_redact_annot(bbox_detectado, fill=color_de_fondo)
                pagina.apply_redactions()
                pagina.clean_contents()

                origen = parrafo.get("origen", (bbox_detectado.x0, bbox_detectado.y1 - 2))
                pagina.insert_text(
                    origen, texto_nuevo, fontsize=tamano_nuevo,
                    fontname=fuente, color=color_normalizado,
                )
            else:
                espacio_arriba, espacio_abajo = self.calcular_espacio_disponible_vertical(pagina, bbox_detectado)
                margen_deseado = bbox_detectado.height * 0.15 + 2
                margen_arriba = max(0, min(margen_deseado, (espacio_arriba - 1.5) if espacio_arriba is not None else margen_deseado))
                margen_abajo = max(0, min(margen_deseado, (espacio_abajo - 1.5) if espacio_abajo is not None else margen_deseado))
                bbox_real = fitz.Rect(
                    bbox_detectado.x0 - 2, bbox_detectado.y0 - margen_arriba,
                    max(bbox_detectado.x1 + 6, bbox_detectado.x0 + bbox_detectado.width),
                    bbox_detectado.y1 + margen_abajo,
                )

                pagina.add_redact_annot(bbox_real, fill=color_de_fondo)
                pagina.apply_redactions()
                pagina.clean_contents()
                pagina.insert_textbox(
                    bbox_real, texto_nuevo, fontsize=tamano_nuevo,
                    fontname=fuente, color=color_normalizado, align=0,
                )

            editor.hide()
            editor.deleteLater()
            self.edicion_inline_activa = None

            # Redibujamos la pagina y refrescamos los recuadros
            self.redibujar_pagina_individual(numero_pagina)
            etiqueta = self.etiquetas_paginas[numero_pagina]
            if etiqueta is not None and etiqueta.pixmap_limpio is not None:
                parrafos = self.obtener_todos_los_parrafos(pagina)
                imagenes = self.obtener_todas_las_imagenes(pagina)
                formas = self.obtener_formas_de_color(pagina)
                etiqueta.setPixmap(self.dibujar_cajas_de_texto(etiqueta.pixmap_limpio, parrafos, imagenes, formas))

            self.statusBar().showMessage("Texto guardado con exito en el PDF.", 4000)
        except Exception as error:
            QMessageBox.critical(self, "Error al editar el texto", str(error))
            self.cancelar_edicion_inline()

    def cancelar_edicion_inline(self):
        """Descarta la edicion en curso y oculta el editor inline."""
        if self.edicion_inline_activa is not None:
            editor = self.edicion_inline_activa["widget"]
            editor.hide()
            editor.deleteLater()
            self.edicion_inline_activa = None
            self.statusBar().showMessage("Edicion cancelada.", 3000)

    def escribir_texto_en_punto(self, numero_pagina, punto, texto, tamano, fuente, color):
        """Escribe una linea de texto en el punto donde el usuario dio clic."""
        if self.documento is None:
            return
        pagina = self.documento[numero_pagina]
        try:
            pagina.insert_text((punto.x, punto.y), texto, fontsize=tamano, fontname=fuente, color=color)
            self.redibujar_pagina_individual(numero_pagina)
        except Exception as error:
            QMessageBox.critical(self, "Error al colocar el texto", str(error))

    def escribir_cuadro_de_texto_en_punto(self, numero_pagina, punto, texto, tamano, fuente, color, ancho, alto):
        """Escribe un cuadro de texto (varias lineas) en el punto donde el usuario dio clic."""
        if self.documento is None:
            return
        pagina = self.documento[numero_pagina]
        try:
            rect = fitz.Rect(punto.x, punto.y, punto.x + ancho, punto.y + alto)
            pagina.insert_textbox(rect, texto, fontsize=tamano, fontname=fuente, color=color, align=0)
            self.redibujar_pagina_individual(numero_pagina)
        except Exception as error:
            QMessageBox.critical(self, "Error al colocar el texto", str(error))

    def editar_imagen(self, pagina, imagen):
        """Muestra opciones para reemplazar o eliminar una imagen detectada."""
        opciones = QMessageBox(self)
        opciones.setWindowTitle("Editar imagen")
        opciones.setText("¿Que quieres hacer con esta imagen?")
        opciones.addButton("Reemplazar imagen...", QMessageBox.ActionRole)
        opciones.addButton("Eliminar imagen", QMessageBox.DestructiveRole)
        opciones.addButton("Cancelar", QMessageBox.RejectRole)
        opciones.exec()

        # IMPORTANTE: comparamos por TEXTO del boton, no por identidad del
        # objeto ("es este boton") - en PySide6, comparar identidad de un
        # boton contra lo que devuelve clickedButton() puede fallar de forma
        # silenciosa y hacer que no se ejecute nada al hacer clic.
        boton_presionado = opciones.clickedButton()
        texto_boton = boton_presionado.text() if boton_presionado else ""

        try:
            if texto_boton == "Reemplazar imagen...":
                ruta_nueva, _ = QFileDialog.getOpenFileName(
                    self, "Selecciona la imagen nueva", "",
                    "Imagenes (*.png *.jpg *.jpeg)"
                )
                if not ruta_nueva:
                    return

                bbox = imagen["bbox"]
                dialogo_posicion = DialogoPosicionarImagen(
                    bbox.x0, bbox.y0, bbox.width, bbox.height, parent=self
                )
                if dialogo_posicion.exec() != QDialog.Accepted:
                    return
                datos = dialogo_posicion.obtener_valores()

                # Borramos la imagen vieja de una vez (haya elegido clic o numeros)
                pagina.delete_image(imagen["xref"])
                pagina.clean_contents()  # limpia referencias que ya no se usan

                if datos["usar_clic"]:
                    self.accion_pendiente_por_clic = lambda num_pag, punto: self.colocar_imagen_en_punto(
                        num_pag, punto, ruta_nueva, datos["ancho"], datos["alto"], datos["mantener_proporcion"]
                    )
                    self.statusBar().showMessage(
                        "Ahora da clic en la pagina donde quieras la esquina "
                        "superior izquierda de la imagen nueva..."
                    )
                    return

                nuevo_rect = fitz.Rect(
                    datos["x"], datos["y"],
                    datos["x"] + datos["ancho"], datos["y"] + datos["alto"],
                )
                pagina.insert_image(
                    nuevo_rect, filename=ruta_nueva,
                    keep_proportion=datos["mantener_proporcion"],
                )
            elif texto_boton == "Eliminar imagen":
                respuesta = QMessageBox.question(self, "Confirmar", "¿Eliminar esta imagen del documento?")
                if respuesta != QMessageBox.Yes:
                    return
                pagina.delete_image(imagen["xref"])
                pagina.clean_contents()  # limpia referencias que ya no se usan
            else:
                return  # Cancelar
        except Exception as error:
            QMessageBox.critical(self, "Error al editar la imagen", str(error))

    def colocar_imagen_en_punto(self, numero_pagina, punto, ruta, ancho, alto, mantener_proporcion):
        """Coloca una imagen ya elegida en el punto donde el usuario dio clic (esquina superior izquierda)."""
        if self.documento is None:
            return
        pagina = self.documento[numero_pagina]
        nuevo_rect = fitz.Rect(punto.x, punto.y, punto.x + ancho, punto.y + alto)
        try:
            pagina.insert_image(nuevo_rect, filename=ruta, keep_proportion=mantener_proporcion)
            self.redibujar_pagina_individual(numero_pagina)
            if self.combo_herramienta.currentText() == "Editar contenido (texto e imagenes)":
                parrafos = self.obtener_todos_los_parrafos(pagina)
                imagenes = self.obtener_todas_las_imagenes(pagina)
                formas = self.obtener_formas_de_color(pagina)
                etiqueta = self.etiquetas_paginas[numero_pagina]
                if etiqueta is not None and etiqueta.pixmap_limpio is not None:
                    etiqueta.setPixmap(self.dibujar_cajas_de_texto(etiqueta.pixmap_limpio, parrafos, imagenes, formas))
        except Exception as error:
            QMessageBox.critical(self, "Error al colocar la imagen", str(error))

    def rotar_pagina(self):
        if self.documento is None:
            return
        pagina = self.documento[self.pagina_actual]
        pagina.set_rotation((pagina.rotation + 90) % 360)
        self.dibujar_todas_las_paginas()
        self.ir_a_pagina(self.pagina_actual)

    def eliminar_pagina(self):
        if self.documento is None:
            return
        if len(self.documento) == 1:
            QMessageBox.warning(self, "Aviso", "No puedes eliminar la unica pagina del documento.")
            return
        respuesta = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar la pagina {self.pagina_actual + 1}?"
        )
        if respuesta == QMessageBox.Yes:
            self.documento.delete_page(self.pagina_actual)
            self.dibujar_todas_las_paginas()
            self.ir_a_pagina(self.pagina_actual)

    def insertar_pagina_blanco(self):
        if self.documento is None:
            return
        self.documento.new_page(pno=self.pagina_actual + 1)
        self.pagina_actual += 1
        self.dibujar_todas_las_paginas()
        self.ir_a_pagina(self.pagina_actual)

    def reordenar_paginas(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        if len(self.documento) < 2:
            QMessageBox.information(self, "Aviso", "Necesitas al menos 2 paginas para reordenar.")
            return

        dialogo = DialogoReordenarPaginas(self.documento, parent=self)
        if dialogo.exec() == QDialog.Accepted:
            nuevo_orden = dialogo.obtener_nuevo_orden()
            try:
                # Document.select() reconstruye el documento dejando SOLO las
                # paginas de esa lista, y EN ESE ORDEN. Como pasamos todas las
                # paginas (solo que revueltas), el resultado es "reordenar".
                self.documento.select(nuevo_orden)
                self.pagina_actual = 0
                self.dibujar_todas_las_paginas()
                self.ir_a_pagina(0)
                QMessageBox.information(self, "Listo", "Orden aplicado. Recuerda usar 'Guardar como' para conservarlo.")
            except Exception as error:
                QMessageBox.critical(self, "Error al reordenar", str(error))

    # ---------------------------------------------------------------
    # GUARDAR / EXPORTAR / COMPRIMIR (sin cambios respecto a la version anterior)
    # ---------------------------------------------------------------

    def guardar_como(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(self, "Guardar como", "", "Archivos PDF (*.pdf)")
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".pdf"):
            ruta_destino += ".pdf"
        try:
            self.documento.save(ruta_destino, deflate=True, garbage=3)
            QMessageBox.information(self, "Listo", f"Guardado en:\n{ruta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error al guardar", str(error))

    def guardar(self):
        """Sobreescribe el archivo original con los cambios actuales."""
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        if not self.ruta_actual:
            # Si el PDF no vino de un archivo en disco (poco probable aqui), usamos "Guardar como"
            self.guardar_como()
            return
        try:
            carpeta = os.path.dirname(self.ruta_actual) or "."
            # PyMuPDF no permite guardar en el MISMO archivo que ya esta abierto para lectura,
            # asi que guardamos primero en un archivo temporal en la misma carpeta...
            descriptor, ruta_temporal = tempfile.mkstemp(suffix=".pdf", dir=carpeta)
            os.close(descriptor)
            self.documento.save(ruta_temporal, deflate=True, garbage=3)
            self.documento.close()
            # ...y luego reemplazamos el original por ese temporal.
            os.replace(ruta_temporal, self.ruta_actual)
            # Volvemos a abrir el archivo ya guardado para seguir trabajando sobre el
            self.documento = fitz.open(self.ruta_actual)
            self.dibujar_todas_las_paginas()
            self.ir_a_pagina(min(self.pagina_actual, len(self.documento) - 1))
            self.statusBar().showMessage(f"Guardado: {self.ruta_actual}", 5000)
        except Exception as error:
            QMessageBox.critical(self, "Error al guardar", str(error))

    def cerrar_documento(self):
        """Cierra el PDF actual sin guardar (pide confirmacion) y deja la ventana vacia."""
        if self.documento is None:
            return
        respuesta = QMessageBox.question(
            self, "Cerrar documento",
            "¿Cerrar el documento actual? Si tienes cambios sin guardar, se perderan."
        )
        if respuesta != QMessageBox.Yes:
            return

        if self.edicion_inline_activa is not None:
            self.cancelar_edicion_inline()

        self.documento.close()
        self.documento = None
        self.ruta_actual = None
        self.pagina_actual = 0
        self.dibujar_todas_las_paginas()  # como documento es None, esto deja el panel vacio

        etiqueta_vacia = QLabel("Abre un PDF con el menu Archivo -> Abrir PDF")
        etiqueta_vacia.setAlignment(Qt.AlignCenter)
        self.layout_paginas.addWidget(etiqueta_vacia)

        self.setWindowTitle("Mi Adobe PDF - Fase 2")
        self.actualizar_indicador_pagina()

    def convertir_a_word(self):
        """Convierte el PDF actual (con los cambios que tengas hechos) a un archivo Word (.docx)."""
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return

        ruta_destino, _ = QFileDialog.getSaveFileName(
            self, "Guardar como Word", "", "Documentos Word (*.docx)"
        )
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".docx"):
            ruta_destino += ".docx"

        try:
            from pdf2docx import Converter
        except ImportError:
            QMessageBox.critical(
                self, "Falta una libreria",
                "Falta instalar 'pdf2docx'. En tu terminal (con el venv activado) ejecuta:\n\n"
                "pip install -r requirements.txt"
            )
            return

        ruta_temporal = None
        try:
            self.statusBar().showMessage("Convirtiendo a Word, espera un momento...")
            QApplication.processEvents()  # refresca la ventana para que se vea el mensaje antes de la espera

            # pdf2docx necesita un ARCHIVO en disco como entrada, asi que primero
            # guardamos el documento actual (con tus anotaciones/cambios) en un PDF temporal.
            carpeta_temporal = tempfile.gettempdir()
            descriptor, ruta_temporal = tempfile.mkstemp(suffix=".pdf", dir=carpeta_temporal)
            os.close(descriptor)
            self.documento.save(ruta_temporal)

            convertidor = Converter(ruta_temporal)
            convertidor.convert(ruta_destino)
            convertidor.close()

            self.statusBar().showMessage("Conversion terminada.", 5000)
            QMessageBox.information(
                self, "Listo",
                f"Word guardado en:\n{ruta_destino}\n\n"
                "Nota: en documentos con diseños complicados (tablas raras, columnas, "
                "PDFs escaneados sin texto real) el formato puede no quedar identico."
            )
        except Exception as error:
            self.statusBar().clearMessage()
            QMessageBox.critical(self, "Error al convertir", str(error))
        finally:
            if ruta_temporal and os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)

    def hacer_ocr(self):
        """
        Le agrega al PDF una capa de texto invisible (reconocido por OCR) sobre
        las paginas que sean solo imagen (escaneadas), para que ese texto se
        pueda seleccionar, copiar y buscar. Las paginas que YA tengan texto
        se dejan intactas (no se tocan ni se re-escanean).
        """
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF con OCR como", "", "Archivos PDF (*.pdf)"
        )
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".pdf"):
            ruta_destino += ".pdf"

        ruta_pdf_temporal = None
        try:
            import ocrmypdf

            descriptor, ruta_pdf_temporal = tempfile.mkstemp(suffix=".pdf")
            os.close(descriptor)
            self.documento.save(ruta_pdf_temporal)

            self.statusBar().showMessage(
                "Aplicando OCR... esto puede tardar varios segundos por pagina, espera."
            )
            QApplication.processEvents()

            ocrmypdf.ocr(
                ruta_pdf_temporal,
                ruta_destino,
                language="spa+eng",   # reconoce texto en espanol e ingles
                deskew=True,          # endereza paginas escaneadas torcidas
                skip_text=True,       # si una pagina YA tiene texto, no la toca
                progress_bar=False,
            )
            QMessageBox.information(self, "Listo", f"PDF con OCR guardado en:\n{ruta_destino}")
        except ImportError:
            QMessageBox.critical(
                self, "Falta instalar componentes",
                "Falta 'ocrmypdf'. Con tu (venv) activado:\n\n"
                "pip install ocrmypdf\n\n"
                "Y en el sistema (una sola vez):\n"
                "sudo apt install tesseract-ocr tesseract-ocr-spa ghostscript -y"
            )
        except Exception as error:
            QMessageBox.critical(self, "Error al aplicar OCR", str(error))
        finally:
            if ruta_pdf_temporal and os.path.exists(ruta_pdf_temporal):
                os.remove(ruta_pdf_temporal)
            self.statusBar().clearMessage()

    def unir_pdfs(self):
        rutas, _ = QFileDialog.getOpenFileNames(
            self, "Selecciona 2 o mas PDFs, EN EL ORDEN en que se deben unir",
            "", "Archivos PDF (*.pdf)"
        )
        if len(rutas) < 2:
            QMessageBox.information(self, "Aviso", "Selecciona al menos 2 archivos.")
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(self, "Guardar PDF unido como", "", "Archivos PDF (*.pdf)")
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".pdf"):
            ruta_destino += ".pdf"
        try:
            resultado = fitz.open()
            for ruta in rutas:
                with fitz.open(ruta) as origen:
                    resultado.insert_pdf(origen)
            resultado.save(ruta_destino)
            resultado.close()
            QMessageBox.information(self, "Listo", f"PDFs unidos en:\n{ruta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error al unir", str(error))

    def dividir_pdf(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        carpeta_destino = QFileDialog.getExistingDirectory(self, "Elige carpeta donde guardar las paginas")
        if not carpeta_destino:
            return
        try:
            base = os.path.splitext(os.path.basename(self.ruta_actual or "documento"))[0]
            for i in range(len(self.documento)):
                nuevo = fitz.open()
                nuevo.insert_pdf(self.documento, from_page=i, to_page=i)
                nombre = os.path.join(carpeta_destino, f"{base}_pagina_{i + 1}.pdf")
                nuevo.save(nombre)
                nuevo.close()
            QMessageBox.information(self, "Listo", f"{len(self.documento)} paginas guardadas en:\n{carpeta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error al dividir", str(error))

    def exportar_imagenes(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        carpeta_destino = QFileDialog.getExistingDirectory(self, "Elige carpeta donde guardar las imagenes")
        if not carpeta_destino:
            return
        try:
            base = os.path.splitext(os.path.basename(self.ruta_actual or "documento"))[0]
            matriz_zoom = fitz.Matrix(2.0, 2.0)
            for i, pagina in enumerate(self.documento):
                pix = pagina.get_pixmap(matrix=matriz_zoom)
                nombre = os.path.join(carpeta_destino, f"{base}_pagina_{i + 1}.png")
                pix.save(nombre)
            QMessageBox.information(self, "Listo", f"Imagenes guardadas en:\n{carpeta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error al exportar", str(error))

    def comprimir_pdf(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(self, "Guardar PDF comprimido como", "", "Archivos PDF (*.pdf)")
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".pdf"):
            ruta_destino += ".pdf"
        try:
            self.documento.save(ruta_destino, deflate=True, garbage=4, clean=True)
            tamano_kb = os.path.getsize(ruta_destino) / 1024
            QMessageBox.information(self, "Listo", f"PDF comprimido guardado ({tamano_kb:.1f} KB):\n{ruta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error al comprimir", str(error))

    # ---------------------------------------------------------------
    # SEGURIDAD (sin cambios respecto a la version anterior)
    # ---------------------------------------------------------------

    def agregar_contrasena(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        contrasena, ok = QInputDialog.getText(self, "Agregar contrasena", "Nueva contrasena:", QLineEdit.Password)
        if not ok or not contrasena:
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(self, "Guardar PDF protegido como", "", "Archivos PDF (*.pdf)")
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".pdf"):
            ruta_destino += ".pdf"
        try:
            self.documento.save(
                ruta_destino, encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=contrasena, owner_pw=contrasena,
            )
            QMessageBox.information(self, "Listo", f"PDF protegido guardado en:\n{ruta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error", str(error))

    def quitar_contrasena(self):
        if self.documento is None:
            QMessageBox.information(self, "Aviso", "Primero abre un PDF.")
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(self, "Guardar PDF sin contrasena como", "", "Archivos PDF (*.pdf)")
        if not ruta_destino:
            return
        if not ruta_destino.lower().endswith(".pdf"):
            ruta_destino += ".pdf"
        try:
            self.documento.save(ruta_destino)
            QMessageBox.information(self, "Listo", f"PDF sin contrasena guardado en:\n{ruta_destino}")
        except Exception as error:
            QMessageBox.critical(self, "Error", str(error))


# =========================================================================
# PUNTO DE ENTRADA
# =========================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cargamos la traduccion oficial de Qt al espanol, para que los dialogos
    # nativos (Guardar, Abrir, Cancelar, etc.) tambien salgan en espanol
    # y no se queden en ingles como vienen por defecto.
    traductor = QTranslator()
    ruta_traducciones = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if traductor.load(QLocale(QLocale.Language.Spanish), "qtbase", "_", ruta_traducciones):
        app.installTranslator(traductor)

    ventana = EditorPDF()
    ventana.show()
    sys.exit(app.exec())

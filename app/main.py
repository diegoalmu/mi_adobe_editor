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
    QHBoxLayout, QAbstractItemView,
)
from PySide6.QtGui import QPixmap, QImage, QAction, QIcon
from PySide6.QtCore import Qt, QRect, QSize, Signal


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

ESPACIO_ENTRE_PAGINAS = 15  # pixeles de separacion visual entre una pagina y la siguiente


# =========================================================================
# ETIQUETA_PDF: una instancia por cada pagina dibujada en pantalla.
# =========================================================================

class EtiquetaPDF(QLabel):
    """
    Muestra UNA pagina del PDF y detecta arrastres de mouse sobre ELLA
    para colocar anotaciones. Cada instancia "sabe" su propio numero de
    pagina (self.numero_pagina), asi que no importa que haya muchas
    paginas en pantalla a la vez: siempre se anota la correcta.
    """

    # Envia: (numero_de_pagina, rectangulo_en_pixeles_de_esa_pagina)
    seleccion_lista = Signal(int, QRect)

    def __init__(self, numero_pagina: int):
        super().__init__()
        self.numero_pagina = numero_pagina
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.punto_inicio = None
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)

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
            if rect.width() > 4 or rect.height() > 4:
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
    ]

    def __init__(self):
        super().__init__()

        self.documento = None
        self.ruta_actual = None
        self.zoom = 1.5
        self.pagina_actual = 0          # pagina que se considera "visible" ahora mismo
        self.etiquetas_paginas = []      # lista de EtiquetaPDF, una por pagina
        self.offsets_top = []            # posicion vertical (en pixeles) donde empieza cada pagina

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
    # MENU DESPLEGABLE "ARCHIVO"
    # ---------------------------------------------------------------

    def crear_menu_archivo(self):
        menu_archivo = self.menuBar().addMenu("Archivo")

        accion_abrir = QAction("Abrir PDF...", self)
        accion_abrir.triggered.connect(self.abrir_pdf)
        menu_archivo.addAction(accion_abrir)

        menu_archivo.addSeparator()

        accion_guardar = QAction("Guardar", self)
        accion_guardar.triggered.connect(self.guardar)
        menu_archivo.addAction(accion_guardar)

        accion_guardar_como = QAction("Guardar como...", self)
        accion_guardar_como.triggered.connect(self.guardar_como)
        menu_archivo.addAction(accion_guardar_como)

        menu_archivo.addSeparator()

        accion_cerrar = QAction("Cerrar documento", self)
        accion_cerrar.triggered.connect(self.cerrar_documento)
        menu_archivo.addAction(accion_cerrar)

        menu_archivo.addSeparator()

        accion_salir = QAction("Salir del programa", self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

    # ---------------------------------------------------------------
    # CONSTRUCCION DE BARRA DE HERRAMIENTAS
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
        self.combo_herramienta.currentTextChanged.connect(self.actualizar_ayuda)
        barra.addWidget(self.combo_herramienta)
        barra.addSeparator()

        self.agregar_boton(barra, "Rotar pagina", self.rotar_pagina)
        self.agregar_boton(barra, "Eliminar pagina", self.eliminar_pagina)
        self.agregar_boton(barra, "Insertar pagina en blanco", self.insertar_pagina_blanco)
        self.agregar_boton(barra, "Reordenar paginas", self.reordenar_paginas)
        barra.addSeparator()

        self.agregar_boton(barra, "Unir PDFs", self.unir_pdfs)
        self.agregar_boton(barra, "Dividir PDF", self.dividir_pdf)
        self.agregar_boton(barra, "Exportar a imagenes", self.exportar_imagenes)
        self.agregar_boton(barra, "Comprimir PDF", self.comprimir_pdf)
        barra.addSeparator()

        self.agregar_boton(barra, "Agregar contrasena", self.agregar_contrasena)
        self.agregar_boton(barra, "Quitar contrasena", self.quitar_contrasena)

    def agregar_boton(self, barra, texto, funcion):
        accion = QAction(texto, self)
        accion.triggered.connect(funcion)
        barra.addAction(accion)
        return accion

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
        }
        self.statusBar().showMessage(mensajes.get(herramienta, ""))

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
            pixmap_fitz = pagina.get_pixmap(matrix=matriz_zoom)
            imagen_qt = QImage(
                pixmap_fitz.samples, pixmap_fitz.width, pixmap_fitz.height,
                pixmap_fitz.stride, QImage.Format_RGB888,
            )
            pixmap_qt = QPixmap.fromImage(imagen_qt)

            etiqueta = EtiquetaPDF(numero)
            etiqueta.setPixmap(pixmap_qt)
            etiqueta.setFixedSize(pixmap_qt.size())
            etiqueta.seleccion_lista.connect(self.al_seleccionar_rectangulo)

            self.layout_paginas.addWidget(etiqueta)
            self.etiquetas_paginas.append(etiqueta)
            self.offsets_top.append(posicion_y)
            posicion_y += pixmap_qt.height() + ESPACIO_ENTRE_PAGINAS

        self.pagina_actual = max(0, min(self.pagina_actual, len(self.documento) - 1))
        self.actualizar_indicador_pagina()
        self.setWindowTitle(f"Mi Adobe PDF - {len(self.documento)} paginas")

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
        self.zoom += 0.2
        self.dibujar_todas_las_paginas()
        self.ir_a_pagina(self.pagina_actual)

    def zoom_menos(self):
        if self.zoom > 0.4:
            self.zoom -= 0.2
            self.dibujar_todas_las_paginas()
            self.ir_a_pagina(self.pagina_actual)

    # ---------------------------------------------------------------
    # ANOTACIONES
    # ---------------------------------------------------------------

    def al_seleccionar_rectangulo(self, numero_pagina: int, rect_pixeles: QRect):
        if self.documento is None:
            return

        herramienta = self.combo_herramienta.currentText()
        if herramienta == "Ninguna (solo ver)":
            return

        x0 = rect_pixeles.left() / self.zoom
        y0 = rect_pixeles.top() / self.zoom
        x1 = rect_pixeles.right() / self.zoom
        y1 = rect_pixeles.bottom() / self.zoom
        rect_pdf = fitz.Rect(x0, y0, x1, y1)

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

            # Solo hace falta re-dibujar la pagina afectada, no todas (mas rapido)
            self.redibujar_pagina_individual(numero_pagina)
        except Exception as error:
            QMessageBox.critical(self, "No se pudo agregar la anotacion", str(error))

    def redibujar_pagina_individual(self, numero_pagina):
        pagina = self.documento[numero_pagina]
        matriz_zoom = fitz.Matrix(self.zoom, self.zoom)
        pixmap_fitz = pagina.get_pixmap(matrix=matriz_zoom)
        imagen_qt = QImage(
            pixmap_fitz.samples, pixmap_fitz.width, pixmap_fitz.height,
            pixmap_fitz.stride, QImage.Format_RGB888,
        )
        pixmap_qt = QPixmap.fromImage(imagen_qt)
        self.etiquetas_paginas[numero_pagina].setPixmap(pixmap_qt)

    # ---------------------------------------------------------------
    # PAGINAS (rotar/eliminar/insertar actuan sobre self.pagina_actual,
    # la que este marcada en el indicador en ese momento)
    # ---------------------------------------------------------------

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
    ventana = EditorPDF()
    ventana.show()
    sys.exit(app.exec())

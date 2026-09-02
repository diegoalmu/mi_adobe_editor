"""
Mi-Adobe-PDF - Fase 1: Visor de PDF
=====================================

Que hace este programa hoy:
    - Abrir un archivo PDF desde tu computadora
    - Mostrarlo en una ventana
    - Pasar a la pagina siguiente / anterior
    - Hacer zoom (acercar / alejar)

Que NO hace todavia (vendra en las siguientes fases, ver ROADMAP.md):
    - Editar texto, agregar anotaciones, unir/dividir PDFs, etc.

Librerias usadas:
    - PySide6: crea la ventana, botones y menus (la "cara" del programa)
    - fitz (PyMuPDF): abre y "dibuja" el contenido del PDF
"""

# -----------------------------------------------------------------------
# 1) IMPORTS: traemos las herramientas que vamos a usar
# -----------------------------------------------------------------------

import sys                     # Herramientas del sistema (necesario para iniciar la app)
import fitz                    # Este es PyMuPDF. Se importa como "fitz" por razones historicas de la libreria

from PySide6.QtWidgets import (
    QApplication,   # Representa "el programa" en si mismo (siempre se necesita uno)
    QMainWindow,    # La ventana principal, con espacio para menus, barra de herramientas, etc.
    QLabel,         # Un elemento para mostrar texto o imagenes (lo usamos para mostrar la pagina del PDF)
    QScrollArea,    # Un contenedor con barras de scroll (por si la pagina no cabe en pantalla)
    QToolBar,       # La barra de botones de arriba
    QFileDialog,    # La ventana de "Abrir archivo" del sistema operativo
    QMessageBox,    # Ventanas de aviso/error emergentes
)
from PySide6.QtGui import QPixmap, QImage, QAction   # Herramientas para mostrar imagenes y crear botones de menu
from PySide6.QtCore import Qt


# -----------------------------------------------------------------------
# 2) CLASE PRINCIPAL: define como se ve y se comporta la ventana
# -----------------------------------------------------------------------

class VisorPDF(QMainWindow):
    """
    Esta clase representa toda la ventana del programa.
    En Python, una "clase" es como un molde para crear algo (aqui, una ventana)
    que tiene sus propias variables (datos) y funciones (acciones).
    """

    def __init__(self):
        # Esta funcion especial se ejecuta automaticamente al crear la ventana.
        super().__init__()  # Le decimos a QMainWindow que se configure normalmente primero

        # --- Datos internos que el programa necesita recordar ---
        self.documento = None      # Aqui guardaremos el PDF abierto (al inicio, ninguno)
        self.pagina_actual = 0     # Que pagina se esta mostrando (empieza en la pagina 0, la primera)
        self.zoom = 1.5            # Nivel de zoom inicial (1.0 = tamano real, 1.5 = 150%)

        # --- Configuracion basica de la ventana ---
        self.setWindowTitle("Mi Adobe PDF - Fase 1: Visor")
        self.resize(1000, 800)  # Ancho x alto en pixeles al abrir

        # --- Area donde se mostrara la pagina del PDF ---
        self.etiqueta_pagina = QLabel("Abre un PDF con el boton 'Abrir PDF' de arriba")
        self.etiqueta_pagina.setAlignment(Qt.AlignCenter)  # Centra el texto/imagen

        # Metemos esa etiqueta dentro de un area con scroll,
        # por si la pagina es mas grande que la ventana
        self.area_scroll = QScrollArea()
        self.area_scroll.setWidget(self.etiqueta_pagina)
        self.area_scroll.setWidgetResizable(True)
        self.setCentralWidget(self.area_scroll)  # La ponemos como el contenido central de la ventana

        # --- Creamos la barra de herramientas (botones de arriba) ---
        self.crear_barra_herramientas()

    def crear_barra_herramientas(self):
        """Crea los botones de: Abrir, Anterior, Siguiente, Zoom +, Zoom -"""

        barra = QToolBar("Herramientas")
        self.addToolBar(barra)  # La agregamos a la ventana principal

        # Boton "Abrir PDF"
        accion_abrir = QAction("Abrir PDF", self)
        accion_abrir.triggered.connect(self.abrir_pdf)  # Que funcion se ejecuta al hacer clic
        barra.addAction(accion_abrir)

        barra.addSeparator()  # Una linea vertical para separar visualmente los botones

        # Boton "Pagina anterior"
        accion_anterior = QAction("<- Pagina anterior", self)
        accion_anterior.triggered.connect(self.pagina_anterior)
        barra.addAction(accion_anterior)

        # Boton "Pagina siguiente"
        accion_siguiente = QAction("Pagina siguiente ->", self)
        accion_siguiente.triggered.connect(self.pagina_siguiente)
        barra.addAction(accion_siguiente)

        barra.addSeparator()

        # Boton "Zoom -"
        accion_zoom_menos = QAction("Zoom -", self)
        accion_zoom_menos.triggered.connect(self.zoom_menos)
        barra.addAction(accion_zoom_menos)

        # Boton "Zoom +"
        accion_zoom_mas = QAction("Zoom +", self)
        accion_zoom_mas.triggered.connect(self.zoom_mas)
        barra.addAction(accion_zoom_mas)

    # ---------------------------------------------------------------
    # 3) FUNCIONES: cada una es una accion que el programa puede hacer
    # ---------------------------------------------------------------

    def abrir_pdf(self):
        """Se ejecuta al hacer clic en 'Abrir PDF'. Muestra el explorador de archivos."""

        # QFileDialog.getOpenFileName abre la ventana nativa de "Abrir archivo" de Windows/Linux
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona un archivo PDF",   # Titulo de la ventana
            "",                             # Carpeta inicial (vacio = la ultima usada)
            "Archivos PDF (*.pdf)"          # Filtro: solo mostrar archivos .pdf
        )

        if not ruta_archivo:
            # Si el usuario le dio "Cancelar", ruta_archivo llega vacio. No hacemos nada.
            return

        try:
            # fitz.open() carga el PDF en memoria
            self.documento = fitz.open(ruta_archivo)
            self.pagina_actual = 0
            self.mostrar_pagina()
        except Exception as error:
            # Si algo sale mal (archivo dañado, no es un PDF real, etc.), avisamos al usuario
            QMessageBox.critical(self, "Error al abrir el archivo", str(error))

    def mostrar_pagina(self):
        """Dibuja la pagina actual del PDF dentro de la ventana."""

        if self.documento is None:
            return  # No hay ningun PDF abierto todavia

        pagina = self.documento[self.pagina_actual]  # Obtenemos el objeto de esa pagina

        # get_pixmap "renderiza" (convierte) la pagina del PDF en una imagen
        # la matriz de zoom controla que tan grande se dibuja
        matriz_zoom = fitz.Matrix(self.zoom, self.zoom)
        pixmap_fitz = pagina.get_pixmap(matrix=matriz_zoom)

        # Convertimos la imagen de PyMuPDF a un formato que Qt entienda (QImage)
        imagen_qt = QImage(
            pixmap_fitz.samples,
            pixmap_fitz.width,
            pixmap_fitz.height,
            pixmap_fitz.stride,
            QImage.Format_RGB888,
        )

        # La mostramos en la etiqueta central de la ventana
        self.etiqueta_pagina.setPixmap(QPixmap.fromImage(imagen_qt))

        # Actualizamos el titulo de la ventana para mostrar en que pagina vamos
        total_paginas = len(self.documento)
        self.setWindowTitle(
            f"Mi Adobe PDF - Pagina {self.pagina_actual + 1} de {total_paginas}"
        )

    def pagina_siguiente(self):
        """Avanza una pagina, si no estamos ya en la ultima."""
        if self.documento is None:
            return
        if self.pagina_actual < len(self.documento) - 1:
            self.pagina_actual += 1
            self.mostrar_pagina()

    def pagina_anterior(self):
        """Retrocede una pagina, si no estamos ya en la primera."""
        if self.documento is None:
            return
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.mostrar_pagina()

    def zoom_mas(self):
        """Aumenta el zoom un 20% y vuelve a dibujar la pagina."""
        self.zoom += 0.2
        self.mostrar_pagina()

    def zoom_menos(self):
        """Reduce el zoom un 20% (sin bajar de un minimo razonable)."""
        if self.zoom > 0.4:
            self.zoom -= 0.2
            self.mostrar_pagina()


# -----------------------------------------------------------------------
# 4) PUNTO DE ENTRADA: aqui es donde realmente arranca el programa
# -----------------------------------------------------------------------

if __name__ == "__main__":
    # Esta condicion asegura que este codigo solo se ejecute si corremos
    # este archivo directamente (y no si alguien lo importa desde otro archivo)

    app = QApplication(sys.argv)   # Crea "el programa" en si
    ventana = VisorPDF()           # Crea nuestra ventana usando la clase de arriba
    ventana.show()                 # La hace visible en pantalla
    sys.exit(app.exec())           # Mantiene el programa corriendo hasta que se cierre la ventana

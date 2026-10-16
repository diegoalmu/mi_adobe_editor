"""
panel_formularios.py - Panel lateral con los campos del formulario PDF
=====================================================================

Clase PanelFormularios (un QDockWidget titulado "Campos del formulario"
con una lista con desplazamiento: una fila por campo del PDF, con el
nombre a la izquierda y el control para llenarlo a la derecha), segun
el diseno `DISENO_FORMULARIOS.md` (Tarea 3). El control de cada campo
es el de la tabla de "Decisiones tecnicas" del diseno:

- `"texto"` -> QLineEdit (o QPlainTextEdit si es multilinea)
- `"casilla"` -> QCheckBox
- `"opcion"` -> grupo de QRadioButton (uno por opcion del campo)
- `"lista"` -> QComboBox con las opciones del PDF
- `"firma"` -> etiqueta "Firma (no editable aqui)"
- de solo lectura -> el control viene deshabilitado

El panel NO escribe en el PDF: emite la senal `valor_cambiado(nombre,
valor)` (al terminar de editar un texto, o al cambiar casilla, opcion
o lista) y quien lo use escribe con `formularios.escribir_valor`
(main.py, Tarea 4). `cargar(campos)` reconstruye las filas mientras
bloquea las senales de los controles, para que el valor inicial de
cada campo no se cuente como un cambio del usuario.

El codigo usa nombres COMPLETOS de los enums de Qt donde haga falta,
igual que el resto del programa, para que pyright no se queje.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class _TextoMultilinea(QPlainTextEdit):
    """Area de texto multilnea que avisa cuando termina de editarse.

    Qt no tiene `editingFinished` para QPlainTextEdit: aqui se emite
    `terminado` al perder el foco, igual que un QLineEdit con esa
    senal.
    """

    terminado = Signal()

    def focusOutEvent(self, evento):
        super().focusOutEvent(evento)
        self.terminado.emit()


class PanelFormularios(QDockWidget):
    """Dock con una fila por campo del formulario del PDF.

    - `cargar(campos)` vacia el panel y crea una fila por cada campo
      de la lista que devuelve `formularios.listar_campos`. Mientras
      carga, las senales de los controles estan bloqueadas.
    - `valor_cambiado(nombre, valor)` se emite al terminar de editar
      un texto (pierde el foco), o al marcar una casilla, elegir una
      opcion o una opcion de la lista. El valor es un string, o un
      bool en las casillas.
    - `seleccionar(nombre)` resalta la fila del campo y le da foco a
      su control (para enlazarlo con un clic en la pagina).
    - `controles[nombre]` es la lista de widgets de ese campo (uno en
      todos los tipos, y varios en `"opcion"`: un boton por opcion);
      lo usan main.py y las pruebas.
    """

    valor_cambiado = Signal(str, object)

    # Fondo de la fila del campo que selecciono el usuario.
    _COLOR_RESALTE = "background-color: rgb(198, 224, 255);"

    def __init__(self, parent=None):
        super().__init__("Campos del formulario", parent)
        # objectName para que main.py pueda guardar y restaurar la
        # posicion del dock con saveState (como los docks de Qt).
        self.setObjectName("panel_formularios")
        self.controles = {}
        self._etiquetas = {}
        self._resaltado = None
        self._tabla = QGridLayout()
        self._tabla.setHorizontalSpacing(8)
        self._tabla.setVerticalSpacing(6)
        self._tabla.setColumnStretch(1, 1)
        contenedor = QWidget()
        contenedor.setLayout(self._tabla)
        self._area = QScrollArea()
        self._area.setWidgetResizable(True)
        self._area.setWidget(contenedor)
        self.setWidget(self._area)

    def cargar(self, campos):
        """Vacia el panel y crea una fila por cada campo dado.

        `campos` es la lista de `formularios.listar_campos`. Las
        senales de los controles quedan bloqueadas mientras se arma
        cada fila, para no emitir `valor_cambiado` con los valores
        iniciales (solo el usuario puede cambiarlos).
        """
        while self._tabla.count():
            item = self._tabla.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.controles.clear()
        self._etiquetas.clear()
        self._resaltado = None
        for num_fila, campo in enumerate(campos):
            self._agregar_fila(num_fila, campo)

    def seleccionar(self, nombre):
        """Resalta la fila del campo y le da foco a su control."""
        if nombre not in self.controles:
            return
        if self._resaltado is not None:
            self._pintar_fila(self._resaltado, False)
        self._resaltado = nombre
        self._pintar_fila(nombre, True)
        control = self.controles[nombre][0]
        control.setFocus()
        # Que la fila se vea aunque este fuera de la vista.
        self._area.ensureWidgetVisible(control)

    # -----------------------------------------------------------------
    # INTERNOS
    # -----------------------------------------------------------------

    def _agregar_fila(self, num_fila, campo):
        """Agrega al grid la fila de un campo: nombre y control."""
        nombre = campo["nombre"]
        etiqueta = QLabel(nombre)
        self._etiquetas[nombre] = etiqueta
        self._tabla.addWidget(etiqueta, num_fila, 0)
        caja, controles = self._crear_controles(campo)
        if campo["solo_lectura"]:
            for control in controles:
                control.setEnabled(False)
        self.controles[nombre] = controles
        self._tabla.addWidget(caja, num_fila, 1)

    def _crear_controles(self, campo):
        """Crea los controles de un campo del PDF.

        Devuelve `(caja, controles)`: `caja` es el widget que va en la
        celda del grid (el propio control, o una caja vertical con los
        botones de un grupo de opcion) y `controles` es la lista de
        widgets editables del campo.
        """
        tipo = campo["tipo"]
        nombre = campo["nombre"]
        if tipo == "texto":
            if campo["multilinea"]:
                control = _TextoMultilinea()
                control.terminado.connect(
                    lambda n=nombre, c=control:
                        self.valor_cambiado.emit(n, c.toPlainText())
                )
                # QPlainTextEdit no tiene setText: usa setPlainText.
                fijar_texto = control.setPlainText
            else:
                control = QLineEdit()
                control.editingFinished.connect(
                    lambda n=nombre, c=control:
                        self.valor_cambiado.emit(n, c.text())
                )
                fijar_texto = control.setText
            # El valor inicial no debe disparar la senal.
            control.blockSignals(True)
            fijar_texto(campo["valor"])
            control.blockSignals(False)
            return control, [control]
        if tipo == "casilla":
            control = QCheckBox()
            control.toggled.connect(
                lambda estado, n=nombre:
                    self.valor_cambiado.emit(n, estado)
            )
            control.blockSignals(True)
            control.setChecked(bool(campo["valor"]))
            control.blockSignals(False)
            return control, [control]
        if tipo == "opcion":
            return self._crear_opciones(campo)
        if tipo == "lista":
            control = QComboBox()
            control.currentTextChanged.connect(
                lambda texto, n=nombre:
                    self.valor_cambiado.emit(n, texto)
            )
            control.blockSignals(True)
            control.addItems(campo["opciones"])
            if campo["valor"] in campo["opciones"]:
                control.setCurrentText(campo["valor"])
            else:
                # Sin valor elegido en el PDF: el combo queda vacio.
                control.setCurrentIndex(-1)
            control.blockSignals(False)
            return control, [control]
        # "firma": solo una etiqueta; aqui no se puede firmar.
        control = QLabel("Firma (no editable aqui)")
        return control, [control]

    def _crear_opciones(self, campo):
        """Crea un QRadioButton por opcion del grupo, en una caja.

        Los botones comparten la caja como padre, asi que Qt los toma
        como un grupo exclusivo (solo uno encendido), igual que en el
        PDF. La opcion de cada boton (su estado encendido) se guarda en
        la propiedad "estado" para poder emitirla al usuario elegirlo.
        """
        botones = []
        for opcion in campo["opciones"]:
            boton = QRadioButton(opcion)
            boton.setProperty("estado", opcion)
            boton.toggled.connect(
                lambda encendido, b=boton, n=campo["nombre"]:
                    self._al_elegir_opcion(encendido, b, n)
            )
            # El valor inicial no debe disparar la senal (ademas, al
            # encender un boton Qt apaga al anterior y eso si emite).
            boton.blockSignals(True)
            boton.setChecked(opcion == campo["valor"])
            boton.blockSignals(False)
            botones.append(boton)
        caja = QWidget()
        disposicion = QVBoxLayout(caja)
        disposicion.setContentsMargins(0, 0, 0, 0)
        disposicion.setSpacing(2)
        for boton in botones:
            disposicion.addWidget(boton)
        return caja, botones

    def _al_elegir_opcion(self, encendido, boton, nombre):
        """Emite `valor_cambiado` cuando se enciende un boton de
        opcion (se emite solo al encender: apagar no es un valor)."""
        if encendido:
            self.valor_cambiado.emit(nombre, boton.property("estado"))

    def _pintar_fila(self, nombre, resaltada):
        """Pinta o quita el fondo de la fila del campo."""
        color = self._COLOR_RESALTE if resaltada else ""
        self._etiquetas[nombre].setStyleSheet(color)
        for control in self.controles[nombre]:
            control.setStyleSheet(color)

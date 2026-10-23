"""
dialogo_nuevo_campo.py - Ventana "Nuevo campo" para crear campos PDF
====================================================================

Clase DialogoNuevoCampo (un QDialog que pide el NOMBRE de un campo
nuevo, que ya viene sugerido -por ejemplo `texto_1`-, y, si es de
texto, si es de varias lineas), segun el diseno `DISENO_CREAR_CAMPOS.md`
(Tarea 2). La ventana NO toca el documento: quien la use (main.py,
Tarea 3) es quien llama a `formularios.crear_campo` con lo que aqui se
devuelve.

- El tipo decide el titulo: "Nuevo campo de texto", "Nueva casilla" o
  "Nuevo campo de firma".
- `validar` es una funcion `nombre -> mensaje` que recibe el nombre ya
  recortado (sin espacios al inicio ni al final). Se le llama al abrir
  y con cada cambio del texto: mientras devuelva un mensaje, la
  etiqueta roja lo muestra y el boton Aceptar queda deshabilitado. Asi
  el dialogo no depende del documento y se prueba solo
  (`tests/test_dialogo_nuevo_campo.py`).
- La casilla "Varias lineas" solo aparece en los campos de texto (en
  los demas tipos queda oculta y desmarcada).
- `obtener_valores()` devuelve el nombre recortado y si es multilinea.

Los botones son de QDialogButtonBox y sus textos se ponen en espanol
("Aceptar" y "Cancelar"). El codigo usa nombres COMPLETOS de los enums
de Qt, igual que el resto del programa, para que pyright no se queje.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from formularios import TIPOS_CREABLES

# Titulo de la ventana segun el tipo de campo que se va a crear.
_TITULOS = {
    "texto": "Nuevo campo de texto",
    "casilla": "Nueva casilla",
    "firma": "Nuevo campo de firma",
}


class DialogoNuevoCampo(QDialog):
    """Pide nombre (y "Varias lineas", si es texto) para un campo nuevo.

    - `tipo`: uno de `TIPOS_CREABLES` ("texto", "casilla" o "firma");
      con otro tipo se lanza `ValueError`.
    - `nombre_sugerido`: el texto con que arranca el campo del nombre,
      ya seleccionado para poder teclear encima.
    - `multilinea_inicial`: si la casilla "Varias lineas" arranca
      marcada (solo aplica a los campos de texto).
    - `validar`: funcion `nombre -> mensaje` (cadena vacia si el nombre
      se puede usar). Se le pasa el nombre recortado.
    """

    def __init__(
        self, tipo, nombre_sugerido, multilinea_inicial, validar, parent=None
    ):
        super().__init__(parent)
        if tipo not in TIPOS_CREABLES:
            raise ValueError(
                f"Tipo de campo no valido: '{tipo}'. Tipos validos: "
                f"{', '.join(TIPOS_CREABLES)}."
            )
        self._validar = validar
        self.setWindowTitle(_TITULOS[tipo])
        self.resize(360, 150)

        layout_principal = QVBoxLayout(self)
        formulario = QFormLayout()

        self.campo_nombre = QLineEdit(nombre_sugerido)
        # El nombre sugerido viene seleccionado: si no te gusta, se
        # teclea encima y lo reemplaza.
        self.campo_nombre.selectAll()
        formulario.addRow("Nombre:", self.campo_nombre)

        # "Varias lineas" solo existe en los campos de texto: en los
        # demas tipos queda oculta y desmarcada.
        solo_texto = tipo == "texto"
        self.check_multilinea = QCheckBox("Varias lineas")
        self.check_multilinea.setChecked(
            bool(multilinea_inicial) and solo_texto
        )
        self.check_multilinea.setVisible(solo_texto)
        formulario.addRow(self.check_multilinea)

        layout_principal.addLayout(formulario)

        # Etiqueta con el mensaje de `validar`, en rojo.
        self.etiqueta_error = QLabel()
        self.etiqueta_error.setWordWrap(True)
        self.etiqueta_error.setStyleSheet("color: red;")
        layout_principal.addWidget(self.etiqueta_error)

        self.botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.boton_aceptar = self.botones.button(
            QDialogButtonBox.StandardButton.Ok
        )
        self.boton_cancelar = self.botones.button(
            QDialogButtonBox.StandardButton.Cancel
        )
        self.boton_aceptar.setText("Aceptar")
        self.boton_cancelar.setText("Cancelar")
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)
        layout_principal.addWidget(self.botones)

        # Estado inicial: el nombre sugerido pasa la validacion (o no,
        # si quien llama paso uno raro), y la etiqueta y el boton
        # arrancan consistentes con lo que hay en el campo. Despues,
        # cada tecla vuelve a validar.
        self.campo_nombre.textChanged.connect(self._actualizar_estado)
        self._actualizar_estado(self.campo_nombre.text())

    def _actualizar_estado(self, texto):
        """Muestra el mensaje de `validar` y habilita Aceptar.

        Mientras haya mensaje (cadena no vacia) el boton Aceptar queda
        deshabilitado; sin mensaje se vuelve a habilitar. El texto se
        valida recortado, igual que el que devuelve `obtener_valores`.
        """
        mensaje = self._validar(texto.strip())
        self.etiqueta_error.setText(mensaje)
        self.boton_aceptar.setEnabled(not mensaje)

    def obtener_valores(self):
        """Devuelve `(nombre, multilinea)` con lo que quedo en la
        ventana.

        - `nombre`: el texto del campo, sin espacios al inicio ni al
          final.
        - `multilinea`: si la casilla "Varias lineas" esta marcada
          (siempre `False` en los tipos que no son de texto, porque
          ahi la casilla queda oculta y desmarcada).
        """
        return (
            self.campo_nombre.text().strip(),
            self.check_multilinea.isChecked(),
        )

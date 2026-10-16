"""Pruebas de la conexion de los formularios en app/main.py (Tarea 4).

La plataforma offscreen de Qt la fija tests/conftest.py antes de
importar los modulos de la aplicacion. El PDF de prueba se crea en
memoria con fitz.Widget(), igual que en test_formularios.py y
test_panel_formularios.py.
"""

import fitz
import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication, QMessageBox

from formularios import listar_campos
from main import EditorPDF

# Se importa del mismo sitio que formularios.py, por que pyright no
# las ve re-exportadas en el paquete principal de PyMuPDF.
from pymupdf.mupdf import PDF_WIDGET_TYPE_TEXT

# QApplication unica para todas las pruebas (crear varias da error)
_aplicacion = QApplication.instance() or QApplication([])


def _agregar(pagina, nombre, tipo, rect, **extras):
    """Agrega un widget al PDF. Con setattr porque pyright no anota
    los atributos de fitz.Widget."""
    widget = fitz.Widget()
    setattr(widget, "field_name", nombre)
    setattr(widget, "field_type", tipo)
    setattr(widget, "rect", fitz.Rect(*rect))
    for clave, valor in extras.items():
        setattr(widget, clave, valor)
    return pagina.add_widget(widget)


def _documento_con_formulario():
    """PDF en memoria con un campo de texto 'nombre_cliente'."""
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    _agregar(pagina, "nombre_cliente", PDF_WIDGET_TYPE_TEXT, (72, 72, 250, 92))
    return documento


def _documento_blanco():
    """PDF en memoria sin campos de formulario."""
    documento = fitz.open()
    documento.new_page(width=595, height=842)
    return documento


def _cerrar_documento_de(ventana):
    """Cierra el documento que quede abierto en la ventana (si hay uno)."""
    if ventana.documento is not None:
        ventana.documento.close()


def _documento_de(ventana):
    """El documento de la ventana, comprobando que exista (para pyright)."""
    assert ventana.documento is not None
    return ventana.documento


def _valor_del_campo(ventana, nombre):
    """Valor actual de un campo del formulario en el documento."""
    for campo in listar_campos(_documento_de(ventana)):
        if campo["nombre"] == nombre:
            return campo["valor"]
    raise AssertionError(f"el campo '{nombre}' no esta en el documento")


def _escribir_desde_el_panel(panel, nombre, texto):
    """Llena un campo de texto del panel como lo haria el usuario.

    Le da el foco al control (seleccionar ya lo hace), cambia el texto
    y le quita el foco: asi se emite `valor_cambiado` por el camino
    real de editingFinished.
    """
    panel.seleccionar(nombre)
    control = panel.controles[nombre][0]
    assert control.hasFocus()
    control.setText(texto)
    control.clearFocus()


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_llenar_campo_de_texto_desde_el_panel_y_deshacer():
    """Llenar un campo desde el panel escribe en el PDF; Ctrl+Z lo vacia."""
    ventana = EditorPDF()
    documento = _documento_con_formulario()
    try:
        ventana.show()
        QApplication.setActiveWindow(ventana)
        ventana.cargar_documento(documento, None)
        panel = ventana.panel_formularios
        assert panel.isVisible()
        assert ventana.accion_mostrar_campos.isEnabled()

        _escribir_desde_el_panel(panel, "nombre_cliente", "Ana")

        assert _valor_del_campo(ventana, "nombre_cliente") == "Ana"
        assert ventana.historial.descripcion_deshacer() == (
            "Llenar campo: nombre_cliente"
        )
        assert ventana.accion_deshacer.isEnabled()

        # Ctrl+Z: el documento vuelve a quedar vacio, y el panel
        # recarga ese valor vacio (se recrean los controles)
        ventana.deshacer_cambio()
        assert _valor_del_campo(ventana, "nombre_cliente") == ""
        assert panel.controles["nombre_cliente"][0].text() == ""
        assert panel._ultimos_textos["nombre_cliente"] == ""
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_valor_igual_al_del_documento_no_registra_ni_escribe():
    """Avisar un valor igual al del campo no crea un paso de Deshacer."""
    ventana = EditorPDF()
    documento = _documento_con_formulario()
    try:
        ventana.show()
        QApplication.setActiveWindow(ventana)
        ventana.cargar_documento(documento, None)
        panel = ventana.panel_formularios

        # el campo ya esta vacio: avisar que sigue vacio no es un cambio
        ventana.al_cambiar_valor_campo("nombre_cliente", "")
        assert not ventana.historial.puede_deshacer()
        assert _valor_del_campo(ventana, "nombre_cliente") == ""

        # se llena "Ana" (eso si es un cambio)...
        _escribir_desde_el_panel(panel, "nombre_cliente", "Ana")
        assert ventana.historial.puede_deshacer()

        # ...se deshace (el campo vuelve a vacio)...
        ventana.deshacer_cambio()
        assert not ventana.historial.puede_deshacer()

        # ...y avisar de ese mismo vacio no registra cambio ni escribe:
        # el paso de rehacer de "Ana" sigue intacto.
        ventana.al_cambiar_valor_campo("nombre_cliente", "")
        assert not ventana.historial.puede_deshacer()
        assert ventana.historial.puede_rehacer()
        assert _valor_del_campo(ventana, "nombre_cliente") == ""
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_clic_sobre_un_campo_lo_selecciona_en_el_panel():
    """Un clic sobre un campo (herramienta 'Ninguna') lo resalta."""
    ventana = EditorPDF()
    documento = _documento_con_formulario()
    try:
        ventana.show()
        ventana.cargar_documento(documento, None)
        panel = ventana.panel_formularios
        assert ventana.combo_herramienta.currentText() == "Ninguna (solo ver)"

        # el campo "nombre_cliente" ocupa (72, 72)-(250, 92) en puntos
        # PDF; el visor multiplica por el zoom, igual que el mouse
        x = int(100 * ventana.zoom)
        y = int(80 * ventana.zoom)
        ventana.al_seleccionar_rectangulo(0, QRect(x, y, 2, 2))
        assert panel._resaltado == "nombre_cliente"

        # un punto lejos de cualquier campo no cambia la seleccion
        lejos_x = int(500 * ventana.zoom)
        lejos_y = int(700 * ventana.zoom)
        ventana.al_seleccionar_rectangulo(0, QRect(lejos_x, lejos_y, 2, 2))
        assert panel._resaltado == "nombre_cliente"
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_abrir_con_campos_muestra_el_panel_y_sin_campos_lo_oculta(monkeypatch):
    """Abrir un PDF con campos muestra el panel; sin campos lo oculta."""
    monkeypatch.setattr(
        QMessageBox, "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    ventana = EditorPDF()
    con_campos = _documento_con_formulario()
    sin_campos = _documento_blanco()
    try:
        ventana.show()

        # con campos: el panel se muestra solo y la accion se activa
        ventana.cargar_documento(con_campos, None)
        assert ventana.panel_formularios.isVisible()
        assert ventana.accion_mostrar_campos.isEnabled()
        assert ventana.accion_mostrar_campos.isChecked()

        # la accion "Mostrar campos" oculta y vuelve a mostrar el panel
        ventana.accion_mostrar_campos.setChecked(False)
        assert not ventana.panel_formularios.isVisible()
        ventana.accion_mostrar_campos.setChecked(True)
        assert ventana.panel_formularios.isVisible()

        # sin campos: el panel se oculta y la accion queda deshabilitada
        ventana.cargar_documento(sin_campos, None)
        assert not ventana.panel_formularios.isVisible()
        assert not ventana.accion_mostrar_campos.isEnabled()
        assert not ventana.accion_mostrar_campos.isChecked()

        # al cerrar el documento el panel se vacia y se oculta
        ventana.cargar_documento(_documento_con_formulario(), None)
        assert ventana.panel_formularios.isVisible()
        ventana.cerrar_documento()
        assert not ventana.panel_formularios.isVisible()
        assert not ventana.accion_mostrar_campos.isEnabled()
        assert ventana.panel_formularios.controles == {}
    finally:
        _cerrar_documento_de(ventana)
        # con_campos o sin_campos pueden seguir siendo el documento de
        # la ventana si algo fallo antes de cambiar de documento
        for pdf_de_prueba in (con_campos, sin_campos):
            if not pdf_de_prueba.is_closed:
                pdf_de_prueba.close()
        ventana.close()

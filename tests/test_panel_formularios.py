"""Pruebas de app/panel_formularios.py (Tarea 3 del diseno).

La plataforma offscreen de Qt la fija tests/conftest.py antes de
importar los modulos de la aplicacion. El PDF de prueba se crea en
memoria con fitz.Widget(), igual que en test_formularios.py.
"""

# pyright: reportMissingImports=false

import fitz
import pytest
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QRadioButton,
)

from formularios import listar_campos
from panel_formularios import PanelFormularios

# Se importan del mismo sitio que formularios.py, por que pyright no
# las ve re-exportadas en el paquete principal de PyMuPDF.
from pymupdf.mupdf import (
    PDF_FIELD_IS_READ_ONLY,
    PDF_TX_FIELD_IS_MULTILINE,
    PDF_WIDGET_TYPE_CHECKBOX,
    PDF_WIDGET_TYPE_LISTBOX,
    PDF_WIDGET_TYPE_RADIOBUTTON,
    PDF_WIDGET_TYPE_SIGNATURE,
    PDF_WIDGET_TYPE_TEXT,
)

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


def _pdf_de_formulario():
    """PDF en memoria con un campo de cada tipo del diseno."""
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    _agregar(pagina, "nombre_cliente", PDF_WIDGET_TYPE_TEXT, (72, 72, 250, 92))
    _agregar(
        pagina,
        "observaciones",
        PDF_WIDGET_TYPE_TEXT,
        (72, 110, 250, 170),
        field_flags=PDF_TX_FIELD_IS_MULTILINE,
    )
    _agregar(
        pagina, "acepta_terminos", PDF_WIDGET_TYPE_CHECKBOX, (72, 200, 90, 218)
    )
    anotacion_si = _agregar(
        pagina, "genero", PDF_WIDGET_TYPE_RADIOBUTTON, (72, 240, 90, 258),
        field_value=False,
    )
    # PyMuPDF crea los botones con estado "Yes"; a cada uno se le
    # renombra su estado para simular un grupo real.
    objeto = documento.xref_object(anotacion_si.xref, compressed=True)
    documento.update_object(
        anotacion_si.xref, objeto.replace("/Yes", "/Si")
    )
    anotacion_no = _agregar(
        pagina, "genero", PDF_WIDGET_TYPE_RADIOBUTTON, (112, 240, 130, 258),
        field_value=False,
    )
    objeto = documento.xref_object(anotacion_no.xref, compressed=True)
    documento.update_object(
        anotacion_no.xref, objeto.replace("/Yes", "/No")
    )
    _agregar(
        pagina,
        "estado",
        PDF_WIDGET_TYPE_LISTBOX,
        (72, 280, 250, 340),
        choice_values=["CDMX", "Jalisco", "NL"],
    )
    _agregar(
        pagina,
        "folio",
        PDF_WIDGET_TYPE_TEXT,
        (72, 360, 250, 380),
        field_flags=PDF_FIELD_IS_READ_ONLY,
    )
    _agregar(
        pagina, "firma_solicitante", PDF_WIDGET_TYPE_SIGNATURE, (72, 400, 250, 450)
    )
    return documento


def _campos_de_prueba():
    """Lista de campos del PDF de prueba (el documento se puede cerrar:
    los campos son datos simples, sin enlaces al PDF)."""
    documento = _pdf_de_formulario()
    try:
        return listar_campos(documento)
    finally:
        documento.close()


def test_cargar_usa_el_control_segun_el_tipo():
    """Cada tipo del diseno sale con su control en el panel."""
    panel = PanelFormularios()
    panel.cargar(_campos_de_prueba())

    assert panel.windowTitle() == "Campos del formulario"

    texto = panel.controles["nombre_cliente"][0]
    assert isinstance(texto, QLineEdit)

    multilinea = panel.controles["observaciones"][0]
    assert isinstance(multilinea, QPlainTextEdit)

    casilla = panel.controles["acepta_terminos"][0]
    assert isinstance(casilla, QCheckBox)

    botones = panel.controles["genero"]
    assert len(botones) == 2
    assert all(isinstance(boton, QRadioButton) for boton in botones)
    # Los botones muestran el nombre de su estado encendido.
    assert [boton.text() for boton in botones] == ["Si", "No"]
    # Ninguno encendido: el grupo no tiene valor.
    assert not any(boton.isChecked() for boton in botones)

    lista = panel.controles["estado"][0]
    assert isinstance(lista, QComboBox)
    assert [lista.itemText(i) for i in range(lista.count())] == [
        "CDMX",
        "Jalisco",
        "NL",
    ]
    # Sin valor en el PDF: el combo queda sin elegir.
    assert lista.currentIndex() == -1

    firma = panel.controles["firma_solicitante"][0]
    assert isinstance(firma, QLabel)
    assert firma.text() == "Firma (no editable aqui)"


def test_cargar_deshabilita_el_campo_de_solo_lectura():
    """El campo de solo lectura sale con el control deshabilitado."""
    panel = PanelFormularios()
    panel.cargar(_campos_de_prueba())

    assert not panel.controles["folio"][0].isEnabled()
    assert panel.controles["nombre_cliente"][0].isEnabled()


def test_cargar_no_emite_valor_cambiado():
    """Armar las filas no cuenta como cambio del usuario."""
    panel = PanelFormularios()
    recibidos = []
    panel.valor_cambiado.connect(
        lambda nombre, valor: recibidos.append((nombre, valor))
    )
    campos = _campos_de_prueba()

    panel.cargar(campos)
    panel.cargar(campos)

    assert recibidos == []


def test_marcar_casilla_emite_un_solo_valor_cambiado():
    """Marcar (y desmarcar) la casilla emite un evento por accion."""
    panel = PanelFormularios()
    panel.cargar(_campos_de_prueba())
    recibidos = []
    panel.valor_cambiado.connect(
        lambda nombre, valor: recibidos.append((nombre, valor))
    )

    casilla = panel.controles["acepta_terminos"][0]
    casilla.setChecked(True)
    assert recibidos == [("acepta_terminos", True)]

    casilla.setChecked(False)
    assert recibidos == [("acepta_terminos", True), ("acepta_terminos", False)]


def test_elegir_opcion_emite_su_estado():
    """Elegir un boton del grupo emite el nombre de su estado."""
    panel = PanelFormularios()
    panel.cargar(_campos_de_prueba())
    recibidos = []
    panel.valor_cambiado.connect(
        lambda nombre, valor: recibidos.append((nombre, valor))
    )

    botones = panel.controles["genero"]
    botones[1].setChecked(True)

    assert recibidos == [("genero", "No")]
    # El grupo es exclusivo: al encender uno se apaga el otro.
    assert not botones[0].isChecked()


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_seleccionar_resalta_y_da_foco():
    """seleccionar() resalta la fila y le da foco a su control."""
    panel = PanelFormularios()
    panel.cargar(_campos_de_prueba())
    panel.show()
    # En la plataforma offscreen la ventana nunca queda "activa" sola
    # y Qt no da el foco; con setActiveWindow si (en pantalla real no
    # hace falta; la funcion esta deprecada desde Qt 6.5).
    QApplication.setActiveWindow(panel)

    panel.seleccionar("nombre_cliente")

    assert panel._resaltado == "nombre_cliente"
    assert panel._etiquetas["nombre_cliente"].styleSheet() != ""
    texto = panel.controles["nombre_cliente"][0]
    assert texto.hasFocus()

    # Al elegir otro campo, el resalte anterior se quita.
    panel.seleccionar("estado")
    assert panel._resaltado == "estado"
    assert panel._etiquetas["nombre_cliente"].styleSheet() == ""
    assert panel._etiquetas["estado"].styleSheet() != ""


def test_seleccionar_con_nombre_desconocido_no_hace_nada():
    """Un nombre que no esta en el panel no truena."""
    panel = PanelFormularios()
    panel.cargar(_campos_de_prueba())
    panel.seleccionar("no_existe")
    assert panel._resaltado is None

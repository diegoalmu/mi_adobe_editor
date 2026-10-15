"""
formularios.py - Lectura de campos de formulario PDF
=====================================================

Funciones para leer los campos que YA trae un PDF (formato AcroForm),
segun el diseno `DISENO_FORMULARIOS.md` (Tarea 1):

- `listar_campos(documento)`: lista de diccionarios, uno por campo. Los
  botones de opcion que comparten nombre se agrupan en un solo campo.
- `tiene_formulario(documento)`: `True` si hay al menos un campo listable.
- `es_solo_xfa(documento)`: `True` si el PDF usa XFA (formato viejo de
  Adobe LiveCycle) y no tiene campos normales: ese formulario no se
  puede llenar con este programa.

Tipos posibles de campo (los del diseno): `"texto"`, `"casilla"`,
`"opcion"`, `"lista"` y `"firma"`. Los botones de accion (pushbotones)
no se listan, porque no se pueden llenar.

Este modulo no escribe en el PDF (eso viene en la Tarea 2) ni crea
ventanas: se prueba con `tests/test_formularios.py` sin Qt.
"""

# Las constantes de los tipos de campo y de las banderas del PDF viven
# en el modulo "mupdf" de PyMuPDF; se importan de ahi porque PyMuPDF
# las re-exporta en su paquete principal de forma dinamica, y pyright
# no las ve por ese camino (mismos valores, mismo objeto en ejecucion).
from pymupdf.mupdf import (
    PDF_FIELD_IS_READ_ONLY,
    PDF_TX_FIELD_IS_MULTILINE,
    PDF_WIDGET_TYPE_CHECKBOX,
    PDF_WIDGET_TYPE_COMBOBOX,
    PDF_WIDGET_TYPE_LISTBOX,
    PDF_WIDGET_TYPE_RADIOBUTTON,
    PDF_WIDGET_TYPE_SIGNATURE,
    PDF_WIDGET_TYPE_TEXT,
)


def listar_campos(documento):
    """Devuelve los campos del formulario en una lista de diccionarios.

    Un diccionario por campo, con esta forma (del diseno):

        {"nombre": "nombre_cliente", "tipo": "texto", "valor": "",
         "opciones": [], "solo_lectura": False, "multilinea": False,
         "paginas": [0], "rects": [fitz.Rect(...)], "xrefs": [123]}

    - `paginas`, `rects` y `xrefs` tienen una entrada por cada aparicion
      del campo en el PDF; para un grupo de botones de opcion hay una
      entrada por cada boton del grupo.
    - `opciones` solo se usa en `"lista"` (las opciones del PDF) y en
      `"opcion"` (el estado encendido de cada boton del grupo).
    - El orden es el del documento: pagina por pagina, y en cada pagina
      el orden en que PyMuPDF encuentra los campos.
    """
    campos = []
    # Nombre del campo de opciones -> posicion en la lista `campos`.
    # Solo se usa para agrupar los botones de opcion del mismo grupo.
    indices_grupos = {}
    for num_pagina in range(documento.page_count):
        pagina = documento[num_pagina]
        for widget in pagina.widgets():
            tipo = _tipo_de_widget(widget)
            if tipo is None:
                continue  # botones de accion y tipos desconocidos
            if tipo == "opcion":
                campo = _campo_de_grupo(
                    campos, indices_grupos, widget
                )
            else:
                campo = _nuevo_campo(widget, tipo)
                campos.append(campo)
            campo["paginas"].append(num_pagina)
            campo["rects"].append(widget.rect)
            campo["xrefs"].append(widget.xref)
    return campos


def tiene_formulario(documento):
    """`True` si el PDF tiene al menos un campo que se pueda listar."""
    return bool(listar_campos(documento))


def es_solo_xfa(documento):
    """`True` si el PDF tiene XFA y ningun campo normal.

    Un PDF con XFA y ademas campos AcroForm normales si se puede llenar
    (por los campos normales), por eso aqui se exige que no haya
    ninguno.
    """
    return _hay_xfa(documento) and not tiene_formulario(documento)


# ---------------------------------------------------------------------
# INTERNOS
# ---------------------------------------------------------------------


def _tipo_de_widget(widget):
    """Traduce el tipo de PyMuPDF al nombre del diseno.

    Devuelve `None` si el campo no se lista: los botones de accion
    (`PDF_WIDGET_TYPE_BUTTON`) y los tipos desconocidos.
    """
    if widget.field_type == PDF_WIDGET_TYPE_TEXT:
        return "texto"
    if widget.field_type == PDF_WIDGET_TYPE_CHECKBOX:
        return "casilla"
    if widget.field_type == PDF_WIDGET_TYPE_RADIOBUTTON:
        return "opcion"
    if widget.field_type == PDF_WIDGET_TYPE_COMBOBOX:
        return "lista"
    if widget.field_type == PDF_WIDGET_TYPE_LISTBOX:
        return "lista"
    if widget.field_type == PDF_WIDGET_TYPE_SIGNATURE:
        return "firma"
    # PDF_WIDGET_TYPE_BUTTON (botones de accion) y los tipos
    # desconocidos no se listan.
    return None


def _nuevo_campo(widget, tipo):
    """Crea el diccionario de un campo a partir de su primer widget."""
    return {
        "nombre": widget.field_name,
        "tipo": tipo,
        "valor": _valor_de_widget(widget, tipo),
        "opciones": _opciones_de_widget(widget, tipo),
        "solo_lectura": bool(
            widget.field_flags & PDF_FIELD_IS_READ_ONLY
        ),
        "multilinea": bool(
            widget.field_flags & PDF_TX_FIELD_IS_MULTILINE
        ),
        "paginas": [],
        "rects": [],
        "xrefs": [],
    }


def _campo_de_grupo(campos, indices_grupos, widget):
    """Regresa el campo de un grupo de botones de opcion.

    Si el nombre ya se ha visto (es otro boton del mismo grupo) se
    agregan su estado encendido a las opciones y su valor al campo; si
    no, se crea el campo nuevo y se anota su posicion en
    `indices_grupos`.
    """
    if widget.field_name in indices_grupos:
        campo = campos[indices_grupos[widget.field_name]]
        _agregar_boton_al_grupo(campo, widget)
        return campo
    campo = _nuevo_campo(widget, "opcion")
    campos.append(campo)
    indices_grupos[widget.field_name] = len(campos) - 1
    return campo


def _agregar_boton_al_grupo(campo, widget):
    """Agrega otro boton de opcion a un grupo ya existente."""
    estado = _estado_encendido(widget)
    if estado not in campo["opciones"]:
        campo["opciones"].append(estado)
    # Si este boton esta encendido, esa es la opcion elegida del grupo.
    valor = widget.field_value
    if valor and valor != "Off":
        campo["valor"] = str(valor)
    # El grupo es de solo lectura si todos sus botones lo son.
    campo["solo_lectura"] = campo["solo_lectura"] and bool(
        widget.field_flags & PDF_FIELD_IS_READ_ONLY
    )


def _valor_de_widget(widget, tipo):
    """Valor inicial del campo, segun su tipo.

    - `"texto"` y `"lista"`: el texto del campo, vacio si no tiene.
    - `"casilla"`: `True` si esta encendida, `False` si no.
    - `"opcion"`: nombre del estado encendido, vacio si esta apagada.
    - `"firma"`: siempre vacio (aqui no se puede firmar).
    """
    valor = widget.field_value
    if tipo == "casilla":
        return bool(valor) and valor != "Off"
    if tipo == "opcion":
        if not valor or valor == "Off":
            return ""
        return str(valor)
    if tipo == "firma":
        return ""
    return valor or ""


def _opciones_de_widget(widget, tipo):
    """Lista de opciones del campo (del diseno: solo en listas y grupos).

    - `"lista"`: las opciones que trae el PDF (`choice_values`).
    - `"opcion"`: el estado encendido de este boton (una sola opcion por
      ahora; las demas se agregan con `_agregar_boton_al_grupo`).
    - Los demas tipos: lista vacia.
    """
    if tipo == "lista":
        return list(widget.choice_values or [])
    if tipo == "opcion":
        return [_estado_encendido(widget)]
    return []


def _estado_encendido(widget):
    """Nombre del estado encendido de un boton de opcion.

    PyMuPDF lo lee de la apariencia del campo; normalmente es `"Yes"`,
    pero en PDFs reales puede ser cualquier nombre ("Si", "1", ...).
    Cuando el boton aun no tiene estado definido, PyMuPDF devuelve
    `True`; en ese caso se usa `"Yes"`, que es el estandar del PDF.
    """
    estado = widget.on_state()
    if not estado or estado is True:
        return "Yes"
    return str(estado)


def _hay_xfa(documento):
    """`True` si el AcroForm del catalogo del PDF declara XFA."""
    tipo, valor = documento.xref_get_key(
        documento.pdf_catalog(), "AcroForm"
    )
    if tipo == "xref":
        # El AcroForm es un objeto indirecto: se busca XFA dentro.
        xref_acroform = int(valor.split()[0])
        tipo_xfa, _ = documento.xref_get_key(xref_acroform, "XFA")
        return tipo_xfa != "null"
    if tipo == "dict":
        # El AcroForm esta escrito en el catalogo, sin objeto propio.
        return "XFA" in valor
    return False

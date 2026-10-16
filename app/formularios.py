"""
formularios.py - Lectura y escritura de campos de formulario PDF
================================================================

Funciones para leer y escribir los campos que YA trae un PDF (formato
AcroForm), segun el diseno `DISENO_FORMULARIOS.md` (Tareas 1 y 2):

- `listar_campos(documento)`: lista de diccionarios, uno por nombre de
  campo. Todas las apariciones de un mismo nombre (varios botones de
  opcion de un grupo, o un campo repetido en el encabezado de cada
  pagina) comparten un solo diccionario.
- `tiene_formulario(documento)`: `True` si hay al menos un campo listable.
- `es_solo_xfa(documento)`: `True` si el PDF usa XFA (formato viejo de
  Adobe LiveCycle) y no tiene campos normales: ese formulario no se
  puede llenar con este programa.
- `escribir_valor(documento, campo, valor)`: escribe el valor en todos
  los widgets del campo y regenera su apariencia, para que el texto se
  vea en cualquier visor.

Tipos posibles de campo (los del diseno): `"texto"`, `"casilla"`,
`"opcion"`, `"lista"` y `"firma"`. Los botones de accion (pushbotones)
no se listan, porque no se pueden llenar.

Este modulo no crea ventanas: se prueba con `tests/test_formularios.py`
sin Qt.
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

    Un diccionario por nombre de campo, con esta forma (del diseno):

        {"nombre": "nombre_cliente", "tipo": "texto", "valor": "",
         "opciones": [], "solo_lectura": False, "multilinea": False,
         "paginas": [0], "rects": [fitz.Rect(...)], "xrefs": [123]}

    - Todos los widgets que comparten `field_name` forman UN solo
      diccionario: los botones de opcion de un grupo, y tambien un campo
      de texto, casilla o lista que se repite en varias paginas (por
      ejemplo el nombre en el encabezado de cada hoja).
    - `paginas`, `rects` y `xrefs` tienen una entrada por cada aparicion
      del campo en el PDF.
    - `opciones` solo se usa en `"lista"` (las opciones del PDF) y en
      `"opcion"` (el estado encendido de cada boton del grupo).
    - El orden es el del documento: pagina por pagina, y en cada pagina
      el orden en que PyMuPDF encuentra los campos.
    """
    campos = []
    # Nombre del campo -> posicion en la lista `campos`. Se usa para
    # agrupar en un solo diccionario todas las apariciones de un nombre
    # (grupos de opcion y campos repetidos en varias paginas).
    indices_por_nombre = {}
    for num_pagina in range(documento.page_count):
        pagina = documento[num_pagina]
        for widget in pagina.widgets():
            tipo = _tipo_de_widget(widget)
            if tipo is None:
                continue  # botones de accion y tipos desconocidos
            nombre = widget.field_name
            if nombre in indices_por_nombre:
                campo = campos[indices_por_nombre[nombre]]
                _agregar_aparicion(campo, widget, tipo)
            else:
                campo = _nuevo_campo(widget, tipo)
                campos.append(campo)
                indices_por_nombre[nombre] = len(campos) - 1
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


def escribir_valor(documento, campo, valor):
    """Escribe `valor` en el campo y regenera su apariencia en el PDF.

    - `"texto"`: `valor` debe ser un string (con `"\\n"` si es
      multiliena).
    - `"casilla"`: `True` (encendida) o `False` (apagada).
    - `"opcion"`: el estado encendido de uno de los botones del grupo;
      los demas botones quedan apagados.
    - `"lista"`: una de las opciones del campo.
    - Se escribe en TODOS los widgets del campo (el mismo nombre puede
      aparecer en varias paginas) y a cada uno se le llama
      `widget.update()`, que regenera la apariencia para que el valor
      se vea en cualquier visor.
    - Lanza `ValueError` (sin tocar el documento) si el campo es de
      firma, de solo lectura, no existe en el documento, o si el valor
      no es valido para el tipo del campo.
    """
    tipo = campo["tipo"]
    if tipo == "firma":
        raise ValueError(
            f"El campo '{campo['nombre']}' es de firma y no se puede "
            "llenar aqui."
        )
    if campo["solo_lectura"]:
        raise ValueError(
            f"El campo '{campo['nombre']}' es de solo lectura y no se "
            "puede modificar."
        )
    _validar_valor(campo, valor)
    escritos = _escribir_en_widgets(documento, campo, tipo, valor)
    if not escritos:
        raise ValueError(
            f"El campo '{campo['nombre']}' no se encuentra en el "
            "documento."
        )


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


def _agregar_aparicion(campo, widget, tipo):
    """Agrega al campo otro widget que tiene su mismo nombre.

    El valor, las opciones y las banderas del diccionario salen del
    PRIMER widget encontrado (todos los widgets de un mismo nombre
    comparten el valor en el PDF); aqui solo se actualiza lo que puede
    cambiar entre apariciones:

    - `"opcion"`: se agrega el estado encendido del boton a las opciones
      (sin repetir) y, si el boton esta encendido, esa es la opcion
      elegida del grupo.
    - Solo lectura: el grupo es de solo lectura si todas sus
      apariciones lo son.
    """
    if tipo == "opcion":
        estado = _estado_encendido(widget)
        if estado not in campo["opciones"]:
            campo["opciones"].append(estado)
        # Si este boton esta encendido, esa es la opcion del grupo.
        valor = widget.field_value
        if valor and valor != "Off":
            campo["valor"] = str(valor)
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
      ahora; las demas se agregan con `_agregar_aparicion`).
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


def _validar_valor(campo, valor):
    """Lanza `ValueError` si `valor` no es valido para el tipo del campo.

    - `"texto"`: debe ser un string.
    - `"casilla"`: debe ser `True` o `False`.
    - `"opcion"` y `"lista"`: debe ser una de las `opciones` del campo.
    """
    tipo = campo["tipo"]
    nombre = campo["nombre"]
    if tipo == "texto" and not isinstance(valor, str):
        raise ValueError(
            f"El campo '{nombre}' es de texto: el valor debe ser un "
            f"string, no {type(valor).__name__}."
        )
    if tipo == "casilla" and not isinstance(valor, bool):
        raise ValueError(
            f"El campo '{nombre}' es de casilla: el valor debe ser "
            "True o False."
        )
    if tipo in ("opcion", "lista") and valor not in campo["opciones"]:
        raise ValueError(
            f"El valor '{valor}' no es una opcion valida para el campo "
            f"'{nombre}': opciones {campo['opciones']}."
        )


def _escribir_en_widgets(documento, campo, tipo, valor):
    """Escribe `valor` en cada widget del campo y regenera su
    apariencia. Devuelve cuantos widgets se escribieron.

    Se busca cada widget por su `xref` (uno por cada aparicion registrada
    en `campo`), recorriendo solo las paginas donde aparece. La pagina
    se guarda en una variable mientras se escribe: PyMuPDF solo deja
    llamar a `widget.update()` mientras su pagina esta viva en memoria.
    """
    escritos = 0
    for num_pagina, xref in zip(campo["paginas"], campo["xrefs"]):
        pagina = documento[num_pagina]
        for widget in pagina.widgets():
            if widget.xref == xref:
                _asignar_valor(widget, tipo, valor)
                widget.update()
                escritos += 1
                break
    return escritos


def _asignar_valor(widget, tipo, valor):
    """Pone `valor` en un widget y prepara su apariencia.

    - `"casilla"`: PyMuPDF acepta `True`/`False` y traduce al estado
      encendido del PDF (normalmente `"Yes"`) o a `"Off"`.
    - `"opcion"`: solo el boton cuyo estado encendido coincide con
      `valor` se enciende; los demas botones del grupo se apagan
      (PyMuPDF no lo hace solo: si no, todos quedarian encendidos).
      La comparacion se hace con `_estado_encendido`, igual que en
      `listar_campos`: si `on_state()` devuelve `True` (boton sin
      estado On definido), la opcion registrada es `"Yes"` y comparar
      con `on_state()` directamente nunca coincidiria.
    - Los demas tipos: el valor va tal cual al campo.
    """
    if tipo == "opcion":
        if _estado_encendido(widget) == valor:
            widget.field_value = valor
        else:
            widget.field_value = False
        return
    widget.field_value = valor


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

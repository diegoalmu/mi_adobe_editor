"""Pruebas de app/formularios.py (Tareas 1 y 2 del diseno de Formularios).

Este modulo solo usa PyMuPDF (sin Qt), asi que las pruebas corren sin
QApplication. Cada prueba crea su propio PDF en memoria con campos,
usando `fitz.Widget()` y `pagina.add_widget()`, sin archivos externos.

El import va sin prefijo de paquete (from formularios import ...) porque
asi corre el programa.
"""

import fitz
import pytest

from formularios import (
    es_solo_xfa,
    escribir_valor,
    listar_campos,
    tiene_formulario,
)

# Se importan del mismo sitio que formularios.py (el modulo "mupdf" de
# PyMuPDF), porque el paquete principal las re-exporta de forma dinamica
# y pyright no las ve por ahi.
from pymupdf.mupdf import (
    PDF_FIELD_IS_READ_ONLY,
    PDF_TX_FIELD_IS_MULTILINE,
    PDF_WIDGET_TYPE_BUTTON,
    PDF_WIDGET_TYPE_CHECKBOX,
    PDF_WIDGET_TYPE_LISTBOX,
    PDF_WIDGET_TYPE_RADIOBUTTON,
    PDF_WIDGET_TYPE_SIGNATURE,
    PDF_WIDGET_TYPE_TEXT,
)


def _nuevo_widget(**propiedades):
    """Crea un widget de PyMuPDF con las propiedades dadas.

    Se usa `setattr` porque PyMuPDF no anota los tipos de los atributos
    de `Widget` y pyright se queja si se asignan directamente.
    """
    widget = fitz.Widget()
    for nombre, valor in propiedades.items():
        setattr(widget, nombre, valor)
    return widget


def _agregar_texto(
    pagina, nombre, rect, multilinea=False, solo_lectura=False
):
    """Agrega un campo de texto al PDF y regresa su widget."""
    banderas = 0
    if multilinea:
        banderas = PDF_TX_FIELD_IS_MULTILINE
    if solo_lectura:
        banderas = banderas | PDF_FIELD_IS_READ_ONLY
    widget = _nuevo_widget(
        field_name=nombre,
        field_type=PDF_WIDGET_TYPE_TEXT,
        field_flags=banderas,
        rect=fitz.Rect(*rect),
    )
    pagina.add_widget(widget)
    return widget


def _agregar_casilla(pagina, nombre, rect):
    """Agrega una casilla de verificacion al PDF."""
    widget = _nuevo_widget(
        field_name=nombre,
        field_type=PDF_WIDGET_TYPE_CHECKBOX,
        rect=fitz.Rect(*rect),
    )
    pagina.add_widget(widget)
    return widget


def _agregar_opcion(pagina, nombre, rect, estado_encendido="Yes"):
    """Agrega un boton de opcion al PDF.

    PyMuPDF crea los botones de opcion con el estado encendido "Yes";
    para simular grupos reales (donde cada boton tiene su propio
    nombre de estado) se renombra ese estado en el PDF.
    """
    widget = _nuevo_widget(
        field_name=nombre,
        field_type=PDF_WIDGET_TYPE_RADIOBUTTON,
        rect=fitz.Rect(*rect),
        # Sin esto, PyMuPDF no crea el boton de opcion (lo toma como
        # un boton nuevo y falla al agregarlo).
        field_value=False,
    )
    anotacion = pagina.add_widget(widget)
    if estado_encendido != "Yes":
        documento = pagina.parent
        objeto = documento.xref_object(
            anotacion.xref, compressed=True
        )
        documento.update_object(
            anotacion.xref,
            objeto.replace("/Yes", f"/{estado_encendido}"),
        )
    return widget


def _agregar_lista(pagina, nombre, rect, opciones):
    """Agrega una lista (listbox) con las opciones dadas."""
    widget = _nuevo_widget(
        field_name=nombre,
        field_type=PDF_WIDGET_TYPE_LISTBOX,
        rect=fitz.Rect(*rect),
        choice_values=opciones,
    )
    pagina.add_widget(widget)
    return widget


def _agregar_firma(pagina, nombre, rect):
    """Agrega un campo de firma al PDF."""
    widget = _nuevo_widget(
        field_name=nombre,
        field_type=PDF_WIDGET_TYPE_SIGNATURE,
        rect=fitz.Rect(*rect),
    )
    pagina.add_widget(widget)
    return widget


def _agregar_boton_accion(pagina, nombre, rect):
    """Agrega un boton de accion (pushboton), que no debe listarse."""
    widget = _nuevo_widget(
        field_name=nombre,
        field_type=PDF_WIDGET_TYPE_BUTTON,
        rect=fitz.Rect(*rect),
        button_caption="Enviar",
    )
    pagina.add_widget(widget)
    return widget


def _pdf_de_formulario():
    """PDF en memoria con todos los tipos de campo del diseno.

    Campos: texto, texto multilnea, casilla, dos botones de opcion del
    mismo grupo (estados "Si" y "No"), lista con 3 opciones, campo de
    solo lectura, firma y un boton de accion (que no se lista).
    """
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    _agregar_texto(pagina, "nombre_cliente", (72, 72, 250, 92))
    _agregar_texto(
        pagina, "observaciones", (72, 110, 250, 170), multilinea=True
    )
    _agregar_casilla(pagina, "acepta_terminos", (72, 200, 90, 218))
    _agregar_opcion(pagina, "genero", (72, 240, 90, 258), "Si")
    _agregar_opcion(pagina, "genero", (112, 240, 130, 258), "No")
    _agregar_lista(
        pagina, "estado", (72, 280, 250, 340), ["CDMX", "Jalisco", "NL"]
    )
    _agregar_texto(
        pagina, "folio", (72, 360, 250, 380), solo_lectura=True
    )
    _agregar_firma(pagina, "firma_solicitante", (72, 400, 250, 450))
    _agregar_boton_accion(pagina, "enviar", (72, 470, 150, 495))
    return documento


def _pdf_xfa():
    """PDF en memoria que solo tiene XFA (sin campos normales)."""
    documento = fitz.open()
    documento.new_page(width=595, height=842)
    xref_acroform = documento.get_new_xref()
    documento.update_object(
        xref_acroform, "<< /Fields [] /XFA (xfa:xdp) >>"
    )
    documento.xref_set_key(
        documento.pdf_catalog(), "AcroForm", f"{xref_acroform} 0 R"
    )
    return documento


def _pdf_texto_en_dos_paginas():
    """PDF en memoria con un campo de texto repetido en dos paginas.

    Simula el encabezado de un formato de varias hojas: el mismo campo
    (mismo `field_name`) aparece una vez por pagina.
    """
    documento = fitz.open()
    documento.new_page(width=595, height=842)
    documento.new_page(width=595, height=842)
    # Se recarga cada pagina con `documento[n]`: al crear la segunda,
    # PyMuPDF invalida el enlace de la primera.
    for num_pagina in (0, 1):
        _agregar_texto(
            documento[num_pagina], "nombre_cliente", (72, 72, 250, 92)
        )
    return documento


def _campo_de(nombre, campos):
    """Regresa el unico campo con ese nombre (falla si hay 0 o mas)."""
    encontrados = [campo for campo in campos if campo["nombre"] == nombre]
    assert len(encontrados) == 1
    return encontrados[0]


def test_listar_campos_devuelve_un_diccionario_por_tipo():
    """Cada tipo del diseno sale con su nombre, valor y opciones."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)

        # El boton de accion no se lista: quedan 7 campos.
        assert len(campos) == 7

        texto = _campo_de("nombre_cliente", campos)
        assert texto["tipo"] == "texto"
        assert texto["valor"] == ""
        assert texto["opciones"] == []
        assert not texto["solo_lectura"]
        assert not texto["multilinea"]

        casilla = _campo_de("acepta_terminos", campos)
        assert casilla["tipo"] == "casilla"
        assert casilla["valor"] is False
        assert casilla["opciones"] == []

        lista = _campo_de("estado", campos)
        assert lista["tipo"] == "lista"
        assert lista["valor"] == ""
        assert lista["opciones"] == ["CDMX", "Jalisco", "NL"]

        firma = _campo_de("firma_solicitante", campos)
        assert firma["tipo"] == "firma"
        assert firma["valor"] == ""
    finally:
        documento.close()


def test_grupo_de_opciones_sale_como_un_solo_campo():
    """Los dos botones de opcion del mismo nombre forman un campo."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)
        grupos = [c for c in campos if c["nombre"] == "genero"]

        assert len(grupos) == 1
        grupo = grupos[0]
        assert grupo["tipo"] == "opcion"
        # Cada boton aporta su pagina, rect y xref.
        assert len(grupo["paginas"]) == 2
        assert len(grupo["rects"]) == 2
        assert len(grupo["xrefs"]) == 2
        # Cada boton tiene su propio estado encendido.
        assert grupo["opciones"] == ["Si", "No"]
        # Ninguno esta encendido: el grupo no tiene valor.
        assert grupo["valor"] == ""
    finally:
        documento.close()


def test_multilinea_y_solo_lectura_se_detectan_en_las_banderas():
    """El texto multilnea y el campo de solo lectura vienen marcados."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)

        multilinea = _campo_de("observaciones", campos)
        assert multilinea["tipo"] == "texto"
        assert multilinea["multilinea"]

        solo_lectura = _campo_de("folio", campos)
        assert solo_lectura["tipo"] == "texto"
        assert solo_lectura["solo_lectura"]
        assert not solo_lectura["multilinea"]
    finally:
        documento.close()


def test_paginas_rects_y_xrefs_apuntan_al_pdf():
    """Las coordenadas y xrefs del campo coinciden con el widget real."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)
        texto = _campo_de("nombre_cliente", campos)

        assert texto["paginas"] == [0]
        rect_pdf = fitz.Rect(72, 72, 250, 92)
        assert texto["rects"][0] == rect_pdf
        # El xref guardado es el de la anotacion real del PDF.
        widget_real = next(documento[0].widgets())
        assert texto["xrefs"] == [widget_real.xref]
    finally:
        documento.close()


def test_pdf_sin_campos_no_tiene_formulario():
    """Un PDF normal (solo texto) no tiene formulario."""
    documento = fitz.open()
    try:
        pagina = documento.new_page(width=595, height=842)
        pagina.insert_text((72, 100), "hola", fontsize=12)
        assert listar_campos(documento) == []
        assert not tiene_formulario(documento)
    finally:
        documento.close()


def test_pdf_con_campos_si_tiene_formulario():
    """El PDF de prueba tiene formulario: hay campos listables."""
    documento = _pdf_de_formulario()
    try:
        assert tiene_formulario(documento)
    finally:
        documento.close()


def test_pdf_solo_xfa_se_detecta_y_el_normal_no():
    """es_solo_xfa solo es True si hay XFA y ningun campo normal."""
    documento_xfa = _pdf_xfa()
    documento_formulario = _pdf_de_formulario()
    documento_normal = fitz.open()
    try:
        assert es_solo_xfa(documento_xfa)
        # Con XFA pero tambien con campos normales: si se puede llenar.
        assert not es_solo_xfa(documento_formulario)
        # Sin XFA ni campos: no es un formulario XFA.
        documento_normal.new_page()
        assert not es_solo_xfa(documento_normal)
    finally:
        documento_xfa.close()
        documento_formulario.close()
        documento_normal.close()


def test_campo_repetido_en_dos_paginas_sale_una_sola_vez():
    """Un texto con el mismo nombre en dos paginas es un solo campo."""
    documento = _pdf_texto_en_dos_paginas()
    try:
        campos = listar_campos(documento)

        assert len(campos) == 1
        campo = campos[0]
        assert campo["nombre"] == "nombre_cliente"
        assert campo["tipo"] == "texto"
        # Cada aparicion aporta su pagina, rect y xref.
        assert campo["paginas"] == [0, 1]
        assert len(campo["rects"]) == 2
        assert len(campo["xrefs"]) == 2
    finally:
        documento.close()


def test_escribir_valor_llena_los_tipos_y_persisten_al_guardar():
    """Se llenan los tipos, se guarda con tobytes() y al reabrir
    quedan los valores."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)
        escribir_valor(
            documento, _campo_de("nombre_cliente", campos), "Ana Lopez"
        )
        escribir_valor(
            documento,
            _campo_de("observaciones", campos),
            "Una linea\nOtra linea",
        )
        escribir_valor(
            documento, _campo_de("acepta_terminos", campos), True
        )
        escribir_valor(documento, _campo_de("genero", campos), "Si")
        escribir_valor(documento, _campo_de("estado", campos), "Jalisco")
        datos = documento.tobytes()
    finally:
        documento.close()

    reabierto = fitz.open(stream=datos, filetype="pdf")
    try:
        campos = listar_campos(reabierto)
        assert _campo_de("nombre_cliente", campos)["valor"] == "Ana Lopez"
        assert (
            _campo_de("observaciones", campos)["valor"]
            == "Una linea\nOtra linea"
        )
        assert _campo_de("acepta_terminos", campos)["valor"] is True
        assert _campo_de("genero", campos)["valor"] == "Si"
        assert _campo_de("estado", campos)["valor"] == "Jalisco"
    finally:
        reabierto.close()


def test_escribir_valor_actualiza_todos_los_widgets_del_campo():
    """Un texto repetido en dos paginas: los dos widgets quedan con el
    valor nuevo al guardar con tobytes() y reabrir."""
    documento = _pdf_texto_en_dos_paginas()
    try:
        campos = listar_campos(documento)
        escribir_valor(
            documento,
            _campo_de("nombre_cliente", campos),
            "Ana Lopez",
        )
        datos = documento.tobytes()
    finally:
        documento.close()

    reabierto = fitz.open(stream=datos, filetype="pdf")
    try:
        valores = []
        for num_pagina in (0, 1):
            for widget in reabierto[num_pagina].widgets():
                # Con getattr porque PyMuPDF no anota el tipo de
                # "field_value" y pyright lo ve como Annot.
                valores.append(getattr(widget, "field_value"))
        assert valores == ["Ana Lopez", "Ana Lopez"]
    finally:
        reabierto.close()


def test_escribir_valor_invalido_en_lista_lanza_error():
    """Un valor que no es de la lista lanza ValueError sin tocar el
    documento."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)
        lista = _campo_de("estado", campos)

        with pytest.raises(ValueError):
            escribir_valor(documento, lista, "Oaxaca")

        # El documento no se modifica: el campo sigue vacio.
        assert _campo_de("estado", listar_campos(documento))["valor"] == ""
    finally:
        documento.close()


def test_escribir_valor_en_solo_lectura_lanza_error():
    """Escribir en un campo de solo lectura lanza ValueError sin tocar
    el documento."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)
        solo_lectura = _campo_de("folio", campos)

        with pytest.raises(ValueError):
            escribir_valor(documento, solo_lectura, "FOLIO-1")

        # El documento no se modifica: el campo sigue vacio.
        assert _campo_de("folio", listar_campos(documento))["valor"] == ""
    finally:
        documento.close()


def test_escribir_valor_en_firma_lanza_error():
    """Escribir en un campo de firma lanza ValueError (aqui no se
    puede firmar)."""
    documento = _pdf_de_formulario()
    try:
        campos = listar_campos(documento)
        firma = _campo_de("firma_solicitante", campos)

        with pytest.raises(ValueError):
            escribir_valor(documento, firma, "cualquier cosa")
    finally:
        documento.close()

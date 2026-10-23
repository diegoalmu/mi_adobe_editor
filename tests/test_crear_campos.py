"""Pruebas de app/formularios.py - crear campos (Tarea 1 del diseno
`DISENO_CREAR_CAMPOS.md`).

Como en `tests/test_formularios.py`, este modulo solo usa PyMuPDF (sin
Qt), asi que las pruebas corren sin QApplication. Cada prueba crea su
propio PDF en memoria, sin archivos externos.

El import va sin prefijo de paquete (from formularios import ...) porque
asi corre el programa.
"""

import fitz
import pytest

from formularios import (
    TIPOS_CREABLES,
    crear_campo,
    escribir_valor,
    listar_campos,
    rect_para_campo,
    sugerir_nombre,
    validar_nombre_nuevo,
)

# La pagina A4 del PDF de pruebas, en puntos (595 x 842).
RECT_PAGINA = fitz.Rect(0, 0, 595, 842)


def _pdf_vacio():
    """PDF en memoria de una pagina, sin campos de formulario."""
    documento = fitz.open()
    documento.new_page(width=595, height=842)
    return documento


def _campo_de(nombre, campos):
    """Regresa el unico campo con ese nombre (falla si hay 0 o mas)."""
    encontrados = [campo for campo in campos if campo["nombre"] == nombre]
    assert len(encontrados) == 1
    return encontrados[0]


def _num_widgets(documento, num_pagina=0):
    """Cuantos widgets hay en la pagina (para ver que no cambio)."""
    return sum(1 for _ in documento[num_pagina].widgets())


def test_crear_campo_de_cada_tipo_persiste_al_guardar():
    """Se crean texto, texto multilnea, casilla y firma; al guardar con
    `tobytes()` y reabrir, `listar_campos` los ve con su nombre, tipo,
    pagina y multilinea."""
    documento = _pdf_vacio()
    try:
        crear_campo(
            documento, 0, "texto", "texto_1", fitz.Rect(72, 72, 272, 94)
        )
        crear_campo(
            documento,
            0,
            "texto",
            "texto_2",
            fitz.Rect(72, 110, 272, 170),
            multilinea=True,
        )
        crear_campo(
            documento, 0, "casilla", "casilla_1", fitz.Rect(72, 200, 86, 214)
        )
        crear_campo(
            documento,
            0,
            "firma",
            "firma_1",
            fitz.Rect(72, 240, 252, 290),
        )
        datos = documento.tobytes()
    finally:
        documento.close()

    reabierto = fitz.open(stream=datos, filetype="pdf")
    try:
        campos = listar_campos(reabierto)

        texto = _campo_de("texto_1", campos)
        assert texto["tipo"] == "texto"
        assert texto["paginas"] == [0]
        assert not texto["multilinea"]

        multilina = _campo_de("texto_2", campos)
        assert multilina["tipo"] == "texto"
        assert multilina["paginas"] == [0]
        assert multilina["multilinea"]

        casilla = _campo_de("casilla_1", campos)
        assert casilla["tipo"] == "casilla"
        assert casilla["paginas"] == [0]
        assert not casilla["multilinea"]

        firma = _campo_de("firma_1", campos)
        assert firma["tipo"] == "firma"
        assert firma["paginas"] == [0]
        assert not firma["multilinea"]
    finally:
        reabierto.close()


def test_campo_creado_se_llena_y_el_valor_persiste_al_reabrir():
    """Un texto y una casilla creados aqui se llenan con `escribir_valor`
    y el valor sigue ahi despues de guardar con `tobytes()` y reabrir."""
    documento = _pdf_vacio()
    try:
        crear_campo(
            documento, 0, "texto", "nombre", fitz.Rect(72, 72, 272, 94)
        )
        crear_campo(
            documento, 0, "casilla", "acepta", fitz.Rect(72, 110, 86, 124)
        )
        campos = listar_campos(documento)
        escribir_valor(documento, _campo_de("nombre", campos), "Ana Lopez")
        escribir_valor(documento, _campo_de("acepta", campos), True)
        datos = documento.tobytes()
    finally:
        documento.close()

    reabierto = fitz.open(stream=datos, filetype="pdf")
    try:
        campos = listar_campos(reabierto)
        assert _campo_de("nombre", campos)["valor"] == "Ana Lopez"
        assert _campo_de("acepta", campos)["valor"] is True
    finally:
        reabierto.close()


@pytest.mark.parametrize(
    "nombre",
    [
        pytest.param("", id="vacio"),
        pytest.param("cliente.nombre", id="con_punto"),
        pytest.param("a" * 61, id="de_61_caracteres"),
        pytest.param("nombre_cliente", id="repetido"),
        pytest.param("NOMBRE_CLIENTE", id="repetido_otras_mayusculas"),
    ],
)
def test_validar_nombre_nuevo_rechaza_los_invalidos(nombre):
    """Vacio, con punto, de 61 caracteres, repetido y repetido con
    otras mayusculas dan un mensaje de error (no vacio)."""
    documento = _pdf_vacio()
    try:
        crear_campo(
            documento, 0, "texto", "nombre_cliente", fitz.Rect(72, 72, 272, 94)
        )
        mensaje = validar_nombre_nuevo(documento, nombre)
        assert mensaje != ""
    finally:
        documento.close()


def test_validar_nombre_nuevo_acepta_un_nombre_libre():
    """Un nombre que cumple las reglas da la cadena vacia."""
    documento = _pdf_vacio()
    try:
        crear_campo(
            documento, 0, "texto", "nombre_cliente", fitz.Rect(72, 72, 272, 94)
        )
        # 60 caracteres y sin punto: justo en el limite permitido.
        valido = "a" * 60
        assert validar_nombre_nuevo(documento, valido) == ""
    finally:
        documento.close()


def test_crear_campo_con_nombre_repetido_no_toca_el_documento():
    """Nombre repetido (aunque cambien las mayusculas): ValueError y la
    pagina se queda con los mismos widgets."""
    documento = _pdf_vacio()
    try:
        crear_campo(
            documento, 0, "texto", "nombre_cliente", fitz.Rect(72, 72, 272, 94)
        )
        antes = _num_widgets(documento)

        with pytest.raises(ValueError):
            crear_campo(
                documento,
                0,
                "casilla",
                "NOMBRE_CLIENTE",
                fitz.Rect(72, 110, 86, 124),
            )

        assert _num_widgets(documento) == antes
        assert len(listar_campos(documento)) == 1
    finally:
        documento.close()


def test_crear_campo_con_tipo_invalido_no_toca_el_documento():
    """Un tipo que no esta en TIPOS_CREABLES: ValueError y ningun
    widget agregado."""
    documento = _pdf_vacio()
    try:
        with pytest.raises(ValueError):
            crear_campo(
                documento, 0, "opcion", "genero", fitz.Rect(72, 72, 90, 90)
            )

        assert _num_widgets(documento) == 0
        assert listar_campos(documento) == []
    finally:
        documento.close()


def test_crear_campo_multilinea_en_casilla_no_toca_el_documento():
    """`multilinea=True` con un tipo que no es texto: ValueError y
    ningun widget agregado."""
    documento = _pdf_vacio()
    try:
        with pytest.raises(ValueError):
            crear_campo(
                documento,
                0,
                "casilla",
                "casilla_1",
                fitz.Rect(72, 72, 86, 86),
                multilinea=True,
            )

        assert _num_widgets(documento) == 0
        assert listar_campos(documento) == []
    finally:
        documento.close()


def test_sugerir_nombre_en_pdf_vacio_empieza_en_uno():
    """Sin campos, cada tipo sugiere su primer nombre."""
    documento = _pdf_vacio()
    try:
        assert sugerir_nombre(documento, "texto") == "texto_1"
        assert sugerir_nombre(documento, "casilla") == "casilla_1"
        assert sugerir_nombre(documento, "firma") == "firma_1"
    finally:
        documento.close()


def test_sugerir_nombre_salta_los_que_ya_existen():
    """Con `texto_1` y `texto_2` en el documento, sugiere `texto_3`."""
    documento = _pdf_vacio()
    try:
        crear_campo(
            documento, 0, "texto", "texto_1", fitz.Rect(72, 72, 272, 94)
        )
        crear_campo(
            documento, 0, "texto", "texto_2", fitz.Rect(72, 110, 272, 132)
        )
        assert sugerir_nombre(documento, "texto") == "texto_3"
    finally:
        documento.close()


def test_sugerir_nombre_con_tipo_invalido_lanza_error():
    """Un tipo fuera de TIPOS_CREABLES no tiene prefijo: ValueError."""
    documento = _pdf_vacio()
    try:
        with pytest.raises(ValueError):
            sugerir_nombre(documento, "opcion")
    finally:
        documento.close()


def test_rect_para_campo_clic_da_el_tamano_estandar():
    """Un clic (cuadro sin ancho ni alto) usa el tamano de la tabla del
    diseno, desde el punto del clic."""
    texto = rect_para_campo(
        "texto", fitz.Rect(100, 100, 100, 100), RECT_PAGINA
    )
    assert texto == fitz.Rect(100, 100, 300, 122)

    casilla = rect_para_campo(
        "casilla", fitz.Rect(100, 200, 100, 200), RECT_PAGINA
    )
    assert casilla == fitz.Rect(100, 200, 114, 214)

    firma = rect_para_campo(
        "firma", fitz.Rect(100, 300, 100, 300), RECT_PAGINA
    )
    assert firma == fitz.Rect(100, 300, 280, 350)


def test_rect_para_campo_casilla_arrastrada_sale_cuadrada():
    """La casilla arrastrada queda cuadrada con el lado menor, y con
    minimo 10 pt."""
    # Arrastre de 40 x 18: queda el lado menor (18), anclada en la
    # esquina de arriba a la izquierda del arrastre.
    rect = rect_para_campo("casilla", fitz.Rect(72, 72, 112, 90), RECT_PAGINA)
    assert rect == fitz.Rect(72, 72, 90, 90)

    # Arrastre de 30 x 9: el menor es 9, pero el minimo es 10.
    chica = rect_para_campo(
        "casilla", fitz.Rect(72, 200, 102, 209), RECT_PAGINA
    )
    assert chica == fitz.Rect(72, 200, 82, 210)


def test_rect_para_campo_recorta_a_la_pagina():
    """Un cuadro que se sale de la pagina queda cortado en sus
    limites."""
    rect = rect_para_campo("texto", fitz.Rect(500, 800, 700, 900), RECT_PAGINA)
    assert rect == fitz.Rect(500, 800, 595, 842)


def test_rect_para_campo_clic_pegado_al_borde_lanza_error():
    """Un clic 3 pt antes del borde derecho: el cuadro de texto de
    200 pt se recorta a 3 pt de ancho y no se puede crear."""
    with pytest.raises(ValueError):
        rect_para_campo("texto", fitz.Rect(592, 100, 592, 100), RECT_PAGINA)


def test_rect_para_campo_con_tipo_invalido_lanza_error():
    """Los tipos que no se pueden crear no tienen tamano definido."""
    with pytest.raises(ValueError):
        rect_para_campo("opcion", fitz.Rect(72, 72, 172, 92), RECT_PAGINA)


def test_tipos_creadores_son_los_del_diseno():
    """La constante publica del modulo es la tabla de tipos del
    diseno (texto, casilla y firma, en ese orden)."""
    assert TIPOS_CREABLES == ("texto", "casilla", "firma")

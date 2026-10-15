"""Pruebas de app/historial.py (Tarea 1 del diseno de Deshacer/Rehacer).

La clase HistorialCambios no crea ventanas ni toca Qt, asi que estas
pruebas corren sin QApplication: solo usan PDFs en memoria creados con
PyMuPDF.

El import va sin prefijo de paquete (from historial import ...) porque
asi corre el programa.
"""

import fitz

from historial import HistorialCambios


def _documento_texto():
    """PDF en memoria con una pagina y el parrafo 'uno dos tres'."""
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    pagina.insert_text((72, 100), "uno dos tres", fontsize=12, fontname="helv")
    return documento


def _agregar_linea(documento, texto):
    """Simula un cambio: anade una linea debajo del parrafo original."""
    documento[0].insert_text((72, 140), texto, fontsize=12, fontname="helv")


def test_tres_deshacer_regresan_al_original():
    """Registrar 3 cambios y deshacer 3 veces vuelve al documento original."""
    documento = _documento_texto()
    try:
        texto_original = documento[0].get_text()
        historial = HistorialCambios()

        historial.registrar(documento, "cambio 1")
        _agregar_linea(documento, "linea uno")
        historial.registrar(documento, "cambio 2")
        _agregar_linea(documento, "linea dos")
        historial.registrar(documento, "cambio 3")
        _agregar_linea(documento, "linea tres")
        assert "linea tres" in documento[0].get_text()

        tercero = historial.deshacer(documento)
        segundo = historial.deshacer(tercero)
        primero = historial.deshacer(segundo)

        assert primero is not None
        assert segundo is not None
        assert tercero is not None
        assert primero[0].get_text() == texto_original
        assert not historial.puede_deshacer()
        assert historial.puede_rehacer()
        primero.close()
        segundo.close()
        tercero.close()
    finally:
        documento.close()


def test_cambio_nuevo_vacia_la_pila_de_rehacer():
    """Registrar un cambio nuevo borra el rehacer, igual que en Word."""
    documento = _documento_texto()
    try:
        historial = HistorialCambios()
        historial.registrar(documento, "cambio 1")
        _agregar_linea(documento, "linea uno")

        deshecho = historial.deshacer(documento)
        assert deshecho is not None
        assert historial.puede_rehacer()
        assert historial.descripcion_rehacer() == "cambio 1"

        # cambio nuevo: se registra otra vez y el rehacer desaparece
        historial.registrar(deshecho, "cambio 2")
        assert not historial.puede_rehacer()
        assert historial.descripcion_rehacer() is None
        assert historial.descripcion_deshacer() == "cambio 2"
        deshecho.close()
    finally:
        documento.close()


def test_limite_de_pasos_solo_deja_deshacer_los_ultimos():
    """Con limite_pasos=2 y 3 cambios registrados solo se pueden deshacer 2."""
    documento = _documento_texto()
    try:
        historial = HistorialCambios(limite_pasos=2)
        historial.registrar(documento, "cambio 1")
        _agregar_linea(documento, "linea uno")
        historial.registrar(documento, "cambio 2")
        _agregar_linea(documento, "linea dos")
        # al exceder el limite se descarta la copia mas antigua ("cambio 1")
        historial.registrar(documento, "cambio 3")

        assert historial.descripcion_deshacer() == "cambio 3"
        primero = historial.deshacer(documento)
        assert primero is not None
        assert historial.descripcion_deshacer() == "cambio 2"

        segundo = historial.deshacer(primero)
        assert segundo is not None
        assert not historial.puede_deshacer()
        # el tercer deshacer no existe: su copia fue descartada
        assert historial.deshacer(segundo) is None
        primero.close()
        segundo.close()
    finally:
        documento.close()


def test_limite_de_bytes_descarta_las_copias_antiguas():
    """Con un limite_bytes que solo alcanza para la copia nueva, se descartan las viejas."""
    documento_1 = _documento_texto()
    documento_2 = _documento_texto()
    documento_3 = _documento_texto()
    try:
        _agregar_linea(documento_2, "linea uno")
        _agregar_linea(documento_3, "linea uno")
        _agregar_linea(documento_3, "linea dos")

        # el limite cabe justo la copia mas reciente (y un poco mas),
        # pero no las tres juntas
        tamano_ultimo = len(documento_3.tobytes())
        historial = HistorialCambios(limite_bytes=tamano_ultimo + 50)

        historial.registrar(documento_1, "cambio 1")
        historial.registrar(documento_2, "cambio 2")
        historial.registrar(documento_3, "cambio 3")

        # solo quedo la copia mas reciente: las antiguas se descartaron
        assert historial.descripcion_deshacer() == "cambio 3"
        deshecho = historial.deshacer(documento_3)
        assert deshecho is not None
        assert not historial.puede_deshacer()
        assert historial.deshacer(deshecho) is None
        deshecho.close()
    finally:
        documento_1.close()
        documento_2.close()
        documento_3.close()


def test_limite_de_bytes_conserva_la_copia_mas_reciente():
    """Un documento mas grande que limite_bytes aun se puede deshacer un paso."""
    documento = _documento_texto()
    try:
        # el limite es mucho menor que una sola copia del documento
        historial = HistorialCambios(limite_bytes=10)
        historial.registrar(documento, "cambio 1")
        _agregar_linea(documento, "linea uno")
        historial.registrar(documento, "cambio 2")

        # la copia mas reciente nunca se descarta: se puede deshacer 1 vez
        assert historial.puede_deshacer()
        assert historial.descripcion_deshacer() == "cambio 2"
        deshecho = historial.deshacer(documento)
        assert deshecho is not None
        assert not historial.puede_deshacer()
        assert historial.deshacer(deshecho) is None
        deshecho.close()
    finally:
        documento.close()


def test_descartar_ultimo_quita_la_copia_del_cambio_cancelado():
    """descartar_ultimo quita la ultima copia (operacion que fallo o se cancelo)."""
    documento = _documento_texto()
    try:
        historial = HistorialCambios()
        historial.registrar(documento, "cambio 1")
        # este segundo cambio se cancelo: se descarta su copia
        historial.registrar(documento, "cambio 2")
        historial.descartar_ultimo()

        assert historial.puede_deshacer()
        assert historial.descripcion_deshacer() == "cambio 1"

        deshecho = historial.deshacer(documento)
        assert deshecho is not None
        assert not historial.puede_deshacer()
        # descartar sin copias no truena ni deja nada raro
        historial.descartar_ultimo()
        assert not historial.puede_deshacer()
        deshecho.close()
    finally:
        documento.close()


def test_descripciones_de_deshacer_y_rehacer():
    """Las descripciones dicen que se va a deshacer y que se va a rehacer."""
    documento = _documento_texto()
    try:
        historial = HistorialCambios()
        # recien creado: no hay nada que deshacer ni rehacer
        assert historial.descripcion_deshacer() is None
        assert historial.descripcion_rehacer() is None

        historial.registrar(documento, "Rotar pagina")
        _agregar_linea(documento, "linea uno")
        assert historial.descripcion_deshacer() == "Rotar pagina"
        assert historial.descripcion_rehacer() is None

        deshecho = historial.deshacer(documento)
        assert deshecho is not None
        # la misma descripcion sirve para las dos pilas
        assert historial.descripcion_deshacer() is None
        assert historial.descripcion_rehacer() == "Rotar pagina"

        # vaciar borra las dos pilas (abrir o cerrar otro documento)
        historial.vaciar()
        assert not historial.puede_deshacer()
        assert not historial.puede_rehacer()
        assert historial.descripcion_rehacer() is None
        deshecho.close()
    finally:
        documento.close()

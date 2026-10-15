"""Pruebas del menu Editar, del historial y del registro de cambios.

Tarea 2: se abre la ventana principal en modo offscreen
(QT_QPA_PLATFORM lo fija tests/conftest.py) y se comprueba que Deshacer
y Rehacer restauran el documento, que abrir otro documento vacia el
historial (regla 2) y que un PDF con contrasena deja las acciones
deshabilitadas (regla 5, tambien con solo contrasena de permisos).

Tarea 3: cada operacion que modifica el documento registra su copia
antes (resaltar, editar texto, eliminar pagina, ...) y cancelar un
dialogo no deja una copia de mas en el historial.
"""

import fitz
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox

import main as modulo_main
from main import EditorPDF

# QApplication unica para todas las pruebas (crear varias da error)
_aplicacion = QApplication.instance() or QApplication([])


def _documento_pdf():
    """PDF en memoria con una pagina y el parrafo 'uno dos tres'."""
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    pagina.insert_text((72, 100), "uno dos tres", fontsize=12, fontname="helv")
    return documento


def _cerrar_documento_de(ventana):
    """Cierra el documento que quede abierto en la ventana (si hay uno)."""
    if ventana.documento is not None:
        ventana.documento.close()


def _documento_de(ventana):
    """El documento de la ventana, comprobando que exista (para pyright)."""
    assert ventana.documento is not None
    return ventana.documento


def _pagina_de(ventana, numero=0):
    """Una pagina del documento de la ventana."""
    return _documento_de(ventana).load_page(numero)


def _texto_de_pagina(pagina):
    """Texto plano de la pagina, con los espacios duros en normal."""
    return str(pagina.get_text("text")).replace("\xa0", " ")


def test_deshacer_y_rehacer_de_rotar_pagina():
    """Rotar con registrar_cambio: deshacer vuelve a 0 y rehacer a 90."""
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(_documento_pdf(), None)
        assert ventana.documento is not None

        ventana.registrar_cambio("Rotar pagina")
        ventana.documento[0].set_rotation(90)
        assert ventana.documento[0].rotation == 90
        assert ventana.accion_deshacer.isEnabled()
        assert "Rotar pagina" in ventana.accion_deshacer.text()

        ventana.deshacer_cambio()
        assert ventana.documento[0].rotation == 0
        assert not ventana.accion_deshacer.isEnabled()
        assert ventana.accion_rehacer.isEnabled()
        assert "Rotar pagina" in ventana.accion_rehacer.text()

        ventana.rehacer_cambio()
        assert ventana.documento[0].rotation == 90
        assert ventana.accion_deshacer.isEnabled()
        assert not ventana.accion_rehacer.isEnabled()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_abrir_otro_documento_vacia_el_historial():
    """Regla 2: abrir otro documento empieza el historial de cero."""
    ventana = EditorPDF()
    documento_1 = _documento_pdf()
    try:
        ventana.cargar_documento(documento_1, None)
        ventana.registrar_cambio("Rotar pagina")
        assert ventana.historial.puede_deshacer()

        # abrir otro documento (el segundo) vacia las dos pilas
        ventana.cargar_documento(_documento_pdf(), None)
        assert not ventana.historial.puede_deshacer()
        assert not ventana.historial.puede_rehacer()
        assert not ventana.accion_deshacer.isEnabled()
        assert not ventana.accion_rehacer.isEnabled()
        assert ventana.accion_deshacer.text() == "Deshacer"
        assert ventana.accion_rehacer.text() == "Rehacer"
    finally:
        documento_1.close()
        _cerrar_documento_de(ventana)
        ventana.close()


def test_pdf_con_contrasena_deshabilita_las_acciones(tmp_path):
    """Regla 5: con un PDF protegido, Deshacer y Rehacer quedan apagados."""
    ruta = tmp_path / "protegido.pdf"
    origen = _documento_pdf()
    origen.save(
        str(ruta), encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secreta"
    )
    origen.close()

    documento = fitz.open(str(ruta))
    assert documento.authenticate("secreta")
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(documento, None)
        # aunque haya algo registrado para deshacer, las acciones no se
        # habilitan: la copia en memoria se guardaria sin la contrasena
        ventana.registrar_cambio("Rotar pagina")
        assert ventana.documento_protegido
        assert ventana.historial.puede_deshacer()
        assert not ventana.accion_deshacer.isEnabled()
        assert not ventana.accion_rehacer.isEnabled()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_pdf_solo_con_contrasena_de_permisos_deshabilita_las_acciones(tmp_path):
    """Regla 5: un PDF con solo contrasena de permisos tambien queda apagado.

    Se guarda con owner_pw y user_pw vacio: el archivo se abre sin pedir
    contrasena, pero tiene cifrado (contrasena de permisos), asi que
    Deshacer y Rehacer no pueden usarse.
    """
    ruta = tmp_path / "permisos.pdf"
    origen = _documento_pdf()
    origen.save(
        str(ruta), encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="dueno", user_pw="",
    )
    origen.close()

    documento = fitz.open(str(ruta))
    assert not documento.needs_pass  # se abre sin pedir contrasena
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(documento, None)
        ventana.registrar_cambio("Rotar pagina")
        assert ventana.documento_protegido
        assert ventana.historial.puede_deshacer()
        assert not ventana.accion_deshacer.isEnabled()
        assert not ventana.accion_rehacer.isEnabled()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_deshacer_quita_la_anotacion_resaltada():
    """Tarea 3: resaltar registra el cambio y deshacer quita la anotacion."""
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(_documento_pdf(), None)
        ventana.combo_herramienta.setCurrentText("Resaltar")

        ventana.al_seleccionar_rectangulo(0, QRect(100, 130, 150, 40))

        pagina = _pagina_de(ventana)
        assert len(list(pagina.annots())) == 1
        assert ventana.historial.descripcion_deshacer() == "Resaltar"

        ventana.deshacer_cambio()
        assert list(_pagina_de(ventana).annots()) == []
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_deshacer_regresa_la_pagina_eliminada(monkeypatch):
    """Tarea 3: eliminar pagina se registra y deshacer la vuelve a poner."""
    monkeypatch.setattr(
        QMessageBox, "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    ventana = EditorPDF()
    documento = _documento_pdf()
    documento.new_page(width=595, height=842)  # 2 paginas para poder borrar
    try:
        ventana.cargar_documento(documento, None)
        assert len(_documento_de(ventana)) == 2

        ventana.eliminar_pagina()
        assert len(_documento_de(ventana)) == 1
        assert ventana.historial.descripcion_deshacer() == "Eliminar pagina"

        ventana.deshacer_cambio()
        assert len(_documento_de(ventana)) == 2
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_deshacer_regresa_el_texto_original_editado():
    """Tarea 3: aceptar una edicion en linea se registra como 'Editar texto'."""
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(_documento_pdf(), None)
        pagina = _pagina_de(ventana)
        ventana.combo_herramienta.setCurrentText(
            "Editar contenido (texto e imagenes)"
        )

        # mismo truco que en test_edicion_inline: el bbox se ensancha
        # para que el texto quepa y no se abra ningun aviso
        parrafo = dict(ventana.obtener_todos_los_parrafos(pagina)[0])
        bbox = parrafo["bbox"]
        parrafo["bbox"] = fitz.Rect(
            bbox.x0 - 10, bbox.y0 - 5, bbox.x1 + 10, bbox.y1 + 5
        )
        ventana.editar_parrafo_encontrado(0, pagina, parrafo)
        assert ventana.editor_texto_inline is not None

        ventana.editor_texto_inline.setPlainText("texto nuevo")
        assert ventana.aceptar_edicion_texto()
        # insert_htmlbox deja espacios duros (\xa0), se normalizan
        assert "texto nuevo" in _texto_de_pagina(_pagina_de(ventana))
        assert ventana.historial.descripcion_deshacer() == "Editar texto"

        ventana.deshacer_cambio()
        texto = _texto_de_pagina(_pagina_de(ventana))
        assert "uno dos tres" in texto
        assert "texto nuevo" not in texto
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_cancelar_dialogo_de_texto_libre_no_deja_copia(monkeypatch):
    """Tarea 3: cancelar el dialogo de texto libre descarta la copia (regla 4)."""
    monkeypatch.setattr(
        QInputDialog, "getText",
        lambda *args, **kwargs: ("", False),
    )
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(_documento_pdf(), None)
        ventana.combo_herramienta.setCurrentText("Texto libre")

        ventana.al_seleccionar_rectangulo(0, QRect(100, 130, 150, 40))

        # el usuario cancelo: no hay anotacion ni copia en el historial
        assert list(_pagina_de(ventana).annots()) == []
        assert not ventana.historial.puede_deshacer()
        assert not ventana.accion_deshacer.isEnabled()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()


def test_fallo_al_escribir_texto_revuelve_el_documento(monkeypatch):
    """Si insertar_texto_con_formato falla, el parrafo original sigue.

    La redaccion ya tapo el parrafo antes del fallo, asi que descartar
    la copia no basta: _revertir_cambio_fallido deshace el cambio
    registrado y el documento vuelve al estado original (con el parrafo
    "uno dos tres" intacto), sin dejar nada ni para deshacer ni para
    rehacer.
    """

    def _fallar(*args, **kwargs):
        raise RuntimeError("fallo simulado de insertar_texto_con_formato")

    monkeypatch.setattr(modulo_main, "insertar_texto_con_formato", _fallar)
    monkeypatch.setattr(
        QMessageBox, "critical",
        lambda *args, **kwargs: QMessageBox.StandardButton.Ok,
    )
    ventana = EditorPDF()
    try:
        ventana.cargar_documento(_documento_pdf(), None)
        pagina = _pagina_de(ventana)
        ventana.combo_herramienta.setCurrentText(
            "Editar contenido (texto e imagenes)"
        )

        # mismo truco que en las demas pruebas de edicion: el bbox se
        # ensancha para que el texto quepa y no se abra el aviso
        parrafo = dict(ventana.obtener_todos_los_parrafos(pagina)[0])
        bbox = parrafo["bbox"]
        parrafo["bbox"] = fitz.Rect(
            bbox.x0 - 10, bbox.y0 - 5, bbox.x1 + 10, bbox.y1 + 5
        )
        ventana.editar_parrafo_encontrado(0, pagina, parrafo)
        assert ventana.editor_texto_inline is not None
        ventana.editor_texto_inline.setPlainText("texto nuevo")

        # aceptar falla al insertar: el documento se revierte solo
        assert not ventana.aceptar_edicion_texto()
        texto = _texto_de_pagina(_pagina_de(ventana))
        assert "uno dos tres" in texto
        assert "texto nuevo" not in texto
        # el cambio fallido nunca existio: no queda ni deshacer ni rehacer
        assert not ventana.historial.puede_deshacer()
        assert not ventana.historial.puede_rehacer()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()

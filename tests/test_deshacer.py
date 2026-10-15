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
from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QInputDialog, QMessageBox,
)

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


def _documento_con_imagen():
    """PDF en memoria con una pagina que tiene una imagen pegada."""
    documento = fitz.open()
    pagina = documento.new_page(width=595, height=842)
    pixeles = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 8, 8))
    pixeles.set_rect(pixeles.irect, (255, 0, 0))
    pagina.insert_image(fitz.Rect(72, 72, 172, 172), pixmap=pixeles)
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


def _color_en_pagina(pagina, x, y):
    """Color RGB del pixel de la pagina en el punto (x, y) en puntos PDF."""
    pixeles = pagina.get_pixmap(
        matrix=fitz.Matrix(1, 1), clip=fitz.Rect(x, y, x + 1, y + 1)
    )
    return tuple(pixeles.pixel(0, 0))[:3]


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


def test_fallo_al_reemplazar_imagen_revuelve_el_documento(tmp_path, monkeypatch):
    """Si editar_imagen falla despues de borrar la imagen, la original sigue.

    Se simula el fallo con una imagen nueva que el programa no puede abrir
    (el archivo existe pero no es una imagen): el borrado de la imagen
    vieja ya toco la pagina (queda en blanco), asi que descartar la copia
    no basta. _revertir_cambio_fallido deshace el cambio registrado y el
    documento vuelve al estado original (con la imagen roja visible otra
    vez), sin dejar nada ni para deshacer ni para rehacer.
    """

    class _BotonFalso:
        def text(self):
            return "Reemplazar imagen..."

    # la imagen "elegida" no se puede decodificar: insert_image falla
    ruta_mala = tmp_path / "falsa_imagen.png"
    ruta_mala.write_text("esto no es una imagen", encoding="utf-8")

    monkeypatch.setattr(QMessageBox, "exec", lambda *args, **kwargs: 0)
    monkeypatch.setattr(
        QMessageBox, "clickedButton",
        lambda *args, **kwargs: _BotonFalso(),
    )
    monkeypatch.setattr(
        QFileDialog, "getOpenFileName",
        lambda *args, **kwargs: (str(ruta_mala), ""),
    )
    monkeypatch.setattr(
        modulo_main.DialogoPosicionarImagen, "exec",
        lambda *args, **kwargs: QDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(
        modulo_main.DialogoPosicionarImagen, "obtener_valores",
        lambda *args, **kwargs: {
            "x": 72.0, "y": 200.0, "ancho": 50.0, "alto": 50.0,
            "mantener_proporcion": True, "usar_clic": False,
        },
    )
    monkeypatch.setattr(
        QMessageBox, "critical",
        lambda *args, **kwargs: QMessageBox.StandardButton.Ok,
    )

    ventana = EditorPDF()
    try:
        ventana.cargar_documento(_documento_con_imagen(), None)
        imagenes = ventana.obtener_todas_las_imagenes(_pagina_de(ventana))
        assert len(imagenes) == 1
        # la imagen roja se ve en la pagina antes de reemplazarla
        assert _color_en_pagina(_pagina_de(ventana), 100, 100) == (255, 0, 0)

        # reemplazar falla al abrir la imagen nueva, cuando la vieja ya
        # se borro de la pagina
        ventana.editar_imagen(_pagina_de(ventana), imagenes[0])

        # el documento se revirtio: la imagen original sigue visible
        pagina_tras_el_fallo = _pagina_de(ventana)
        assert _color_en_pagina(pagina_tras_el_fallo, 100, 100) == (255, 0, 0)
        # el cambio fallido nunca existio: no queda ni deshacer ni rehacer
        assert not ventana.historial.puede_deshacer()
        assert not ventana.historial.puede_rehacer()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()

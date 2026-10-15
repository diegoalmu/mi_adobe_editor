"""Pruebas del menu Editar y del historial en la ventana (Tarea 2).

Se abre la ventana principal en modo offscreen (QT_QPA_PLATFORM lo fija
tests/conftest.py) y se comprueba que Deshacer y Rehacer restauran el
documento, que abrir otro documento vacia el historial (regla 2) y que
un PDF con contrasena deja las acciones deshabilitadas (regla 5).
"""

import fitz
from PySide6.QtWidgets import QApplication

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
        assert ventana.historial.puede_deshacer()
        assert not ventana.accion_deshacer.isEnabled()
        assert not ventana.accion_rehacer.isEnabled()
    finally:
        _cerrar_documento_de(ventana)
        ventana.close()

"""Pruebas de app/dialogo_nuevo_campo.py (Tarea 2 del diseno
`DISENO_CREAR_CAMPOS.md`).

El dialogo se crea y se revisa sin llamar a `exec()`, asi que aqui no
hay ventanas modales: la plataforma offscreen la fija
`tests/conftest.py` antes de crear la QApplication. Como en las demas
pruebas con Qt, hay una sola QApplication para todo el modulo.

El import va sin prefijo de paquete (from dialogo_nuevo_campo import ...)
porque asi corre el programa.
"""

import pytest
from PySide6.QtWidgets import QApplication

from dialogo_nuevo_campo import DialogoNuevoCampo

# QApplication unica para todas las pruebas (crear varias da error).
_aplicacion = QApplication.instance() or QApplication([])


def _validar_que_no_rechaza(nombre):
    """Funcion `validar` de prueba: acepta cualquier nombre."""
    return ""


def _validar_con_repetido(nombre):
    """Funcion `validar` de prueba: solo rechaza el nombre
    "repetido"."""
    if nombre == "repetido":
        return "Ese nombre ya se uso."
    return ""


def _dialogo(
    tipo="texto",
    nombre="texto_1",
    multilinea=False,
    validar=_validar_que_no_rechaza,
):
    """Dialogo de prueba con los valores por defecto del diseno."""
    return DialogoNuevoCampo(tipo, nombre, multilinea, validar)


@pytest.mark.parametrize(
    "tipo,titulo",
    [
        pytest.param("texto", "Nuevo campo de texto", id="texto"),
        pytest.param("casilla", "Nueva casilla", id="casilla"),
        pytest.param("firma", "Nuevo campo de firma", id="firma"),
    ],
)
def test_el_titulo_corresponde_al_tipo(tipo, titulo):
    """La ventana se titula segun el tipo de campo que se va a crear."""
    dialogo = _dialogo(tipo=tipo)
    assert dialogo.windowTitle() == titulo


@pytest.mark.parametrize(
    "tipo,visible",
    [
        pytest.param("texto", True, id="texto"),
        pytest.param("casilla", False, id="casilla"),
        pytest.param("firma", False, id="firma"),
    ],
)
def test_varias_lineas_solo_es_visible_en_texto(tipo, visible):
    """La casilla "Varias lineas" se muestra solo en los campos de
    texto; en casilla y firma queda oculta."""
    dialogo = _dialogo(tipo=tipo)
    # Se muestra la ventana para poder medir la visibilidad real (un
    # hijo de una ventana sin mostrar nunca "se ve").
    dialogo.show()
    assert dialogo.check_multilinea.isVisible() is visible
    dialogo.close()


def test_el_nombre_sugerido_aparece_ya_seleccionado():
    """El campo del nombre trae el nombre sugerido, listo para
    teclear encima."""
    dialogo = _dialogo(nombre="texto_7")
    assert dialogo.campo_nombre.text() == "texto_7"
    assert dialogo.campo_nombre.hasSelectedText()


def test_los_botones_se_llaman_aceptar_y_cancelar():
    """Los botones del QDialogButtonBox traen sus textos en espanol."""
    dialogo = _dialogo()
    assert dialogo.boton_aceptar.text() == "Aceptar"
    assert dialogo.boton_cancelar.text() == "Cancelar"


def test_el_mensaje_y_el_boton_aceptar_se_actualizan_al_escribir():
    """Con un `validar` que rechaza "repetido": escribirlo muestra el
    mensaje y deshabilita Aceptar; escribir otro nombre hace lo
    contrario."""
    dialogo = _dialogo(validar=_validar_con_repetido)

    # El nombre sugerido no tiene problema: sin mensaje y con
    # Aceptar habilitado.
    assert dialogo.etiqueta_error.text() == ""
    assert dialogo.boton_aceptar.isEnabled()

    dialogo.campo_nombre.setText("repetido")
    assert dialogo.etiqueta_error.text() == "Ese nombre ya se uso."
    assert not dialogo.boton_aceptar.isEnabled()

    dialogo.campo_nombre.setText("libre")
    assert dialogo.etiqueta_error.text() == ""
    assert dialogo.boton_aceptar.isEnabled()


def test_obtener_valores_recorta_el_nombre_y_devuelve_multilinea():
    """`obtener_valores` devuelve el nombre sin espacios en los
    extremos y el estado de la casilla "Varias lineas"."""
    dialogo = _dialogo(nombre="  texto_1  ", multilinea=True)
    assert dialogo.obtener_valores() == ("texto_1", True)

    dialogo.check_multilinea.setChecked(False)
    assert dialogo.obtener_valores() == ("texto_1", False)


def test_en_casilla_y_firma_la_multilinea_queda_apagada():
    """Aunque venga `multilinea_inicial=True`, en los tipos que no son
    de texto la casilla queda oculta y desmarcada (asi no se le pasa
    multilinea a un campo que no lo admite)."""
    for tipo in ("casilla", "firma"):
        dialogo = _dialogo(tipo=tipo, multilinea=True)
        assert dialogo.obtener_valores()[1] is False


def test_con_tipo_invalido_lanza_error():
    """Los tipos que no se pueden crear no tienen titulo en la
    ventana: ValueError al construir el dialogo."""
    with pytest.raises(ValueError):
        _dialogo(tipo="opcion")

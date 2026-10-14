"""
historial.py - Deshacer y Rehacer del documento
=================================================

Clase `HistorialCambios`, que implementa el Deshacer (Ctrl+Z) y el
Rehacer (Ctrl+Y) del editor segun `DISENO_DESHACER.md`.

El metodo es el mas simple y confiable con PyMuPDF: antes de cada cambio
se guarda una copia completa del documento en memoria con
`documento.tobytes()`, y deshacer consiste en volver a abrir esa copia
con `fitz.open("pdf", copia)`. No hay que programar como revertir cada
tipo de cambio por separado.

Reglas del historial (del diseno):

1. Hacer un cambio nuevo borra la pila de Rehacer (igual que en Word).
2. Abrir otro documento o cerrar el documento vacia el historial
   (el llamador llama a `vaciar()`).
3. Guardar no vacia el historial.
4. Si una operacion falla despues de registrar la copia, esa copia se
   descarta con `descartar_ultimo()`, para que Deshacer no "deshaga"
   algo que nunca paso.
5. Documentos con contraseña: Deshacer y Rehacer quedan deshabilitados
   (lo decide quien usa esta clase, aqui solo no se registra nada).
6. Mientras hay una edicion de texto en linea abierta, Deshacer y
   Rehacer del documento quedan deshabilitados (tambien lo decide el
   llamador).

Limites de memoria: maximo 20 pasos y maximo 300 MB en total entre todas
las copias. Si se pasa, se descartan las copias mas antiguas.

Este modulo no crea ventanas: se prueba con `tests/test_historial.py`
sin Qt.
"""

import fitz  # PyMuPDF


class HistorialCambios:
    """Pilas de copias del documento para Deshacer y Rehacer.

    Cada entrada es una tupla `(bytes, descripcion)`, donde `bytes` es
    el resultado de `documento.tobytes()` y `descripcion` es el texto
    que el menu mostrara ("Deshacer: Rotar pagina").
    """

    def __init__(self, limite_pasos=20, limite_bytes=300 * 1024 * 1024):
        # Maximo de copias guardadas (se descartan las mas antiguas).
        self._limite_pasos = limite_pasos
        # Maximo de bytes en total entre todas las copias.
        self._limite_bytes = limite_bytes
        # Copias de los estados anteriores; la ultima es la mas reciente.
        self._pila_deshacer = []
        # Copias de los estados que se deshicieron; lista para rehacer.
        self._pila_rehacer = []

    # -----------------------------------------------------------------
    # REGISTRAR CAMBIOS
    # -----------------------------------------------------------------

    def registrar(self, documento, descripcion):
        """Guarda una copia del documento antes de aplicar un cambio.

        Tambien vacia la pila de Rehacer (regla 1: un cambio nuevo
        descarta lo que se hubiera deshecho) y aplica los limites de
        pasos y bytes, descartando las copias mas antiguas.
        """
        self._pila_deshacer.append((documento.tobytes(), descripcion))
        self._pila_rehacer.clear()
        self._aplicar_limites()

    def descartar_ultimo(self):
        """Quita la ultima copia registrada (regla 4).

        Se usa cuando la operacion que iba a hacerse falla o el usuario
        la cancela: para que Deshacer no "deshaga" algo que nunca paso.
        Si no hay copias, no hace nada.
        """
        if self._pila_deshacer:
            self._pila_deshacer.pop()

    # -----------------------------------------------------------------
    # DESHACER Y REHACER
    # -----------------------------------------------------------------

    def deshacer(self, documento_actual):
        """Regresa el documento al estado anterior al ultimo cambio.

        Devuelve un `fitz.Document` nuevo abierto desde la copia
        guardada, y mete el estado actual en la pila de Rehacer con la
        misma descripcion. Devuelve `None` si no hay nada que deshacer.
        """
        if not self._pila_deshacer:
            return None
        bytes_estado, descripcion = self._pila_deshacer.pop()
        self._pila_rehacer.append((documento_actual.tobytes(), descripcion))
        return fitz.open("pdf", bytes_estado)

    def rehacer(self, documento_actual):
        """Vuelve a aplicar el ultimo cambio deshecho.

        Es lo inverso de `deshacer`. Devuelve `None` si no hay nada que
        rehacer.
        """
        if not self._pila_rehacer:
            return None
        bytes_estado, descripcion = self._pila_rehacer.pop()
        self._pila_deshacer.append((documento_actual.tobytes(), descripcion))
        return fitz.open("pdf", bytes_estado)

    # -----------------------------------------------------------------
    # CONSULTAS
    # -----------------------------------------------------------------

    def puede_deshacer(self):
        """`True` si hay al menos una copia para deshacer."""
        return bool(self._pila_deshacer)

    def puede_rehacer(self):
        """`True` si hay al menos una copia para rehacer."""
        return bool(self._pila_rehacer)

    def descripcion_deshacer(self):
        """Descripcion del proximo cambio en deshacerse, o `None`."""
        if not self._pila_deshacer:
            return None
        return self._pila_deshacer[-1][1]

    def descripcion_rehacer(self):
        """Descripcion del proximo cambio en rehacerse, o `None`."""
        if not self._pila_rehacer:
            return None
        return self._pila_rehacer[-1][1]

    def vaciar(self):
        """Borra las dos pilas (regla 2: abrir o cerrar documento)."""
        self._pila_deshacer.clear()
        self._pila_rehacer.clear()

    # -----------------------------------------------------------------
    # LIMITES DE MEMORIA
    # -----------------------------------------------------------------

    def _aplicar_limites(self):
        """Descarta las copias mas antiguas hasta caber en los limites.

        Se llama despues de cada `registrar`. Primero respeta el limite
        de pasos y despues el de bytes, siempre quitando de la base de
        la pila de Deshacer, que es donde estan las copias mas viejas
        (Rehacer queda vacia al registrar).
        """
        while len(self._pila_deshacer) > self._limite_pasos:
            self._pila_deshacer.pop(0)
        while (
            self._pila_deshacer
            and self._tamano_total() > self._limite_bytes
        ):
            self._pila_deshacer.pop(0)

    def _tamano_total(self):
        """Bytes en memoria de todas las copias de las dos pilas."""
        return sum(
            len(bytes_estado)
            for bytes_estado, _ in self._pila_deshacer + self._pila_rehacer
        )

"""
formato_html.py - Tipografias y HTML para el editor de texto inline
====================================================================

Funciones puras (sin ventanas) que convierten la lista de fragmentos del
editor en HTML para `pagina.insert_htmlbox`, y que arman el CSS con las
tipografias disponibles en el sistema.

Las tipografias son una lista corta (Arial, Times New Roman, Calibri,
Verdana y Courier New) porque cada una usada se incrusta en el PDF y
aumenta su tamano. Los archivos .ttf se leen de la carpeta de fuentes de
Windows; si falta alguno, esa tipografia no se ofrece (el programa nunca
truena por una fuente faltante).
"""

import os


# =========================================================================
# TIPOGRAFIAS DISPONIBLES
# =========================================================================

# Tabla del diseno: nombre visible en la barra de formato y los 4 archivos
# .ttf de cada variante (normal, negrita, cursiva, negrita+cursiva).
TIPOGRAFIAS = {
    "Arial": {
        "normal": "arial.ttf",
        "negrita": "arialbd.ttf",
        "cursiva": "ariali.ttf",
        "negrita_cursiva": "arialbi.ttf",
    },
    "Times New Roman": {
        "normal": "times.ttf",
        "negrita": "timesbd.ttf",
        "cursiva": "timesi.ttf",
        "negrita_cursiva": "timesbi.ttf",
    },
    "Calibri": {
        "normal": "calibri.ttf",
        "negrita": "calibrib.ttf",
        "cursiva": "calibrii.ttf",
        "negrita_cursiva": "calibriz.ttf",
    },
    "Verdana": {
        "normal": "verdana.ttf",
        "negrita": "verdanab.ttf",
        "cursiva": "verdanai.ttf",
        "negrita_cursiva": "verdanaz.ttf",
    },
    "Courier New": {
        "normal": "cour.ttf",
        "negrita": "courbd.ttf",
        "cursiva": "couri.ttf",
        "negrita_cursiva": "courbi.ttf",
    },
}

# Carpeta donde Windows guarda las fuentes del sistema.
CARPETA_FUENTES_WINDOWS = r"C:\Windows\Fonts"


def tipografias_disponibles(carpeta):
    """Devuelve la lista de nombres de tipografia cuyos 4 archivos existen en la carpeta."""
    nombres = []
    for nombre, variantes in TIPOGRAFIAS.items():
        archivos = [
            variantes["normal"],
            variantes["negrita"],
            variantes["cursiva"],
            variantes["negrita_cursiva"],
        ]
        if all(os.path.exists(os.path.join(carpeta, archivo)) for archivo in archivos):
            nombres.append(nombre)
    return nombres


def css_tipografias(carpeta):
    """Devuelve el CSS con un @font-face por variante de cada tipografia disponible.

    Los archivos se referencian solo por nombre (`url(archivo.ttf)`), porque
    el CSS se pasa a insert_htmlbox junto con un fitz.Archive apuntando a la
    misma carpeta `carpeta`.
    """
    lineas = []
    for nombre in tipografias_disponibles(carpeta):
        variantes = TIPOGRAFIAS[nombre]
        # (peso css, estilo css, clave en TIPOGRAFIAS)
        declaraciones = (
            ("normal", "normal", "normal"),
            ("bold", "normal", "negrita"),
            ("normal", "italic", "cursiva"),
            ("bold", "italic", "negrita_cursiva"),
        )
        for peso, estilo, clave in declaraciones:
            archivo = variantes[clave]
            lineas.append(
                f"@font-face {{ font-family: {nombre}; font-weight: {peso}; "
                f"font-style: {estilo}; src: url({archivo}); }}"
            )
    return "\n".join(lineas)


# =========================================================================
# FRAGMENTOS DEL EDITOR -> HTML
# =========================================================================

def fragmentos_a_html(fragmentos):
    """Convierte la lista de fragmentos del editor en un HTML para insert_htmlbox.

    Cada fragmento es un diccionario con las claves: texto, familia, tamano,
    negrita, cursiva, subrayado y color (tupla rgb de 0 a 255). Cada uno se
    convierte en un <span style="...">; solo se agregan las propiedades que
    estan activas (por ejemplo font-weight:bold unicamente si el fragmento
    esta en negrita). Se escapan los caracteres especiales (<, > y &) y los
    saltos de linea se convierten en <br>.
    """
    trozos = []
    for fragmento in fragmentos:
        texto = fragmento["texto"]
        texto = texto.replace("&", "&amp;")
        texto = texto.replace("<", "&lt;")
        texto = texto.replace(">", "&gt;")
        texto = texto.replace("\n", "<br>")

        estilos = [
            f"font-family:{fragmento['familia']}",
            f"font-size:{fragmento['tamano']}pt",
        ]
        if fragmento.get("negrita"):
            estilos.append("font-weight:bold")
        if fragmento.get("cursiva"):
            estilos.append("font-style:italic")
        if fragmento.get("subrayado"):
            estilos.append("text-decoration:underline")

        color = fragmento.get("color", (0, 0, 0))
        estilos.append(
            "color:#{:02x}{:02x}{:02x}".format(
                int(color[0]), int(color[1]), int(color[2])
            )
        )

        trozos.append(f'<span style="{"; ".join(estilos)}">{texto}</span>')
    return "".join(trozos)

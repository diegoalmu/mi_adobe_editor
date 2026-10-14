"""Configuración común de las pruebas.

pytest carga este archivo antes de cualquier prueba. Aquí se prepara el
entorno para que las pruebas importen el código igual que cuando se
lanza el programa con `iniciar.bat`, y para que Qt no abra ventanas
reales en pantalla.
"""

import os
import sys
from pathlib import Path

# Raíz del proyecto: la carpeta que contiene app/, tests/, etc.
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent

# Se agregan las dos rutas que el programa necesita para importar:
# - la raíz del proyecto, por los módulos de nivel superior;
# - app/, porque main.py se ejecuta como script y los imports van sin
#   prefijo de paquete (from formato_html import ...).
for _ruta in (RAIZ_PROYECTO, RAIZ_PROYECTO / "app"):
    _ruta_str = str(_ruta)
    if _ruta_str not in sys.path:
        sys.path.insert(0, _ruta_str)

# Plataforma Qt "offscreen": las ventanas se dibujan en memoria y no
# aparecen en pantalla. Se fija antes de crear cualquier QApplication.
os.environ["QT_QPA_PLATFORM"] = "offscreen"

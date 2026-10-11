# 📅 Bitácora de actividades del proyecto

> Cada sesión de trabajo se registra aquí: fecha, qué se hizo, comandos usados y resultado.
> Esto sirve como evidencia de trabajo para portafolio y para la escuela.

---

## Sesión 1 — 2026-08-31

**Objetivo de la sesión:** Preparar el entorno de desarrollo y crear la Fase 1 (visor de PDF básico).

**Contexto:** Se inicia el proyecto "Mi-Adobe-PDF" como alternativa personal, gratuita
y de código abierto a Adobe Acrobat Pro DC y programas de pago similares (PDNob,
Wondershare PDF, PDF-XChange).

**Decisiones técnicas tomadas:**
- Lenguaje: Python 3.11+
- Interfaz gráfica: PySide6
- Motor de manipulación de PDF: PyMuPDF (fitz)
- Sistema operativo objetivo: Windows y Linux

**Actividades realizadas:**
1. Creación de la estructura de carpetas del proyecto (`app/`, (archivos .md en la raíz), `assets/`, `tests/`).
2. Redacción de `README.md` con el objetivo y alcance del proyecto.
3. Redacción de `ROADMAP.md` con las 9 fases de desarrollo planeadas.
4. Instalación de Python y dependencias (ver `INSTALACION_WINDOWS.md` / `INSTALACION_LINUX.md`).
5. Creación del entorno virtual `venv`.
6. Instalación de librerías: `PySide6`, `PyMuPDF`.
7. Creación de `app/main.py`: visor de PDF funcional con:
   - Abrir archivo PDF
   - Mostrar página actual
   - Botones página siguiente/anterior
   - Zoom + / Zoom -
8. Primera ejecución exitosa del programa.
9. Inicialización de repositorio Git y primer commit.

**Resultado:** Programa capaz de abrir y visualizar cualquier PDF en una ventana propia,
con navegación de páginas y zoom. Base lista para agregar edición en la próxima sesión.

**Pendiente para la próxima sesión (Fase 2):**
- Agregar herramienta de resaltado de texto
- Agregar herramienta de texto libre
- Agregar guardado de los cambios sobre el PDF original

---

## Sesión 2 — 2026-08-31

**Objetivo de la sesión:** Instalar y ejecutar por primera vez el visor de PDF en la máquina real (Linux Mint), y dejar el proyecto organizado y subido a GitHub.

**Entorno de desarrollo confirmado:**
- Sistema operativo: Linux Mint (basado en Ubuntu/Debian)
- Python: 3.12.3 (ya venía instalado con el sistema)
- Editor de documentación: Obsidian (para leer/editar los `.md` del proyecto)
- Control de versiones: GitHub Desktop (versión para Linux)

**Actividades realizadas:**
1. Verificación de Python (`python3 --version` → 3.12.3) ✅
2. Verificación de `venv` (`python3 -m venv --help`) ✅
3. Se limpió un archivo `main.py` duplicado que quedó fuera de la carpeta `app/` al descomprimir.
4. Se movió el proyecto de `~/Descargas/mi-adobe-pdf` a `~/Documentos/mi-adobe-pdf` para mantener el orden.
5. Creación del entorno virtual: `python3 -m venv venv`
6. Activación del entorno virtual: `source venv/bin/activate`
7. Instalación de dependencias: `pip install -r requirements.txt` → PySide6 6.7.2 y PyMuPDF 1.24.9 instalados correctamente.
8. Primer intento de ejecución (`python app/main.py`) → error: faltaba la librería del sistema `libxcb-cursor0` (necesaria para que Qt dibuje ventanas en este entorno de escritorio).
9. Solución: `sudo apt install libxcb-cursor0 -y`
10. Segunda ejecución → **✅ éxito**. El visor abre PDFs, navega páginas y hace zoom correctamente.
11. Publicación del repositorio en GitHub usando GitHub Desktop (ver `GITHUB_DESKTOP.md`).

**Problema encontrado y resuelto:**
- Al ejecutar el programa por primera vez en Linux Mint, faltaba `libxcb-cursor0`. Es una dependencia del sistema (no de Python) que Qt necesita en este entorno gráfico. Se instaló con `apt` y no volvió a dar problema.

**Nota importante para el futuro (Fase 8 - Windows):**
Cuando empaquetemos el programa como `.exe` para Windows más adelante, Windows Defender/SmartScreen puede marcarlo como "app desconocida" (esto le pasó antes al usuario con otro proyecto hecho en un editor poco conocido, y tuvo que desbloquearlo manualmente). Hay que preparar bien el empaquetado con PyInstaller y documentar el proceso de desbloqueo/firma para que no sea un susto la primera vez que se ejecute en Windows.

**Resultado:** Fase 1 (Visor de PDF) funcionando de punta a punta en la máquina de desarrollo real. Proyecto publicado en GitHub como respaldo y evidencia de portafolio.

**Pendiente para la próxima sesión (Fase 2):**
- Agregar herramienta de resaltado de texto
- Agregar herramienta de texto libre
- Agregar guardado de los cambios sobre el PDF original

---

## Sesión 3 — 2026-09-02

**Objetivo de la sesión:** Reorganizar el repositorio en GitHub (carpeta definitiva y estructura plana de `.md`), y construir la Fase 2 completa del editor: anotaciones, gestión de páginas, unir/dividir, seguridad y exportación.

**Reorganización de GitHub:**
- El proyecto se re-clonó en su ubicación definitiva: `~/Documentos/GitHub/mi_adobe_editor` (se eliminó la carpeta vieja `~/Documentos/mi-adobe-pdf` para evitar confusión entre dos copias).
- Se detectó que subir archivos por la web de GitHub ("Add file → Upload files") no permite seleccionar carpetas completas — es una limitación del selector de archivos nativo del sistema operativo, no de GitHub. Se estandarizó el flujo de trabajo para usar **siempre GitHub Desktop** de aquí en adelante.
- Se aplanó la documentación: se movieron todos los `.md` de `docs/` a la raíz del repositorio (`BITACORA.md`, `INSTALACION_WINDOWS.md`, `INSTALACION_LINUX.md`, `GITHUB_DESKTOP.md`), eliminando la subcarpeta `docs/`, para que coincida con la convención que se usa en los demás proyectos del usuario.
- Se recreó el `.gitignore` (se había perdido al mover archivos), agregando también `.obsidian/` ya que el proyecto se abre como bóveda de Obsidian.

**Funciones nuevas construidas en `app/main.py` (Fase 2):**
1. **Anotaciones**: resaltar, subrayar, tachar, texto libre, rectángulo, línea, círculo — seleccionables desde un desplegable, se aplican arrastrando el mouse sobre la página.
2. **Páginas**: rotar, eliminar, insertar página en blanco.
3. **Reordenar páginas**: ventana con cuadrícula de miniaturas (estilo panel de páginas de Adobe Acrobat). Se agregaron botones "Mover" como alternativa confiable al arrastrar-y-soltar nativo, ya que en Linux Mint el drag-and-drop de Qt mostraba un ícono de "no permitido" de forma inconsistente.
4. **Archivo**: unir varios PDFs, dividir el PDF actual en un archivo por página, exportar cada página a imagen PNG, comprimir PDF.
5. **Seguridad**: agregar contraseña, quitar contraseña, y abrir PDFs que ya tienen contraseña.
6. **Visor**: se cambió de "una página con botones siguiente/anterior" a **scroll continuo** (todas las páginas apiladas, como cualquier lector de PDF normal), con un indicador fijo en la barra de herramientas que muestra "Página X de Y" y se actualiza solo mientras se hace scroll.
7. **Menú "Archivo"** agregado en la parte superior de la ventana: Abrir, Guardar (sobrescribe el archivo original usando un archivo temporal + reemplazo, para no arriesgar corromperlo), Guardar como, Cerrar documento, Salir.

**Problemas encontrados y resueltos:**
- El entorno virtual (`venv`) de la nueva carpeta clonada estaba vacío al principio; se reinstalaron las dependencias ahí con `pip install -r requirements.txt`.
- El comando `python` no existe en este Linux Mint (solo `python3`); se usa `venv/bin/python3` de forma explícita para evitar ambigüedad con el PATH del sistema.
- El arrastrar-y-soltar nativo de Qt para reordenar páginas mostraba un ícono de cancelación en este entorno Linux; se solucionó agregando una forma alternativa con botones de mover, que no depende del comportamiento del sistema operativo.

**Resultado:** Editor de PDF funcional con la mayoría de las funciones "del día a día" de Adobe Acrobat Pro DC (ver casillas actualizadas en `README.md`). Falta la parte más difícil técnicamente: edición del texto que ya existe en el documento, OCR, conversión a Word/Excel y firma digital.

**Pendiente para la próxima sesión (Fase 3):**
- Definir prioridad entre: edición de texto existente, OCR, conversión a Word, o firma digital.

---

## Sesión 4 — 2026-09-02

**Objetivo de la sesión:** Terminar las funciones que faltaban del checklist original: convertir a Word, OCR, firma por imagen, y la más difícil — editar texto que ya existe en el PDF. Además, reorganizar la interfaz y pulir detalles.

**Funciones nuevas construidas:**
1. **Convertir a Word (.docx)**: usa la librería `pdf2docx`. El texto queda como texto real editable en Word, no como imagen. Probado y confirmado antes de integrarlo.
2. **OCR (Archivo → Hacer PDF buscable)**: usa `ocrmypdf` + Tesseract (motor de OCR) + Ghostscript. Le agrega una capa de texto invisible a las páginas escaneadas para que se puedan buscar/copiar, sin tocar las páginas que ya tenían texto (`skip_text=True`). Requiere instalar en el sistema: `sudo apt install tesseract-ocr tesseract-ocr-spa ghostscript`.
3. **Firma por imagen**: se carga una imagen (PNG con transparencia funciona mejor) con el botón "Cargar imagen de firma...", y se coloca en el documento como una herramienta más (arrastrando un cuadro).
4. **Editar texto existente**: la función técnicamente más compleja del proyecto. Detecta el texto/tamaño/color real dentro del área que arrastra el usuario (usando `get_text("dict")`), muestra un diálogo para editarlo, y usa `add_redact_annot()` + `apply_redactions()` para tapar el texto viejo y escribir el nuevo en su lugar. Limitación real y esperada: funciona mejor para cambios cortos (precios, fechas, nombres); no "empuja" el resto del párrafo como Word, porque los PDFs no son documentos de flujo.

**Reorganización de la interfaz:**
- Con tantas funciones ya no cabían todos los botones en una sola barra. Se reorganizó todo en 4 menús desplegables arriba: **Archivo, Páginas, Herramientas, Seguridad**. La barra de herramientas quedó reducida solo a lo de uso constante: zoom, indicador de página, y el selector de herramienta de anotación activa.

**Detalles pulidos:**
- Los diálogos nativos (Guardar, Abrir, Cancelar) aparecían en inglés a pesar de que el sistema está en español. Se solucionó cargando la traducción oficial de Qt al español (`qtbase_es.qm`, incluida en PySide6, no requiere instalar nada nuevo).
- Se agregó manejo de errores página por página: si un PDF tiene alguna página con datos corruptos/raros internamente, el programa muestra un aviso solo en esa página en vez de arriesgarse a fallar en toda la ventana. Esto surgió al toparse con un PDF real que generaba un `zlib error` en la terminal (MuPDF se recuperaba solo, pero se blindó el programa para el futuro).

**Resultado:** Editor de PDF con prácticamente todas las funciones "del día a día" de Adobe Acrobat Pro DC: ver, anotar, editar texto existente, gestionar páginas, unir/dividir, exportar, comprimir, proteger con contraseña, convertir a Word, y hacer OCR. Sin errores pendientes al cierre de esta sesión.

**Pendiente para futuras sesiones (funciones menores que faltan):**
- Rellenar y crear formularios PDF (campos de texto, checkboxes)
- Notas tipo "sticky note" (comentarios, distinto del texto libre que ya existe)
- Empaquetar como `.exe` para Windows (Fase 8 del ROADMAP — cuidado especial con Windows Defender/SmartScreen)

---

---

## Sesión 5 — 2026-09-05

**Objetivo de la sesión:** Empaquetar el programa como ejecutable independiente (Fase 8 del ROADMAP), para que se pueda abrir con doble clic sin necesitar Python, `venv`, ni terminal.

**Trabajo previo de esta sesión (correcciones a la Fase 4):**
Antes del empaquetado, se corrigieron varios errores reales encontrados al probar
"Editar contenido" contra documentos reales del usuario (catálogo técnico y
manual universitario):
- La detección de párrafos usaba el espacio entre líneas para saber dónde
  termina un párrafo, pero eso falla en documentos con interlineado uniforme
  (sin salto extra entre párrafos). Se cambió la señal a "si la línea llega
  al margen derecho normal" (línea llena = continúa el párrafo; línea corta
  = ahí termina).
- Se agregó una regla de ancho mínimo para evitar que etiquetas cortas sueltas
  (ej. "Terminado", "Pantalla" en una ficha técnica) se mezclaran por accidente.
- **Bug crítico de pérdida de datos**: al editar texto, si el texto nuevo no
  cabía, el programa ya había borrado el original antes de darse cuenta. Se
  corrigió para probar primero en un documento descartable, y solo borrar el
  original si YA se confirmó que el reemplazo cabe.
- Se agregó edición de **imágenes** (reemplazar/eliminar) e **imágenes con
  fondo de color** ("formas" vectoriales grandes, tipo banners) como parte de
  la misma herramienta "Editar contenido", con recuadros de colores distintos
  (azul=texto, verde=imagen, naranja=forma de color).
- Al recolorear una forma, se detectó que el texto encima se borraba junto
  con ella; se corrigió guardando ese texto antes de borrar y reescribiéndolo
  después en su lugar exacto.
- Bug real encontrado: comparar botones de un `QMessageBox` por identidad
  (`is`) en PySide6 puede fallar silenciosamente. Se cambió a comparar por
  el texto del botón, lo cual resolvió que "Eliminar imagen"/"Reemplazar
  imagen" no hicieran nada.
- Se agregó `pagina.clean_contents()` después de cada redacción/borrado de
  imagen, para evitar errores de "recurso no encontrado" (GS1, GS2, I2) que
  aparecían tras varias ediciones seguidas en la misma sesión.
- Se agregó un botón "Usar clic en la página" como alternativa a escribir
  coordenadas X/Y a mano, para reposicionar texto e imágenes con solo un clic.

**Empaquetado (Fase 8):**
1. Se instaló PyInstaller en el entorno virtual.
2. Se generó el ejecutable con:
   ```
   pyinstaller --name mi_adobe_editor --windowed --onedir \
     --collect-all pymupdf --collect-all pdf2docx --collect-all ocrmypdf \
     app/main.py
   ```
3. Se probó exitosamente: el programa abre sin necesitar `venv` activado
   ni Python visible, directo desde `dist/mi_adobe_editor/mi_adobe_editor`.
4. Se creó un lanzador de escritorio (`~/.local/share/applications/mi-adobe-editor.desktop`)
   para que aparezca en el menú de aplicaciones de Linux Mint como cualquier
   otro programa instalado — confirmado funcionando.
5. Se documentó en `EMPAQUETADO.md` el mismo proceso para Windows (pendiente
   de generar y probar en una PC con Windows real, no se puede hacer desde Linux).
6. Se actualizó `.gitignore` para excluir `build/`, `dist/` y `*.spec`
   (archivos generados, pesan cientos de MB, no deben subirse al repositorio).

**Resultado:** Editor de PDF funcionando como aplicación de escritorio real
en Linux Mint, con ícono propio en el menú de aplicaciones. Varios bugs
importantes de la Fase 4 corregidos y probados contra documentos reales.

**Pendiente para futuras sesiones:**
- Generar y probar el `.exe` en una PC con Windows real
- Rellenar formularios PDF, notas tipo "sticky note"
- Ícono propio del programa (por ahora usa el genérico de PDF del sistema)

---

## Sesión 6 — 2026-10-10

**Objetivo de la sesión:** Revisar el estado completo del proyecto en una máquina Windows
nueva (esta sesión se hizo desde Windows, no desde el Linux Mint de siempre), limpiar
código y sincronizar la documentación (`README.md`, `ROADMAP.md` y esta bitácora) para
que digan exactamente lo que el programa puede hacer hoy.

**Contexto:** El último trabajo de código real fue la Sesión 5 (2026-09-05). Después solo
se agregaron la licencia MIT y su sección en el README (2026-09-18). La rama
`estandarizar` tenía 2 commits sin publicar. Al releer todo el proyecto se encontraron
cosas que habían quedado sin registrar ni corregir.

**Actividades realizadas:**
1. Lectura completa de la estructura y de todos los archivos del proyecto
   (`README.md`, `ROADMAP.md`, `BITACORA.md`, `EMPAQUETADO.md`, las guías de
   instalación, `requirements.txt` y `app/main.py`, que tiene 1803 líneas).
2. **Corrección de bug**: la función `convertir_a_word()` estaba **definida dos veces**
   seguidas en `app/main.py`. En Python, si defines una función con el mismo nombre dos
   veces, la segunda "pisa" a la primera y el código anterior queda muerto (nunca se
   ejecuta, aunque parezca que sí al leerlo). Se eliminó la segunda copia y se conservó
   la primera, que tenía el manejo de errores más completo y el aviso sobre las
   limitaciones del formato Word.
3. **Limpieza de `requirements.txt`**: `pdf2docx` aparecía dos veces, con dos comentarios
   distintos para la misma librería. Se dejó una sola entrada.
4. **Título de ventana**: decía "Mi Adobe PDF - Fase 2" (etiqueta vieja de cuando el
   programa era solo el visor). Se cambió a "Mi Adobe PDF" en los dos lugares donde
   aparecía.
5. **Docstring de `app/main.py`**: el texto de cabecera describía el programa como
   "Fase 2 (v2)" y solo mencionaba el scroll continuo. Se reescribió para que liste el
   estado real: anotaciones, edición de contenido, gestión de páginas, Word, OCR,
   compresión y contraseñas.
6. **`ROADMAP.md` sincronizado con la realidad**: la Fase 4 (edición de texto real) ya
   estaba construida y probada desde las Sesiones 4 y 5, pero **nunca se había marcado
   como completada**. Se marcó ✅, se detalló lo que sí hace (detectar bloques de texto,
   editar contenido, tamaño/color/negrita/cursiva, y de bonus también imágenes y formas
   de color) y se dejó escrita la limitación técnica real de los PDFs. También se
   marcaron los avances parciales de las Fases 6 (OCR, Word, imágenes) y 7 (contraseña,
   firma por imagen), y se actualizó la Fase 2 (la firma por imagen ya existe).
7. **`README.md` corregido**: la "Estructura del proyecto" anunciaba carpetas `assets/`
   y `tests/` que no existen (prometer cosas que no están confunde a quien llegue al
   repositorio). Se dejó la estructura real, se agregaron `LICENSE` y `EMPAQUETADO.md`
   (que existía pero no estaba enlazado desde ningún lado del README), y se agregó una
   sección breve de "Estado actual" junto al checklist de objetivos.
8. Verificación con Python (`ast.parse`) de que `app/main.py` sigue siendo un archivo
   válido tras los cambios: quedó en 1771 líneas, sin errores de sintaxis.

**Problemas encontrados y explicación:**
- **Función duplicada (`convertir_a_word`)**: no rompía el arranque del programa (Python
  no se queja de eso), pero la copia muerta engañaba al leer el código: parecía que
  había dos formas de convertir a Word cuando en realidad solo se ejecutaba una. Es el
  tipo de cosa que se ve leyendo el código completo, no usando el programa.
- **Documentación desincronizada**: el README decía que la edición de texto y el OCR
  estaban hechos, y el ROADMAP no los marcaba como completados. Dos archivos diciendo
  cosas distintas sobre el mismo programa.

**Resultado:** Código limpio (sin funciones duplicadas) y los tres archivos de control
(README, ROADMAP y BITACORA) diciendo lo mismo y coincidiendo con lo que el programa
realmente hace. Base ordenada para arrancar la Fase 5.

**Pendiente para futuras sesiones:**
- Fase 5: formularios PDF (rellenar los existentes y crear campos nuevos)
- Notas tipo "sticky note", redacción permanente, firma con certificado, exportar a Excel
- Generar y probar el `.exe` en Windows: esta sesión fue en Windows, pero **todavía no
  existe el entorno virtual (`venv/`) en esta máquina**, así que no se instaló nada ni
  se ejecutó el programa
- Ícono propio del programa y creación de la carpeta `assets/`
- Fase 9: manual de usuario, capturas de pantalla, video demo
- **Git:** los cambios de esta sesión están en la rama local `estandarizar`, que además
  tenía 2 commits sin publicar desde 2026-09-18. Falta decidir con el usuario cuándo
  hacer commit y cuándo subirlos a GitHub.

---

## Sesión 7 — 2026-10-10

**Objetivo de la sesión:** Tarea 0 del plan `DISENO_EDITOR_TEXTO.md`: preparar las
herramientas de desarrollo (pytest y pyright) y el punto de partida de las pruebas
automáticas (`tests/conftest.py`), sin tocar el código del programa.

**Actividades realizadas:**
1. **`requirements-dev.txt` creado** con `pytest` y `pyright`, marcados como
   dependencias solo de desarrollo (el programa no las necesita para funcionar).
2. **Instalación en el `venv`** con `pip install -r requirements-dev.txt`:
   `pytest 9.1.1` se instaló nuevo (más sus dependencias `colorama` e `iniconfig`);
   `pyright 1.1.414` ya estaba instalado.
3. **`tests/conftest.py` creado**: agrega la raíz del proyecto y `app/` a `sys.path`
   (los imports van sin prefijo de paquete, igual que al lanzar `iniciar.bat`) y
   fija `QT_QPA_PLATFORM=offscreen` para que las ventanas de prueba no se abran en
   pantalla.
4. Verificación manual del `conftest.py` con `runpy`: la variable
   `QT_QPA_PLATFORM` queda en `offscreen` y las dos rutas aparecen en `sys.path`.
5. **Pyright**: 44 errores, todos preexistentes en `app/main.py` (enums cortos de
   Qt, `Document` iterable, `PDF_ENCRYPT_AES_256`, `pixmap_limpio`, más algunos
   `reportOptionalMemberAccess`/`reportOptionalSubscript`); ninguno en los archivos
   nuevos.
6. **Pytest**: corre sin error de configuración; termina con "no tests ran" y
   código de salida 5, que es el código estándar de pytest cuando no hay pruebas
   (todavía no existe ningún archivo `test_*.py`).

**Resultado:** Base de pruebas lista: a partir de la Tarea 1, cada módulo nuevo
tendrá sus pruebas en `tests/` y bastará con `pytest -v`. El programa no se tocó.

**Pendiente:**
- Tarea 1: `app/formato_html.py` (tipografías, CSS, fragmentos → HTML) y sus pruebas.
- Errores de pyright en `app/main.py` que no están en la lista de "ruido conocido"
  de AGENTS.md (`"widget" is not a known attribute of "None"` en la línea 610 y
  varios `Object of type "None" is not subscriptable` en 778, 1298, 1307 y 1384).
  No se corrigieron: están fuera del alcance de la Tarea 0.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` es el resto de pruebas de
  una sesión anterior que ya no existen; no se borró nada sin permiso.

---

<!-- Copia el bloque de abajo cada vez que trabajemos una nueva sesión -->
<!--
## Sesión N — YYYY-MM-DD

**Objetivo de la sesión:**

**Actividades realizadas:**
1.

**Resultado:**

**Pendiente:**
-->

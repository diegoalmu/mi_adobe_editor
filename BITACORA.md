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

## Sesión 8 — 2026-10-10

**Objetivo de la sesión:** Mantenimiento (fuera del plan `DISENO_EDITOR_TEXTO.md`):
corregir los 5 errores de pyright que quedaron al aire en `app/main.py` después de
la Sesión 7 y que no forman parte del "ruido conocido" de AGENTS.md, sin tocar nada
más.

**Actividades realizadas:**
1. **`app/main.py` línea 610** (`dibujar_todas_las_paginas`): `takeAt(0)` puede
   devolver `None`. Se agregó `if item is None: continue` (líneas 610–611) antes de
   llamar `item.widget()`.
2. **`app/main.py` línea 776** (`redibujar_pagina_individual`): al inicio del método
   se agregó `if self.documento is None: return` (líneas 776–777), el mismo estilo
   que ya se usa en otros métodos (por ejemplo `al_seleccionar_rectangulo`).
3. **`app/main.py` línea 1302** (`escribir_texto_en_punto`): mismo guard
   `if self.documento is None: return` (líneas 1302–1303) antes de
   `pagina = self.documento[numero_pagina]`.
4. **`app/main.py` línea 1313** (`escribir_cuadro_de_texto_en_punto`): mismo guard
   (líneas 1313–1314).
5. **`app/main.py` línea 1392** (`colocar_imagen_en_punto`): mismo guard
   (líneas 1392–1393).
6. **Pyright**: de 44 errores a **39**, todos restantes son el ruido conocido de
   AGENTS.md (enums cortos de Qt, `Document` iterable, `PDF_ENCRYPT_AES_256`,
   `pixmap_limpio`). Los 5 objetivos desaparecieron.
7. **Pytest**: sin pruebas todavía (sale "no tests ran", código 5), igual que en la
   Sesión 7; no hay errores de configuración.

**Resultado:** `app/main.py` ya no tiene errores de pyright fuera de la lista de
ruido conocido. Las 5 correcciones son defensivas: en condiciones normales el
documento está abierto y `takeAt` no devuelve `None`, así que el comportamiento del
programa no cambia; solo se evita un choque teórico si eso llegara a pasar.

**Pendiente:**
- Tarea 1 del diseño: `app/formato_html.py` (tipografías, CSS, fragmentos → HTML)
  y sus pruebas.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no se borró
  nada sin permiso.
- **Corrección posterior (misma sesión):** en `dibujar_todas_las_paginas` se cambió
  `continue` por `break` en la guarda de `takeAt` (línea 611): si `takeAt(0)`
  devolviera `None`, `count` no bajaría y `continue` causaría un ciclo infinito;
  con `break` se sale del `while` y no queda colgado el programa.

---

## Sesión 9 — 2026-10-10

**Objetivo de la sesión:** Tarea 1 del plan `DISENO_EDITOR_TEXTO.md`: crear
`app/formato_html.py` con las tipografías, el CSS de los `@font-face` y la
conversión de fragmentos del editor a HTML para `insert_htmlbox`, más sus
pruebas automáticas. No se tocó `app/main.py` ni la ventana de edición.

**Actividades realizadas:**
1. **`app/formato_html.py` creado** (144 líneas), con tres piezas:
   - Constante `TIPOGRAFIAS` (líneas 25–56): la tabla del diseño con las 5
     tipografías (Arial, Times New Roman, Calibri, Verdana y Courier New) y
     sus 4 archivos .ttf cada una (normal, negrita, cursiva, negrita+cursiva).
   - `CARPETA_FUENTES_WINDOWS = r"C:\Windows\Fonts"` (línea 59).
   - `tipografias_disponibles(carpeta)` (líneas 62–74): devuelve solo los
     nombres cuyos 4 archivos existen en la carpeta indicada; si falta
     alguno, esa tipografía no se ofrece y el programa no truena.
   - `css_tipografias(carpeta)` (líneas 77–100): un `@font-face` por
     variante (familia + font-weight + font-style + `src: url(archivo.ttf)`)
     de cada tipografía disponible; con carpeta vacía el CSS queda vacío.
     Los archivos se referencian solo por nombre porque el CSS se pasará a
     `insert_htmlbox` junto con un `fitz.Archive` de esa misma carpeta
     (eso llega en la Tarea 2).
   - `fragmentos_a_html(fragmentos)` (líneas 107–144): convierte cada
     fragmento (texto, familia, tamano, negrita, cursiva, subrayado, color)
     en un `<span style="...">`; solo agrega las propiedades activas
     (`font-weight:bold` únicamente si el fragmento está en negrita),
     escapa `<`, `>` y `&`, convierte `\n` en `<br>` y pone el color como
     `#rrggbb`.
2. **`tests/test_formato_html.py` creado** (65 líneas) con las 4 pruebas que
   pide el diseño, todas en verde:
   - `test_escapa_caracteres_especiales`: `"<b>"` queda como `&lt;b&gt;`.
   - `test_negrita_solo_en_su_span`: `font-weight:bold` aparece una sola
     vez, solo en el fragmento en negrita.
   - `test_salto_de_linea_se_convierte_en_br`: `"\n"` produce `<br>`.
   - `test_carpeta_vacia_no_hay_tipografias_ni_css`: carpeta temporal vacía
     → lista vacía y CSS `""`.
   - El import va sin prefijo de paquete (`from formato_html import ...`,
     igual que correrá el programa); como Pyright no ve la ruta que agrega
     `conftest.py` en tiempo de ejecución, el archivo lleva
     `# pyright: reportMissingImports=false` explicado en su docstring.
3. **Pyright**: 39 errores, los mismos 39 de ruido conocido de
   `app/main.py` que ya había antes de esta tarea; cero errores nuevos en
   los archivos creados.
4. **Pytest**: 4 pruebas, 4 en verde.

**Resultado:** `app/formato_html.py` queda listo como módulo puro (sin
ventanas): la Tarea 2 podrá usar `fragmentos_a_html` y `css_tipografias`
para escribir texto con formato mixto en el PDF real. El programa en
funcionamiento no cambió todavía (nada lo importa aún).

**Pendiente:**
- Tarea 2: `cabe_texto_con_formato` e `insertar_texto_con_formato` en
  `app/formato_html.py`, usando `insert_htmlbox` con un `fitz.Archive` de
  la carpeta de fuentes, y sus pruebas con un PDF en memoria.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no se
  borró nada sin permiso.

---

## Sesión 10 — 2026-10-11

**Objetivo de la sesión:** Tarea 2 del plan `DISENO_EDITOR_TEXTO.md`: agregar a
`app/formato_html.py` las funciones que comprueban si un HTML con formato cabe en
un cuadro y que lo escriben en el PDF real con `insert_htmlbox`, más sus pruebas
con un PDF en memoria. No se tocó `app/main.py` ni la ventana de edición.

**Actividades realizadas:**
1. **`app/formato_html.py` modificado**:
   - Línea 19: se agregó `import fitz  # PyMuPDF` (el módulo ya lo usará para
     crear el documento temporal y escribir en la página).
   - Líneas 154–175: `cabe_texto_con_formato(rect, html, css, archivo)` → crea un
     documento PDF temporal descartable (mismo patrón que `texto_cabe_en_cuadro`
     de `main.py`), llama `insert_htmlbox(..., scale_low=1)` y devuelve
     `True`/`False` según la holgura devuelta (negativa = no cabe). Con
     `scale_low=1` el texto nunca se reduce para que quepa.
   - Líneas 178–185: `insertar_texto_con_formato(pagina, rect, html, css,
     archivo)` → escribe en la página real con el mismo `scale_low=1`; solo se
     llama después de confirmar con la función anterior que cabe.
   - Líneas 5–7: se ajustó el docstring del módulo para mencionar estas
     funciones.
2. **`tests/test_insertar_formato.py` creado** (85 líneas), con las 2 pruebas
   que pide el diseño, usando un PDF en memoria (`fitz.open()` sin archivos):
   - `test_inserta_negrita_solo_en_actualizado` (líneas 47–68): construye el
     HTML de "Precio actualizado" con solo la segunda palabra en negrita (con
     `fragmentos_a_html`), confirma que cabe, lo inserta y verifica con
     `get_text("dict")` que hay un span en negrita con "actualizado" (bit 16 de
     flags = `TEXT_FONT_BOLD`) y otro sin negrita con "Precio".
   - `test_texto_enorme_no_cabe_y_no_modifica_el_documento` (líneas 71–85):
     4000 palabras en un cuadro de 40x40 puntos → `cabe_texto_con_formato`
     devuelve `False` y el documento real queda intacto (el texto de la página
     no cambia).
3. **Pyright**: 39 errores, los mismos 39 de ruido conocido de `app/main.py`;
   cero errores nuevos en los archivos creados o modificados.
4. **Pytest**: 6 pruebas (las 4 de la Tarea 1 + las 2 nuevas), todas en verde.

**Resultado:** El lado PyMuPDF de `app/formato_html.py` queda completo para el
editor de texto: ya se puede pasar de fragmentos → HTML → PDF con formato mixto,
y antes de tocar el documento real se puede preguntar si el texto cabe. El
programa en funcionamiento no cambió todavía (nada importa estas funciones
todavía); eso llega en la Tarea 5.

**Pendiente:**
- Tarea 3: `app/editor_texto.py` con la clase `EditorTextoInline` y la función
  `documento_a_fragmentos`, y sus pruebas en modo offscreen.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no se borró
  nada sin permiso.

---

## Sesión 11 — 2026-10-11

**Objetivo de la sesión:** Tarea 3 del plan `DISENO_EDITOR_TEXTO.md`: crear
`app/editor_texto.py` con la clase `EditorTextoInline` (el `QTextEdit` que se
pone encima de un párrafo) y la función `documento_a_fragmentos`, más sus
pruebas en modo offscreen. También corregir la fecha de la sesión anterior y
agregar la regla de la fecha a `AGENTS.md`.

**Actividades realizadas:**
1. **`app/editor_texto.py` creado** (112 líneas):
   - Líneas 20–46: clase `EditorTextoInline(QTextEdit)` → sin marco
     (`QFrame.Shape.NoFrame`, línea 33), fondo blanco semitransparente
     (`rgba(255, 255, 255, 200)`, línea 34) y señales `cancelado`/`aceptado`
     (líneas 28–29). En `keyPressEvent` (líneas 36–46), Esc → `cancelado` y
     Ctrl+Enter (`Qt.Key.Key_Return`/`Key_Enter` + `ControlModifier`) →
     `aceptado`; todo lo demás pasa al `QTextEdit` de base. Se usaron enums
     completos de Qt en todo el archivo.
   - Líneas 53–112: `documento_a_fragmentos(documento_qt)` → recorre bloques
     y fragmentos del documento con `bloque.begin()` + `iterador += 1`, y
     devuelve diccionarios con `texto`, `familia`, `tamano`, `negrita`,
     `cursiva`, `subrayado` y `color` (tupla rgb), el formato que consume
     `fragmentos_a_html`. `negrita` se decide con
     `fontWeight() >= int(QFont.Weight.Bold)` (línea 87); la familia y el
     tamaño caen a la fuente por defecto del documento si el fragmento no los
     trae (líneas 76–77); el color negro `(0, 0, 0)` si es inválido (líneas
     78–82). Entre bloques agrega `"\n"` al final del último fragmento, o un
     fragmento solo con `"\n"` si el bloque está vacío (líneas 94–107), para
     que después se convierta en `<br>`.
2. **`tests/test_editor_texto.py` creado** (63 líneas, con
   `# pyright: reportMissingImports=false` y `QApplication` única a nivel de
   módulo), con 3 pruebas:
   - `test_documento_a_fragmentos_con_negrita_en_dos`: escribe "uno dos tres",
     selecciona "dos" (posiciones 4–7), le pone negrita con
     `mergeCharFormat` y verifica que ese fragmento tiene `negrita=True` y
     que "uno"/"tres" no.
   - `test_esc_emite_cancelado` y `test_ctrl_enter_emite_aceptado`:
     envían un `QKeyEvent` directo a `keyPressEvent` y comprueban la señal.
3. **Verificación previa de la API de Qt** (script temporal fuera del
   repositorio): se confirmó que `iterador += 1`, `mergeCharFormat`,
   `fontFamilies()` (el antiguo `fontFamily()` está obsoleto) y la lectura de
   `fontWeight()`, `fontItalic()`, `fontUnderline()` y `foreground()` funcionan
   en el venv; se descartó el script sin borrar nada del proyecto.
4. **`BITACORA.md` corregido**: la sesión 10 estaba fechada 2026-10-10 y el
   comando `Get-Date -Format yyyy-MM-dd` dio 2026-10-11, así que se cambió la
   fecha de la sesión 10 a 2026-10-11 (misma fecha que esta sesión).
5. **`AGENTS.md` modificado** (líneas 59–62): en "Al terminar cada sesión",
   punto 1, se agregó la regla de obtener la fecha con
   `Get-Date -Format yyyy-MM-dd` y nunca copiarla de la entrada anterior.
6. **Pyright**: 39 errores, los mismos 39 de ruido conocido de `app/main.py`;
   cero errores en `app/editor_texto.py` ni `tests/test_editor_texto.py`.
7. **Pytest**: 9 pruebas (4 de la Tarea 1 + 2 de la Tarea 2 + 3 nuevas),
   todas en verde.

**Resultado:** El lado Qt del editor de texto queda listo: `EditorTextoInline`
es el cuadro que se superpondrá al párrafo (con Esc/Ctrl+Enter) y
`documento_a_fragmentos` traduce lo que el usuario escribió al formato de
fragmentos que ya sabe consumir `formato_html.py`. El programa en
funcionamiento todavía no lo usa; eso llega en la Tarea 5.

**Pendiente:**
- Tarea 4: la barra de formato (negrita, cursiva, etc.) según
  `DISENO_EDITOR_TEXTO.md`.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no se borró
  nada sin permiso.

---

## Sesión 12 — 2026-10-11

**Objetivo de la sesión:** Tarea 4 del plan `DISENO_EDITOR_TEXTO.md`: agregar
a `app/editor_texto.py` la clase `BarraFormato(QToolBar)` con selector de
tipografía, tamaño, botones de Negrita/Cursiva/Subrayado, botón de color,
Aceptar y Cancelar, y sus pruebas en modo offscreen. No se tocó `main.py`.

**Actividades realizadas:**
1. **`app/editor_texto.py` modificado** (de 112 a 314 líneas):
   - Líneas 1–28: se actualizó el docstring del módulo para mencionar
     `BarraFormato` y se agregaron los imports (`QColor`, `QComboBox`,
     `QColorDialog`, `QPushButton`, `QToolBar`, `QToolButton`, y de
     `formato_html` las constantes `CARPETA_FUENTES_WINDOWS` y
     `tipografias_disponibles`). Los imports entre módulos de `app/` van
     sin prefijo de paquete, como manda `AGENTS.md`.
   - Línea 67: constante `TAMANOS` con los 16 tamaños en puntos que ofrece
     la barra (8 a 72, como un procesador de textos clásico).
   - Líneas 70–249: clase `BarraFormato(QToolBar)` →
     - `__init__` (líneas 85–143): recibe el editor como parámetro
       obligatorio; arma el selector de tipografía con **solo**
       `tipografias_disponibles(CARPETA_FUENTES_WINDOWS)` (líneas 90–95),
       el de tamaño con `TAMANOS` (líneas 98–102), los botones activables
       N/C/S (`QToolButton` con `setCheckable(True)`, líneas 105–119), el
       botón Color (líneas 122–125), Aceptar y Cancelar (líneas 128–134);
       al final se conecta `editor.cursorPositionChanged` a
       `actualizar_desde_cursor` y se llama una vez (líneas 137–138). Se
       usaron enums completos de Qt en todo el archivo (p. ej.
       `QFont.Weight.Bold`).
     - Cada control aplica el formato **solo a la selección** con
       `mergeCurrentCharFormat`: `aplicar_tipografia` (145–151),
       `aplicar_tamano` (153–159), `alternar_negrita` (161–168),
       `alternar_cursiva` (170–174) y `alternar_subrayado` (176–180).
       Sin selección aplica a lo que se escriba después (comportamiento
       normal de Qt, igual que Word).
     - Botón de color en **dos partes**: `elegir_color` (líneas 182–186)
       abre el `QColorDialog` de Windows y `aplicar_color(QColor)`
       (líneas 188–194) aplica el color a la selección y pinta el botón
       con `_pintar_boton_color` (196–202). Las pruebas usan solo
       `aplicar_color`; el diálogo nunca se abre en pruebas.
     - Señales `aceptar` y `cancelar` (líneas 80–81), emitidas por los
       botones Aceptar/Cancelar.
     - `actualizar_desde_cursor` (líneas 204–244): lee el
       `charFormat()` del cursor y refleja familia, tamaño, los tres
       botones y el color; **bloquea las señales de sus controles**
       (`blockSignals`) mientras actualiza, para que marcar un botón no
       vuelva a aplicar el formato al cursor ni dispare un bucle de
       señales. El tamaño más cercano se resuelve con
       `_indice_de_tamano` (246–249).
2. **`tests/test_editor_texto.py` modificado** (de 63 a 142 líneas), con
   las 2 pruebas que pide el diseño más 2 que cubren las reglas
   adicionales (color y tipografías):
   - `test_barra_negrita_aplica_solo_a_la_seleccion` (líneas 67–89):
     selecciona "dos" en "uno dos tres", activa `barra.boton_negrita` y
     verifica con `documento_a_fragmentos` que solo "dos" quedó en
     negrita.
   - `test_barra_refleja_negrita_del_cursor` (líneas 91–117): pone "dos"
     en negrita, deja el cursor en "uno", crea la barra (botón sin
     marcar) y al mover el cursor dentro de "dos" verifica que el botón
     Negrita se marca solo.
   - `test_barra_aplicar_color_a_la_seleccion` (líneas 119–135): usa
     `aplicar_color(QColor(200, 10, 50))` sobre "dos" y verifica la
     tupla rgb del fragmento; el diálogo no se abre.
   - `test_barra_tipografias_solo_las_disponibles` (líneas 137–142):
     verifica que el combo contiene exactamente
     `tipografias_disponibles(CARPETA_FUENTES_WINDOWS)`.
3. **Pyright**: 39 errores, los mismos 39 de ruido conocido de `app/main.py`;
   cero errores en `app/editor_texto.py` ni `tests/test_editor_texto.py`.
4. **Pytest**: 13 pruebas (3 de la Tarea 3 + 4 nuevas + 4 de la Tarea 1 +
   2 de la Tarea 2), todas en verde.

**Resultado:** La barra de formato queda completa y probada: aplica
tipografía, tamaño, negrita, cursiva, subrayado y color solo a la
selección, refleja el formato del cursor sin bucles de señales, y expone
las señales `aceptar`/`cancelar`. Con esto están listos el cuadro editable
(Tarea 3) y la barra (Tarea 4); el programa en funcionamiento todavía no
los usa porque falta la Tarea 5, que los conecta en `main.py`.

**Pendiente:**
- Tarea 5: conectar todo en `app/main.py` (`editar_contenido_en_punto`),
  con su validación visual de Diego.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no se
  borró nada sin permiso.

---

## Sesión 13 — 2026-10-11

**Objetivo de la sesión:** Tarea 5 del plan `DISENO_EDITOR_TEXTO.md`:
conectar el editor en línea y la barra de formato en `app/main.py`, con la
conversión de tamaños puntos PDF ↔ puntos Qt según el zoom del visor.

**Actividades realizadas:**
1. **`app/editor_texto.py` modificado** (de 314 a 365 líneas):
   - Líneas 10–15: docstring del módulo actualizado para mencionar
     `tamano_pdf_a_editor` / `tamano_editor_a_pdf`.
   - Líneas 80–98: nuevas funciones `tamano_pdf_a_editor` (punto PDF →
     punto Qt: `punto_pdf * zoom * 72 / dpi_logica`) y `tamano_editor_a_pdf`
     (inversa exacta). Fórmula verificada empíricamente: a 96 DPI y zoom 1,
     12 puntos PDF = 9 puntos Qt.
   - Líneas 111–124: `BarraFormato.__init__` ahora recibe `zoom=1.0` y
     `dpi_logica=96.0` y los guarda; docstring explica que el combo de
     tamaños muestra puntos PDF.
   - Líneas 190–200: `aplicar_tamano` convierte el punto PDF elegido a
     puntos Qt antes de aplicarlo.
   - Líneas 268–274: `actualizar_desde_cursor` convierte el punto Qt del
     cursor a puntos PDF para resaltar el tamaño en el combo.
   - Líneas 299–365: `documento_a_fragmentos` acepta `zoom=None` y
     `dpi_logica=None`; si se pasan, convierte cada tamaño Qt → PDF
     (para el HTML del PDF). Sin parámetros se comporta como antes (las
     pruebas viejas no cambian).
2. **`app/main.py` modificado** (de 1776 a 1855 líneas):
   - Líneas 39–51: imports nuevos (`QFont`, `QTextCharFormat`,
     `QTextCursor` en QtGui; de `editor_texto` las 4 funciones; de
     `formato_html` las 6 utilidades del HTML con formato).
   - Líneas 440–445: atributos `editor_texto_inline`, `barra_formato` y
     `parrafo_editando` (todos en `None` al arrancar).
   - Línea 628: `dibujar_todas_las_paginas` cancela la edición activa
     antes de destruir las etiquetas (cubre también abrir PDF, rotar,
     eliminar/insertar página, guardar).
   - Líneas 715 y 722: `zoom_mas` / `zoom_menos` cancelan la edición
     antes de redibujar con el nuevo zoom.
   - Líneas 737–738: `al_seleccionar_rectangulo` no hace nada si hay
     una edición en línea abierta (los clics quedan bloqueados).
   - Líneas 788 y 795: la llamada a `editar_contenido_en_punto` ahora
     pasa `numero_pagina`; el refresco de recuadros se delegó a
     `refrescar_recuadros_pagina`.
   - Líneas 819–838: nuevo método `refrescar_recuadros_pagina`
     (extraído del bloque viejo de `al_seleccionar_rectangulo`; también
     verifica que la herramienta siga siendo "Editar contenido").
   - Líneas 1136–1154: `editar_contenido_en_punto` ahora recibe
     `numero_pagina` y pasa el párrafo encontrado a
     `editar_parrafo_encontrado(numero_pagina, pagina, parrafo)`.
   - Líneas 1218–1289: `editar_parrafo_encontrado` reescrito por
     completo: cancela edición previa, crea un `EditorTextoInline` hijo
     de la `EtiquetaPDF` con `setGeometry(bbox * zoom)`, le pone el
     texto y el formato inicial (primera tipografía disponible,
     tamaño PDF→Qt, color del párrafo, negrita/cursiva según la fuente
     original), conecta `aceptado`/`cancelado`, y agrega una
     **`BarraFormato` nueva** debajo de la barra principal con
     `addToolBarBreak` + `addToolBar`. Guarda los tres atributos.
   - Líneas 1291–1296: nuevo método `_dpi_logica` (DPI lógico de la
     pantalla; 96 si no hay pantalla, por ejemplo en pruebas).
   - Líneas 1298–1352: nuevo método `aceptar_edicion_texto`: convierte
     el documento Qt a fragmentos **con** zoom/DPI (tamaños ya en
     puntos PDF), arma el HTML, prueba primero con
     `cabe_texto_con_formato` en el documento real (si no cabe, avisa
     y el editor sigue abierto), tapa el párrafo con
     `muestrear_color_de_fondo` + redact, escribe con
     `insertar_texto_con_formato`, y cierra + redibuja la página.
   - Líneas 1354–1367: `cancelar_edicion_texto` y `cerrar_edicion_texto`
     (quita la barra con `removeToolBar`, destruye editor y barra, y
     deja los tres atributos en `None`).
   - Líneas 1541, 1560 y 1596: `guardar_como`, `guardar` y
     `cerrar_documento` cancelan la edición activa (en `cerrar_documento`
     solo después de confirmar con Yes).
3. **`tests/test_editor_texto.py` modificado** (de 142 a 157 líneas):
   - `test_tamano_pdf_y_editor_ida_y_vuelta` (líneas 146–157): verifica
     la ida y vuelta exacta en 4 tamaños × 4 zooms y el caso 12 pt PDF
     = 9 pt Qt a 96 DPI y zoom 1.
4. **`tests/test_edicion_inline.py` creado** (140 líneas, 2 pruebas):
   - `test_editar_parrafo_en_linea_y_aceptar` (líneas 62–106): crea un
     PDF real en `tmp_path` con "uno dos tres" a 12 pt, abre
     `EditorPDF`, detecta el párrafo (bbox ensanchado +-10/+-5 para que
     la prueba de "si cabe" no dispare un QMessageBox que bloquearía la
     ejecución offscreen), edita en línea, pone "dos" en negrita con el
     botón de la barra, acepta, y verifica que la edición se cerró, que
     el span de "dos" tiene la marca de negrita (`flags & 16`), que el
     texto sigue legible (normalizando los espacios duros `\xa0` que
     genera `insert_htmlbox`), y que tras `guardar()` el archivo en
     disco conserva todo.
   - `test_editar_parrafo_y_cancelar_no_toca_el_pdf` (líneas 109–124):
     cambia el texto en el editor pero cancela; verifica que el PDF no
     cambió y que los atributos quedaron en `None`.
5. **Pyright**: 38 errores, los mismos de ruido conocido de `app/main.py`
   (enums Qt, `Document` iterable, `PDF_ENCRYPT_AES_256`,
   `pixmap_limpio`); cero errores en `app/editor_texto.py` ni en los
   tests.
6. **Pytest**: 16 pruebas (2 de la Tarea 5 + 8 de la Tarea 4/3 + 1 nueva
   de conversión + 4 de la Tarea 1 + 2 de la Tarea 2), todas en verde.

**Resultado:** La herramienta "Editar contenido (texto e imagenes)" ya
abre el párrafo en línea con una barra de formato completa debajo de la
principal. El texto solo se escribe en el PDF al dar Aceptar (o
Ctrl+Enter); Esc, Cancelar, guardar, cerrar y cambiar el zoom descartan
lo no aceptado. Los tamaños del combo son puntos PDF y el editor los
muestra a la escala del zoom, con ida y vuelta exacta.

**Pendiente:**
- Validación visual de Diego (ver checklist del resumen): tamaño del
  editor vs página a distintos zooms y DPI de Windows, barra debajo de
  la principal, Esc/Ctrl+Enter, clics bloqueados durante la edición,
  guardar/cerrar/zoom descartando la edición.
- Tarea 6: limpiar `DialogoEditarCuadroDeTexto` y los métodos
  `escribir_texto_en_punto` / `escribir_cuadro_de_texto_en_punto` que
  quedaron sin llamadores.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no
  se borró nada sin permiso.

---

## Sesión 14 — 2026-10-11

**Objetivo de la sesión:** Corrección de la Tarea 5 tras la validación
visual de Diego: fondo opaco del editor con el color real de la página,
sin barras de desplazamiento (el editor crece hacia abajo), cambio de
párrafo como Acrobat (clic en otro párrafo acepta el actual y abre el
nuevo) y pruebas de todo.

**Actividades realizadas:**
1. **Punto 1 — texto doble (fondo opaco):**
   - `app/editor_texto.py`: docstring del módulo (líneas 5–18) y de la
     clase (40–49) actualizados; `EditorTextoInline.__init__` (52–62)
     ya no usa `rgba(..., 200)` sino blanco opaco por defecto, y tiene
     el nuevo método `pintar_fondo(color_rgb)` (64–69) que pinta el
     fondo opaco con una tupla rgb 0–255.
   - `app/main.py`: en `editar_parrafo_encontrado` (1277–1280) se mide
     el color con `muestrear_color_de_fondo(pagina, bbox)` y se pinta
     con `editor.pintar_fondo(...)` (convertido de 0–1 a 0–255): el
     cuadro se ve del mismo color que la página y no se ve el texto
     original debajo.
2. **Punto 2 — sin scrollbars, crece hacia abajo:**
   - `app/editor_texto.py`: en `__init__` (55–58) las dos barras de
     desplazamiento quedan siempre apagadas
     (`Qt.ScrollBarPolicy.ScrollBarAlwaysOff`); nueva función pura
     `calcular_altura_editor(altura_contenido, altura_minima,
     altura_maxima)` (122–138) que devuelve el contenido sin bajar del
     piso (parrafo original) ni pasar del techo (parrafo + espacio
     libre).
   - `app/main.py`: `editar_parrafo_encontrado` calcula
     `altura_minima` = alto del párrafo × zoom y `altura_maxima` = esa
     más `calcular_espacio_disponible_vertical` × zoom (si no hay texto
     debajo, hasta `pagina.rect.height - bbox.y1`, líneas 1259–1265);
     las guarda en `parrafo_editando` (1318–1322); conecta
     `documentSizeChanged` a `_ajustar_altura_editor` (1310–1312), el
     nuevo método (1336–1358) que recalculla la altura con
     `calcular_altura_editor` y solo cambia la geometría del editor.
     `aceptar_edicion_texto` (1365–1436) ahora usa un `rect_destino`
     (1384–1389) con la altura final del editor en píxeles convertida
     a puntos PDF (`altura_editor_px / self.zoom`); el aviso de "no
     cabe" quedó solo para cuando ya no queda espacio libre (mensaje
     actualizado, 1409–1418).
3. **Punto 3 — cambio de párrafo como Acrobat:**
   - `app/main.py`: `al_seleccionar_rectangulo` (732–773) ya no
     bloquea los clics con la edición abierta: si hay editor y la
     herramienta es "Editar contenido", un clic sobre un párrafo (el
     mismo u otro) intenta `aceptar_edicion_texto()`; si devuelve
     `True` (cabió), se rebusca el párrafo en el punto del clic (la
     página ya se redibujó) y se abre ahí el editor; si devuelve
     `False` (no cabe), el aviso ya salió y se sigue en la edición
     actual. Clics fuera de párrafos u otras herramientas: no hacen
     nada (749–755).
   - `aceptar_edicion_texto` ahora devuelve `True`/`False` (True solo
     al escribir y cerrar).
4. **Punto 4 — pruebas:**
   - `tests/test_editor_texto.py` (de 157 a 168 líneas):
     `test_calcular_altura_editor_limita_entre_minima_y_maxima`
     (líneas 161–168): contenido cómodo, piso, techo y techo<piso.
   - `tests/test_edicion_inline.py` (de 140 a 193 líneas):
     `test_clic_en_otro_parrafo_acepta_y_abre_el_nuevo` (143–193):
     PDF con "parrafo A" y "parrafo B", edición de A con texto
     cambiado, clic simulado en el centro de B vía
     `al_seleccionar_rectangulo` con `QRect` en píxeles (y la
     herramienta puesta en "Editar contenido"), verifica que "A
     editado" quedó en el PDF y que el editor abierto es el de B
     (`parrafo_editando["bbox"] == parrafo_b["bbox"]`). La aserción de
     `parrafo_editando` del test de aceptar se ajustó a las 4 claves
     nuevas (líneas 82–84).
5. **Pyright**: 0 errores en `app/editor_texto.py` y los tests; los
   mismos 38 de ruido conocido de `app/main.py` (enums Qt, `Document`
   iterable, `PDF_ENCRYPT_AES_256`, `pixmap_limpio`).
6. **Pytest**: 18 pruebas (3 de esta corrección + 15 previas), todas en
   verde.

**Resultado:** El editor en línea ya no muestra el texto original
debajo (fondo opaco del color real de la página), no tiene scrollbars y
crece hacia abajo conforme se escribe hasta el espacio libre (y al
aceptar, el texto se escribe en el PDF con esa altura). Cambiar de
párrafo funciona como en Acrobat: con una edición abierta, un clic en
otro párrafo acepta el actual (si cabe) y abre el nuevo; si no cabe, se
queda en el actual con el aviso.

**Pendiente:**
- Validación visual de Diego de esta corrección: fondo del cuadro igual
  al de la página (títulos con color), editor creciendo al escribir
  varias líneas (sin scrollbars), aviso solo al no tener espacio, y
  clic en otro párrafo aceptando y abriendo el nuevo.
- Tarea 6: limpiar `DialogoEditarCuadroDeTexto` y los métodos
  `escribir_texto_en_punto` / `escribir_cuadro_de_texto_en_punto` que
  quedaron sin llamadores.
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no
  se borró nada sin permiso.

---

## Sesión 15 — 2026-10-11

**Objetivo de la sesión:** Tarea 6 del plan `DISENO_EDITOR_TEXTO.md`
(limpieza y documentación), ya validada por Diego la Tarea 5 y su
corrección. Reglas: buscar cada candidato en todo el proyecto antes de
borrar, no tocar `DialogoPosicionarImagen` ni nada de imágenes/formas,
y documentar el estado + limitaciones conocidas.

**Actividades realizadas:**

1. **Búsquedas previas (grep en `app/` y `tests/`, antes de borrar):**
   - `DialogoEditarCuadroDeTexto`: solo la definición de la clase;
     cero instanciaciones ni referencias en código (las únicas apariciones
     eran en `BITACORA.md` y este documento de diseño, que son
     documentación histórica).
   - `texto_cabe_en_cuadro`: solo la definición; cero llamadas
     (`self.texto_cabe_en_cuadro(` no aparece en ningún archivo `.py`).
   - `escribir_texto_en_punto` / `escribir_cuadro_de_texto_en_punto`:
     solo las definiciones; ningún llamador.
   - `QTextEdit` en el import de `app/main.py`: su único uso era la
     caja de texto del diálogo borrado.
2. **Borrados en `app/main.py` (de 1939 a 1774 líneas, −165):**
   - Cabecera de sección + clase `DialogoEditarCuadroDeTexto` completas
     (antes líneas 236–358: 123 líneas con sus 7 métodos).
   - `texto_cabe_en_cuadro` (antes 1113–1131: 19 líneas) — era el helper
     de "¿cabe?" del flujo viejo; el flujo nuevo usa
     `cabe_texto_con_formato` de `formato_html.py`.
   - `escribir_texto_en_punto` y `escribir_cuadro_de_texto_en_punto`
     (antes 1453–1474: 22 líneas) — escribes del diálogo eliminado.
   - `QTextEdit` quitado del import de `PySide6.QtWidgets` (hoy línea
     36 del bloque 32–38). El resto de imports (`QFormLayout`,
     `QDoubleSpinBox`, `QCheckBox`, `QDialog`, `QColorDialog`, …) se
     queda: siguen usados por `DialogoPosicionarImagen`,
     `DialogoReordenarPaginas` y `editar_forma`.
   - **No se tocó** `DialogoPosicionarImagen` (156–233) ni nada de
     imágenes y formas.
3. **Referencias rotas por el borrado (documentación viva):**
   - `app/formato_html.py` docstring de `cabe_texto_con_formato` (hoy
     líneas 157–158): dejó de citar a `texto_cabe_en_cuadro de main.py`.
   - `DISENO_EDITOR_TEXTO.md` línea ~65: ídem, la frase ahora dice que
     la prueba vive en `cabe_texto_con_formato`.
   - `BITACORA.md` NO se modifica: es historial.
4. **Documentación del estado y de las 4 limitaciones conocidas:**
   - `README.md`: checklist actualizado (líneas 15–16: edición tipo
     Word en línea), sección "Estado actual" (31–38) con la Tarea 0–6
     completada, y nueva subsección "✏️ Limitaciones conocidas de la
     edición de texto" (40–48) con las 4 limitaciones.
   - `ROADMAP.md` Fase 4 (26–45): ítem nuevo de la edición en línea con
     barra de formato + ventana vieja eliminada, y las 4 limitaciones
     reemplazan la nota técnica anterior.
   - `DISENO_EDITOR_TEXTO.md`: bloque de estado COMPLETADA (8–11),
     nueva sección "⚠️ Limitaciones conocidas" (40–48), y encabezados
     de Tarea 0 a Tarea 6 marcados con ✅ (137, 147, 162, 177, 190,
     206, 227).
5. **Verificación:** grep final en `app/` y `tests/` → cero referencias
   a lo borrado; **pyright** → mismos 38 ruidos conocidos de
   `app/main.py` (enums Qt, `Document`, `PDF_ENCRYPT_AES_256`), 0
   errores nuevos y 0 en los demás archivos; **pytest** → 18/18 en
   verde.

**Resultado:** El plan `DISENO_EDITOR_TEXTO.md` queda COMPLETO (Tareas
0–6). La ventana "Editar cuadro de texto" y sus helpers ya no existen:
la única forma de editar texto es la edición en línea tipo Word;
imágenes y formas siguen intactos. README, ROADMAP (Fase 4) y el
documento de diseño reflejan el estado terminado y las 4 limitaciones
conocidas.

**Pendiente:**
- Validación visual de Diego de la documentación (revisión de README,
  ROADMAP Fase 4 y del documento de diseño).
- `tests/__pycache__/test_inline_editor.cpython-314.pyc` sigue ahí; no
  se borró nada sin permiso.

---

## Sesión 16 — 2026-10-14

**Objetivo de la sesión:** Tarea 1 del plan `DISENO_DESHACER.md`:
crear `app/historial.py` con la clase `HistorialCambios` (pilas de
copias en memoria para Deshacer/Rehacer), sus pruebas sin Qt, y
apuntar `AGENTS.md` al plan nuevo.

**Actividades realizadas:**

1. **`app/historial.py` (nuevo, 165 líneas):** clase
   `HistorialCambios(limite_pasos=20, limite_bytes=300 * 1024 * 1024)`
   con dos pilas de tuplas `(bytes, descripcion)`; `registrar` guarda
   `documento.tobytes()`, vacía la pila de Rehacer (regla 1) y aplica
   los límites descartando las copias más antiguas;
   `descartar_ultimo` quita la última copia para operaciones que
   fallan o se cancelan (regla 4); `deshacer`/`rehacer` devuelven un
   `fitz.Document` nuevo abierto desde la copia y meten el estado
   actual en la pila contraria con la misma descripción (`None` si no
   hay nada); consultas `puede_deshacer`, `puede_rehacer`,
   `descripcion_deshacer`, `descripcion_rehacer` y `vaciar`. Sin Qt,
   solo `import fitz`.
2. **`tests/test_historial.py` (nuevo, 195 líneas):** las 6 pruebas
   que pide el diseño, con helpers `_documento_texto` y
   `_agregar_linea` (PDFs en memoria, sin QApplication): registrar 3
   cambios y deshacer 3 veces regresa al original; un cambio nuevo
   vacía el Rehacer; con `limite_pasos=2` al registrar 3 solo se
   pueden deshacer 2; con `limite_bytes` pequeño se descartan las
   copias antiguas; `descartar_ultimo` quita la copia del cambio
   cancelado; descripciones correctas en las dos pilas (y `vaciar`).
3. **`AGENTS.md` (línea 15):** "Plan vigente" pasa de
   `DISENO_EDITOR_TEXTO.md` a `DISENO_DESHACER.md`.
4. **Verificación:** **pyright** → mismos 38 ruidos conocidos de
   `app/main.py` (enums Qt, `Document`, `PDF_ENCRYPT_AES_256`,
   `pixmap_limpio`), 0 errores en `app/historial.py` y en
   `tests/test_historial.py` (sin `reportMissingImports`:
   `extraPaths` de `pyrightconfig.json` alcanza para el import de
   `historial`); **pytest** → 24/24 en verde (las 6 nuevas incluidas).

**Resultado:** El corazón del Deshacer/Rehacer queda listo y probado
sin ventanas: copias completas del documento en memoria con límites
de 20 pasos / 300 MB, y la API completa que la Tarea 2 conectará al
menú Editar de `main.py`.

**Pendiente:**
- Tarea 2 del plan: menú "Editar" en `EditorPDF` con Deshacer
  (`QKeySequence.StandardKey.Undo`) y Rehacer
  (`QKeySequence.StandardKey.Redo`), descripciones en el menú,
  restaurar el documento y redibujar.

---

## Sesión 17 — 2026-10-14

**Objetivo de la sesión:** Tarea 2 del plan `DISENO_DESHACER.md`
(conectar `HistorialCambios` a `EditorPDF` con el menú Editar) más una
corrección pedida por Diego en `app/historial.py`: el límite de bytes
debe conservar siempre la copia más reciente, para que un PDF que por
sí solo pese más que `limite_bytes` aún se pueda deshacer un paso.

**Actividades realizadas:**

1. **Corrección en `app/historial.py` (`_aplicar_limites`, líneas
   144–162):** el ciclo del límite de bytes ahora exige
   `len(self._pila_deshacer) > 1` antes de descartar, así que nunca se
   elimina la última copia. Nueva prueba
   `test_limite_de_bytes_conserva_la_copia_mas_reciente` en
   `tests/test_historial.py` (líneas 144–164): con `limite_bytes=10`
   (mucho menor que una sola copia) aun queda un deshacer posible.
2. **`app/main.py`:**
   - Imports: `QKeySequence` en QtGui (línea 41) y
     `from historial import HistorialCambios` (línea 53).
   - `__init__` (línea 321): `self.historial = HistorialCambios()`.
   - `crear_menu_archivo` (línea 376) llama a `crear_menu_editar()`
     entre los menús Archivo y Páginas.
   - `crear_menu_editar` (línea 407): acciones "Deshacer" y "Rehacer"
     con `QKeySequence.StandardKey.Undo` y `QKeySequence.StandardKey.Redo`,
     arrancan deshabilitadas.
   - `actualizar_acciones_editar` (línea 428): el texto lleva la
     descripción ("Deshacer: Rotar página"); se deshabilitan sin nada
     en el historial, con PDF protegido (`needs_pass`, regla 5) o con
     edición en línea abierta (regla 6). Se llama también al abrir y
     cerrar edición en línea (líneas 1342 y 1462).
   - `registrar_cambio(descripcion)` (línea 466), `deshacer_cambio`
     (línea 479), `rehacer_cambio` (línea 495) y
     `_restaurar_documento` (línea 511): reemplaza `self.documento`,
     conserva `pagina_actual` (ajustada), redibuja todo (los recuadros
     de "Editar contenido" los redibuja `dibujar_todas_las_paginas`) y
     muestra "Deshecho: …" / "Rehecho: …" en la barra de estado.
   - `abrir_pdf` ahora llama a `cargar_documento(documento, ruta)`
     (línea 633), que vacía el historial (regla 2); `cerrar_documento`
     también lo vacía (líneas 1675 y 1684).
3. **`tests/test_deshacer.py` (nuevo, 105 líneas, offscreen):** las 3
   pruebas que pide el diseño: rotar con `registrar_cambio` y deshacer
   → rotación 0, rehacer → rotación 90; abrir otro documento vacía el
   historial y apaga las acciones; PDF con contraseña
   (`fitz.PDF_ENCRYPT_AES_256`) deja las acciones deshabilitadas.
4. **Verificación:** **pyright** → mismos 38 ruidos conocidos de
   `app/main.py` + 1 del mismo tipo (`PDF_ENCRYPT_AES_256` no
   "conocido" en `fitz`, ruido documentado en AGENTS.md) en
   `test_deshacer.py:88`, 0 errores reales nuevos; **pytest** → 28/28
   en verde (las 4 nuevas: 1 de historial + 3 de deshacer).

**Resultado:** El Deshacer/Rehacer ya está conectado a la ventana: menú
Editar entre Archivo y Páginas con Ctrl+Z / Ctrl+Y, descripción de lo
que se deshace, deshabilitado con PDF protegido o edición en línea
abierta, y el historial se vacía al abrir o cerrar un documento. La
corrección del límite de bytes garantiza al menos un paso de deshacer
aunque el PDF pese más que `limite_bytes`.

**Pendiente:**
- Tarea 3 del plan: llamar `registrar_cambio(...)` antes de cada
  operación de la tabla "Qué cuenta como cambio" y
  `historial.descartar_ultimo()` si algo falla o se cancela, con su
  validación visual de Diego (4 cambios, deshacer 4, rehacer 2).

---

## Sesión 18 — 2026-10-15

**Objetivo de la sesión:** Tarea 3 del plan `DISENO_DESHACER.md`
(registrar cada operación que modifica el documento y descartar la
copia si algo falla o se cancela), más la corrección pedida por Diego
en la regla 5: detectar también los PDFs con solo contraseña de
permisos, no solo `needs_pass`.

**Actividades realizadas:**

1. **Corrección de la regla 5 en `app/main.py`:**
   - `__init__` (línea 324): `self.documento_protegido = False`.
   - `cargar_documento` (línea 647):
     `bool(documento.needs_pass or documento.metadata.get("encryption"))`,
     que detecta tanto la contraseña de usuario como la de permisos
     (guardada con `owner_pw` y `user_pw` vacío queda
     `metadata["encryption"] = "Standard V5 R6 256-bit AES"`).
   - `actualizar_acciones_editar` (línea 455), `deshacer_cambio`
     (línea 485) y `rehacer_cambio` (línea 501) usan
     `self.documento_protegido` en vez de `needs_pass`; al cerrar el
     documento vuelve a `False` (línea 1753).
   - Prueba nueva
     `test_pdf_solo_con_contrasena_de_permisos_deshabilita_las_acciones`
     en `tests/test_deshacer.py` (líneas 126–152).
2. **Registro de cambios (Tarea 3) en `app/main.py`:**
   - `al_seleccionar_rectangulo` (líneas 808–875): mapa de herramienta
     a descripción ("Resaltar", "Subrayar", "Tachar", "Texto libre",
     "Rectangulo", "Linea", "Circulo", "Firma") con
     `registrar_cambio` antes de aplicar; `descartar_ultimo` si el
     usuario cancela el diálogo de texto libre, si falta la firma o si
     la operación lanza excepción (regla 4). "Editar contenido" no
     registra aquí: su cambio cuenta al aceptar.
   - `aceptar_edicion_texto` (líneas 1464–1489): registra "Editar
     texto" antes de tocar el PDF y descarta si no cabe o si falla.
   - `editar_forma` (líneas 1244 y 1279): "Cambiar color de forma".
   - `editar_imagen` (líneas 1553 y 1587): "Reemplazar imagen" /
     "Eliminar imagen" después de elegir y confirmar, con descarte en
     excepción; `colocar_imagen_en_punto` no registra (completa el
     mismo cambio).
   - Páginas: `rotar_pagina` (1622), `eliminar_pagina` (1640, después
     de confirmar), `insertar_pagina_blanco` (1648) y
     `reordenar_paginas` (1667, con descarte si `select` falla).
3. **Pruebas nuevas en `tests/test_deshacer.py` (ahora 259 líneas):**
   ayuda `_documento_de`/`_pagina_de`/`_texto_de_pagina` (líneas
   33–47) y 5 pruebas: resaltar y deshacer quita la anotación (155),
   eliminar página y deshacer la regresa con `monkeypatch` de
   `QMessageBox.question` (173), aceptar edición en línea y deshacer
   regresa "uno dos tres" (191), cancelar el diálogo de texto libre no
   deja copia (231), y la de contraseña de permisos (126).
4. **Verificación:** **pyright** → 40 errores, todos ruido conocido
   (38 de `app/main.py` + 2 de `PDF_ENCRYPT_AES_256` en
   `test_deshacer.py:110` y `:141`, tipo documentado en AGENTS.md),
   0 errores reales nuevos; **pytest** → 33/33 en verde (5 nuevas).

**Resultado:** Todas las operaciones de la tabla "Qué cuenta como
cambio" registran su copia antes de modificar el PDF y la descartan si
fallan o se cancelan, así que Deshacer/Rehacer refleja solo cambios
reales. La regla 5 ahora también protege a los PDFs con contraseña de
permisos que se abren sin pedirla.

**Pendiente:**
- Validación visual de Diego (Tarea 3): hacer 4 cambios distintos
  (resaltar, texto libre, rotar página, editar texto en línea),
  deshacer los 4 con Ctrl+Z revisando que cada uno regresa, rehacer 2
  con Ctrl+Y y confirmar que el menú Editar muestra la descripción
  correcta; probar también cancelar el diálogo de texto libre y
  verificar que el menú Editar no queda con nada para deshacer.
- Tarea 4 del plan: documentación (README, ROADMAP, marcar el diseño
  como completado).

---

## Sesión 19 — 2026-10-15

**Objetivo de la sesión:** Tarea 4 del plan `DISENO_DESHACER.md`
(documentación: README, ROADMAP y marcar el diseño como completado), más
la corrección pedida por Diego: si una operación falla *después* de haber
modificado el PDF, descartar la copia deja el documento a medias y sin
forma de deshacer; hay que revertir el cambio registrado.

**Actividades realizadas:**

1. **Corrección en `app/main.py`:**
   - Nuevo método `_revertir_cambio_fallido` (líneas 532–549): usa
     `self.historial.deshacer(self.documento)` para restaurar el estado
     anterior, lo carga con `_restaurar_documento` y luego vacía la pila
     de Rehacer con `vaciar_rehacer()` (ese "cambio" nunca existió),
     actualizando las acciones del menú Editar.
   - `aceptar_edicion_texto`: el `except` de después de
     `add_redact_annot`/`apply_redactions`/`insertar_texto_con_formato`
     (líneas 1507–1514) ahora llama a `_revertir_cambio_fallido()` en
     vez de `descartar_ultimo()`. Los casos de cancelación (diálogo
     cancelado, texto no cabe, líneas 1466 y 1486) siguen usando
     `descartar_ultimo()`.
   - `al_seleccionar_rectangulo`: el `except` general (líneas 890–896)
     también usa `_revertir_cambio_fallido()` (solo si se registró un
     cambio). Los casos de cancelación (texto libre cancelado, falta la
     firma, líneas 866 y 873) siguen usando `descartar_ultimo()`.
2. **`app/historial.py`:** nuevo método `vaciar_rehacer` (líneas
   140–147) que borra solo la pila de Rehacer, dejando la de Deshacer.
3. **`tests/test_historial.py`:** nueva prueba
   `test_vaciar_rehacer_borra_solo_el_rehacer` (líneas 190–212).
4. **`tests/test_deshacer.py`:** nueva prueba
   `test_fallo_al_escribir_texto_revuelve_el_documento` (líneas
   263–310): simula un fallo de `insertar_texto_con_formato` con
   `monkeypatch` y verifica que el párrafo original "uno dos tres"
   sigue en el documento y que no queda nada ni para deshacer ni para
   rehacer. El import `import main as modulo_main` se agregó para poder
   parchear la función.
5. **Tarea 4 — documentación:**
   - `README.md`: casilla nueva del checklist ("Deshacer y Rehacer",
     línea 20), mención en "Estado actual" (líneas 30–42) y subsección
     "↩️ Limitaciones conocidas del Deshacer/Rehacer" (líneas 44–49):
     20 pasos / 300 MB y deshabilitado en PDFs con contraseña.
   - `ROADMAP.md` Fase 8: ítem completado del Deshacer/Rehacer (líneas
     68–70).
   - `DISENO_DESHACER.md`: bloque de estado COMPLETADO arriba (líneas
     3–7), regla 4 actualizada con el comportamiento de revertir (líneas
     34–40) y encabezados de Tarea 1 a Tarea 4 marcados con ✅.
6. **Verificación:** **pyright** → 40 errores, todos ruido conocido (38
   de `app/main.py` + 2 de `PDF_ENCRYPT_AES_256` en `test_deshacer.py`),
   0 errores reales nuevos; **pytest** → 35/35 en verde (2 nuevas).

**Resultado:** Cuando una operación falla después de tocar el PDF, el
documento se revierte al estado anterior y el cambio fallido no queda ni
en Deshacer ni en Rehacer. La documentación del plan (README, ROADMAP
Fase 8 y el diseño) refleja la función terminada y sus limitaciones.

**Pendiente:**
- Validación visual de Diego: probar el fallo real (por ejemplo, un PDF
  raro donde falle la edición de texto) y confirmar que el documento
  regresa solo; y revisar la documentación actualizada.

---

## Sesión 20 — 2026-10-15

**Objetivo de la sesión:** Terminar la corrección de la sesión 19
("revertir si el fallo ocurre después de tocar el PDF") aplicándola a
las operaciones que aún usaban `descartar_ultimo()` en ese caso:
`editar_forma`, `editar_imagen` (reemplazar y eliminar) y
`reordenar_paginas`, con su prueba.

**Actividades realizadas:**

1. **`app/main.py` — los 4 `except` que podían fallar después de
   modificar el PDF ahora llaman a `_revertir_cambio_fallido()`** (en
   vez de `historial.descartar_ultimo()` + `actualizar_acciones_editar()`,
   que `_revertir_cambio_fallido` ya hace por dentro):
   - `editar_forma` (líneas 1298–1303): el `try` cubre
     `add_redact_annot`/`apply_redactions`/`insert_text`, ya con la
     redacción aplicada.
   - `editar_imagen` – reemplazar (líneas 1603–1608): el `try` empieza
     después de `delete_image` + `clean_contents`, es decir con la
     imagen vieja ya borrada; el error se vuelve a lanzar y lo captura
     el `except` general de `editar_imagen`.
   - `editar_imagen` – eliminar (líneas 1620–1624): mismo caso.
   - `reordenar_paginas` (líneas 1707–1712): `documento.select()` ya
     reconstruyó el documento.
   - Los comentarios de al lado (líneas 1262–1263, 1573–1576 y
     1613–1615) se actualizaron para no decir ya "la copia se descarta".
   - **Siguen con `descartar_ultimo()` los cancelar antes de tocar el
     PDF**, como debe ser: diálogo de texto libre cancelado (línea 866),
     firma sin cargar (línea 873) y texto que no cabe (línea 1488).
2. **`tests/test_deshacer.py`:** ayuda `_documento_con_imagen` (líneas
   35–42, PDF con una imagen roja pegada) y `_color_en_pagina` (líneas
   62–66, color del píxel de la página en un punto PDF); import de
   `QDialog` y `QFileDialog` (línea 16). Nueva prueba
   `test_fallo_al_reemplazar_imagen_revuelve_el_documento` (líneas
   333–398): con `monkeypatch` de los diálogos, la imagen "elegida" es
   un archivo que no se puede decodificar, así que `insert_image` falla
   *después* de que `delete_image` borró la imagen vieja. Se verifica que
   el píxel vuelve a ser rojo (255, 0, 0) — con `descartar_ultimo()`
   quedaba blanco (255, 255, 255), o sea que la prueba atrapa el bug —
   y que no queda nada ni para deshacer ni para rehacer.
3. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums de Qt y `PDF_ENCRYPT_AES_256`), 0 errores nuevos;
   **pytest** → 36/36 en verde (1 nueva).

**Resultado:** Si `editar_forma`, `editar_imagen` o `reordenar_paginas`
fallan después de haber modificado el PDF, el documento entero se
revierte al estado anterior y el cambio fallido no queda ni en Deshacer
ni en Rehacer; los diálogos cancelados antes de tocar el PDF siguen
deshaciendo solo la copia registrada.

**Pendiente:**
- Validación visual de Diego: en "Editar contenido", cambiar el color
  de una forma y reemplazar/eliminar una imagen en un PDF real,
  simulando un fallo (o usando un PDF raro) y confirmando que la forma
  o la imagen original regresan solas.

---

## Sesión 21 — 2026-10-15

**Objetivo de la sesión:** Empezar la Fase 5 (llenar formularios PDF)
con la Tarea 1 del diseño `DISENO_FORMULARIOS.md`: el módulo
`app/formularios.py` para leer los campos que ya trae un PDF.

**Actividades realizadas:**

1. **`AGENTS.md`:** la línea "Plan vigente" ahora apunta a
   `DISENO_FORMULARIOS.md` (antes decía `DISENO_DESHACER.md`).
2. **`app/formularios.py` (nuevo):** funciones puras sobre PyMuPDF,
   sin ventanas:
   - `listar_campos(documento)` (líneas 39–76): recorre las páginas con
     `pagina.widgets()`, traduce cada tipo de PyMuPDF al nombre del
     diseño (`"texto"`, `"casilla"`, `"opcion"`, `"lista"`, `"firma"`)
     y devuelve un diccionario por campo con `nombre`, `tipo`, `valor`,
     `opciones`, `solo_lectura`, `multilinea`, `paginas`, `rects` y
     `xrefs`. Los botones de opción que comparten nombre se agrupan en
     un solo campo (páginas/rects/xrefs por cada botón, opciones = el
     estado encendido de cada uno); los botones de acción no se listan.
   - `tiene_formulario(documento)` (líneas 79–81): `True` si hay al
     menos un campo listable.
   - `es_solo_xfa(documento)` (líneas 84–91): `True` si el AcroForm
     declara XFA y no hay campos normales (detecta XFA con
     `xref_get_key`, tanto si el AcroForm es objeto indirecto como si
     está escrito en el catálogo).
   - Banderas: solo lectura = `PDF_FIELD_IS_READ_ONLY` (bit 0) y
     multilínea = `PDF_TX_FIELD_IS_MULTILINE` (bit 13).
3. **`tests/test_formularios.py` (nuevo):** 7 pruebas que crean sus
   PDFs en memoria con `fitz.Widget()` + `pagina.add_widget()`:
   tipos/valores/opciones de cada campo, grupo de opción como un solo
   campo con estados "Si"/"No" (se renombra el estado "Yes" que crea
   PyMuPDF para simular grupos reales), multilínea y solo lectura,
   páginas/rects/xrefs contra el widget real, PDF sin campos →
   `tiene_formulario` es `False`, y detección de XFA (solo XFA →
   `True`; con campos normales o sin XFA → `False`).
4. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums cortos de Qt y `PDF_ENCRYPT_AES_256`), 0 errores
   nuevos; **pytest** → 43/43 en verde (7 nuevas). Para que pyright no
   marcara cosas nuevas, las constantes de PyMuPDF se importan de
   `pymupdf.mupdf` (donde están declaradas) y en las pruebas las
   propiedades del widget se asignan con `setattr` en un solo
   ayudante.

**Resultado:** El programa ya puede leer los campos de un formulario
PDF (texto, casillas, grupos de opción, listas y firmas) y detectar los
formularios XFA que no se pueden llenar; esto es la base del panel de
las tareas 2 a 4.

**Pendiente:**
- Tarea 2: `escribir_valor(documento, campo, valor)` con sus pruebas.

---

## Sesión 22 — 2026-10-15

**Objetivo de la sesión:** Continuar la Fase 5 con la Tarea 2 del diseño
`DISENO_FORMULARIOS.md`: escribir valores en los campos, más la corrección
de `listar_campos` para agrupar por `field_name` todos los tipos (no solo
los botones de opción).

**Actividades realizadas:**

1. **`app/formularios.py`:**
   - `listar_campos` (líneas 44–86): ahora agrupa por `field_name` TODOS
     los tipos con un diccionario (`indices_por_nombre`, línea 68): un
     campo de texto, casilla o lista que aparece en varias páginas (por
     ejemplo el nombre en el encabezado de cada hoja) sale una sola vez,
     con todas sus `paginas`, `rects` y `xrefs`. Se reemplazaron
     `_campo_de_grupo` y `_agregar_boton_al_grupo` por
     `_agregar_aparicion` (líneas 188–212), que además de las opciones
     del grupo mantiene el solo-lectura como AND de todas las
     apariciones.
   - `escribir_valor(documento, campo, valor)` (líneas 104–138): escribe
     el valor en TODOS los widgets del campo y llama `widget.update()`
     en cada uno. Lanza `ValueError` con mensaje en español (sin tocar
     el documento) si el campo es de firma, de solo lectura, no existe
     en el documento, o si el valor no es válido para su tipo.
   - Internos nuevos: `_validar_valor` (líneas 264–287; texto → string,
     casilla → bool, opción/lista → una de las opciones),
     `_escribir_en_widgets` (líneas 290–308; busca cada widget por su
     `xref` y lo escribe mientras su página viva en memoria: PyMuPDF
     solo permite `update()` con la página viva) y `_asignar_valor`
     (líneas 311–327; en grupos de opción solo enciende el botón cuyo
     `on_state()` coincide y apaga los demás, porque PyMuPDF no los
     apaga solo).
2. **`tests/test_formularios.py`:** 6 pruebas nuevas (13 en total):
   - `test_campo_repetido_en_dos_paginas_sale_una_sola_vez` (línea 336)
     y `test_escribir_valor_actualiza_todos_los_widgets_del_campo`
     (línea 392): un texto con el mismo nombre en dos páginas sale una
     sola vez en `listar_campos` y, al escribirlo, ambos widgets quedan
     con el valor nuevo después de `tobytes()` y reabrir.
   - `test_escribir_valor_llena_los_tipos_y_persisten_al_guardar`
     (línea 354): texto, multilínea, casilla, opción y lista persisten
     al guardar y reabrir.
   - `test_escribir_valor_invalido_en_lista_lanza_error` (línea 420),
     `test_escribir_valor_en_solo_lectura_lanza_error` (línea 437) y
     `test_escribir_valor_en_firma_lanza_error` (línea 454): lanzan
     `ValueError` sin modificar el documento.
   - Ayudante `_pdf_texto_en_dos_paginas` (línea 182): crea dos páginas
     y recarga cada una con `documento[n]` (al crear la segunda página,
     PyMuPDF invalida el enlace de la primera).
3. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums cortos de Qt y `PDF_ENCRYPT_AES_256`), 0 errores
   nuevos; **pytest** → 49/49 en verde (6 nuevas).

**Resultado:** `app/formularios.py` ya lee y escribe los campos de un
formulario PDF: texto (incluidos repetidos en varias páginas),
casillas, grupos de opción, listas y firmas, con validación de valores
y regeneración de apariencia; esto completa la base para el panel de
las tareas 3 y 4.

**Pendiente:**
- Tarea 3: `app/panel_formularios.py` (`PanelFormularios(QDockWidget)`).

---

## Sesión 23 — 2026-10-16

**Objetivo de la sesión:** Continuar la Fase 5 con la Tarea 3 del diseño
`DISENO_FORMULARIOS.md`: el panel lateral de campos, más una corrección
en `_asignar_valor` (comparar con `_estado_encendido(widget)` y no con
`widget.on_state()`).

**Actividades realizadas:**

1. **Corrección en `app/formularios.py`:**
   - `_asignar_valor` (líneas 311–331): para los grupos de opción ahora
     compara `_estado_encendido(widget) == valor` (línea 326) y no
     `widget.on_state() == valor`. El caso: cuando el PDF no define
     estado On en la apariencia del botón, `on_state()` devuelve `True`
     (PyMuPDF avisa) y `listar_campos` registra la opción como `"Yes"`;
     al escribir, `True == "Yes"` nunca coincidía y el botón quedaba
     apagado. Se pudo reproducir con un PDF de prueba (helper
     `_pdf_opcion_sin_estado_on` en las pruebas) y se confirmó que, con
     el fix, el valor `"Yes"` persiste tras `tobytes()`.
2. **`app/panel_formularios.py` (nuevo):**
   - `PanelFormularios(QDockWidget)` (línea 60), título "Campos del
     formulario", con `QScrollArea` y `QGridLayout`: una fila por campo
     (nombre + control). Señal `valor_cambiado(nombre, valor)`
     (`Signal(str, object)`, línea 77).
   - Controles por tipo (líneas 152–212): texto → `QLineEdit`
     (`editingFinished`) o `_TextoMultilinea(QPlainTextEdit)` (línea 45,
     emite `terminado` al perder el foco); casilla → `QCheckBox`
     (`toggled`); opción → un `QRadioButton` por opción en una caja
     (`_crear_opciones`, línea 214; Qt los toma como grupo exclusivo);
     lista → `QComboBox`; firma → etiqueta "Firma (no editable aqui)".
     Los campos de solo lectura salen deshabilitados (líneas 145–147).
   - `cargar(campos)` (línea 101): vacía el grid y reconstruye las
     filas; mientras arma cada control usa `blockSignals` para no
     emitir `valor_cambiado` con los valores iniciales.
   - `seleccionar(nombre)` (línea 122): resalta la fila
     (`_pintar_fila`, línea 250), le da foco al control y la trae a la
     vista con `ensureWidgetVisible`.
   - `controles[nombre]` (público) guarda los widgets de cada campo
     (varios en los grupos de opción), al estilo de `BarraFormato`.
3. **Pruebas:**
   - `tests/test_formularios.py` (14 en total): ayudante
     `_pdf_opcion_sin_estado_on` (línea 184, reescribe el AP del botón
     para que `on_state()` sea `True`) y
     `test_escribir_valor_enciende_boton_sin_estado_on` (línea 508):
     con el fix el botón queda en `"Yes"`; sin él quedaba `"Off"`.
   - `tests/test_panel_formularios.py` (nuevo, 7 pruebas, línea 116 en
     adelante): control correcto por tipo (incluidos los dos botones
     "Si"/"No" del grupo), solo lectura deshabilitado, `cargar()` no
     emite señales, marcar casilla emite una sola vez, elegir opción
     emite su estado, `seleccionar()` resalta y da foco (en offscreen
     hay que llamar `QApplication.setActiveWindow`, deprecada, porque
     la ventana nunca queda activa sola), y nombre desconocido no
     truena.
4. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums cortos de Qt y `PDF_ENCRYPT_AES_256`), 0 errores
   nuevos; **pytest** → 57/57 en verde (8 nuevas).

**Resultado:** El panel lateral `PanelFormularios` muestra una fila por
campo del formulario con el control adecuado (texto, casilla, opciones,
lista y firma), emite `valor_cambiado` solo por acción del usuario y
sabe resaltar y enfocar un campo; con la corrección de `_asignar_valor`
también se llenan los botones de opción de PDFs mal formados (sin
estado On). Lista la base para conectarlo en `main.py`.

**Pendiente:**
- Tarea 4: conectar el panel en `app/main.py` (menú, escritura con
  deshacer, clic en la página).

---

## Sesión 24 — 2026-10-16

**Objetivo de la sesión:** Continuar la Fase 5 con la Tarea 4 del diseño
`DISENO_FORMULARIOS.md`: conectar el panel de formularios en
`app/main.py` (menú, escritura con deshacer, clic en la página), más una
corrección en `app/panel_formularios.py` para que los campos de texto no
emitan cambios vacíos.

**Actividades realizadas:**

1. **Corrección en `app/panel_formularios.py`:**
   - Nuevo atributo `_ultimos_textos` (línea 98): el último valor
     conocido de cada campo de texto; se vacía en `cargar` (línea 130)
     y se guarda al armar cada fila de texto (línea 197, con el valor
     inicial que trae el PDF).
   - `_crear_controles` (línea 165): los `QLineEdit` (`editingFinished`)
     y los `_TextoMultilinea` (`terminado`) ya no emiten directo, sino
     que pasan por `_al_terminar_texto` (línea 260), que compara con el
     último valor conocido y solo emite `valor_cambiado` si el texto
     cambió; después de emitir guarda el texto nuevo. Así, dar y quitar
     el foco sin editar (por ejemplo recorriendo el formulario con Tab)
     no llena el historial de Deshacer con pasos vacíos.
2. **`app/main.py` (Tarea 4):**
   - Docstring del programa (línea 16) e imports (líneas 56 y 58):
     `formularios.escribir_valor`, `es_solo_xfa`, `listar_campos` y
     `panel_formularios.PanelFormularios`.
   - `__init__` (líneas 353–364): se crea el dock
     `PanelFormularios` a la derecha (`Qt.DockWidgetArea.RightDockWidgetArea`),
     oculto, con `valor_cambiado` conectado a `al_cambiar_valor_campo`.
   - `crear_menu_formularios` (línea 580): menú **"Formularios"** con la
     acción **"Mostrar campos"** conmutable (`toggled` → mostrar/ocultar
     el panel, `visibilityChanged` → mantener la casilla sincronizada
     con el botón X del dock); arranca deshabilitada y se activa sola
     cuando el PDF tiene campos. Se llama desde `crear_menu_archivo`
     (línea 420).
   - `al_cambiar_valor_campo` (línea 605): si el valor es igual al que
     ya tiene el campo en el documento no registra cambio ni escribe
     nada (compara en `_valor_ya_esta_en_el_documento`, línea 655);
     si es distinto registra `"Llenar campo: <nombre>"` antes de
     escribir con `escribir_valor` y redibuja cada página del campo
     (`campo["paginas"]`); si falla, `_revertir_cambio_fallido()` (que
     recarga el panel) y `QMessageBox.critical`.
   - `_campo_de_formulario` (línea 646), `_recargar_panel_formularios`
     (línea 667, devuelve los campos cargados y habilita/deshabilita
     la acción) y `_mostrar_panel_formularios` (línea 683).
   - `cargar_documento` (líneas 833–841): si el PDF es solo XFA avisa
     "Este formulario usa XFA y no se puede llenar con este programa";
     recarga el panel y lo muestra a la derecha si hay campos, u oculta
     si no los hay.
   - `_restaurar_documento` (línea 553): después de deshacer o rehacer
     el panel se vuelve a cargar con los valores restaurados.
   - `al_seleccionar_rectangulo` (línea 998) y
     `_seleccionar_campo_en_punto` (línea 688): con la herramienta
     "Ninguna (solo ver)", un clic sobre un campo de la página lo
     selecciona y resalta en el panel.
   - `cerrar_documento` (líneas 1970–1971): el panel se vacía y se
     oculta.
3. **Pruebas:**
   - `tests/test_panel_formularios.py` (9 en total, +2 en las líneas
     247 y 282): dar y quitar el foco sin cambiar el texto no emite
     `valor_cambiado` (ni en el `QLineEdit` ni en el `_TextoMultilinea`);
     cambiarlo sí emite una sola vez, y volver a enfocar sin editar no
     vuelve a emitir.
   - `tests/test_main_formularios.py` (nuevo, 4 pruebas): llenar un
     campo de texto desde el panel escribe en el documento y `Ctrl+Z`
     deja el documento y el panel vacíos; avisar un valor igual al del
     documento no registra cambio ni escribe; un clic sobre un campo
     (herramienta "Ninguna") lo resalta en el panel; abrir con campos
     muestra el panel y la acción, sin campos los oculta/apaga, la
     acción conmutable oculta y muestra, y cerrar el documento vacía y
     oculta el panel.
4. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums cortos de Qt, `Document` vs `Iterable`,
   `PDF_ENCRYPT_AES_256`, `pixmap_limpio`), 0 errores nuevos (el código
   nuevo usa enums completos como `Qt.DockWidgetArea.RightDockWidgetArea`);
   **pytest** → 63/63 en verde (6 nuevas).

**Resultado:** El formulario se puede llenar desde el panel lateral: con
un PDF con campos el panel se muestra solo, cada cambio escribe en el
PDF y se redibuja la página (con Deshacer y Rehacer), un clic sobre un
campo lo identifica en el panel, y ni el Tab ni los valores repetidos
ensucian el historial de Deshacer.

**Pendiente:**
- Validación visual de Diego con un formulario PDF real (llenar texto,
  casillas y listas, guardar con "Guardar como" y abrir el resultado en
  Edge o Chrome).
- Tarea 5: documentación (README, ROADMAP, BITACORA y marcar el diseño
  como completado).

---

## Sesión 25 — 2026-10-16

**Objetivo de la sesión:** Terminar la Fase 5, parte 1, con la Tarea 5
del diseño `DISENO_FORMULARIOS.md`: documentación (README, ROADMAP,
BITACORA) y marcar el diseño como completado. Solo documentación, sin
cambios de código.

**Actividades realizadas:**

1. **`DISENO_FORMULARIOS.md`:**
   - Bloque de "✅ COMPLETADO (Tareas 1–5, 2026-10-16)" al inicio del
     documento (líneas 3–8), al estilo de `DISENO_DESHACER.md`.
   - Las cinco tareas quedan marcadas con ✅ en sus títulos (líneas
     124, 147, 160, 174 y 192).
2. **`README.md`:**
   - Checklist del objetivo (líneas 22–24): el punto "Rellenar y crear
     formularios PDF" se divide en "Rellenar los campos que ya trae el
     PDF" (hecho, con enlace al diseño) y "Crear campos de formulario
     nuevos" (pendiente).
   - "Estado actual" (líneas 35–42): se menciona la parte 1 de la Fase 5
     (panel lateral, control por tipo, Deshacer/Rehacer y selección con
     clic en la página).
   - Nueva sección **"📝 Limitaciones conocidas de los formularios"**
     (líneas 70–81): sin crear campos nuevos, sin XFA, sin JavaScript
     del formulario, sin firmas digitales (solo "Firma (no editable
     aquí)") y sin aplanar el formulario.
   - Párrafo de pendientes (líneas 83–85): ya no dice "formularios
     (Fase 5)" a secas, sino "crear campos de formulario nuevos (Fase
     5, parte 2)".
3. **`ROADMAP.md`:**
   - Fase 5 (líneas 45–66): de "sin empezar" a "parte 1 completada",
     con el punto hecho de rellenar campos existentes (Tareas 1–5 del
     diseño), el pendiente de la parte 2 (crear campos) y cinco
     limitaciones conocidas al estilo de la Fase 4.
4. **`BITACORA.md`:** esta entrada (Sesión 25).
5. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums cortos de Qt, `Document` vs `Iterable`,
   `PDF_ENCRYPT_AES_256`, `pixmap_limpio`), 0 errores nuevos;
   **pytest** → 63/63 en verde (sin cambios de código, todo sigue en
   verde).

**Resultado:** La Fase 5, parte 1 (llenar formularios PDF) queda
documentada y marcada como completada: el README explica la función y
sus límites, el ROADMAP marca la parte 1 hecha y deja la parte 2
(crear campos) como pendiente, y el diseño `DISENO_FORMULARIOS.md`
cierra con sus cinco tareas completadas. Diego ya hizo la validación
visual con un formulario PDF real (Tarea 4) y todo funcionó bien.

**Pendiente:**
- Fase 5, parte 2: crear campos de formulario nuevos (con su propio
  diseño).

---

## Sesión 26 — 2026-10-22

**Objetivo de la sesión:** Tarea de mantenimiento (sin tocar código de
`app/` ni de `tests/`): cerrar la migración del proyecto de Windows a
Debian 13 reinstalando las dependencias en el `venv/` de Linux y
comprobando que todo sigue en verde.

**Actividades realizadas:**

1. **`requirements.txt`:** verificación del fijado de PyMuPDF a
   `>=1.24.9,<2.0` (líneas 4–7). La causa: en PyMuPDF 2.0 los botones de
   opción de los formularios no guardan el valor elegido (probado el
   2026-10-22 comparando 2.0 con 1.28.2), así que 2.0 queda excluido
   hasta que se investigue el cambio.
2. **Instalación:** `venv/bin/python -m pip install -r requirements.txt`
   desinstaló `pymupdf 2.0` y instaló `PyMuPDF-1.28.2`. Confirmado con
   `venv/bin/python -c "import pymupdf; print(pymupdf.VersionBind)"` →
   `1.28.2` (menor que 2.0).
3. **`iniciar.sh`:** `chmod +x iniciar.sh` para poder lanzar el programa
   con `./iniciar.sh` en Debian (en Windows se usaba `iniciar.bat`).
4. **Verificación:** **pyright** → 40 errores, los mismos ruidos
   conocidos (enums cortos de Qt, `Document` vs `Iterable`,
   `PDF_ENCRYPT_AES_256`, `pixmap_limpio`), 0 errores nuevos;
   **pytest** → 63/63 en verde.

**Resultado:** El entorno de Debian 13 queda listo: las dependencias se
instalan desde `requirements.txt` con PyMuPDF 1.28.2 (por debajo de
2.0, por el fallo de los botones de opción), `iniciar.sh` es ejecutable
y pyright/pytest dan los mismos resultados que antes de la migración.

**Pendiente:**
- Investigar el cambio de PyMuPDF 2.0 que hace que los botones de opción
  no guarden su valor, para poder subir de versión cuando se resuelva.

---

## Sesión 27 — 2026-10-22

**Objetivo de la sesión:** Tarea 1 de `DISENO_CREAR_CAMPOS.md`: agregar
a `app/formularios.py` la creación de campos de formulario nuevos
(texto, casilla y firma) sin ventanas, con sus pruebas. No se tocó nada
más (ninguna función existente se modificó).

**Actividades realizadas:**

1. **`app/formularios.py`:** docstring del módulo ampliado (líneas
   20–40) con las funciones nuevas y `import fitz` (línea 43). Al final
   del archivo, la sección "CREAR CAMPOS" (líneas 366–565):
   `TIPOS_CREABLES` (línea 373) y constantes internas de tamaños;
   `validar_nombre_nuevo` (línea 402: vacío, máximo 60 caracteres, sin
   punto, sin repetir un nombre existente comparando sin distinguir
   mayúsculas); `sugerir_nombre` (línea 434: primer nombre libre
   `texto_1`, `casilla_1`…, `ValueError` si el tipo no es creable);
   `rect_para_campo` (línea 455: tamaño estándar si hubo un clic,
   casilla cuadrada con lado mínimo de 10 pt, recorte a la página y
   `ValueError` si queda menor de 8 pt); `crear_campo` (línea 495:
   valida tipo, `multilinea` y nombre **antes** de tocar el documento,
   crea el widget con borde gris y fondo azul claro y devuelve su
   diccionario tal como lo listaría `listar_campos`); y el interno
   `_nombres_existentes` (línea 558).
2. **`tests/test_crear_campos.py`** (nuevo, 326 líneas, 20 pruebas con
   PDFs en memoria): los tres tipos persisten al guardar con `tobytes()`
   y reabrir (línea 48); los campos creados se llenan con
   `escribir_valor` y el valor persiste (línea 106); las reglas del
   nombre (líneas 143 y 157: vacío, con punto, de 61 caracteres,
   repetido y repetido con otras mayúsculas dan mensaje, uno válido da
   `""`); los tres errores de `crear_campo` no tocan el documento
   (líneas 171, 196 y 212: mismos widgets en la página); `sugerir_nombre`
   (líneas 233, 244 y 259); y `rect_para_campo` (líneas 269, 288, 303,
   310 y 317: tamaños estándar, casilla cuadrada, recorte a la página,
   clic pegado al borde y tipo inválido).
3. **`BITACORA.md`:** esta entrada (Sesión 27).

**Resultado:** **pyright** → 40 errores, los mismos ruidos conocidos de
siempre y ninguno en `app/formularios.py` ni en
`tests/test_crear_campos.py`; **pytest** → 83/83 en verde (las 63 de
antes + 20 nuevas). Sin validación visual: la Tarea 1 no tiene ventanas.

**Pendiente:**
- Tarea 2: la ventana "Nuevo campo" (`app/dialogo_nuevo_campo.py`).
- Decisión tomada al seguir el diseño: `rect_para_campo` también lanza
  `ValueError` si el tipo no está en `TIPOS_CREABLES`, porque la tabla
  de tamaños no le define cuadro.

---

## Sesión 28 — 2026-10-22

**Objetivo de la sesión:** Tarea 2 de `DISENO_CREAR_CAMPOS.md`: crear
`app/dialogo_nuevo_campo.py` con la ventana "Nuevo campo" (pide nombre
y, si es texto, si es multilínea), sin tocar `main.py` ni ninguna función
ya existente.

**Actividades realizadas:**

1. **`app/dialogo_nuevo_campo.py`** (nuevo, 149 líneas): docstring del
   módulo (líneas 1–27); imports de Qt y `TIPOS_CREABLES` de
   `formularios` (líneas 29–39); título por tipo en `_TITULOS` (línea
   42: "Nuevo campo de texto", "Nueva casilla", "Nuevo campo de firma");
   `DialogoNuevoCampo(QDialog)` (línea 49) con `__init__(tipo,
   nombre_sugerido, multilinea_inicial, validar, parent=None)` (línea
   62: `ValueError` con tipo fuera de `TIPOS_CREABLES`, `QLineEdit` con
   el nombre sugerido ya seleccionado, `QCheckBox` "Varias líneas" solo
   visible en texto, etiqueta roja del mensaje, `QDialogButtonBox` con
   "Aceptar" y "Cancelar"); `_actualizar_estado` (línea 125: valida con
   `textChanged` y deshabilita Aceptar mientras haya mensaje); y
   `obtener_valores` (línea 136: nombre recortado y estado de la
   casilla). Todo con nombres completos de enums de Qt
   (`QDialogButtonBox.StandardButton.Ok`, `.Cancel`).
2. **`tests/test_dialogo_nuevo_campo.py`** (nuevo, 136 líneas, 12
   pruebas, offscreen y sin `exec()`): títulos por tipo (línea 53);
   "Varias líneas" visible solo en texto (línea 67); nombre sugerido
   seleccionado (línea 78); textos de los botones (línea 86); el
   mensaje y el botón Aceptar al escribir "repetido" y al borrarlo
   (línea 93); `obtener_valores` recortado (línea 113); multilinea
   apagada en casilla y firma (línea 123); tipo inválido → `ValueError`
   (línea 132).
3. **`BITACORA.md`:** esta entrada (Sesión 28).

**Resultado:** **pyright** → 40 errores, los mismos ruidos conocidos y
ninguno en `app/dialogo_nuevo_campo.py` ni en
`tests/test_dialogo_nuevo_campo.py`; **pytest** → 95/95 en verde (83
de antes + 12 nuevas).

**Pendiente:**
- Tarea 3: conectar las herramientas nuevas en `main.py` (ahí sí hay
  validación visual de Diego).
- Decisiones tomadas al seguir el diseño: el diálogo valida el nombre
  **recortado** (consistente con la regla de `validar_nombre_nuevo` de
  que el nombre llega sin espacios), los textos de los botones se fijan
  en español de forma explícita, en casilla y firma la multilinea
  queda oculta y desmarcada aunque venga `multilinea_inicial=True`, y
  un tipo fuera de `TIPOS_CREABLES` lanza `ValueError` al abrir.

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

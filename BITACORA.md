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

<!-- Copia el bloque de abajo cada vez que trabajemos una nueva sesión -->
<!--
## Sesión N — YYYY-MM-DD

**Objetivo de la sesión:**

**Actividades realizadas:**
1.

**Resultado:**

**Pendiente:**
-->

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
1. Creación de la estructura de carpetas del proyecto (`app/`, `docs/`, `assets/`, `tests/`).
2. Redacción de `README.md` con el objetivo y alcance del proyecto.
3. Redacción de `ROADMAP.md` con las 9 fases de desarrollo planeadas.
4. Instalación de Python y dependencias (ver `docs/INSTALL_WINDOWS.md` / `docs/INSTALL_LINUX.md`).
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
11. Publicación del repositorio en GitHub usando GitHub Desktop (ver `docs/GITHUB_DESKTOP.md`).

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

<!-- Copia el bloque de abajo cada vez que trabajemos una nueva sesión -->
<!--
## Sesión N — YYYY-MM-DD

**Objetivo de la sesión:**

**Actividades realizadas:**
1.

**Resultado:**

**Pendiente:**
-->

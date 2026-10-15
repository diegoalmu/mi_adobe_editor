# Mi-Adobe-PDF 📄

Editor de PDF propio, gratuito y de código abierto, creado como alternativa personal a:
- Adobe Acrobat Pro DC
- PDNob
- Wondershare PDF
- PDF-XChange

## 🎯 Objetivo del proyecto

Construir, paso a paso y documentando todo el proceso (para portafolio y evidencia académica),
un programa de escritorio (Windows y Linux) capaz de:

- [x] Abrir y visualizar PDFs (zoom, scroll continuo tipo Adobe)
- [x] Editar texto que YA EXISTE en el PDF (edición tipo Word en línea: clic sobre el
  párrafo → cuadro editable con barra de formato; ver [DISENO_EDITOR_TEXTO.md](DISENO_EDITOR_TEXTO.md))
- [x] Agregar texto nuevo, formas, y firma por imagen
- [x] Resaltar, subrayar, tachar
- [x] Deshacer y Rehacer (Ctrl+Z / Ctrl+Y, menú Editar, hasta 20 pasos)
- [ ] Comentar (notas tipo "sticky note")
- [x] Unir, dividir, reordenar (arrastrar o botones), rotar y eliminar páginas
- [ ] Rellenar y crear formularios PDF
- [x] Exportar PDF a imágenes
- [x] Convertir PDF → Word (.docx)
- [x] OCR (convertir PDFs escaneados en texto editable/buscable)
- [ ] Redactar/tachar información sensible de forma permanente (distinto de "editar texto")
- [ ] Firmar digitalmente con certificado (por ahora: firma por imagen, no criptográfica)
- [x] Comprimir y optimizar el tamaño del archivo
- [x] Proteger con contraseña / quitar contraseña

### 📍 Estado actual (octubre 2026)

Fases 1 a 4 del [ROADMAP](ROADMAP.md) completadas y funcionando (visor, anotaciones,
gestión de páginas y edición de contenido real). La **edición de texto tipo Word**
está terminada y validada (plan [DISENO_EDITOR_TEXTO.md](DISENO_EDITOR_TEXTO.md),
Tareas 0–6): clic sobre un párrafo → cuadro editable en línea con barra de formato
(tipografía, tamaño, negrita/cursiva/subrayado, color), sin abrir ventanas. También
está terminado el **Deshacer y Rehacer** (plan [DISENO_DESHACER.md](DISENO_DESHACER.md),
Tareas 1–4): menú Editar con Ctrl+Z / Ctrl+Y, que muestra qué se va a deshacer
("Deshacer: Rotar página") y registra cada cambio real del documento. El
programa ya está **empaquetado
y probado como aplicación de escritorio en Linux** (ver [EMPAQUETADO.md](EMPAQUETADO.md)).

#### ↩️ Limitaciones conocidas del Deshacer/Rehacer

1. Máximo **20 pasos** y **300 MB** en total entre las copias en memoria; si se
   pasa, se descartan los pasos más antiguos.
2. Queda **deshabilitado** en PDFs con contraseña (de usuario o de permisos):
   las copias en memoria se guardarían sin cifrar y al guardar se perdería la
   contraseña del archivo.

#### ✏️ Limitaciones conocidas de la edición de texto

1. El texto no empuja a los párrafos de abajo; si no cabe en el espacio libre, el
   programa avisa y el usuario reduce la letra o divide el texto.
2. El espacio libre para crecer solo considera texto debajo del párrafo, no imágenes
   ni dibujos.
3. Guardar, cerrar o cambiar el zoom con una edición abierta la descarta.
4. La fuente original del PDF no se conserva; se usa una de las 5 tipografías de la
   lista (Arial, Times New Roman, Calibri, Verdana, Courier New).

Pendientes: formularios (Fase 5), notas "sticky note", redacción permanente,
firma con certificado, exportar a Excel, generar el `.exe` de Windows, ícono
propio y la documentación final de portafolio (Fase 9).

## 🛠️ Tecnología usada

| Necesidad | Herramienta | Por qué |
|---|---|---|
| Lenguaje | Python 3.11+ | Fácil de aprender, enorme ecosistema para PDFs |
| Interfaz gráfica | PySide6 (Qt) | Gratis, profesional, funciona igual en Windows y Linux |
| Motor de PDF | PyMuPDF (fitz) | El motor más completo y rápido, gratis, usado en editores comerciales |
| OCR | ocrmypdf + Tesseract | Motor de OCR gratuito; le agrega capa de texto invisible a PDFs escaneados |
| Conversión a Word | pdf2docx | Convierte PDF a .docx conservando formato |

## 📂 Estructura del proyecto

```
mi_adobe_editor/
├── app/                      # Código fuente del programa (hoy todo en main.py)
├── README.md                 # Esta página
├── ROADMAP.md                # Plan de desarrollo por fases
├── BITACORA.md               # Registro sesión por sesión de todo lo que hacemos
├── INSTALACION_WINDOWS.md    # Instalación paso a paso en Windows
├── INSTALACION_LINUX.md      # Instalación paso a paso en Linux
├── GITHUB_DESKTOP.md         # Cómo publicar el proyecto con GitHub Desktop
├── EMPAQUETADO.md            # Cómo generar el ejecutable independiente (sin Python)
├── LICENSE                   # Licencia AGPL-3.0
└── requirements.txt          # Librerías necesarias
```

> Nota 1: toda la documentación vive en archivos `.md` sueltos en la raíz del
> proyecto (no en subcarpetas), para poder navegarlos y editarlos fácilmente
> desde Obsidian o directo en GitHub.
>
> Nota 2: todavía **no existen** las carpetas `assets/` (íconos) ni `tests/`
> (pruebas). Son parte del plan (ícono propio en la Fase 8, pruebas y pulido
> en la Fase 9 del [ROADMAP](ROADMAP.md)).

## 🚀 Instalación rápida

Ver instrucciones completas paso a paso en:
- [INSTALACION_WINDOWS.md](INSTALACION_WINDOWS.md)
- [INSTALACION_LINUX.md](INSTALACION_LINUX.md)
- [GITHUB_DESKTOP.md](GITHUB_DESKTOP.md) — cómo publicar el proyecto en GitHub usando GitHub Desktop
- [EMPAQUETADO.md](EMPAQUETADO.md) — cómo generar el ejecutable independiente (Linux y Windows) con PyInstaller

## 📅 Bitácora de avance

Todo el progreso, fecha por fecha, se documenta en [BITACORA.md](BITACORA.md)
(útil para portafolio de trabajo y evidencia de proyecto escolar).

## 🗺️ Plan de desarrollo por fases

Ver [ROADMAP.md](ROADMAP.md)

## 📄Licencia

Copyright (C) 2026 Diego Alvarez

Este programa se distribuye bajo la licencia **GNU Affero General Public License v3.0** (AGPL-3.0). Ver el archivo [LICENSE](LICENSE).

Se eligió AGPL-3.0 porque el proyecto usa [PyMuPDF](https://pymupdf.readthedocs.io/), que también se distribuye bajo AGPL-3.0.

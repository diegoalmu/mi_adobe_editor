# Mi-Adobe-PDF 📄

Editor de PDF propio, gratuito y de código abierto, creado como alternativa personal a:
- Adobe Acrobat Pro DC
- PDNob
- Wondershare PDF
- PDF-XChange

## 🎯 Objetivo del proyecto

Construir, paso a paso y documentando todo el proceso (para portafolio y evidencia académica),
un programa de escritorio (Windows y Linux) capaz de:

- [ ] Abrir y visualizar PDFs (zoom, scroll, miniaturas de páginas)
- [ ] Editar texto existente dentro del PDF
- [ ] Agregar texto nuevo, imágenes, formas y sellos
- [ ] Resaltar, subrayar, tachar y comentar (anotaciones)
- [ ] Unir, dividir, reordenar, rotar y eliminar páginas
- [ ] Rellenar y crear formularios PDF
- [ ] Convertir PDF ↔ Word/Excel/Imágenes
- [ ] OCR (convertir PDFs escaneados en texto editable/buscable)
- [ ] Redactar/tachar información sensible de forma permanente
- [ ] Firmar digitalmente documentos
- [ ] Comprimir y optimizar el tamaño del archivo
- [ ] Proteger con contraseña / quitar contraseña

## 🛠️ Tecnología usada

| Necesidad | Herramienta | Por qué |
|---|---|---|
| Lenguaje | Python 3.11+ | Fácil de aprender, enorme ecosistema para PDFs |
| Interfaz gráfica | PySide6 (Qt) | Gratis, profesional, funciona igual en Windows y Linux |
| Motor de PDF | PyMuPDF (fitz) | El motor más completo y rápido, gratis, usado en editores comerciales |
| OCR | Tesseract + pytesseract | Motor de OCR gratuito de Google |
| Conversión a Word | pdf2docx | Convierte PDF a .docx conservando formato |

## 📂 Estructura del proyecto

```
mi-adobe-pdf/
├── app/                      # Código fuente del programa (main.py, etc.)
├── assets/                   # Íconos, imágenes del programa
├── tests/                    # Pruebas del programa
├── README.md                 # Esta página
├── ROADMAP.md                # Plan de desarrollo por fases
├── BITACORA.md                # Registro sesión por sesión de todo lo que hacemos
├── INSTALACION_WINDOWS.md    # Instalación paso a paso en Windows
├── INSTALACION_LINUX.md      # Instalación paso a paso en Linux
├── GITHUB_DESKTOP.md         # Cómo publicar el proyecto con GitHub Desktop
└── requirements.txt          # Librerías necesarias
```

> Nota: toda la documentación vive en archivos `.md` sueltos en la raíz del
> proyecto (no en subcarpetas), para poder navegarlos y editarlos fácilmente
> desde Obsidian o directo en GitHub.

## 🚀 Instalación rápida

Ver instrucciones completas paso a paso en:
- [INSTALACION_WINDOWS.md](INSTALACION_WINDOWS.md)
- [INSTALACION_LINUX.md](INSTALACION_LINUX.md)
- [GITHUB_DESKTOP.md](GITHUB_DESKTOP.md) — cómo publicar el proyecto en GitHub usando GitHub Desktop en Linux

## 📅 Bitácora de avance

Todo el progreso, fecha por fecha, se documenta en [BITACORA.md](BITACORA.md)
(útil para portafolio de trabajo y evidencia de proyecto escolar).

## 🗺️ Plan de desarrollo por fases

Ver [ROADMAP.md](ROADMAP.md)

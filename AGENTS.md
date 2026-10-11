# AGENTS.md — Reglas para agentes de código en Mi-Adobe-PDF

Este archivo lo leen automáticamente los agentes de código (OpenCode, etc.)
al trabajar en este repositorio. Las reglas son obligatorias.

## Proyecto

Editor de PDF de escritorio en Python + PySide6 + PyMuPDF.
Licencia AGPL-3.0. Código y comentarios en español.

- Carpeta oficial y única: `D:\GITHUB\mi_adobe_editor`
- Entrada del programa: `app\main.py` (se lanza con `iniciar.bat`)
- Entorno virtual: `venv\` (Windows). Usar SIEMPRE `.\venv\Scripts\python.exe`,
  nunca el `python` del sistema.
- Plan vigente: `DISENO_EDITOR_TEXTO.md`

## Reglas de trabajo

1. **Una tarea a la vez.** Haz solo la tarea que se te pidió. Si ves otro
   problema, menciónalo en tu resumen; no lo arregles por tu cuenta.
2. **No cambies nada fuera del alcance de la tarea.** Ni nombres, ni estilo,
   ni archivos que la tarea no menciona.
3. **No dejes piezas a medias.** No llames funciones que no existen ni dejes
   parámetros "para uso futuro". Si algo no se puede terminar, dilo.
4. **No agregues dependencias** sin pedir permiso. Las permitidas están en
   `requirements.txt` y `requirements-dev.txt`.
5. **No toques** `venv\`, `LICENSE`, `pyrightconfig.json` ni `.gitignore`.
6. **No hagas commits ni push.** Diego hace los commits con GitHub Desktop.
7. **No borres archivos del usuario** (PDFs, imágenes, documentos).
8. Sigue el estilo del código existente: nombres en español sin acentos ni
   ñ en identificadores (`tamano`, `pagina`), comentarios explicativos en
   español, mensajes al usuario en español.
9. Los imports entre módulos de `app\` van sin prefijo de paquete
   (`from formato_html import ...`), porque `main.py` se ejecuta como script.

## Verificación obligatoria antes de terminar

```powershell
.\venv\Scripts\pyright.exe
```

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

- **Pyright:** no debe haber errores nuevos. Son ruido conocido y NO se
  corrigen salvo que la tarea lo pida:
  - `Cannot access attribute "..." for class "type[Qt]"` (y de `QListWidget`,
    `QAbstractItemView`, `QMessageBox`, `QDialog`, `QFont`, `QTextCursor`,
    `QTextEdit`, `QLineEdit`, `QImage`, `QRubberBand`): enums cortos de Qt.
  - `"Document" is incompatible with protocol "Iterable"`.
  - `"PDF_ENCRYPT_AES_256" is not a known attribute of module "fitz"`.
  - `Cannot assign to attribute "pixmap_limpio"`.
- **Pytest:** todas las pruebas en verde. Una prueba que falla no se borra
  ni se "ajusta" para que pase: se corrige el código o se reporta.

## Al terminar cada sesión

1. Agrega una entrada en `BITACORA.md` con la plantilla que está al final
   de ese archivo (fecha, objetivo, actividades, resultado, pendientes).
2. Entrega un resumen con: archivos creados o modificados, qué se cambió
   en cada uno (con números de línea), resultado de pyright y de pytest, y
   qué debe validar Diego visualmente (si aplica).

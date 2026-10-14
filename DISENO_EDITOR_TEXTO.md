# 🖋️ Diseño — Editor de texto tipo Word

> Documento de diseño de la nueva edición de texto de Mi-Adobe-PDF.
> Se escribe ANTES de programar, para que cada tarea sea pequeña, tenga
> una prueba, y no queden piezas a medias (lección de la versión de
> Antigravity, ver `BITACORA.md`).

> **✅ Estado (2026-10-11): COMPLETADA.** Tareas 0–6 ejecutadas en las
> Sesiones 7–14 de `BITACORA.md` y validadas visualmente por Diego
> (Tarea 5 + correcciones de la Sesión 14; limpieza y documentación en
> la Tarea 6).

## 🎯 Objetivo

Reemplazar la ventana "Editar cuadro de texto" (que pide posición X/Y y
medidas en puntos) por una edición directa sobre la página, como en Word
o Acrobat:

1. El usuario elige la herramienta **"Editar contenido (texto e imagenes)"**.
2. Da **un clic** sobre un párrafo (recuadro azul).
3. Aparece un **cuadro editable encima del párrafo**, con el texto actual.
4. Aparece una **barra de formato arriba** (debajo de la barra principal).
5. Puede seleccionar **una sola palabra** y ponerla en negrita, cursiva,
   subrayado, otro color, otro tamaño u otra tipografía, sin afectar al
   resto del párrafo.
6. **Aceptar** (botón o `Ctrl+Enter`) escribe el resultado en el PDF.
   **Cancelar** (botón o `Esc`) cierra sin cambiar nada.

## 🚫 Fuera de alcance (a propósito)

- **Reflujo entre párrafos:** el texto se reacomoda dentro de su propio
  cuadro, pero no empuja los párrafos de abajo. Los PDFs no son documentos
  de flujo; ni Acrobat lo hace bien.
- **Conservar la fuente original del PDF:** casi siempre viene incrustada
  incompleta (solo las letras que se usaron). El texto editado se escribe
  con la tipografía que elija el usuario de la lista de abajo; se verá muy
  parecido, no idéntico.
- **Edición de imágenes y formas de color:** se quedan como están hoy.

## ⚠️ Limitaciones conocidas (documentadas al completar)

1. El texto no empuja a los párrafos de abajo; si no cabe en el espacio libre, el
   programa avisa y el usuario reduce la letra o divide el texto.
2. El espacio libre para crecer solo considera texto debajo del párrafo, no imágenes
   ni dibujos.
3. Guardar, cerrar o cambiar el zoom con una edición abierta la descarta.
4. La fuente original del PDF no se conserva; se usa una de las 5 tipografías de la
   lista (Arial, Times New Roman, Calibri, Verdana, Courier New).

## 🧱 Decisiones técnicas

### Escribir texto con formato mixto: `insert_htmlbox`

El método actual (`insert_textbox`) escribe todo el cuadro con **una sola
fuente y un solo estilo**. Por eso, al poner una palabra en negrita, se
ponía en negrita todo el párrafo.

PyMuPDF tiene `pagina.insert_htmlbox(rect, html, css=..., archive=..., scale_low=1)`,
que escribe HTML sencillo dentro de un rectángulo, respetando el formato de
cada palabra (`<b>`, `<i>`, `<u>`, `<span style="...">`) y haciendo el
salto de línea automático.

- `scale_low=1` → **nunca** reduce el texto para que quepa. Si no cabe,
  la función lo indica (primer valor devuelto negativo) y el programa
  avisa al usuario sin tocar el documento.
- Antes de modificar el PDF real, se prueba en un **documento temporal
  descartable** (la prueba vive en `cabe_texto_con_formato`).

### Tipografías: lista corta incrustada desde Windows

| Nombre en la barra | Normal | Negrita | Cursiva | Negrita+Cursiva |
|---|---|---|---|---|
| Arial | `arial.ttf` | `arialbd.ttf` | `ariali.ttf` | `arialbi.ttf` |
| Times New Roman | `times.ttf` | `timesbd.ttf` | `timesi.ttf` | `timesbi.ttf` |
| Calibri | `calibri.ttf` | `calibrib.ttf` | `calibrii.ttf` | `calibriz.ttf` |
| Verdana | `verdana.ttf` | `verdanab.ttf` | `verdanai.ttf` | `verdanaz.ttf` |
| Courier New | `cour.ttf` | `courbd.ttf` | `couri.ttf` | `courbi.ttf` |

- Los archivos se leen de `C:\Windows\Fonts` con `fitz.Archive(...)` y se
  declaran en el CSS con `@font-face` (familia + `font-weight` +
  `font-style` + `src: url(archivo.ttf)`).
- **Solo se incluyen** en el CSS las tipografías cuyos archivos existan.
  Si falta alguno (por ejemplo en Linux), esa tipografía no aparece en la
  barra y se usa `sans-serif` como respaldo. El programa nunca truena por
  una fuente faltante.
- Cada tipografía usada se incrusta en el PDF y aumenta su tamaño: por eso
  la lista es corta.

### Del editor de Qt al HTML: convertidor propio

El cuadro editable es un `QTextEdit` (texto enriquecido). **No** se usa su
`toHtml()`, porque genera HTML con estilos propios de Qt que MuPDF no
interpreta bien. En su lugar, el programa recorre el documento de Qt
(bloques → fragmentos con su `QTextCharFormat`) y arma una lista de
**fragmentos**:

```python
{"texto": "Precio", "familia": "Arial", "tamano": 11.0,
 "negrita": True, "cursiva": False, "subrayado": False,
 "color": (0, 0, 0)}
```

Esa lista se convierte a HTML sencillo con una función propia, que
escapa los caracteres especiales (`<`, `>`, `&`) y convierte los saltos de
párrafo en `<br>`.

### Organización del código: módulos nuevos

`app/main.py` ya tiene más de 1,700 líneas. El código nuevo **no** se
agrega ahí, sino en módulos aparte dentro de `app/`:

| Archivo | Contenido | ¿Necesita ventana para probarse? |
|---|---|---|
| `app/formato_html.py` | Tipografías, CSS, fragmentos → HTML, escribir en el PDF | No (funciones puras + PyMuPDF) |
| `app/editor_texto.py` | Cuadro editable (`EditorTextoInline`) y barra de formato (`BarraFormato`) | Sí, pero se prueba en modo `offscreen` |

- Como `iniciar.bat` ejecuta `app\main.py` como script, los imports son
  **sin prefijo de paquete**: `from formato_html import ...`.
- Las pruebas agregan la carpeta `app/` a `sys.path` antes de importar.
- Las pruebas que usan Qt fijan `os.environ["QT_QPA_PLATFORM"] = "offscreen"`
  antes de crear la `QApplication`, para correr sin abrir ventanas.

## 🧪 Cómo se verifica cada tarea

Ninguna tarea se da por terminada sin estas tres cosas:

1. **Pyright** sin errores nuevos (`.\venv\Scripts\pyright.exe`). Los
   errores conocidos de enums cortos de Qt (`Cannot access attribute ...
   for class type[Qt]` y similares) y de `Document` iterable son ruido
   previo y no cuentan.
2. **Pruebas automáticas** en verde (`.\venv\Scripts\python.exe -m pytest -v`).
3. **Validación visual de Diego** en las tareas que cambian lo que se ve
   en pantalla (indicadas abajo).

## 📋 Tareas (en orden, una por sesión de OpenCode)

### Tarea 0 — Herramientas de desarrollo ✅

- Crear `requirements-dev.txt` con `pytest` y `pyright` (solo para
  desarrollo; el programa no los necesita para funcionar).
- Instalarlos en el `venv`.
- Crear `tests/conftest.py` que agregue la raíz del proyecto y `app/` a
  `sys.path`, y fije `QT_QPA_PLATFORM=offscreen`.
- **Prueba:** `pytest -v` corre (aunque sea con 0 pruebas) sin error de
  configuración.

### Tarea 1 — `app/formato_html.py`: tipografías y HTML ✅

- Constante `TIPOGRAFIAS` con la tabla de arriba.
- `CARPETA_FUENTES_WINDOWS = r"C:\Windows\Fonts"`.
- `tipografias_disponibles(carpeta)` → lista de nombres cuyos 4 archivos existen.
- `css_tipografias(carpeta)` → texto CSS con los `@font-face` de las disponibles.
- `fragmentos_a_html(fragmentos)` → HTML con un `<span style="...">` por
  fragmento (familia, tamaño en `pt`, `font-weight`, `font-style`,
  `text-decoration`, color en `#rrggbb`), escapando caracteres especiales
  y convirtiendo `\n` en `<br>`.
- **Pruebas** (`tests/test_formato_html.py`): escapa `<b>` como texto
  literal; un fragmento en negrita genera `font-weight:bold` solo en ese
  span; `\n` produce `<br>`; con una carpeta vacía no hay tipografías
  disponibles y el CSS queda vacío.

### Tarea 2 — Escribir en el PDF con formato ✅

- En `app/formato_html.py`:
  - `cabe_texto_con_formato(rect, html, css, archivo)` → prueba en un
    documento temporal con `insert_htmlbox(..., scale_low=1)` y devuelve
    `True`/`False`.
  - `insertar_texto_con_formato(pagina, rect, html, css, archivo)` →
    escribe en la página real (solo se llama después de confirmar que cabe).
- **Pruebas** (`tests/test_insertar_formato.py`): crear un PDF en memoria,
  insertar "Precio **actualizado**" con solo la segunda palabra en negrita,
  y verificar con `get_text("dict")` que hay un span en negrita con
  "actualizado" y otro sin negrita con "Precio"; un texto enorme en un
  cuadro pequeño devuelve `False` en `cabe_texto_con_formato` y no
  modifica el documento.

### Tarea 3 — `app/editor_texto.py`: cuadro editable ✅

- Clase `EditorTextoInline(QTextEdit)`: sin marco, fondo blanco
  semitransparente, se coloca encima del párrafo según el zoom.
  `Esc` emite la señal `cancelado`; `Ctrl+Enter` emite `aceptado`.
- Función `documento_a_fragmentos(documento_qt)` → recorre bloques y
  fragmentos y devuelve la lista de fragmentos (formato de arriba),
  agregando `"\n"` entre bloques.
- **Pruebas** (`tests/test_editor_texto.py`, modo offscreen): escribir
  "uno dos tres", seleccionar "dos" con un `QTextCursor`, aplicar negrita
  con `mergeCharFormat`, y verificar que `documento_a_fragmentos` devuelve
  "dos" con `negrita=True` y "uno"/"tres" con `negrita=False`.

### Tarea 4 — `app/editor_texto.py`: barra de formato ✅

- Clase `BarraFormato(QToolBar)` con: selector de tipografía (solo las
  disponibles), tamaño, botones activables de Negrita / Cursiva /
  Subrayado, botón de color, **Aceptar** y **Cancelar**.
- Cada control aplica el formato **solo a la selección** del editor
  (`mergeCurrentCharFormat`); sin selección, aplica a lo que se escriba
  después (comportamiento normal de Word).
- Al mover el cursor, la barra refleja el formato del texto donde está
  (si el cursor está en una palabra en negrita, el botón Negrita se ve activo).
- Señales `aceptar` y `cancelar`.
- **Pruebas** (offscreen): seleccionar una palabra, activar el botón
  Negrita de la barra, y verificar con `documento_a_fragmentos` que solo
  esa palabra quedó en negrita; mover el cursor a esa palabra y verificar
  que el botón Negrita queda marcado.

### Tarea 5 — Conectar todo en `app/main.py` (👁️ validación visual) ✅

- En `editar_contenido_en_punto`, al dar clic en un párrafo: crear el
  `EditorTextoInline` encima del párrafo (con su texto, tamaño y color
  actuales), mostrar la `BarraFormato` debajo de la barra principal y
  dar foco al editor.
- Mientras se edita: un solo editor a la vez, y los clics en la página no
  crean anotaciones.
- **Aceptar:** convertir a fragmentos → HTML; si no cabe, avisar y dejar
  el editor abierto (sin tocar el documento); si cabe, tapar el párrafo
  original con su color de fondo (`muestrear_color_de_fondo` +
  `add_redact_annot` + `apply_redactions` + `clean_contents`), escribir el
  HTML con `insertar_texto_con_formato`, cerrar editor y barra, y
  redibujar la página.
- **Cancelar:** cerrar editor y barra; el documento queda intacto.
- **Prueba automática:** abrir un PDF de prueba, simular la aceptación con
  una palabra en negrita, guardar, y verificar con `get_text("dict")`.
- **Validación visual de Diego:** con un PDF real, editar un párrafo,
  poner una palabra en negrita y otra en otro color, cambiar tipografía,
  aceptar, guardar con "Guardar como" y abrir el resultado en el navegador.

### Tarea 6 — Limpieza y documentación ✅

- Solo después de que Diego valide la Tarea 5: eliminar
  `DialogoEditarCuadroDeTexto` y el código que solo usaba esa ventana
  (para texto; imágenes y formas no se tocan).
- Actualizar `README.md`, `ROADMAP.md` (Fase 4) y `BITACORA.md`.
- **Prueba:** pyright sin errores nuevos y todas las pruebas en verde.

## 📝 Prompt para cada tarea

Abrir OpenCode Desktop en `D:\GITHUB\mi_adobe_editor` y pegar, cambiando
el número:

```
Lee AGENTS.md y DISENO_EDITOR_TEXTO.md. Haz SOLO la Tarea N, siguiendo el
diseño al pie de la letra. Al terminar corre pyright y pytest, agrega la
entrada de la sesión en BITACORA.md, y dame un resumen de cada archivo
creado o modificado.
```

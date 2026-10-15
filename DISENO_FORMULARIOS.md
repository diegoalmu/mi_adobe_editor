# 📝 Diseño — Llenar formularios PDF (Fase 5, parte 1)

> Documento de diseño para llenar los campos de formularios que YA existen
> en un PDF. Mismo método que `DISENO_EDITOR_TEXTO.md` y `DISENO_DESHACER.md`:
> diseño primero, tareas pequeñas con pruebas, validación visual de Diego
> al final.

## 🎯 Objetivo

Muchos PDFs de oficina traen campos para llenar: solicitudes, formatos de
gobierno, constancias, cotizaciones. Hoy el editor los muestra, pero no
deja escribir en ellos. Con esta función:

1. Al abrir un PDF con campos, el programa lo detecta y muestra un
   **panel lateral "Campos del formulario"** con la lista de campos.
2. Cada campo aparece con su nombre, su tipo y un control para llenarlo:
   cuadro de texto, casilla, botones de opción o lista desplegable.
3. Al cambiar un valor, la página se redibuja y el campo se ve lleno.
4. Dar clic sobre un campo en la página lo **selecciona en el panel**,
   para saber cuál es cuál.
5. Cada cambio se puede deshacer con `Ctrl+Z` (usa el historial que ya
   existe, `DISENO_DESHACER.md`).
6. Al guardar, los valores quedan dentro del PDF y se ven en cualquier
   otro visor (Edge, Chrome, Acrobat).

## 🤔 Por qué un panel lateral y no escribir directo sobre la página

- Es el método más confiable: no depende de calcular posiciones con el
  zoom ni de dibujar controles de Qt encima de la página (lo que dio más
  trabajo en el editor de texto).
- Muestra **todos** los campos, incluso los que no se ven bien en la página
  (campos ocultos tras otros, muy pequeños o en otras páginas).
- Es como lo hace el panel de campos de Acrobat y de PdfCraft.

Escribir directamente sobre la página puede agregarse después, cuando el
panel esté probado.

## 🚫 Fuera de alcance (a propósito)

- **Crear campos nuevos** (Fase 5, parte 2, con su propio diseño).
- **Firmas digitales** con certificado: los campos de firma se listan como
  "Firma (no editable aquí)".
- **Formularios XFA** (formato viejo de Adobe LiveCycle): si el PDF solo
  tiene XFA, se avisa que no se puede llenar con este programa.
- **Cálculos y validaciones con JavaScript** del formulario: no se ejecutan.
  Si un campo calcula un total automáticamente en Acrobat, aquí no.
- **Aplanar el formulario** (convertir los campos en texto fijo): se evalúa
  después de que funcione el llenado.

## 🧱 Decisiones técnicas

### Leer y escribir campos con PyMuPDF

- `pagina.widgets()` recorre los campos de cada página.
- Cada campo (`fitz.Widget`) tiene: `field_name`, `field_type`,
  `field_value`, `rect`, `field_flags`, `choice_values` (listas),
  `button_states()` / `on_state()` (casillas y opciones), `xref`.
- Para escribir: se cambia `field_value` y se llama `widget.update()`, que
  regenera la apariencia del campo para que se vea en cualquier visor.
- Tipos soportados:

| Tipo PyMuPDF | Cómo se muestra en el panel | Valor |
|---|---|---|
| `PDF_WIDGET_TYPE_TEXT` | `QLineEdit` (o `QPlainTextEdit` si es multilínea) | texto |
| `PDF_WIDGET_TYPE_CHECKBOX` | `QCheckBox` | encendido / apagado |
| `PDF_WIDGET_TYPE_RADIOBUTTON` | Grupo de `QRadioButton` con el mismo nombre | la opción elegida |
| `PDF_WIDGET_TYPE_COMBOBOX` | `QComboBox` | una de `choice_values` |
| `PDF_WIDGET_TYPE_LISTBOX` | `QComboBox` | una de `choice_values` |
| `PDF_WIDGET_TYPE_SIGNATURE` | Texto "Firma (no editable aquí)" | — |
| `PDF_WIDGET_TYPE_BUTTON` | No se lista (son botones de acción) | — |

- **Solo lectura:** si `field_flags & 1` (bandera ReadOnly del PDF), el
  control aparece deshabilitado.
- **Casillas y opciones:** el valor de "encendido" no siempre es `"Yes"`;
  se usa `widget.on_state()`, y para apagar se usa `"Off"`.
- **Opciones con el mismo nombre:** los botones de opción de un mismo grupo
  comparten `field_name`; en el panel se muestran juntos como un grupo.

### Detección de XFA

`documento.is_form_pdf` indica si hay formulario. Si el catálogo del PDF
tiene XFA y **no** hay campos normales (`widgets()` vacío en todas las
páginas), se muestra un aviso: "Este formulario usa XFA y no se puede
llenar con este programa".

### Integración con Deshacer

- Cada cambio de valor llama a `registrar_cambio("Llenar campo: <nombre>")`
  **antes** de escribir, y `_revertir_cambio_fallido()` si la escritura falla.
- Para no llenar el historial con un paso por cada letra: los campos de
  texto escriben al PDF cuando el usuario **termina** (pierde el foco o
  presiona Enter), no en cada tecla.
- Al deshacer o rehacer, el panel se vuelve a cargar desde el documento,
  para que muestre los valores restaurados.

### Organización del código

| Archivo | Contenido | ¿Necesita ventana para probarse? |
|---|---|---|
| `app/formularios.py` (nuevo) | Leer campos, escribir valores, detectar XFA | No (funciones puras + PyMuPDF) |
| `app/panel_formularios.py` (nuevo) | `PanelFormularios(QDockWidget)` | Sí, en modo offscreen |
| `app/main.py` | Mostrar el panel, conectar cambios, clic en campo, deshacer | Sí, en modo offscreen |

Las pruebas crean sus propios PDFs con campos usando `fitz.Widget()` y
`pagina.add_widget()`, sin depender de archivos externos.

## 🧪 Cómo se verifica cada tarea

Igual que en los diseños anteriores:

1. **Pyright** sin errores nuevos (`.\venv\Scripts\pyright.exe`).
2. **Pytest** en verde (`.\venv\Scripts\python.exe -m pytest -v`).
3. **Validación visual de Diego** donde se indique.

## 📋 Tareas (en orden, una por sesión de OpenCode)

### Tarea 1 — `app/formularios.py`: leer campos

- `listar_campos(documento)` → lista de diccionarios, uno por campo (los
  botones de opción del mismo nombre se agrupan en uno solo):

```python
{"nombre": "nombre_cliente", "tipo": "texto", "valor": "",
 "opciones": [],            # para listas y grupos de opción
 "solo_lectura": False, "multilinea": False,
 "paginas": [0], "rects": [fitz.Rect(...)], "xrefs": [123]}
```

  Tipos posibles: `"texto"`, `"casilla"`, `"opcion"`, `"lista"`, `"firma"`.
  Los botones de acción no se incluyen.
- `tiene_formulario(documento)` → `True` si hay al menos un campo listable.
- `es_solo_xfa(documento)` → `True` si tiene XFA y ningún campo normal.
- **Pruebas** (`tests/test_formularios.py`): un PDF creado en la prueba
  con un campo de texto, una casilla, dos botones de opción del mismo grupo,
  una lista con 3 opciones y un campo de solo lectura; verificar tipos,
  valores, opciones, que el grupo de opción salga como un solo campo y que
  el de solo lectura venga marcado. Un PDF sin campos → `tiene_formulario`
  es `False`.

### Tarea 2 — `app/formularios.py`: escribir valores

- `escribir_valor(documento, campo, valor)`:
  - texto → string; casilla → `True`/`False`; opción y lista → una de las
    opciones válidas.
  - Lanza `ValueError` con mensaje en español si el campo es de solo
    lectura, de firma, o si el valor no es válido para su tipo.
  - Llama `widget.update()` en cada widget afectado.
- **Pruebas:** llenar cada tipo, guardar con `tobytes()`, volver a abrir y
  verificar que los valores persisten; un valor inválido en una lista y
  escribir en un campo de solo lectura lanzan `ValueError` sin modificar el
  documento.

### Tarea 3 — `app/panel_formularios.py`: el panel

- `PanelFormularios(QDockWidget)` con título "Campos del formulario" y una
  lista con desplazamiento: una fila por campo (nombre + control según el
  tipo, tabla de arriba).
- `cargar(campos)`: reconstruye el panel. Mientras carga, bloquea señales
  (`blockSignals`) para no disparar cambios.
- Señal `valor_cambiado(nombre, valor)`: los de texto la emiten al terminar
  de editar (`editingFinished`), los demás al cambiar.
- `seleccionar(nombre)`: resalta la fila del campo y le da foco.
- **Pruebas** (offscreen): cargar los campos del PDF de prueba, verificar el
  control correcto por tipo y el de solo lectura deshabilitado; marcar una
  casilla emite `valor_cambiado` una sola vez; `cargar()` no emite señales.

### Tarea 4 — Conectar en `app/main.py` (👁️ validación visual)

- Menú **"Formularios"** con la acción **"Mostrar campos"** (activable).
- Al abrir un PDF con campos, el panel se muestra solo, a la derecha; sin
  campos, se oculta. Si es solo XFA, aviso.
- Al recibir `valor_cambiado`: `registrar_cambio(...)`, `escribir_valor`,
  redibujar la página del campo; si falla, `_revertir_cambio_fallido()` y
  mensaje de error.
- Clic en un campo de la página (con la herramienta "Ninguna (solo ver)")
  selecciona ese campo en el panel.
- Después de deshacer, rehacer, abrir o cerrar documento, el panel se
  vuelve a cargar.
- **Pruebas** (offscreen): llenar un campo de texto desde el panel →
  el documento lo tiene; `Ctrl+Z` → vuelve a vacío y el panel también.
- **Validación visual de Diego:** con un formulario PDF real (por ejemplo
  un formato de gobierno descargado), llenar texto, casillas y listas,
  guardar con "Guardar como" y abrir el resultado en Edge o Chrome.

### Tarea 5 — Documentación

- `README.md` (checklist "Rellenar formularios PDF"), `ROADMAP.md` (Fase 5,
  parte 1 completada), `BITACORA.md`, y marcar este diseño como completado.
- Documentar las limitaciones: sin XFA, sin JavaScript, sin firmas
  digitales, sin crear campos todavía.

## 📝 Prompt para cada tarea

Abrir OpenCode Desktop en `D:\GITHUB\mi_adobe_editor`, empezar con `/new`,
modo **Build**, y pegar cambiando el número:

```
Lee AGENTS.md y DISENO_FORMULARIOS.md. Haz SOLO la Tarea N, siguiendo el
diseño al pie de la letra. Usa nombres completos de enums de Qt en el
código nuevo. Al terminar corre pyright y pytest, agrega la entrada de la
sesión en BITACORA.md (fecha con Get-Date), y dame un resumen de cada
archivo creado o modificado con números de línea. No preguntes si sigues.
```

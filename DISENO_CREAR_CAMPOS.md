# 📝 Diseño — Crear campos de formulario (Fase 5, parte 2)

> Documento de diseño para **crear campos nuevos** en un PDF: texto,
> casilla y firma. Continúa `DISENO_FORMULARIOS.md` (parte 1: llenar los
> campos que el PDF ya trae). Mismo método de siempre: diseño primero,
> tareas pequeñas con pruebas y validación visual de Diego al final.

## 🎯 Objetivo

Convertir un PDF "plano" (por ejemplo una solicitud escaneada o un
formato hecho en Word) en un formulario que se pueda llenar:

1. En el desplegable **Herramienta** aparecen tres opciones nuevas:
   **"Crear campo de texto"**, **"Crear casilla"** y **"Crear campo de
   firma"**.
2. El usuario arrastra un cuadro sobre la página (o da un solo clic, y se
   usa un tamaño estándar).
3. Se abre una ventana pequeña **"Nuevo campo"** que pide el nombre (ya
   viene sugerido, por ejemplo `texto_1`) y, en los de texto, si es
   multilínea.
4. Al aceptar, el campo queda en la página con borde gris y fondo azul
   claro, el panel "Campos del formulario" se muestra con el campo nuevo
   seleccionado y ya se puede llenar desde ahí.
5. Cada campo creado es un paso de `Ctrl+Z`.
6. Al guardar, el campo funciona en cualquier visor (Chrome, Edge,
   Acrobat): se puede escribir en él, marcarlo o firmarlo.

## ✅ Comprobado antes de escribir este diseño (PyMuPDF 1.28.2)

Se probó en un entorno aparte, para que ninguna tarea se tope con una
sorpresa como la de los botones de opción en PyMuPDF 2.0:

- `pagina.add_widget()` crea sin errores campos de texto (normal y
  multilínea), casillas y firmas.
- `listar_campos()` (parte 1) los reconoce con su tipo correcto:
  `"texto"` (con `multilinea` en `True` si aplica), `"casilla"` y
  `"firma"`.
- `escribir_valor()` (parte 1) los llena sin ningún cambio, y los valores
  persisten al guardar con `tobytes()` y volver a abrir.
- Con `border_color`, `border_width` y `fill_color` los campos vacíos se
  ven con borde y fondo, tanto en el programa como en el motor de Chrome
  (pdfium). El campo de firma no toma el borde: PyMuPDF le pone su propia
  apariencia, una etiqueta "SIGN", que también se ve en ambos.
- ⚠️ **PyMuPDF deja crear dos campos con el mismo nombre.** Eso produce un
  PDF ambiguo: cada visor decide distinto qué hacer con ellos. Por eso
  la validación del nombre es obligatoria (Tarea 1).

## 🚫 Fuera de alcance (a propósito)

- **Botones de opción y listas desplegables:** necesitan pedir varias
  opciones y, en el caso de las opciones, varios cuadros con el mismo
  nombre. Se dejan para otra parte si hacen falta.
- **Mover, cambiar el tamaño o renombrar** un campo ya creado. Si quedó
  mal, se deshace con `Ctrl+Z` y se vuelve a crear.
- **Eliminar campos** que el PDF ya traía.
- **Firmar con certificado digital:** el campo de firma queda vacío para
  firmarlo en otro programa (eso sigue pendiente en la Fase 7).
- **Detectar campos automáticamente** (buscar líneas o cuadros vacíos en
  un PDF plano y convertirlos en campos, como hace Acrobat).
- **Formato, validación o cálculos** (solo números, fechas, totales):
  requieren JavaScript del PDF.

## 🧱 Decisiones técnicas

### Crear el campo con PyMuPDF

```python
widget = fitz.Widget()
widget.field_name = nombre
widget.field_type = PDF_WIDGET_TYPE_TEXT   # o CHECKBOX, SIGNATURE
widget.rect = rect
widget.border_color = (0.5, 0.5, 0.5)      # gris
widget.border_width = 1
widget.fill_color = (0.93, 0.95, 1.0)      # azul muy claro
widget.text_fontsize = 0                   # solo texto: tamaño automático
widget.field_flags = PDF_TX_FIELD_IS_MULTILINE  # solo texto multilínea
pagina.add_widget(widget)
```

- Las constantes se importan de `pymupdf.mupdf`, igual que en
  `formularios.py` (pyright no las ve en el paquete principal).
- Los atributos de `fitz.Widget` se asignan con `setattr(...)`, como en
  las pruebas que ya existen, porque pyright no los tiene anotados.

### Tamaño y forma del cuadro

| Tipo | Si el usuario solo da clic (cuadro menor a 8 pt de ancho o alto) | Si arrastra |
|---|---|---|
| Texto | 200 × 22 pt desde el punto del clic | el cuadro arrastrado |
| Casilla | 14 × 14 pt desde el punto del clic | cuadrado con lado = el menor de ancho y alto (mínimo 10 pt) |
| Firma | 180 × 50 pt desde el punto del clic | el cuadro arrastrado |

- El cuadro final se recorta a los límites de la página. Si después del
  recorte mide menos de 8 pt de ancho o de alto (por ejemplo, un clic
  pegado al borde), no se crea el campo y se avisa.
- **Multilínea:** en la ventana "Nuevo campo", la casilla "Varias líneas"
  aparece marcada de inicio si el cuadro mide 40 pt de alto o más.

### Reglas del nombre

`validar_nombre_nuevo(documento, nombre)` devuelve un mensaje de error en
español, o `""` si el nombre es válido. El nombre se recibe ya sin
espacios al inicio ni al final.

1. No puede estar vacío.
2. Máximo 60 caracteres.
3. **No puede llevar punto (`.`):** en los PDF el punto separa niveles
   de un nombre (`cliente.nombre` es el campo `nombre` dentro de
   `cliente`), y un punto metido sin querer rompe el formulario en otros
   visores.
4. **No puede repetir el nombre de un campo existente**, comparando sin
   distinguir mayúsculas y minúsculas (`Nombre` y `nombre` cuentan como
   el mismo, para no confundir al usuario).

`sugerir_nombre(documento, tipo)` devuelve el primer nombre libre de la
forma `texto_1`, `texto_2`… (`casilla_N` y `firma_N` para los otros
tipos).

### Integración con Deshacer

- La ventana "Nuevo campo" se muestra **antes** de registrar el cambio:
  si el usuario la cancela, no hay nada que descartar.
- Al aceptar: `registrar_cambio("Crear campo: <nombre>")`, se crea el
  campo y, si falla, `_revertir_cambio_fallido()` y un mensaje de error.
- Después de crear, deshacer o rehacer, el panel se vuelve a cargar con
  `_recargar_panel_formularios()` (eso ya existe y ya lo hacen deshacer y
  rehacer).

### Organización del código

| Archivo | Contenido | ¿Necesita ventana para probarse? |
|---|---|---|
| `app/formularios.py` | `validar_nombre_nuevo`, `sugerir_nombre`, `rect_para_campo`, `crear_campo` | No |
| `app/dialogo_nuevo_campo.py` (nuevo) | `DialogoNuevoCampo(QDialog)` | Sí, en modo offscreen |
| `app/main.py` | Herramientas nuevas, flujo de creación, Deshacer y panel | Sí, en modo offscreen |

## 🧪 Cómo se verifica cada tarea

1. **Pyright** sin errores nuevos (`venv/bin/pyright`).
2. **Pytest** en verde (`venv/bin/python -m pytest -v`). Hoy son 63
   pruebas; cada tarea suma las suyas y ninguna de las anteriores se
   toca.
3. **Validación visual de Diego** donde se indique.

## 📋 Tareas (en orden, una por sesión de OpenCode)

### Tarea 1 — `app/formularios.py`: crear campos (sin ventanas)

Agregar al final de `app/formularios.py`, sin modificar las funciones
que ya existen (actualizar solo el docstring del módulo para listar las
nuevas):

- `TIPOS_CREABLES = ("texto", "casilla", "firma")`.
- `validar_nombre_nuevo(documento, nombre)` → `str`, según las reglas de
  arriba. Usa `listar_campos(documento)` para saber qué nombres existen.
- `sugerir_nombre(documento, tipo)` → `str`. Lanza `ValueError` si el
  tipo no está en `TIPOS_CREABLES`.
- `rect_para_campo(tipo, rect, rect_pagina)` → `fitz.Rect`, según la
  tabla de tamaños: aplica el tamaño estándar si es un clic, hace
  cuadrada la casilla, recorta a `rect_pagina` y lanza `ValueError` si
  el resultado mide menos de 8 pt de ancho o de alto.
- `crear_campo(documento, num_pagina, tipo, nombre, rect, multilinea=False)`
  → el diccionario del campo nuevo, tal como lo devolvería
  `listar_campos` (se busca por nombre después de crearlo).
  - Valida el tipo y el nombre **antes** de tocar el documento; si algo
    no es válido, lanza `ValueError` con el mensaje en español y el
    documento queda igual.
  - Usa el `rect` tal como llega (el ajuste de tamaño es trabajo de
    `rect_para_campo`, que llama quien use esta función).
  - `multilinea=True` solo se permite con `tipo == "texto"`; con otro
    tipo, `ValueError`.
- **Pruebas** (`tests/test_crear_campos.py`, nuevo, con PDFs creados en
  memoria como en `tests/test_formularios.py`):
  - crear un campo de cada tipo, guardar con `tobytes()`, volver a abrir
    y comprobar con `listar_campos` el nombre, el tipo, la página y
    `multilinea`;
  - un campo de texto y una casilla creados se pueden llenar con
    `escribir_valor` y el valor persiste al reabrir;
  - `validar_nombre_nuevo`: vacío, con punto, de 61 caracteres, repetido
    y repetido con otras mayúsculas dan mensaje; uno válido da `""`;
  - `crear_campo` con nombre repetido, tipo inválido o `multilinea=True`
    en una casilla lanza `ValueError` y el documento no cambia (mismo
    número de widgets en la página);
  - `sugerir_nombre`: en un PDF vacío da `texto_1`; si ya existen
    `texto_1` y `texto_2`, da `texto_3`;
  - `rect_para_campo`: un clic da el tamaño estándar de cada tipo; la
    casilla arrastrada sale cuadrada; un cuadro que se sale de la página
    se recorta; un clic pegado al borde derecho lanza `ValueError`.

### Tarea 2 — `app/dialogo_nuevo_campo.py`: la ventana "Nuevo campo"

- `DialogoNuevoCampo(QDialog)` con:
  - `__init__(self, tipo, nombre_sugerido, multilinea_inicial, validar, parent=None)`,
    donde `validar` es una función `nombre -> mensaje` (en `main.py` será
    `lambda n: validar_nombre_nuevo(self.documento, n)`). Así el diálogo
    no depende del documento y se prueba solo.
  - Título "Nuevo campo de texto", "Nueva casilla" o "Nuevo campo de
    firma", según el tipo.
  - `QLineEdit` del nombre con el nombre sugerido ya seleccionado.
  - `QCheckBox` "Varias líneas", visible **solo** si el tipo es
    `"texto"`.
  - Una etiqueta en rojo con el mensaje de `validar`, que se actualiza
    al escribir (`textChanged`); el botón **Aceptar** queda
    deshabilitado mientras haya mensaje.
  - Botones Aceptar y Cancelar (`QDialogButtonBox`).
  - `obtener_valores()` → `(nombre_sin_espacios_al_inicio_ni_final, multilinea)`.
- **Pruebas** (`tests/test_dialogo_nuevo_campo.py`, offscreen; el
  diálogo se crea y se revisa sin llamar a `exec()`):
  - con tipo `"texto"` la casilla "Varias líneas" es visible y con
    `"casilla"` o `"firma"` no;
  - el nombre sugerido aparece en el campo;
  - con un `validar` que rechaza `"repetido"`: escribir `"repetido"`
    deshabilita Aceptar y muestra el mensaje; escribir otro nombre lo
    vuelve a habilitar y borra el mensaje;
  - `obtener_valores()` devuelve el nombre sin espacios al inicio ni al
    final y el estado de "Varias líneas".

### Tarea 3 — Conectar en `app/main.py` (👁️ validación visual)

- Agregar a `HERRAMIENTAS`, justo antes de "Editar contenido (texto e
  imagenes)": `"Crear campo de texto"`, `"Crear casilla"` y `"Crear
  campo de firma"`, cada una con su mensaje en `actualizar_ayuda`
  ("Arrastra un cuadro (o da un clic) donde quieras el campo…").
- En `al_seleccionar_rectangulo`, cuando la herramienta es una de las
  tres, se llama a un método nuevo `crear_campo_desde_seleccion(numero_pagina, rect_pdf, tipo)`
  **antes** del bloque de anotaciones y se sale con `return`. Estas
  herramientas no entran en el diccionario `descripcion_cambio` de las
  anotaciones.
- `crear_campo_desde_seleccion`:
  1. `rect_para_campo(...)`; si lanza `ValueError`, mensaje y salir.
  2. Abre `DialogoNuevoCampo` con `sugerir_nombre(...)` y "Varias
     líneas" marcada si `rect.height >= 40`. Si se cancela, salir sin
     registrar nada.
  3. Llama a `crear_campo_en_documento(numero_pagina, tipo, nombre, rect, multilinea)`.
- `crear_campo_en_documento` (separado del diálogo para poder probarlo
  sin ventanas modales): `registrar_cambio(f"Crear campo: {nombre}")`,
  `crear_campo(...)`; si falla, `_revertir_cambio_fallido()` y
  `QMessageBox.critical`. Si sale bien: `redibujar_pagina_individual`,
  `_recargar_panel_formularios()`, `_mostrar_panel_formularios(True)` y
  `panel_formularios.seleccionar(nombre)`. Devuelve `True` o `False`.
- **Pruebas** (`tests/test_main_crear_campos.py`, offscreen, con el estilo
  de `tests/test_main_formularios.py`):
  - en un PDF sin campos, `crear_campo_en_documento` crea un campo de
    texto: el documento lo tiene, el panel se muestra y lo lista, y la
    acción "Mostrar campos" queda habilitada;
  - después, `deshacer_cambio()` lo quita del documento y del panel, y
    `rehacer_cambio()` lo regresa;
  - con un nombre repetido devuelve `False`, el documento no cambia y no
    queda paso en Deshacer (con `QMessageBox.critical` sustituido por
    `monkeypatch`);
  - las tres herramientas nuevas están en el desplegable.
- **Validación visual de Diego:** abrir un PDF sin campos (por ejemplo
  una hoja de Word exportada a PDF), crear un campo de texto de una
  línea, uno multilínea, una casilla y una firma; llenarlos desde el
  panel; `Ctrl+Z` y `Ctrl+Y`; "Guardar como" y abrir el resultado en
  Chrome o Firefox para escribir en los campos.

### Tarea 4 — Documentación

- `README.md` (función "Crear campos de formulario"), `ROADMAP.md` (Fase
  5, parte 2 completada, con sus limitaciones), `BITACORA.md`, y marcar
  este diseño como completado.
- Limitaciones a documentar: solo texto, casilla y firma; no se mueven
  ni se renombran (se usa `Ctrl+Z`); la firma no se firma aquí; sin
  formato ni cálculos.

## 📝 Prompt para cada tarea

Abrir OpenCode en `/home/endoralex/Documentos/Proyectos/github/mi_adobe_editor`,
empezar con `/new`, modo **Build**, y pegar cambiando el número:

```
Lee AGENTS.md y DISENO_CREAR_CAMPOS.md. Haz SOLO la Tarea N, siguiendo el
diseño al pie de la letra. Usa nombres completos de enums de Qt en el
código nuevo. Al terminar corre pyright y pytest, agrega la entrada de la
sesión en BITACORA.md (fecha con date +%F), y dame un resumen de cada
archivo creado o modificado con números de línea. No preguntes si sigues.
```

# ↩️ Diseño — Deshacer y Rehacer

> **✅ COMPLETADO (Tareas 1–4, 2026-10-15).** Menú Editar con Ctrl+Z / Ctrl+Y,
> historial de copias en memoria, registro de cada cambio y documentación.
> Última corrección: si un cambio falla *después* de modificar el PDF, el
> documento se revierte (`_revertir_cambio_fallido`), no solo se descarta la
> copia.

> Documento de diseño de la función Deshacer/Rehacer de Mi-Adobe-PDF.
> Mismo método que `DISENO_EDITOR_TEXTO.md`: diseño primero, tareas
> pequeñas con pruebas, validación visual de Diego al final.

## 🎯 Objetivo

Hoy, si el usuario se equivoca (borra la página equivocada, edita mal un
párrafo, resalta de más), la única forma de regresar es cerrar sin guardar
y perder **todos** los cambios. Con esta función:

- **Deshacer (`Ctrl+Z`)** regresa el documento al estado anterior al
  último cambio, sin perder los cambios previos.
- **Rehacer (`Ctrl+Y`)** vuelve a aplicar lo que se deshizo.
- El menú dice **qué** se va a deshacer: "Deshacer: Rotar página".

## 🧱 Decisión técnica: copias del documento en memoria

Antes de cada cambio, el programa guarda una copia completa del documento
en memoria con `documento.tobytes()`. Deshacer = volver a abrir la copia
anterior con `fitz.open("pdf", copia)`.

- Es el método más simple y confiable con PyMuPDF: no hay que programar
  "cómo revertir" cada tipo de cambio por separado.
- **Límite de memoria:** máximo **20 pasos** y máximo **300 MB** en total
  entre todas las copias. Si se pasa, se descartan las copias más antiguas.

### Reglas del historial

1. Hacer un cambio nuevo **borra** la pila de Rehacer (igual que en Word).
2. Abrir otro documento o cerrar el documento **vacía** el historial.
3. Guardar **no** vacía el historial: se puede deshacer después de guardar.
4. Si una operación falla o el usuario la cancela **antes** de tocar el
   PDF, la copia se descarta (`descartar_ultimo`), para que Deshacer no
   "deshaga" algo que nunca pasó. Si falla **después** de haber
   modificado el documento (por ejemplo, al escribir el texto de la
   edición en línea), la copia se usa para **revertir** el cambio
   (`_revertir_cambio_fallido`: deshacer + restaurar + vaciar rehacer),
   porque descartar sola la copia dejaría el documento a medias.
5. **Documentos con contraseña:** Deshacer y Rehacer quedan **deshabilitados**.
   Motivo: las copias en memoria se guardan sin cifrar, y al guardar se
   perdería la contraseña del archivo. Se informa en la barra de estado.
6. **Mientras hay una edición de texto en línea abierta**, Deshacer y
   Rehacer del documento quedan deshabilitados; ahí `Ctrl+Z` deshace lo que
   se escribe dentro del cuadro (comportamiento propio de Qt).

### Qué cuenta como "cambio"

| Operación | Descripción en el menú |
|---|---|
| Resaltar, subrayar, tachar | "Resaltar", "Subrayar", "Tachar" |
| Texto libre, rectángulo, línea, círculo | "Texto libre", "Rectángulo", etc. |
| Firma (imagen) | "Firma" |
| Aceptar una edición de texto en línea | "Editar texto" |
| Reemplazar / eliminar imagen | "Reemplazar imagen" / "Eliminar imagen" |
| Cambiar color de forma | "Cambiar color de forma" |
| Rotar, eliminar, insertar página | "Rotar página", "Eliminar página", "Insertar página" |
| Reordenar páginas | "Reordenar páginas" |

**No** cuentan (no modifican el documento abierto, crean archivos nuevos):
unir, dividir, exportar a imágenes, comprimir, poner/quitar contraseña,
convertir a Word, OCR, guardar como.

## 🗂️ Organización del código

| Archivo | Contenido | ¿Necesita ventana para probarse? |
|---|---|---|
| `app/historial.py` (nuevo) | Clase `HistorialCambios`: pilas, límites, deshacer, rehacer | No |
| `app/main.py` | Menú "Editar", atajos, registrar cada cambio, restaurar el documento | Sí (modo offscreen) |

## 📋 Tareas (en orden, una por sesión de OpenCode)

### Tarea 1 ✅ — `app/historial.py`

- Clase `HistorialCambios(limite_pasos=20, limite_bytes=300 * 1024 * 1024)`.
- `registrar(documento, descripcion)`: guarda `documento.tobytes()` con su
  descripción en la pila de deshacer, vacía la de rehacer y aplica los
  límites (descarta las copias más antiguas).
- `descartar_ultimo()`: quita la última copia registrada (regla 4).
- `deshacer(documento_actual)` → devuelve un `fitz.Document` nuevo con el
  estado anterior y guarda el estado actual en la pila de rehacer, con la
  misma descripción. Devuelve `None` si no hay nada que deshacer.
- `rehacer(documento_actual)` → lo inverso. `None` si no hay nada.
- `puede_deshacer()`, `puede_rehacer()`, `descripcion_deshacer()`,
  `descripcion_rehacer()`, `vaciar()`.
- **Pruebas** (`tests/test_historial.py`, sin Qt): registrar 3 cambios y
  deshacer 3 veces regresa al original; un cambio nuevo vacía rehacer; con
  `limite_pasos=2`, al registrar 3 solo se pueden deshacer 2; con un
  `limite_bytes` pequeño se descartan las copias antiguas;
  `descartar_ultimo` funciona; las descripciones son correctas.
- Actualizar en `AGENTS.md` la línea "Plan vigente" a `DISENO_DESHACER.md`.

### Tarea 2 ✅ — Menú Editar y restaurar el documento

- En `EditorPDF`: un `HistorialCambios`, un menú **"Editar"** (entre
  Archivo y Páginas) con **Deshacer** (`QKeySequence.StandardKey.Undo`) y
  **Rehacer** (`QKeySequence.StandardKey.Redo`).
- Las acciones muestran la descripción ("Deshacer: Rotar página") y se
  deshabilitan cuando no hay nada, cuando el documento tiene contraseña, o
  cuando hay una edición en línea abierta (reglas 5 y 6).
- Método `registrar_cambio(descripcion)` que llaman las operaciones.
- Al deshacer/rehacer: reemplazar `self.documento`, redibujar todas las
  páginas, conservar `pagina_actual` (ajustada si ya no existe), volver a
  dibujar los recuadros si la herramienta "Editar contenido" está activa,
  y mostrar en la barra de estado "Deshecho: …" / "Rehecho: …".
- Vaciar el historial al abrir y al cerrar documento (regla 2).
- **Pruebas** (offscreen): rotar una página con `registrar_cambio` antes,
  deshacer → rotación 0; rehacer → rotación 90; abrir otro documento vacía
  el historial; con un PDF con contraseña las acciones están deshabilitadas.

### Tarea 3 ✅ — Registrar cada operación (👁️ validación visual)

- Llamar `registrar_cambio(...)` **antes** de cada operación de la tabla
  "Qué cuenta como cambio", y `historial.descartar_ultimo()` si la
  operación falla o el usuario la cancela.
- **Pruebas** (offscreen): resaltar → deshacer quita la anotación; eliminar
  una página → deshacer la regresa; aceptar una edición de texto en línea →
  deshacer regresa el texto original; cancelar un diálogo no deja una copia
  de más en el historial.
- **Validación visual de Diego:** hacer 4 cambios distintos, deshacer los 4
  con `Ctrl+Z` revisando que cada uno regresa, rehacer 2 con `Ctrl+Y`, y
  confirmar que el menú Editar muestra la descripción correcta.

### Tarea 4 ✅ — Documentación

- `README.md` (checklist y estado), `ROADMAP.md` (Fase 8 u otra que
  corresponda), `BITACORA.md`, y marcar este diseño como completado.
- Documentar las limitaciones: 20 pasos / 300 MB; deshabilitado en PDFs
  con contraseña.

## 📝 Prompt para cada tarea

Abrir OpenCode Desktop en `D:\GITHUB\mi_adobe_editor`, empezar con `/new`
y pegar, cambiando el número:

```
Lee AGENTS.md y DISENO_DESHACER.md. Haz SOLO la Tarea N, siguiendo el
diseño al pie de la letra. Usa nombres completos de enums de Qt en el
código nuevo. Al terminar corre pyright y pytest, agrega la entrada de la
sesión en BITACORA.md (fecha con Get-Date), y dame un resumen de cada
archivo creado o modificado con números de línea. No preguntes si sigues.
```

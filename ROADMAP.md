# 🗺️ Roadmap — Mi-Adobe-PDF

Cada fase es una entrega funcional. No pasamos a la siguiente hasta que la actual funcione.

## Fase 1 — Visor de PDF ✅ (completado)
- Ventana con menú (Archivo, Editar, Ver)
- Abrir un PDF y mostrarlo en pantalla
- Scroll continuo (se cambió el plan original de botones siguiente/anterior)
- Zoom +/-

## Fase 2 — Anotaciones ✅ (completado)
- Resaltar, subrayar, tachar texto
- Agregar texto libre sobre la página
- Dibujar formas (rectángulo, círculo, línea)
- Firma por imagen (se carga un PNG/JPG y se coloca arrastrando un cuadro)
- [ ] Pendiente: notas/comentarios tipo "sticky note", sello/timbre

## Fase 3 — Edición de páginas ✅ (completado)
- Unir varios PDFs en uno
- Dividir un PDF en varios archivos
- Eliminar y rotar páginas
- Insertar páginas en blanco
- Reordenar páginas (cuadrícula de miniaturas + botones de mover)
- [x] Extraer páginas sueltas → se logra con "Dividir PDF" (guarda una página por archivo)

## Fase 4 — Edición de texto real (la parte difícil) ✅ (completado)
- [x] Detectar bloques de texto existentes (se agrupan en "párrafos" leyendo las líneas reales)
- [x] Editar el contenido de esos bloques (tapar lo viejo con el color de fondo y escribir lo nuevo)
- [x] Cambiar tamaño y color del texto (elige tamaño, color, negrita y cursiva en el diálogo)
- [x] Bonus: también edita **imágenes** (reemplazar/eliminar) y **formas de color** (recuadros de colores: azul = texto, verde = imagen, naranja = forma)
- (Limitación técnica real: los PDFs no son documentos "de flujo" como Word,
  así que la edición es por bloques/cajas de texto, sin reflujo de párrafos.
  Funciona bien para cambios cortos: precios, fechas, nombres.)

## Fase 5 — Formularios (sin empezar)
- Detectar campos de formulario existentes y rellenarlos
- Crear campos de formulario nuevos (texto, checkbox, firma)
- [ ] Pendiente: es la siguiente fase en la lista

## Fase 6 — OCR y conversión (parcialmente completado)
- [x] OCR de PDFs escaneados (ocrmypdf + Tesseract, español e inglés)
- [x] Exportar PDF a Word (.docx) con `pdf2docx`
- [x] Exportar páginas a imágenes (PNG)
- [ ] Pendiente: exportar a Excel (.xlsx) si hay tablas
- [ ] Pendiente: importar imágenes/Word y convertir a PDF

## Fase 7 — Seguridad (parcialmente completado)
- [x] Poner y quitar contraseña (AES-256)
- [x] Firma por imagen (no criptográfica)
- [ ] Pendiente: redacción permanente (tachar y eliminar datos de verdad, no solo visualmente)
- [ ] Pendiente: firma digital con certificado

## Fase 8 — Optimización y pulido ✅ (empaquetado hecho, probado en Linux)
- [x] Empaquetado con PyInstaller (`--windowed --onedir`), probado y funcionando en Linux sin necesitar Python/venv
- [x] Documentado en `EMPAQUETADO.md`: pasos para Linux Y Windows, ícono/lanzador de escritorio
- [x] Documentado el manejo de Windows Defender/SmartScreen (por qué pasa, cómo desbloquear, por qué usamos `--onedir` en vez de `--onefile`)
- [x] Comprimir PDFs pesados desde el menú Herramientas → "Comprimir PDF..."
- [ ] Pendiente: generar y probar el `.exe` en una PC con Windows de verdad (esto no se puede hacer desde Linux)
- [ ] Pendiente: ícono propio del programa (por ahora usa el ícono genérico de PDF)

## Fase 9 — Documentación final para portafolio
- Manual de usuario
- Capturas de pantalla de cada función
- Video demo corto
- README final pulido para GitHub

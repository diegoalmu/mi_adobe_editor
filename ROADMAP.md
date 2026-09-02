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
- [ ] Pendiente: notas/comentarios tipo "sticky note", sello/timbre e imágenes

## Fase 3 — Edición de páginas ✅ (completado)
- Unir varios PDFs en uno
- Dividir un PDF en varios archivos
- Eliminar y rotar páginas
- Reordenar páginas (cuadrícula de miniaturas + botones de mover)
- [ ] Pendiente: extraer páginas sueltas como función independiente (ahora mismo se logra con "Dividir")

## Fase 4 — Edición de texto real (la parte difícil)
- Detectar bloques de texto existentes
- Editar el contenido de esos bloques
- Cambiar fuente, tamaño y color
- (Limitación técnica real: PDFs no son documentos "de flujo" como Word,
  así que la edición será por bloques/cajas de texto, no reflujo de párrafos)

## Fase 5 — Formularios
- Detectar campos de formulario existentes y rellenarlos
- Crear campos de formulario nuevos (texto, checkbox, firma)

## Fase 6 — OCR y conversión
- OCR de PDFs escaneados (Tesseract)
- Exportar PDF a Word (.docx)
- Exportar PDF a Excel (.xlsx) si hay tablas
- Exportar páginas a imágenes (PNG/JPG)
- Importar imágenes/Word y convertir a PDF

## Fase 7 — Seguridad
- Poner y quitar contraseña
- Redacción permanente (tachar y eliminar datos de verdad, no solo visualmente)
- Firma digital con certificado o imagen de firma

## Fase 8 — Optimización y pulido
- Comprimir PDFs pesados
- Instalador para Windows (.exe) y paquete para Linux
- Ícono y nombre propio del programa
- Empaquetado final con PyInstaller
- ⚠️ **Importante:** al generar el `.exe`, Windows Defender/SmartScreen puede
  marcarlo como "app desconocida y potencialmente peligrosa" (esto ya le pasó
  antes al autor con otro proyecto). Hay que documentar bien cómo empaquetar
  con PyInstaller de forma más "confiable" (evitar el modo `--onefile` cuando
  sea posible, usar `--noconsole` correctamente, y explicar el proceso de
  desbloqueo manual en Windows Defender como plan B) para que no sea una
  sorpresa la primera vez que se ejecute en una PC con Windows.

## Fase 9 — Documentación final para portafolio
- Manual de usuario
- Capturas de pantalla de cada función
- Video demo corto
- README final pulido para GitHub

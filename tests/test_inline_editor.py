import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import fitz
from PySide6.QtWidgets import QApplication

def run_test():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from app.main import EditorPDF, EditorTextoInline

    # 1. Crear PDF de prueba
    ruta_pdf = os.path.abspath("test_sample.pdf")
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    page.insert_text((100, 150), "Precio Original: $100", fontsize=14, fontname="helv", color=(0, 0, 0))
    doc.save(ruta_pdf)
    doc.close()

    print("[1] PDF de prueba creado:", ruta_pdf)

    # 2. Iniciar ventana y abrir PDF
    editor = EditorPDF()
    editor.documento = fitz.open(ruta_pdf)
    editor.ruta_actual = ruta_pdf
    editor.pagina_actual = 0
    editor.dibujar_todas_las_paginas()
    print("[2] PDF cargado en EditorPDF, paginas:", len(editor.etiquetas_paginas))

    # 3. Cambiar a herramienta de edicion de contenido
    editor.combo_herramienta.setCurrentText("Editar contenido (texto e imagenes)")
    assert not editor.barra_formato.isHidden(), "La barra de formato no debe estar oculta"
    print("[3] Barra de formato visible correctamente")

    # 4. Encontrar parrafo
    pagina = editor.documento[0]
    parrafos = editor.obtener_todos_los_parrafos(pagina)
    assert len(parrafos) > 0, "Debe detectar al menos un parrafo"
    parrafo = parrafos[0]
    print("[4] Parrafo detectado:", parrafo["texto"])

    # 5. Iniciar edicion inline
    editor.editar_parrafo_encontrado(pagina, parrafo)
    assert editor.edicion_inline_activa is not None, "Debe haber una edicion inline activa"
    widget_inline = editor.edicion_inline_activa["widget"]
    assert isinstance(widget_inline, EditorTextoInline), "El widget debe ser EditorTextoInline"
    assert widget_inline.toPlainText() == "Precio Original: $100"
    print("[5] EditorTextoInline abierto con texto correcto:", widget_inline.toPlainText())

    # 6. Modificar texto y formato
    widget_inline.setPlainText("Precio Actualizado: $250")
    editor.spin_tamano.setValue(16.0)
    editor.btn_negrita.setChecked(True)

    # 7. Aplicar edicion inline
    editor.aplicar_edicion_inline()
    assert editor.edicion_inline_activa is None, "La edicion inline debe haber finalizado"
    print("[6] Edicion aplicada con exito")

    # 8. Verificar contenido en el PDF
    texto_extraido = editor.documento[0].get_text()
    print("[7] Texto extraido tras edicion:", repr(texto_extraido))
    assert "Precio Actualizado: $250" in texto_extraido, "El texto actualizado debe estar en el PDF"
    assert "Precio Original: $100" not in texto_extraido, "El texto original debe haber sido reemplazado"

    # Limpieza
    editor.documento.close()
    if os.path.exists(ruta_pdf):
        os.remove(ruta_pdf)

    print("\n[OK] TODAS LAS PRUEBAS DE EDICION INLINE PASARON EXITOSAMENTE.")

if __name__ == "__main__":
    run_test()

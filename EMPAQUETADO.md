# 📦 Empaquetar como ejecutable independiente (Linux y Windows)

Esto genera un programa que se abre con doble clic, **sin necesitar Python,
sin activar ningún `venv`, sin terminal**. Se probó y funciona.

## Cómo funciona (para que lo entiendas, no es magia)

`PyInstaller` empaqueta tu código Python + el interprete de Python + todas
las librerías (PySide6, PyMuPDF, etc.) en una sola carpeta que se basta a
sí misma. Por eso pesa varios cientos de MB — lleva todo adentro.

**Importante:** el ejecutable que generes en Linux solo sirve para Linux,
y el que generes en Windows solo sirve para Windows. No se puede "generar
el .exe desde Linux" de forma confiable — cada uno se genera en su propio
sistema operativo.

---

## 🐧 Generarlo en Linux Mint

### Paso 1 — Instalar PyInstaller en tu proyecto

```bash
cd ~/Documentos/GitHub/mi_adobe_editor
source venv/bin/activate
pip install pyinstaller
```

### Paso 2 — Generar el ejecutable

```bash
pyinstaller --name mi_adobe_editor --windowed --onedir \
  --collect-all pymupdf \
  --collect-all pdf2docx \
  --collect-all ocrmypdf \
  app/main.py
```

**Qué hace cada parte:**
- `--name mi_adobe_editor`: como se va a llamar el programa final.
- `--windowed`: no abre una ventana de terminal negra detrás, solo tu programa.
- `--onedir`: mete todo en una CARPETA (en vez de un solo archivo gigante).
  Es más rápido de abrir y es la forma que recomienda PyInstaller para
  programas con interfaz gráfica.
- `--collect-all pymupdf/pdf2docx/ocrmypdf`: le dice explícitamente que
  incluya TODOS los archivos internos de esas 3 librerías (a veces
  PyInstaller no detecta automáticamente todo lo que usan).

Esto tarda 1-3 minutos. Al terminar, tu programa queda en:

```
dist/mi_adobe_editor/mi_adobe_editor
```

### Paso 3 — Probarlo

```bash
./dist/mi_adobe_editor/mi_adobe_editor
```

Debería abrirse la ventana del editor, igual que con `python app/main.py`,
pero esta vez sin necesitar el `venv` activado.

> Si te da el mismo error de `libxcb-cursor` que la primera vez que
> instalamos el programa, es porque esa carpeta se movió a una máquina que
> no tiene esa librería del sistema instalada. Solución (una sola vez por
> máquina): `sudo apt install libxcb-cursor0 -y`

### Paso 4 — Crear un ícono para abrirlo con doble clic desde el menú

Crea este archivo:

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/mi-adobe-editor.desktop << 'EOF'
[Desktop Entry]
Name=Mi Adobe Editor
Comment=Editor de PDF propio
Exec=/home/endoralex/Documentos/GitHub/mi_adobe_editor/dist/mi_adobe_editor/mi_adobe_editor
Icon=application-pdf
Terminal=false
Type=Application
Categories=Office;
EOF
```

**Qué hace:** crea un "lanzador" que Linux Mint reconoce como una aplicación
normal. Después de esto, busca "Mi Adobe Editor" en el menú de aplicaciones
(como buscarías cualquier otro programa) y podrás abrirlo desde ahí, o
anclarlo a la barra de tareas.

> Nota: la ruta en `Exec=` debe ser la ruta completa y exacta donde quedó
> el ejecutable en TU máquina. Si algún día mueves la carpeta del proyecto,
> hay que actualizar esta línea.

### Cómo distribuirlo a otra PC con Linux

Comprime toda la carpeta `dist/mi_adobe_editor/` (con `zip -r` o el
compresor de archivos de Linux Mint) y pásala a la otra máquina. Ahí
solo se descomprime y se ejecuta `./mi_adobe_editor` — no necesita
instalar Python ni nada, siempre que sea una versión de Linux
razonablemente similar (Ubuntu/Mint/Debian recientes).

---

## 🪟 Generarlo en Windows

Esto se debe hacer **en una PC con Windows** (no se puede generar el
`.exe` desde Linux de forma confiable). Los pasos son casi idénticos:

### Paso 1 — Preparar el proyecto en Windows

Sigue primero tu guía `INSTALACION_WINDOWS.md` para tener Python, el
`venv`, y `pip install -r requirements.txt` funcionando ahí. Luego:

```powershell
pip install pyinstaller
```

### Paso 2 — Generar el .exe

```powershell
pyinstaller --name mi_adobe_editor --windowed --onedir --collect-all pymupdf --collect-all pdf2docx --collect-all ocrmypdf app/main.py
```

(Es el mismo comando, todo en una sola línea porque PowerShell no siempre
acepta bien el `\` para continuar en varias líneas).

El resultado queda en `dist\mi_adobe_editor\mi_adobe_editor.exe`.

### ⚠️ Sobre Windows Defender / SmartScreen (esto YA te pasó antes)

La primera vez que alguien ejecute este `.exe` en una PC con Windows,
es **muy probable** que salga una pantalla azul de SmartScreen diciendo
"Windows protegió su PC" — esto NO significa que el programa tenga un
virus, significa que Windows no "conoce" el programa porque no está
firmado digitalmente (firmar cuesta dinero y requiere un certificado de
una empresa verificadora).

**Cómo abrirlo de todas formas:**
1. En la pantalla de SmartScreen, dale clic a **"Más información"**.
2. Va a aparecer un botón **"Ejecutar de todas formas"** — dale clic ahí.

Esto solo hace falta la primera vez en cada PC nueva donde lo instales.

**Por qué usamos `--onedir` y no `--onefile`:** el modo `--onefile` (un
solo `.exe` gigante) es más propenso a que los antivirus lo marquen como
sospechoso, porque tiene que "descomprimirse a sí mismo" en una carpeta
temporal cada vez que se abre, y eso se parece al comportamiento de un
virus. `--onedir` (carpeta con el .exe + sus archivos) es más confiable
y además abre más rápido.

### Crear un acceso directo en el Escritorio

1. Ve a la carpeta `dist\mi_adobe_editor\`.
2. Click derecho sobre `mi_adobe_editor.exe` → **Crear acceso directo**.
3. Mueve ese acceso directo al Escritorio o anclalo a la barra de tareas.

### Cómo distribuirlo a otra PC con Windows

Comprime la carpeta completa `dist\mi_adobe_editor\` en un `.zip`, pásala
a la otra PC (USB, nube, lo que sea), se descomprime ahí, y se ejecuta el
`.exe` de adentro. No necesita tener Python instalado.

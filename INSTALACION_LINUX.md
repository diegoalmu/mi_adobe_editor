# 🐧 Instalación en Linux — paso a paso

Comandos probados para distribuciones basadas en Debian/Ubuntu (las más comunes).
Si usas otra (Fedora, Arch, etc.) dime cuál y te doy los comandos exactos.

## Paso 1 — Verificar/instalar Python

La mayoría de distribuciones Linux ya traen Python. Verifica la versión:

```bash
python3 --version
```

Explicación: pregunta qué versión de Python 3 está instalada. Necesitamos 3.10 o superior.

Si no está instalado o es muy viejo:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

Explicación:
- `sudo apt update`: actualiza la lista de programas disponibles para instalar.
- `sudo apt install ... -y`: instala Python 3, su instalador de paquetes (`pip`) y
  el módulo para crear entornos virtuales (`venv`). El `-y` responde "sí" automáticamente
  a la confirmación.

## Paso 2 — Instalar Visual Studio Code

```bash
sudo apt update
sudo apt install snapd -y
sudo snap install code --classic
```

Explicación: instala VS Code usando Snap (el gestor de paquetes universal de Ubuntu).
Alternativa: puedes descargar el `.deb` directamente desde https://code.visualstudio.com/
y hacer doble clic para instalarlo.

## Paso 3 — Abrir la carpeta del proyecto

```bash
cd ruta/donde/guardaste/mi-adobe-pdf
code .
```

Explicación: `cd` (change directory) te mueve a la carpeta del proyecto,
y `code .` abre VS Code justo ahí. Luego abre la terminal integrada con
`Terminal` → `Nueva terminal`.

## Paso 4 — Crear el entorno virtual

```bash
python3 -m venv venv
```

Explicación: crea una carpeta `venv` con una copia aislada de Python solo para este proyecto.

**Activarlo:**

```bash
source venv/bin/activate
```

Explicación: activa el entorno aislado. Verás `(venv)` al inicio de la línea de comandos.
Debes hacer esto cada vez que abras una terminal nueva para trabajar en el proyecto.

## Paso 5 — Instalar las librerías

```bash
pip install -r requirements.txt
```

Explicación: instala automáticamente `PySide6` (interfaz gráfica) y `PyMuPDF` (motor de PDF),
que están listadas en el archivo `requirements.txt`.

> Si al ejecutar el programa más adelante da error relacionado con "libxcb" o pantalla,
> instala estas dependencias del sistema (comunes en Linux para apps gráficas Qt):
> ```bash
> sudo apt install libxcb-cursor0 libxkbcommon-x11-0 -y
> ```

## Paso 5.5 — Dependencias del sistema para OCR

La función de OCR (hacer buscable un PDF escaneado) necesita dos programas del
sistema (no son librerías de Python, por eso no basta con `pip install`):

```bash
sudo apt install tesseract-ocr tesseract-ocr-spa ghostscript -y
```

**Qué hace:**
- `tesseract-ocr`: el motor que "lee" el texto dentro de las imágenes.
- `tesseract-ocr-spa`: el paquete de idioma español para ese motor (sin esto,
  solo reconocería bien texto en inglés).
- `ghostscript`: herramienta que usa `ocrmypdf` por dentro para procesar las
  páginas del PDF.

## Paso 6 — Ejecutar el programa

```bash
python app/main.py
```

## Paso 7 — Subir el proyecto a GitHub

```bash
sudo apt install git -y
git init
git add .
git commit -m "Inicio del proyecto: visor de PDF basico (Fase 1)"
```

Explicación:
- `git init`: convierte la carpeta en repositorio Git.
- `git add .`: prepara todos los archivos para guardarse.
- `git commit -m "..."`: guarda el estado actual del proyecto con una descripción.

Crea el repositorio vacío en https://github.com/new (nómbralo `mi-adobe-pdf`), luego:

```bash
git remote add origin https://github.com/TU-USUARIO/mi-adobe-pdf.git
git branch -M main
git push -u origin main
```

Explicación:
- `git remote add origin ...`: conecta tu carpeta local con el repositorio en GitHub.
- `git branch -M main`: nombra la rama principal "main".
- `git push -u origin main`: sube el proyecto completo a GitHub.

## Nota sobre trabajar en ambos sistemas (Windows y Linux)

Como quieres usarlo en los dos sistemas, la recomendación es:
1. Trabaja el código en uno de los dos (el que uses más) y súbelo a GitHub.
2. En el otro sistema, en vez de crear el proyecto de nuevo, usa:
   ```bash
   git clone https://github.com/TU-USUARIO/mi-adobe-pdf.git
   ```
   Esto descarga una copia idéntica del proyecto. Luego solo repites desde el
   Paso 4 (crear y activar entorno virtual) de la guía correspondiente a ese sistema.

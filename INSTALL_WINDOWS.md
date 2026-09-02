# 🪟 Instalación en Windows — paso a paso

Sigue los pasos EN ORDEN. Cada comando se escribe en **PowerShell** o en la terminal
integrada de VS Code (te explico cuál abrir).

## Paso 1 — Instalar Python

1. Ve a https://www.python.org/downloads/
2. Descarga la última versión (botón grande amarillo "Download Python 3.x.x").
3. Ejecuta el instalador descargado.
4. **MUY IMPORTANTE**: en la primera pantalla del instalador, marca la casilla
   `Add python.exe to PATH` (abajo del todo) ANTES de darle a "Install Now".
   Si no marcas esto, Windows no reconocerá el comando `python` después.
5. Dale a "Install Now" y espera a que termine.

**Verificar que se instaló bien:**
Abre PowerShell (busca "PowerShell" en el menú inicio) y escribe:

```powershell
python --version
```

Explicación: este comando le pregunta a Windows "¿tienes Python instalado y qué versión?".
Debe responder algo como `Python 3.12.4`. Si dice que no reconoce el comando,
Python no quedó bien instalado o falta reiniciar la terminal/PC.

## Paso 2 — Instalar Visual Studio Code (el editor donde escribiremos y correremos el código)

1. Ve a https://code.visualstudio.com/
2. Descarga la versión para Windows e instálala (siguiente, siguiente, instalar).
3. Ábrelo una vez instalado.

## Paso 3 — Abrir la carpeta del proyecto en VS Code

1. En VS Code: `Archivo` → `Abrir carpeta...`
2. Selecciona la carpeta `mi-adobe-pdf` que descargaste/creaste.
3. Abre la terminal integrada: menú `Terminal` → `Nueva terminal`.
   (A partir de aquí, todos los comandos se escriben en esa terminal, dentro de VS Code).

## Paso 4 — Crear un "entorno virtual" (una caja aislada solo para este proyecto)

```powershell
python -m venv venv
```

Explicación: esto crea una carpeta llamada `venv` con una copia aislada de Python
solo para este proyecto. Así las librerías que instalemos no se mezclan con
otros programas de tu PC.

**Activar el entorno virtual** (hay que hacerlo cada vez que abras el proyecto):

```powershell
.\venv\Scripts\Activate.ps1
```

Explicación: "activa" esa caja aislada. Sabrás que funcionó porque a la izquierda
de la línea de comandos aparecerá `(venv)`.

> ⚠️ Si PowerShell te da un error de "ejecución de scripts deshabilitada", ejecuta primero
> este comando (una sola vez) y acepta con "S" o "Y":
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

## Paso 5 — Instalar las librerías del proyecto

Con el entorno virtual activado (debe verse `(venv)` a la izquierda), ejecuta:

```powershell
pip install -r requirements.txt
```

Explicación: `pip` es el "instalador de paquetes" de Python. Este comando lee el
archivo `requirements.txt` (que ya está en el proyecto) y descarga/instala
automáticamente todas las librerías necesarias: `PySide6` (interfaz gráfica)
y `PyMuPDF` (motor de PDF).

## Paso 6 — Ejecutar el programa

```powershell
python app/main.py
```

Explicación: le dice a Python "ejecuta el archivo main.py dentro de la carpeta app".
Debería abrirse la ventana del programa.

## Paso 7 — Subir el proyecto a GitHub (para tu portafolio)

1. Instala Git: https://git-scm.com/download/win (siguiente, siguiente, instalar).
2. En la terminal de VS Code (dentro de la carpeta del proyecto):

```powershell
git init
git add .
git commit -m "Inicio del proyecto: visor de PDF basico (Fase 1)"
```

Explicación:
- `git init`: convierte la carpeta en un repositorio de Git (empieza a llevar historial de cambios).
- `git add .`: marca todos los archivos actuales para guardarlos en el historial.
- `git commit -m "..."`: guarda una "fotografía" del proyecto en este punto, con un mensaje describiendo qué se hizo.

3. Crea un repositorio vacío en https://github.com/new (ponle nombre `mi-adobe-pdf`, no marques
   ninguna opción adicional).
4. GitHub te mostrará unos comandos parecidos a estos (usa los que a TI te muestre GitHub,
   con tu usuario):

```powershell
git remote add origin https://github.com/TU-USUARIO/mi-adobe-pdf.git
git branch -M main
git push -u origin main
```

Explicación:
- `git remote add origin ...`: le dice a Git dónde está tu repositorio en línea (GitHub).
- `git branch -M main`: nombra la rama principal "main".
- `git push -u origin main`: sube todos tus archivos y el historial a GitHub.

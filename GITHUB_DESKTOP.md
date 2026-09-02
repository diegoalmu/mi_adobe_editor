# 🖥️ Publicar el proyecto con GitHub Desktop (Linux Mint)

GitHub no ofrece oficialmente "GitHub Desktop" para Linux, pero existe una versión
mantenida por la comunidad (`shiftkey/desktop`) que funciona igual de bien.
La forma más fácil de instalarla en Linux Mint es con **Flatpak**.

## Paso 1 — Verificar/instalar Flatpak

Linux Mint casi siempre ya trae Flatpak. Verifica:

```bash
flatpak --version
```

**Qué hace:** pregunta si Flatpak (un gestor de aplicaciones) está instalado.

Si te da error de "comando no encontrado", instálalo con:

```bash
sudo apt update
sudo apt install flatpak -y
```

Después reinicia la sesión (cerrar y volver a entrar) para que quede bien configurado.

## Paso 2 — Agregar la tienda Flathub (si no la tienes)

```bash
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

**Qué hace:** agrega "Flathub", que es como la tienda de aplicaciones de donde
Flatpak descarga los programas. `--if-not-exists` evita error si ya la tenías agregada.

## Paso 3 — Instalar GitHub Desktop

```bash
flatpak install flathub io.github.shiftey.Desktop -y
```

**Qué hace:** descarga e instala la versión de GitHub Desktop para Linux
mantenida por la comunidad. Puede tardar unos minutos.

## Paso 4 — Abrir GitHub Desktop

Búscalo en tu menú de aplicaciones como **"GitHub Desktop"**, o desde terminal:

```bash
flatpak run io.github.shiftey.Desktop
```

## Paso 5 — Iniciar sesión con tu cuenta de GitHub

1. Al abrir la app, dale a **"Sign in to GitHub.com"**.
2. Se abrirá tu navegador para autorizar el acceso. Inicia sesión con tu cuenta.
3. Vuelve a la app de GitHub Desktop, debería reconocer que ya iniciaste sesión.

(Si no tienes cuenta de GitHub, créala gratis en https://github.com/signup antes de este paso.)

## Paso 6 — Agregar tu proyecto ya existente

Como tu carpeta `mi-adobe-pdf` ya existe en `~/Documentos/mi-adobe-pdf` pero
todavía no es un repositorio Git:

1. En GitHub Desktop: `File` → `Add local repository...`
2. En "Local path", pon o navega hasta: `/home/endoralex/Documentos/mi-adobe-pdf`
3. Como esa carpeta aún no es un repositorio Git, la app te va a mostrar un aviso
   con un botón que dice algo como **"create a repository here instead"** —
   dale clic ahí.
4. Te pedirá:
   - **Name**: `mi-adobe-pdf`
   - **Description** (opcional): `Editor de PDF propio (visor por ahora), alternativa gratuita a Adobe Acrobat Pro DC`
   - Verifica que el `.gitignore` seleccionado sea el que ya tienes en tu carpeta
     (o déjalo en "None" ya que tu proyecto ya trae su propio `.gitignore`).
5. Dale a **"Create Repository"**.

## Paso 7 — Hacer tu primer "commit" (guardar una fotografía del proyecto)

1. En la columna izquierda de GitHub Desktop verás la lista de todos los
   archivos del proyecto marcados con un check (listos para guardar).
2. Abajo a la izquierda hay dos cajas de texto:
   - **Summary** (obligatorio): escribe algo como
     `Fase 1: visor de PDF funcionando en Linux Mint`
   - **Description** (opcional): puedes pegar un resumen, por ejemplo
     "Se probó exitosamente en Linux Mint, se corrigió dependencia libxcb-cursor0"
3. Dale clic al botón azul **"Commit to main"**.

**Qué es un "commit":** es como guardar una fotografía del estado actual de
tu proyecto, con una nota explicando qué cambió. Vas a hacer un commit nuevo
cada vez que avancemos una fase o hagamos un cambio importante.

## Paso 8 — Publicar el repositorio en GitHub (subirlo a internet)

1. Arriba, en la barra superior de GitHub Desktop, verás un botón que dice
   **"Publish repository"**.
2. Te preguntará:
   - **Name**: puedes dejar `mi-adobe-pdf`
   - **Description** (opcional)
   - Casilla **"Keep this code private"**: márcala si NO quieres que sea público
     todavía (recomendado mientras el proyecto está muy inicial), o desmárcala
     si quieres que cualquiera lo vea desde ya (bueno para portafolio).
3. Dale clic en **"Publish Repository"**.

¡Listo! Esto crea el repositorio en tu cuenta de GitHub (en
`https://github.com/TU-USUARIO/mi-adobe-pdf`) y sube todos los archivos actuales.

## De aquí en adelante (flujo normal de trabajo)

Cada vez que hagamos cambios en el proyecto (nuevas fases, código nuevo):

1. Abre GitHub Desktop.
2. Verás los archivos que cambiaron en la lista de la izquierda.
3. Escribe un resumen corto de qué cambió (Summary).
4. Dale a **"Commit to main"**.
5. Dale clic a **"Push origin"** (arriba) para subir esos cambios a GitHub.

## Nota sobre Obsidian

Como vas a leer/editar los `.md` con Obsidian: puedes abrir directamente la
carpeta `~/Documentos/mi-adobe-pdf` como una "bóveda" (vault) de Obsidian
(`Abrir carpeta como bóveda`). Así ves el `README.md`, `ROADMAP.md` y
`BITACORA.md` con su formato bonito, y GitHub Desktop se encarga de
la parte de respaldo/versión sin que se interpongan entre sí — son dos
programas trabajando sobre la misma carpeta sin conflicto.

#!/usr/bin/env bash
# Arranca Mi-Adobe-PDF en Linux usando el entorno virtual del proyecto.
cd "$(dirname "$0")"
exec venv/bin/python app/main.py "$@"

#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# Crear venv si no existe
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Activar venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar una corrida de ejemplo (CPU, 20s, offline Argentina)
python measure.py --task cpu --seconds 20 --mode offline --country ARG --project TP_Green_Software --output results --interval 1

echo "Listo. Mirá la carpeta results/"

\
@echo off
setlocal enabledelayedexpansion
REM Ir a la raíz del proyecto
cd /d %~dp0
cd ..

REM Crear venv si no existe
if not exist .venv (
  python -m venv .venv
)

REM Activar venv
call .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

REM Ejecutar una corrida de ejemplo (CPU, 20s, offline Argentina)
python measure.py --task cpu --seconds 20 --mode offline --country ARG --project TP_Green_Software --output results --interval 1

echo Listo. Revisá la carpeta results\
pause

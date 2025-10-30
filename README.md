<<<<<<< HEAD
# TP Green Software — Alternativa 2 (Python + CodeCarbon)

Este paquete contiene lo necesario para medir el consumo de energía y las emisiones de CO₂eq
de un bloque de código en Python utilizando la librería **[codecarbon]**.


## Estructura
```
tp_green_software_codecarbon/
├─ measure.py                 # Script principal (CLI) para ejecutar y medir tareas
├─ tasks.py                   # Tareas de ejemplo: CPU, IO y baseline
├─ requirements.txt           # Dependencias (instalación por pip)
├─ scripts/
│  └─ run_example.bat         # Ejecución automática en Windows
├─ Informe/
│  └─ Informe_TP_Green_Software.md  
└─ results/
   └─ (se generan emissions.csv, summary.json/md, logs, etc.)
```

### Ejemplos
1) **CPU 30s, offline en Argentina:**
```bash
python measure.py --task cpu --seconds 30 --mode offline --country ARG
```

2) **IO 15s, offline en Argentina:**
```bash
python measure.py --task io --seconds 15 --mode offline --country ARG
```

3) **Baseline 10s (reposo), offline:**
```bash
python measure.py --task baseline --seconds 10 --mode offline --country ARG
```

> Equivalencia árboles: 1 árbol ≈ 300 kg CO₂/año. Para una ejecución, **árboles necesarios ≈ emisiones_kg / 300**.


=======
# TP1-GreenSoftware-VarengoBossi
>>>>>>> 8a3b8dee5cbf66beb34964d914f2710d4a8419fd

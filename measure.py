#!/usr/bin/env python
import argparse, time, json, os, csv, sys
from datetime import datetime
from pathlib import Path

# Dependencias de CodeCarbon
try:
    from codecarbon import EmissionsTracker, OfflineEmissionsTracker
except Exception as e:
    print("[ERROR] No se pudo importar codecarbon. Asegurate de instalar dependencias con 'pip install -r requirements.txt'")
    raise

# Tareas de ejemplo
from tasks import cpu_task, io_task, baseline_task

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def read_last_row(csv_path: str, run_id: str | None):
    if not os.path.exists(csv_path):
        return None
    last = None
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            return None
        if run_id and "run_id" in rows[0]:
            # Filtrar por run_id si existe
            rows = [r for r in rows if r.get("run_id") == run_id] or rows
        # Tomar última fila
        last = rows[-1]
    return last

def build_tracker(args):
    # Modo offline recomendado para la consigna (factor país)
    if args.mode.lower() == "offline":
        tracker = OfflineEmissionsTracker(
            project_name=args.project,
            output_dir=args.output,
            country_iso_code=args.country,
            measure_power_secs=args.interval,
            save_to_file=True,
            log_level="error",
        )
    else:
        tracker = EmissionsTracker(
            project_name=args.project,
            output_dir=args.output,
            measure_power_secs=args.interval,
            save_to_file=True,
            log_level="error",
        )
    return tracker

def main():
    parser = argparse.ArgumentParser(description="Medición de energía y CO2eq usando CodeCarbon")
    parser.add_argument("--task", choices=["cpu", "io", "baseline"], default="cpu", help="Tarea a ejecutar")
    parser.add_argument("--seconds", type=int, default=20, help="Duración aproximada de la tarea")
    parser.add_argument("--mode", choices=["offline", "online"], default="offline", help="Modo de medición")
    parser.add_argument("--country", type=str, default="ARG", help="Código ISO-3 del país (solo offline)")
    parser.add_argument("--project", type=str, default="TP_Green_Software", help="Nombre del proyecto")
    parser.add_argument("--output", type=str, default="results", help="Directorio de salida")
    parser.add_argument("--interval", type=int, default=1, help="Período de muestreo de potencia (segundos)")
    args = parser.parse_args()

    ensure_dir(args.output)

    # Elegir función de tarea
    task_map = {
        "cpu": cpu_task,
        "io": io_task,
        "baseline": baseline_task,
    }
    func = task_map[args.task]

    tracker = build_tracker(args)

    print(f"[INFO] Iniciando medición ({args.mode}) - Tarea: {args.task} - {args.seconds}s")
    start_ts = time.time()
    tracker.start()
    run_id = getattr(tracker, "run_id", None)

    try:
        func(args.seconds, args.output)  # Ejecuta la tarea
    finally:
        emissions_kg = tracker.stop()

    end_ts = time.time()
    duration = end_ts - start_ts

    # Leer última fila del emissions.csv
    csv_path = os.path.join(args.output, "emissions.csv")
    last = read_last_row(csv_path, run_id)

    # Armar resumen
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "task": args.task,
        "mode": args.mode,
        "country": args.country if args.mode == "offline" else None,
        "seconds": args.seconds,
        "duration_s": round(duration, 3),
        "emissions_kg": float(emissions_kg) if emissions_kg is not None else None,
        "project_name": args.project,
        "output_csv": csv_path,
        "notes": "Ejecución con CodeCarbon",
    }

    # Agregar campos si existen en el CSV
    if last:
        def f(x):
            try:
                return float(x)
            except Exception:
                return x
        for key in ["cpu_power", "gpu_power", "ram_power",
                    "cpu_energy", "gpu_energy", "ram_energy",
                    "energy_consumed", "emissions", "emissions_rate", "duration"]:
            if key in last and last[key] not in (None, "", "None"):
                summary[key] = f(last[key])

    # Árboles necesarios + horas compensadas
    if summary.get("emissions_kg") is not None:
        summary["trees_needed_per_year_equiv"] = round(summary["emissions_kg"] / 300.0, 8)

        # Cálculo de emisiones por hora
        emissions_per_hour = summary["emissions_kg"] / (summary["duration_s"] / 3600.0)

        # Horas compensadas por árboles (joven: 30 kg/año, adulto: 300 kg/año)
        summary["hours_compensated_tree_young"] = round(30.0 / emissions_per_hour, 3)
        summary["hours_compensated_tree_adult"] = round(300.0 / emissions_per_hour, 3)

    # Guardar resumen JSON y Markdown
    json_path = os.path.join(args.output, "summary.json")
    md_path = os.path.join(args.output, "summary.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Resumen de ejecución (CodeCarbon)\n\n")
        f.write(f"- Fecha (UTC): **{summary['timestamp']}**\n")
        f.write(f"- Tarea: **{summary['task']}** — Modo: **{summary['mode']}**\n")
        if summary['mode'] == 'offline':
            f.write(f"- País (factor): **{summary['country']}**\n")
        f.write(f"- Duración: **{summary['duration_s']} s** (solicitado: {summary['seconds']} s)\n")
        f.write(f"- Emisiones estimadas: **{summary.get('emissions_kg','?')} kg CO₂eq**\n")
        if 'energy_consumed' in summary:
            f.write(f"- Energía consumida: **{summary['energy_consumed']} kWh**\n")
        for k in ["cpu_power","gpu_power","ram_power","cpu_energy","gpu_energy","ram_energy"]:
            if k in summary:
                unit = "W" if "power" in k else "kWh"
                f.write(f"- {k}: **{summary[k]} {unit}**\n")
        if "trees_needed_per_year_equiv" in summary:
            f.write(f"- Árboles necesarios (aprox.): **{summary['trees_needed_per_year_equiv']}**  \n")
            f.write("  (Asumiendo 1 árbol ≈ 300 kg CO₂/año)\n")
        if "hours_compensated_tree_young" in summary:
            f.write(f"- Horas compensadas (árbol joven, 30 kg/año): **{summary['hours_compensated_tree_young']} h**\n")
        if "hours_compensated_tree_adult" in summary:
            f.write(f"- Horas compensadas (árbol adulto, 300 kg/año): **{summary['hours_compensated_tree_adult']} h**\n")
        f.write("\nArchivo detallado: `emissions.csv`\n")

    print(f"[OK] Listo. Emisiones (kg CO2eq): {summary.get('emissions_kg','?')}")
    print(f"[OK] Ver resumen: {md_path}")
    print(f"[OK] CSV detallado: {csv_path}")


if __name__ == "__main__":
    main()


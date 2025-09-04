import os, time, numpy as np

def cpu_task(seconds: int, _outdir: str):
    """
    Trabajo CPU-bound: multiplicaciones de matrices aleatorias en bucle
    durante ~seconds segundos.
    """
    end = time.time() + seconds
    size = 700  # tamaño moderado para ocupar CPU
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    c = None
    iters = 0
    while time.time() < end:
        c = a @ b  # multiplicación matricial
        a, b = b, c  # cambiar referencias para variar cálculos
        iters += 1
    # Guardar un artefacto mínimo para evitar optimización total del intérprete
    with open(os.path.join(_outdir, "cpu_last_shape.txt"), "w", encoding="utf-8") as f:
        f.write(str(c.shape if c is not None else "none"))
    return iters

def io_task(seconds: int, outdir: str):
    """
    Trabajo IO-bound: escritura de bloques a disco durante ~seconds segundos.
    """
    path = os.path.join(outdir, "io_temp.bin")
    block = os.urandom(2 * 1024 * 1024)  # ~2MB por bloque
    end = time.time() + seconds
    written = 0
    with open(path, "wb") as f:
        while time.time() < end:
            f.write(block)
            written += len(block)
            f.flush()
            os.fsync(f.fileno())
    # Limpiar archivo (dejar un marcador del total escrito)
    with open(os.path.join(outdir, "io_written_bytes.txt"), "w", encoding="utf-8") as m:
        m.write(str(written))
    try:
        os.remove(path)
    except Exception:
        pass
    return written

def baseline_task(seconds: int, _outdir: str):
    """
    Baseline: reposo/espera para medir consumo casi inactivo.
    """
    time.sleep(seconds)
    return seconds

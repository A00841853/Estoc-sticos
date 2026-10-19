"""Entrada sin interfaz para generar las 20 corridas y entregables."""
import argparse
from datetime import datetime
from motor import Configuracion, ejecutar, indicadores, exportar

def main():
    parser = argparse.ArgumentParser(description="Simulación FIFO Monte Carlo")
    parser.add_argument("--salida", default="resultados")
    parser.add_argument("--semilla", type=int, default=20261019)
    parser.add_argument("--repeticiones", type=int, default=20)
    parser.add_argument("--trabajos-min", type=int, default=20)
    parser.add_argument("--trabajos-max", type=int, default=30)
    parser.add_argument("--maquinas-min", type=int, default=3)
    parser.add_argument("--maquinas-max", type=int, default=5)
    parser.add_argument("--tamanos", type=int, nargs="+", default=[10, 20, 30])
    parser.add_argument("--velocidades", type=int, nargs="+", default=[5, 10, 15])
    parser.add_argument("--inicio", default="2026-10-19 08:00")
    args = parser.parse_args()
    config = Configuracion(
        trabajos_min=args.trabajos_min, trabajos_max=args.trabajos_max,
        maquinas_min=args.maquinas_min, maquinas_max=args.maquinas_max,
        tamanos=tuple(args.tamanos), velocidades=tuple(args.velocidades),
        repeticiones=args.repeticiones, semilla=args.semilla,
        fecha_inicio=datetime.strptime(args.inicio, "%Y-%m-%d %H:%M"),
    )
    resultados = ejecutar(config)
    carpeta = exportar(config, resultados, args.salida)
    for r in resultados:
        print(f"Sim {r.numero:2d}: trabajos={r.num_trabajos:2d}, máquinas={r.num_maquinas}, "
              f"makespan={r.makespan_horas:8.4f} horas")
    resumen = indicadores(resultados)
    print("\nPROMEDIO = {makespan_promedio_horas:.4f} h; "
          "MÍNIMO = {makespan_minimo_horas:.4f} h; "
          "MÁXIMO = {makespan_maximo_horas:.4f} h".format(**resumen))
    print(f"Archivos exportados: {carpeta.resolve()}")

if __name__ == "__main__":
    main()

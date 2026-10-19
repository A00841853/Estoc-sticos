"""Motor de simulación Monte Carlo para calendarización FIFO de tareas.

Solo usa la biblioteca estándar de Python.
Cada réplica genera N tareas, M máquinas, una matriz de velocidades
trabajo-máquina y una asignación independiente y uniforme por tarea.
"""
from __future__ import annotations

import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

TAMANOS_PERMITIDOS = (10, 20, 30)
VELOCIDADES_PERMITIDAS = (5, 10, 15)
ENCABEZADO_SECUENCIA = (
    "Maquina", "idTrabajo", "fechaHoraInicio", "fechaHoraFin",
    "OrdenSecuenciacion", "IdProducto",
)


@dataclass(frozen=True)
class Configuracion:
    trabajos_min: int = 20
    trabajos_max: int = 30
    maquinas_min: int = 3
    maquinas_max: int = 5
    tamanos: tuple[int, ...] = TAMANOS_PERMITIDOS
    velocidades: tuple[int, ...] = VELOCIDADES_PERMITIDAS
    repeticiones: int = 20
    semilla: int = 20261019
    fecha_inicio: datetime = datetime(2026, 10, 19, 8, 0)

    def validar(self) -> None:
        if not (20 <= self.trabajos_min <= self.trabajos_max <= 30):
            raise ValueError("Los trabajos deben estar entre 20 y 30 (inclusive).")
        if not (3 <= self.maquinas_min <= self.maquinas_max <= 5):
            raise ValueError("Las máquinas deben estar entre 3 y 5 (inclusive).")
        if not self.tamanos or not set(self.tamanos).issubset(TAMANOS_PERMITIDOS):
            raise ValueError("Los tamaños permitidos son 10, 20 y 30.")
        if not self.velocidades or not set(self.velocidades).issubset(VELOCIDADES_PERMITIDAS):
            raise ValueError("Las velocidades permitidas son 5, 10 y 15.")
        if len(set(self.tamanos)) != len(self.tamanos):
            raise ValueError("No repitas tamaños.")
        if len(set(self.velocidades)) != len(self.velocidades):
            raise ValueError("No repitas velocidades.")
        if not (1 <= self.repeticiones <= 10000):
            raise ValueError("Las repeticiones deben estar entre 1 y 10000.")
        if not isinstance(self.semilla, int):
            raise ValueError("La semilla debe ser un número entero.")


@dataclass(frozen=True)
class Trabajo:
    id_trabajo: int
    unidades: int
    maquina: int
    velocidades_por_maquina: tuple[int, ...]
    id_producto: str

    @property
    def velocidad_asignada(self) -> int:
        return self.velocidades_por_maquina[self.maquina - 1]

    @property
    def duracion_horas(self) -> float:
        return self.unidades / self.velocidad_asignada


@dataclass(frozen=True)
class Evento:
    maquina: int
    id_trabajo: int
    inicio: datetime
    fin: datetime
    orden: int
    id_producto: str
    unidades: int
    velocidad: int

    def fila_csv(self) -> tuple:
        return (
            self.maquina, self.id_trabajo,
            self.inicio.isoformat(sep=" ", timespec="microseconds"),
            self.fin.isoformat(sep=" ", timespec="microseconds"),
            self.orden, self.id_producto,
        )


@dataclass
class Resultado:
    numero: int
    semilla: int
    num_trabajos: int
    num_maquinas: int
    trabajos: list[Trabajo]
    eventos: list[Evento]
    cargas_horas: list[float]
    makespan_horas: float

    @property
    def desequilibrio(self) -> float:
        return max(self.cargas_horas) - min(self.cargas_horas)


def calendarizar(trabajos: list[Trabajo], num_maquinas: int,
                 fecha_inicio: datetime) -> tuple[list[Evento], list[float]]:
    """Asigna cada tarea a su única máquina; FIFO por orden de llegada (id).

    Todas las tareas llegan en fecha_inicio. No se interrumpe una tarea
    ni una máquina ejecuta dos simultáneamente.
    """
    if num_maquinas <= 0:
        raise ValueError("Se requiere al menos una máquina.")
    identificadores = [t.id_trabajo for t in trabajos]
    if len(identificadores) != len(set(identificadores)):
        raise ValueError("Los IDs de trabajos deben ser únicos.")

    colas: dict[int, list[Trabajo]] = {m: [] for m in range(1, num_maquinas + 1)}
    for trabajo in sorted(trabajos, key=lambda t: t.id_trabajo):
        if not 1 <= trabajo.maquina <= num_maquinas:
            raise ValueError("Máquina asignada fuera de rango.")
        if len(trabajo.velocidades_por_maquina) != num_maquinas:
            raise ValueError("Matriz trabajo-máquina inconsistente.")
        if trabajo.unidades <= 0 or any(v <= 0 for v in trabajo.velocidades_por_maquina):
            raise ValueError("Unidades y velocidades deben ser positivas.")
        colas[trabajo.maquina].append(trabajo)

    eventos: list[Evento] = []
    cargas = [0.0] * num_maquinas
    for maquina, cola in colas.items():
        inicio = fecha_inicio
        for orden, trabajo in enumerate(cola, start=1):
            fin = inicio + timedelta(hours=trabajo.duracion_horas)
            eventos.append(Evento(
                maquina=maquina, id_trabajo=trabajo.id_trabajo,
                inicio=inicio, fin=fin, orden=orden,
                id_producto=trabajo.id_producto, unidades=trabajo.unidades,
                velocidad=trabajo.velocidad_asignada,
            ))
            cargas[maquina - 1] += trabajo.duracion_horas
            inicio = fin
    return eventos, cargas


def ejecutar(config: Configuracion) -> list[Resultado]:
    """Genera repeticiones independientes con semillas derivadas de la inicial."""
    config.validar()
    generador_maestro = random.Random(config.semilla)
    resultados: list[Resultado] = []
    for numero in range(1, config.repeticiones + 1):
        semilla_corrida = generador_maestro.getrandbits(64)
        rng = random.Random(semilla_corrida)
        n = rng.randint(config.trabajos_min, config.trabajos_max)
        m = rng.randint(config.maquinas_min, config.maquinas_max)
        trabajos = []
        for id_trabajo in range(1, n + 1):
            unidades = rng.choice(config.tamanos)
            velocidades = tuple(rng.choice(config.velocidades) for _ in range(m))
            maquina = rng.randint(1, m)
            trabajos.append(Trabajo(
                id_trabajo, unidades, maquina, velocidades, f"P{unidades}"
            ))
        eventos, cargas = calendarizar(trabajos, m, config.fecha_inicio)
        resultados.append(Resultado(
            numero, semilla_corrida, n, m, trabajos, eventos,
            cargas, max(cargas),
        ))
    return resultados


def indicadores(resultados: list[Resultado]) -> dict:
    if not resultados:
        raise ValueError("No existen simulaciones.")
    makespans = [r.makespan_horas for r in resultados]
    return {
        "repeticiones": len(resultados),
        "makespan_promedio_horas": statistics.mean(makespans),
        "makespan_minimo_horas": min(makespans),
        "makespan_maximo_horas": max(makespans),
        "desviacion_estandar_horas": statistics.stdev(makespans) if len(makespans) > 1 else 0,
        "promedio_desequilibrio_horas": statistics.mean(r.desequilibrio for r in resultados),
    }


def _texto_reporte(config: Configuracion, resultados: list[Resultado]) -> str:
    k = indicadores(resultados)
    total_tareas = sum(r.num_trabajos for r in resultados)
    media_n = statistics.mean(r.num_trabajos for r in resultados)
    media_m = statistics.mean(r.num_maquinas for r in resultados)
    por_maquinas: dict[int, list[float]] = defaultdict(list)
    for r in resultados:
        por_maquinas[r.num_maquinas].append(r.makespan_horas)
    desglose = "\n".join(
        f"| {m} | {len(tiempos)} | {statistics.mean(tiempos):.4f} |"
        for m, tiempos in sorted(por_maquinas.items())
    )
    filas = "\n".join(
        f"| {r.numero} | {r.num_trabajos} | {r.num_maquinas} | "
        f"{r.makespan_horas:.4f} | {r.desequilibrio:.4f} |"
        for r in resultados
    )
    return f"""# Reporte de simulación: calendarización FIFO, Monte Carlo

## Planteamiento
Se ejecutan trabajos independientes en máquinas paralelas. Cada trabajo
tiene **una sola máquina asignada**, elegida al azar con igual probabilidad.
Todas las tareas llegan al tiempo inicial; en cada máquina se respeta FIFO
(orden ascendente del identificador). El procesamiento no se interrumpe.
Todas las máquinas pueden procesar cualquier trabajo.

Las variables aleatorias son **uniformes discretas**; se generan mediante
un generador de números pseudoaleatorios (Mersenne Twister de Python):
el número de trabajos es uniforme entre los extremos enteros elegidos;
el número de máquinas también; cada tamaño toma un valor equiprobable
entre {list(config.tamanos)}; las velocidades de **cada combinación de
trabajo y máquina** se eligen entre {list(config.velocidades)};
la asignación de cada trabajo es uniforme sobre las máquinas existentes.

Tiempo de servicio en horas: unidades / velocidad. Makespan = máximo
de las cargas de las máquinas, contado desde el inicio de la corrida.

## Parámetros de entrada
- Trabajos posibles: {config.trabajos_min} a {config.trabajos_max}, inclusive.
- Máquinas posibles: {config.maquinas_min} a {config.maquinas_max}, inclusive.
- Tamaños permitidos: {list(config.tamanos)} unidades.
- Velocidades permitidas: {list(config.velocidades)} unidades/hora.
- Repeticiones: {config.repeticiones}.
- Semilla principal: {config.semilla}.
- Inicio común: {config.fecha_inicio.isoformat(sep=" ")}.
- IdProducto = P10, P20 o P30 según unidades del trabajo.

## Resultados
- **Makespan promedio:** {k["makespan_promedio_horas"]:.4f} h
- **Makespan mínimo:** {k["makespan_minimo_horas"]:.4f} h
- **Makespan máximo:** {k["makespan_maximo_horas"]:.4f} h
- **Desviación estándar muestral:** {k["desviacion_estandar_horas"]:.4f} h
- **Desequilibrio promedio** (carga mayor menos carga menor): {k["promedio_desequilibrio_horas"]:.4f} h
- Total de tareas simuladas: {total_tareas}; promedio de tareas: {media_n:.2f}
- Promedio de máquinas: {media_m:.2f}

| Corrida | Trabajos | Máquinas | Makespan (h) | Desequilibrio (h) |
|---:|---:|---:|---:|---:|
{filas}

### Desglose descriptivo por cantidad de máquinas
| Máquinas | Corridas | Makespan medio (h) |
|---:|---:|---:|
{desglose}

## Interpretación y conclusiones
1. El makespan mide el final de la **última máquina**, no la suma
   de los tiempos de todas las tareas. El trabajo paralelo disminuye
   el tiempo calendario respecto del procesamiento completamente secuencial,
   aunque una asignación aleatoria puede concentrar tareas en una máquina.
2. En igualdad de otros factores, más tareas o trabajos más grandes
   aumentan la carga; tasas más altas reducen la duración individual
   (unidades/velocidad). Más máquinas permiten repartir la carga,
   pero **no garantizan** una mejora en una réplica aleatoria.
3. En estas {len(resultados)} realizaciones se observó un makespan entre
   {k["makespan_minimo_horas"]:.4f} y {k["makespan_maximo_horas"]:.4f} h,
   con promedio {k["makespan_promedio_horas"]:.4f} h. El desequilibrio
   promedio fue {k["promedio_desequilibrio_horas"]:.4f} h, indicador
   del efecto del reparto aleatorio.
4. Las medias por número de máquinas son **descriptivas**: el número
   de trabajos, tamaños, tasas y asignaciones también cambian entre
   corridas, así que no constituyen un experimento controlado ni
   permiten atribuir causalmente una diferencia solo a las máquinas.
   Para aislar efectos, fije los demás factores y ejecute 20 o más
   réplicas por escenario con semillas comparables.
5. El sistema cumple los supuestos del enunciado: asignación única,
   velocidades elegidas de manera equiprobable, ejecución FIFO por
   máquina y terminación de todos los trabajos. No es un algoritmo
   de optimización del makespan: es una **política aleatoria base**.

## Archivos para auditoría
- `resultados_simulaciones.csv`: estadísticas por corrida, rangos y semilla.
- `parametros_simulaciones.json`: todos los trabajos, la matriz de
  velocidades de cada trabajo en cada máquina, asignación y cargas.
- `secuenciacion_sim_XX.csv`: secuencia exacta de cada corrida,
  con las seis columnas solicitadas.
- `reporte.md`: este documento, generado automáticamente.

Nota: las fechas horarias representan tiempos simulados, no ejecución real.
"""


def exportar(config: Configuracion, resultados: list[Resultado],
             carpeta: str | Path) -> Path:
    """Guarda tablas, parámetros completos, secuencia CSV y reporte."""
    if len(resultados) != config.repeticiones:
        raise ValueError("Faltan simulaciones para esta configuración.")
    ruta = Path(carpeta)
    ruta.mkdir(parents=True, exist_ok=True)
    with (ruta / "resultados_simulaciones.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as archivo:
        writer = csv.writer(archivo)
        writer.writerow((
            "Simulacion", "SemillaCorrida", "NumeroTrabajos", "NumeroMaquinas",
            "TamanosPermitidos", "VelocidadesPermitidas", "MakespanHoras",
            "DesequilibrioHoras", "CargasPorMaquinaHoras",
        ))
        for r in resultados:
            writer.writerow((
                r.numero, r.semilla, r.num_trabajos, r.num_maquinas,
                "/".join(map(str, config.tamanos)),
                "/".join(map(str, config.velocidades)),
                f"{r.makespan_horas:.8f}", f"{r.desequilibrio:.8f}",
                "/".join(f"{c:.8f}" for c in r.cargas_horas),
            ))

    detalle = {
        "configuracion": {
            **{k: v for k, v in asdict(config).items() if k != "fecha_inicio"},
            "fecha_inicio": config.fecha_inicio.isoformat(sep=" "),
        },
        "indicadores": indicadores(resultados),
        "simulaciones": [
            {
                "simulacion": r.numero, "semilla": r.semilla,
                "numero_trabajos": r.num_trabajos, "numero_maquinas": r.num_maquinas,
                "cargas_horas": r.cargas_horas, "makespan_horas": r.makespan_horas,
                "trabajos": [
                    {**asdict(t), "velocidad_asignada": t.velocidad_asignada,
                     "duracion_horas": t.duracion_horas}
                    for t in r.trabajos
                ],
            } for r in resultados
        ],
    }
    (ruta / "parametros_simulaciones.json").write_text(
        json.dumps(detalle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for r in resultados:
        with (ruta / f"secuenciacion_sim_{r.numero:02d}.csv").open(
            "w", newline="", encoding="utf-8-sig"
        ) as archivo:
            writer = csv.writer(archivo)
            writer.writerow(ENCABEZADO_SECUENCIA)
            for e in r.eventos:
                writer.writerow(e.fila_csv())

    (ruta / "reporte.md").write_text(
        _texto_reporte(config, resultados), encoding="utf-8"
    )
    return ruta

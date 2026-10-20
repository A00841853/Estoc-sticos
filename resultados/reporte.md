# Reporte de simulación: calendarización FIFO, Monte Carlo

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
entre [10, 20, 30]; las velocidades de **cada combinación de
trabajo y máquina** se eligen entre [5, 10, 15];
la asignación de cada trabajo es uniforme sobre las máquinas existentes.

Tiempo de servicio en horas: unidades / velocidad. Makespan = máximo
de las cargas de las máquinas, contado desde el inicio de la corrida.

## Parámetros de entrada
- Trabajos posibles: 20 a 30, inclusive.
- Máquinas posibles: 3 a 5, inclusive.
- Tamaños permitidos: [10, 20, 30] unidades.
- Velocidades permitidas: [5, 10, 15] unidades/hora.
- Repeticiones: 20.
- Semilla principal: 20261019.
- Inicio común: 2026-10-19 08:00:00.
- IdProducto = P10, P20 o P30 según unidades del trabajo.

## Resultados
- **Makespan promedio:** 24.6667 h
- **Makespan mínimo:** 13.6667 h
- **Makespan máximo:** 37.3333 h
- **Desviación estándar muestral:** 5.7032 h
- **Desequilibrio promedio** (carga mayor menos carga menor): 14.6000 h
- Total de tareas simuladas: 505; promedio de tareas: 25.25
- Promedio de máquinas: 3.85

| Corrida | Trabajos | Máquinas | Makespan (h) | Desequilibrio (h) |
|---:|---:|---:|---:|---:|
| 1 | 28 | 5 | 22.3333 | 17.6667 |
| 2 | 29 | 4 | 20.3333 | 6.3333 |
| 3 | 22 | 3 | 18.6667 | 7.6667 |
| 4 | 28 | 5 | 20.0000 | 11.3333 |
| 5 | 28 | 3 | 29.3333 | 14.0000 |
| 6 | 26 | 3 | 26.6667 | 15.6667 |
| 7 | 27 | 5 | 27.0000 | 20.0000 |
| 8 | 25 | 3 | 34.6667 | 25.6667 |
| 9 | 30 | 5 | 13.6667 | 7.0000 |
| 10 | 21 | 3 | 26.6667 | 13.3333 |
| 11 | 24 | 3 | 25.3333 | 12.3333 |
| 12 | 22 | 4 | 20.3333 | 13.0000 |
| 13 | 28 | 3 | 33.0000 | 4.3333 |
| 14 | 20 | 3 | 23.0000 | 17.6667 |
| 15 | 20 | 3 | 22.3333 | 11.3333 |
| 16 | 27 | 4 | 23.0000 | 11.6667 |
| 17 | 26 | 4 | 37.3333 | 32.0000 |
| 18 | 21 | 5 | 24.0000 | 22.0000 |
| 19 | 25 | 5 | 25.3333 | 18.6667 |
| 20 | 28 | 4 | 20.3333 | 10.3333 |

### Desglose descriptivo por cantidad de máquinas
| Máquinas | Corridas | Makespan medio (h) |
|---:|---:|---:|
| 3 | 9 | 26.6296 |
| 4 | 5 | 24.2667 |
| 5 | 6 | 22.0556 |

## Interpretación y conclusiones
1. El makespan mide el final de la **última máquina**, no la suma
   de los tiempos de todas las tareas. El trabajo paralelo disminuye
   el tiempo calendario respecto del procesamiento completamente secuencial,
   aunque una asignación aleatoria puede concentrar tareas en una máquina.
2. En igualdad de otros factores, más tareas o trabajos más grandes
   aumentan la carga; tasas más altas reducen la duración individual
   (unidades/velocidad). Más máquinas permiten repartir la carga,
   pero **no garantizan** una mejora en una réplica aleatoria.
3. En estas 20 realizaciones se observó un makespan entre
   13.6667 y 37.3333 h,
   con promedio 24.6667 h. El desequilibrio
   promedio fue 14.6000 h, indicador
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

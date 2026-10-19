# Ex2M4M5 — Simulación Monte Carlo de calendarización FIFO

## Entregables
- `interfaz.py`: interfaz gráfica interactiva para el usuario (Tkinter).
- `motor.py`: clases, algoritmos, 20 réplicas Monte Carlo y exportación.
- `ejecutar_lote.py`: ejecutor automático para generar resultados verificables.
- `test_motor.py`: pruebas unitarias de rangos, FIFO, duración, asignación y exportación.
- `salidas_ejemplo/`: resultados reales de una ejecución de referencia (si están disponibles).
- `reporte.md` dentro de la carpeta exportada: conclusiones y datos numéricos.
- `.github/workflows/ex2m4m5-windows.yml` (en la raíz del repositorio):
  compila automáticamente un **EXE para Windows** al actualizar estos archivos.

## ¿Cómo usar el ejecutable (sin abrir el código)?
En [Actions](https://github.com/A00841853/Estoc-sticos/actions), abre la ejecución
**Ex2M4M5 - Windows EXE** del último commit exitoso, descarga el artifact
**Ex2M4M5-Windows**, descomprímelo y abre `Ex2M4M5.exe`.
No requiere Python instalado en el equipo Windows. Si Windows advierte que
el archivo no está firmado, verifica que proceda de tu repositorio y del
workflow antes de ejecutarlo.

La ventana permite establecer intervalos de trabajos (20 a 30), número de
máquinas (3 a 5), subconjuntos de tamaños 10/20/30, velocidades 5/10/15,
número de repeticiones (20 por defecto), semilla y fecha de inicio. Presiona
**Ejecutar simulaciones**, explora las réplicas y utiliza
**Exportar CSV y reporte**. Se crea una carpeta `Ex2M4M5_resultados`.

## Uso alternativo / verificación de resultados
Con Python 3.11 o superior (sin paquetes adicionales):

```bash
cd Ex2M4M5
python interfaz.py
python -m unittest discover -v
python ejecutar_lote.py --salida salidas_ejemplo --semilla 20261019 --repeticiones 20
```

Para compilar tú mismo en Windows con Python y PyInstaller:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Ex2M4M5 interfaz.py
# Archivo generado: dist/Ex2M4M5.exe
```

## Especificación matemática
Se extrae un número entero de trabajos `N ~ Uniforme{20,...,30}`
y uno de máquinas `M ~ Uniforme{3,4,5}`, en rangos parametrizables.
Cada trabajo recibe `Unidades ~ Uniforme{10,20,30}`, una velocidad
independiente para **cada** máquina `Rate(i,j) ~ Uniforme{5,10,15}` y
una sola asignación `Máquina(i) ~ Uniforme{1,...,M}`.

Como todas las tareas llegan simultáneamente, su orden de llegada se toma
como el orden de generación (IDs ascendentes). En cada máquina se ejecutan
sin interrupción, FIFO, secuencialmente, mientras diferentes máquinas
trabajan en paralelo. La duración del trabajo i en máquina j es
`unidades_i / rate_ij` horas. El makespan es la mayor suma de duraciones
de las máquinas (hora de salida de la última tarea menos hora de inicio).

Se generan **20 soluciones independientes** por ejecución (predeterminado);
cada réplica sortea de nuevo todos los factores. La semilla maestra deriva
semillas individuales que aparecen en el CSV y JSON. Para estudiar un
escenario fijo, iguala límites mínimo y máximo y restringe a un único valor
cada lista. Repite **20 veces por escenario** para comparaciones controladas;
no confundas mezclar combinaciones aleatorias con un diseño factorial.

## Archivos exportados y trazabilidad
- `resultados_simulaciones.csv`: número de réplica, factores sorteados,
  tasas/tamaños permitidos, semillas, makespan y cargas.
- `parametros_simulaciones.json`: condiciones completas, dimensiones,
  **cada tamaño, asignación y todos los rates por trabajo-máquina**.
- `secuenciacion_sim_01.csv`, ..., `secuenciacion_sim_20.csv`:
  encabezados exactos `Maquina,idTrabajo,fechaHoraInicio,fechaHoraFin,OrdenSecuenciacion,IdProducto`.
  `IdProducto=P10/P20/P30` identifica el tipo por unidades.
- `reporte.md`: resumen numérico, todas las corridas y conclusiones.

Nota: la uniformidad se refiere a distribuciones discretas equiprobables
obtenidas con un PRNG que produce valores en [0,1). El tiempo es simulado,
no tiempo real de ejecución. Esta es una política aleatoria comparativa,
**no un optimizador** de makespan.

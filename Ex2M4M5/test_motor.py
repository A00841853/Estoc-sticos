"""Pruebas automáticas: python -m unittest discover -v."""
import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from motor import (
    Configuracion, Trabajo, calendarizar, ejecutar, exportar,
    indicadores, ENCABEZADO_SECUENCIA,
)

INICIO = datetime(2026, 10, 19, 8)

class PruebasSimulacion(unittest.TestCase):
    def test_fifo_duracion_y_no_solapamiento(self):
        trabajos = [
            Trabajo(3, 30, 1, (10, 15), "P30"),
            Trabajo(1, 10, 1, (5, 5), "P10"),
            Trabajo(2, 20, 2, (15, 10), "P20"),
        ]
        eventos, cargas = calendarizar(trabajos, 2, INICIO)
        m1 = sorted((e for e in eventos if e.maquina == 1), key=lambda e: e.orden)
        self.assertEqual([e.id_trabajo for e in m1], [1, 3])
        self.assertEqual([e.orden for e in m1], [1, 2])
        self.assertEqual(m1[0].inicio, INICIO)
        self.assertEqual(m1[1].inicio, m1[0].fin)
        self.assertEqual(m1[0].fin, INICIO + timedelta(hours=2))
        self.assertEqual(m1[1].fin, INICIO + timedelta(hours=5))
        self.assertEqual(cargas, [5.0, 2.0])

    def test_semilla_reproducible_y_rangos(self):
        config = Configuracion()
        a = ejecutar(config)
        b = ejecutar(config)
        self.assertEqual(len(a), 20)
        self.assertEqual([r.makespan_horas for r in a],
                         [r.makespan_horas for r in b])
        self.assertEqual([r.semilla for r in a], [r.semilla for r in b])
        for r in a:
            self.assertTrue(20 <= r.num_trabajos <= 30)
            self.assertTrue(3 <= r.num_maquinas <= 5)
            self.assertEqual(len(r.trabajos), r.num_trabajos)
            self.assertEqual(len(r.eventos), r.num_trabajos)
            self.assertEqual({t.id_trabajo for t in r.trabajos},
                             set(range(1, r.num_trabajos + 1)))
            self.assertEqual({e.id_trabajo for e in r.eventos},
                             set(range(1, r.num_trabajos + 1)))
            for t in r.trabajos:
                self.assertIn(t.unidades, (10, 20, 30))
                self.assertEqual(len(t.velocidades_por_maquina), r.num_maquinas)
                self.assertTrue(all(v in (5, 10, 15) for v in t.velocidades_por_maquina))
                self.assertTrue(1 <= t.maquina <= r.num_maquinas)
                self.assertAlmostEqual(t.duracion_horas, t.unidades / t.velocidad_asignada)
            self.assertAlmostEqual(r.makespan_horas, max(r.cargas_horas))
            self.assertAlmostEqual(sum(r.cargas_horas),
                                   sum(t.duracion_horas for t in r.trabajos))
            for maquina in range(1, r.num_maquinas + 1):
                eventos = sorted(
                    (e for e in r.eventos if e.maquina == maquina),
                    key=lambda e: e.orden,
                )
                self.assertEqual([e.id_trabajo for e in eventos],
                                 sorted(e.id_trabajo for e in eventos))
                for anterior, siguiente in zip(eventos, eventos[1:]):
                    self.assertEqual(anterior.fin, siguiente.inicio)

    def test_condiciones_invalidas(self):
        for config in [
            Configuracion(trabajos_min=19),
            Configuracion(maquinas_max=6),
            Configuracion(tamanos=(10, 40)),
            Configuracion(velocidades=(0, 10)),
            Configuracion(repeticiones=0),
        ]:
            with self.assertRaises(ValueError):
                ejecutar(config)

    def test_parametros_fijos_y_exportacion(self):
        config = Configuracion(
            trabajos_min=20, trabajos_max=20,
            maquinas_min=3, maquinas_max=3,
            tamanos=(10,), velocidades=(5,), repeticiones=2,
        )
        resultados = ejecutar(config)
        resumen = indicadores(resultados)
        self.assertLessEqual(resumen["makespan_minimo_horas"],
                             resumen["makespan_promedio_horas"])
        self.assertLessEqual(resumen["makespan_promedio_horas"],
                             resumen["makespan_maximo_horas"])
        for r in resultados:
            self.assertEqual((r.num_trabajos, r.num_maquinas), (20, 3))
            self.assertEqual(r.makespan_horas, max(r.cargas_horas))
        with tempfile.TemporaryDirectory() as dir_temporal:
            ruta = exportar(config, resultados, dir_temporal)
            with (ruta / "secuenciacion_sim_01.csv").open(
                newline="", encoding="utf-8-sig"
            ) as archivo:
                lector = csv.DictReader(archivo)
                self.assertEqual(tuple(lector.fieldnames), ENCABEZADO_SECUENCIA)
                filas = list(lector)
                self.assertEqual(len(filas), 20)
                self.assertTrue(all(f["IdProducto"] == "P10" for f in filas))
            datos = json.loads((ruta / "parametros_simulaciones.json").read_text("utf-8"))
            self.assertEqual(len(datos["simulaciones"]), 2)
            self.assertTrue((ruta / "reporte.md").exists())
            self.assertTrue((ruta / "resultados_simulaciones.csv").exists())

if __name__ == "__main__":
    unittest.main()

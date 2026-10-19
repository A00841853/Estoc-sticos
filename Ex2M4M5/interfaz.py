"""Interfaz gráfica del simulador FIFO, sin dependencias de terceros."""
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from motor import Configuracion, ejecutar, exportar, indicadores


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ex2M4M5 | Simulación Monte Carlo · FIFO")
        self.geometry("1090x730")
        self.minsize(850, 620)
        self.configure(bg="#f5f7fb")
        self.resultados = None
        self.configuracion = None
        self.campos = {}
        self._construir()

    def _campo(self, padre, nombre, valor, fila, columna, ancho=12):
        marco = ttk.Frame(padre)
        marco.grid(row=fila, column=columna, padx=8, pady=7, sticky="ew")
        ttk.Label(marco, text=nombre).pack(anchor="w")
        variable = tk.StringVar(value=str(valor))
        ttk.Entry(marco, textvariable=variable, width=ancho).pack(fill="x", pady=3)
        self.campos[nombre] = variable

    def _construir(self):
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TButton", font=("Segoe UI", 10), padding=7)
        estilo.configure("Treeview", rowheight=27)
        contenedor = ttk.Frame(self, padding=16)
        contenedor.pack(fill="both", expand=True)
        ttk.Label(contenedor, text="Simulación de calendarización FIFO",
                  font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(contenedor,
                  text="Asignación uniforme por máquina · velocidades por trabajo-máquina · makespan en horas").pack(anchor="w", pady=(2, 12))
        controles = ttk.LabelFrame(contenedor, text="Parámetros de la simulación", padding=8)
        controles.pack(fill="x")
        for i in range(4):
            controles.columnconfigure(i, weight=1)
        parametros = [
            ("Trabajos mínimo", 20), ("Trabajos máximo", 30),
            ("Máquinas mínimo", 3), ("Máquinas máximo", 5),
            ("Tamaños permitidos", "10,20,30"),
            ("Velocidades permitidas", "5,10,15"),
            ("Repeticiones", 20), ("Semilla", 20261019),
            ("Inicio YYYY-MM-DD HH:MM", "2026-10-19 08:00"),
        ]
        for posicion, (nombre, valor) in enumerate(parametros):
            self._campo(controles, nombre, valor, posicion // 4, posicion % 4, ancho=23)
        acciones = ttk.Frame(contenedor)
        acciones.pack(fill="x", pady=12)
        ttk.Button(acciones, text="▶ Ejecutar simulaciones", command=self.simular).pack(side="left")
        ttk.Button(acciones, text="⬇ Exportar CSV y reporte", command=self.guardar).pack(side="left", padx=10)
        ttk.Button(acciones, text="Restablecer valores", command=self.restablecer).pack(side="left")
        self.resumen = tk.StringVar(value="Configura los parámetros y pulsa «Ejecutar simulaciones».")
        ttk.Label(contenedor, textvariable=self.resumen, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 8))
        tabla_marco = ttk.LabelFrame(contenedor, text="Resultado por simulación", padding=8)
        tabla_marco.pack(fill="both", expand=True)
        columnas = ("corrida", "semilla", "trabajos", "maquinas", "makespan", "desequilibrio")
        self.tabla = ttk.Treeview(tabla_marco, columns=columnas, show="headings", height=9)
        for clave, titulo, ancho in [
            ("corrida", "Simulación", 95), ("semilla", "Semilla", 185),
            ("trabajos", "Trabajos", 95), ("maquinas", "Máquinas", 95),
            ("makespan", "Makespan (h)", 130), ("desequilibrio", "Desequilibrio (h)", 135),
        ]:
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, anchor="center")
        desplazador = ttk.Scrollbar(tabla_marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=desplazador.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        desplazador.pack(side="right", fill="y")
        self.detalle = tk.Text(contenedor, height=5, wrap="word", font=("Consolas", 10), background="#f0f5fc")
        self.detalle.pack(fill="x", pady=(9, 0))
        self.detalle.insert("end", "Selecciona una simulación en la tabla para ver la carga de sus máquinas.")
        self.detalle.configure(state="disabled")
        self.tabla.bind("<<TreeviewSelect>>", self.ver_detalle)

    def _leer_configuracion(self):
        valor = lambda nombre: self.campos[nombre].get().strip()
        lista = lambda nombre: tuple(int(s.strip()) for s in valor(nombre).split(",") if s.strip())
        fecha = datetime.strptime(valor("Inicio YYYY-MM-DD HH:MM"), "%Y-%m-%d %H:%M")
        config = Configuracion(
            trabajos_min=int(valor("Trabajos mínimo")),
            trabajos_max=int(valor("Trabajos máximo")),
            maquinas_min=int(valor("Máquinas mínimo")),
            maquinas_max=int(valor("Máquinas máximo")),
            tamanos=lista("Tamaños permitidos"),
            velocidades=lista("Velocidades permitidas"),
            repeticiones=int(valor("Repeticiones")),
            semilla=int(valor("Semilla")),
            fecha_inicio=fecha,
        )
        config.validar()
        return config

    def simular(self):
        try:
            configuracion = self._leer_configuracion()
            resultados = ejecutar(configuracion)
        except (ValueError, OverflowError) as error:
            messagebox.showerror("Parámetros inválidos", str(error), parent=self)
            return
        self.configuracion, self.resultados = configuracion, resultados
        self.tabla.delete(*self.tabla.get_children())
        for r in resultados:
            self.tabla.insert("", "end", iid=str(r.numero), values=(
                r.numero, r.semilla, r.num_trabajos, r.num_maquinas,
                f"{r.makespan_horas:.4f}", f"{r.desequilibrio:.4f}"
            ))
        estadisticas = indicadores(resultados)
        self.resumen.set(
            f"{len(resultados)} corridas  |  Makespan promedio: "
            f"{estadisticas['makespan_promedio_horas']:.4f} h"
            f"  |  Mínimo: {estadisticas['makespan_minimo_horas']:.4f} h"
            f"  |  Máximo: {estadisticas['makespan_maximo_horas']:.4f} h"
        )
        if resultados:
            self.tabla.selection_set("1")
            self.ver_detalle()

    def ver_detalle(self, _evento=None):
        if not self.resultados or not self.tabla.selection():
            return
        numero = int(self.tabla.selection()[0])
        r = self.resultados[numero - 1]
        texto = (
            f"Simulación {r.numero}: {r.num_trabajos} trabajos, {r.num_maquinas} máquinas, "
            f"makespan = {r.makespan_horas:.5f} h\n"
            + "  |  ".join(f"Máquina {m}: {t:.4f} h" for m, t in enumerate(r.cargas_horas, start=1))
            + f"\nTrabajos asignados: "
            + ", ".join(f"T{t.id_trabajo}→M{t.maquina}" for t in r.trabajos)
        )
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("end", texto)
        self.detalle.configure(state="disabled")

    def guardar(self):
        if not self.resultados:
            messagebox.showwarning("Sin resultados", "Ejecuta las simulaciones antes de exportar.", parent=self)
            return
        carpeta = filedialog.askdirectory(title="Carpeta de destino para CSV y reporte", parent=self)
        if not carpeta:
            return
        try:
            ruta = exportar(self.configuracion, self.resultados, Path(carpeta) / "Ex2M4M5_resultados")
        except (OSError, ValueError) as error:
            messagebox.showerror("Error al exportar", str(error), parent=self)
            return
        messagebox.showinfo("Exportación terminada", f"Archivos guardados en:\n{ruta}", parent=self)

    def restablecer(self):
        valores = ("20", "30", "3", "5", "10,20,30", "5,10,15", "20", "20261019", "2026-10-19 08:00")
        for variable, valor in zip(self.campos.values(), valores):
            variable.set(valor)


if __name__ == "__main__":
    Aplicacion().mainloop()

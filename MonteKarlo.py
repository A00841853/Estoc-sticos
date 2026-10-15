import pandas as pd
from IPython.display import display

# Función 1: Generador de cuadrados medios
def generar_pseudoaleatorio(x, digitos):

    cuadrado = str(x**2).zfill(2 * digitos)

    inicio = digitos // 2
    nuevo = int(cuadrado[inicio:inicio + digitos])

    u = nuevo / (10**digitos)

    return nuevo, u


# Función 2: Simular un experimento del satélite
def simular_experimento(x, digitos, vistos):

    tiempos = []

    for panel in range(5):

        # Generar número pseudoaleatorio
        nuevo, u = generar_pseudoaleatorio(x, digitos)

        # Verificar que no se repita
        if nuevo in vistos:
            raise ValueError("El generador comenzó a repetir números.")

        vistos.add(nuevo)

        # Transformar a tiempo de falla
        tiempo = 1000 + 4000 * u

        tiempos.append(tiempo)

        # Actualizar el estado
        x = nuevo

    # El satélite falla cuando falla el cuarto panel
    vida_satelite = sorted(tiempos)[3]

    return tiempos, vida_satelite, x


# Paso 3: Repetir la simulación n veces

semilla = 5735
digitos = 4
n = 5

x = semilla
vistos = {semilla}
resultados = []

for i in range(n):

    try:
        tiempos, vida, x = simular_experimento(
            x, digitos, vistos
        )

    except ValueError as error:
        print(f"Simulación detenida: {error}")
        break

    resultados.append([i + 1] + tiempos + [vida])


# Paso 4: Crear la tabla de resultados

columnas = [
    "Experimento",
    "Panel 1",
    "Panel 2",
    "Panel 3",
    "Panel 4",
    "Panel 5",
    "Vida satélite"
]

tabla = pd.DataFrame(resultados, columns=columnas)

display(tabla.round(2))

# Calcular vida útil promedio
if len(tabla) > 0:
    promedio = tabla["Vida satélite"].mean()

    print(f"\nVida útil promedio: {promedio:.2f} horas")
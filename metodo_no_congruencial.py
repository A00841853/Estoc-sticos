"""Generador no congruencial de números pseudoaleatorios: cuadrados medios.

Pide una semilla y un número par de dígitos. Imprime una tabla con
las operaciones de cada iteración y se detiene al detectar la primera
repetición. No requiere instalar bibliotecas externas.
"""


def generar_cuadrados_medios(
    semilla: int, digitos: int
) -> tuple[list[float], int, int, int]:
    """Devuelve (numeros, estado_repetido, paso_repeticion, longitud_ciclo).

    La última fila muestra el cálculo que produjo un estado repetido,
    pero ese valor repetido no se agrega otra vez a la lista numeros.
    """
    if not isinstance(digitos, int) or digitos < 2 or digitos % 2 != 0:
        raise ValueError("El número de dígitos debe ser par y mayor o igual que 2.")
    if not isinstance(semilla, int) or not 0 <= semilla < 10**digitos:
        raise ValueError(f"La semilla debe estar entre 0 y {10**digitos - 1}.")

    encabezados = [
        "Paso", "X_anterior", "Cuadrado", "Cuadrado_2d",
        "Centrales", "X_nuevo", "U", "Repetido"
    ]
    anchos = [
        5, max(10, digitos), max(8, 2 * digitos),
        max(11, 2 * digitos), max(9, digitos),
        max(7, digitos), max(7, digitos + 2), 8
    ]

    def imprimir_fila(valores):
        print(" | ".join(
            str(valor).rjust(ancho)
            for valor, ancho in zip(valores, anchos)
        ))

    print(f"\nSemilla: {semilla:0{digitos}d} | Dígitos: {digitos}")
    imprimir_fila(encabezados)
    print("-+-".join("-" * ancho for ancho in anchos))

    estado = semilla
    vistos = {semilla: 0}  # El estado inicial también cuenta.
    numeros = []
    paso = 0

    while True:
        paso += 1

        # 1. Elevar el estado anterior al cuadrado.
        cuadrado = estado**2

        # 2. Agregar ceros a la izquierda hasta tener 2*d dígitos.
        cuadrado_2d = str(cuadrado).zfill(2 * digitos)

        # 3. Extraer los d dígitos centrales.
        inicio = digitos // 2
        centrales = cuadrado_2d[inicio:inicio + digitos]
        nuevo_estado = int(centrales)

        # 4. Normalizar el estado a un número en [0, 1).
        u = nuevo_estado / (10**digitos)

        # 5. Detectar la primera repetición.
        repetido = nuevo_estado in vistos

        # 6. Mostrar las operaciones, incluso en la iteración repetida.
        imprimir_fila([
            paso,
            f"{estado:0{digitos}d}",
            cuadrado,
            cuadrado_2d,
            centrales,
            f"{nuevo_estado:0{digitos}d}",
            f"{u:.{digitos}f}",
            "Sí" if repetido else "No"
        ])

        if repetido:
            periodo = paso - vistos[nuevo_estado]
            return numeros, nuevo_estado, paso, periodo

        # 7. Guardar el nuevo estado y continuar.
        numeros.append(u)
        vistos[nuevo_estado] = paso
        estado = nuevo_estado


def main() -> None:
    print("MÉTODO NO CONGRUENCIAL: CUADRADOS MEDIOS")
    try:
        semilla = int(input("Introduce la semilla (ejemplo: 5735): "))
        digitos = int(input("Introduce el número PAR de dígitos (ejemplo: 4): "))

        numeros, repetido, paso, periodo = generar_cuadrados_medios(
            semilla, digitos
        )

        print("\n¡Se detectó una repetición y se detuvo la generación!")
        print(f"Estado repetido: {repetido:0{digitos}d} (paso {paso})")
        print(f"Longitud del ciclo detectado: {periodo}")
        print(f"Total de números generados antes de repetir: {len(numeros)}")
        print("La última fila muestra el valor repetido y no se cuenta dos veces.")
        print("Números pseudoaleatorios:", numeros)

    except ValueError as error:
        print(f"Entrada inválida: {error}")


if __name__ == "__main__":
    main()

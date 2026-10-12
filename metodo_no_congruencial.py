"""Generador no congruencial de números pseudoaleatorios: cuadrados medios.

Solicita la semilla y el número (par) de dígitos. Calcula los
números pseudoaleatorios hasta detectar el primer estado repetido.

No requiere bibliotecas externas.
"""


def generar_cuadrados_medios(semilla: int, digitos: int) -> tuple[list[float], int, int, int]:
    """Devuelve (numeros, estado_repetido, paso_repeticion, longitud_ciclo).

    Los números se normalizan a [0, 1). No se incluye en la lista
    el número que causó la primera repetición.
    """
    if digitos < 2 or digitos % 2 != 0:
        raise ValueError("El número de dígitos debe ser par y mayor o igual a 2.")
    if semilla < 0 or semilla >= 10**digitos:
        raise ValueError(f"La semilla debe estar entre 0 y {10**digitos - 1}.")

    estado = semilla
    vistos = {semilla: 0}  # Estado -> paso en el que apareció por primera vez
    numeros = []
    paso = 0

    print(f"\nSemilla: {semilla:0{digitos}d} | Dígitos: {digitos}")
    print(f"{'Paso':>6} | {'Estado':>{digitos}} | {'U (0 a 1)':>12}")
    print("-" * (25 + digitos))

    while True:
        # 1. Elevar el estado al cuadrado y completar con ceros.
        cuadrado = str(estado**2).zfill(2 * digitos)

        # 2. Tomar los 'digitos' del centro del cuadrado.
        inicio = digitos // 2
        nuevo_estado = int(cuadrado[inicio:inicio + digitos])
        paso += 1

        # 3. Detenerse si ese estado ya apareció.
        if nuevo_estado in vistos:
            longitud_ciclo = paso - vistos[nuevo_estado]
            return numeros, nuevo_estado, paso, longitud_ciclo

        # 4. Normalizar el estado a [0, 1) y mostrarlo.
        u = nuevo_estado / (10**digitos)
        numeros.append(u)
        print(f"{paso:>6} | {nuevo_estado:0{digitos}d} | {u:>12.{digitos}f}")

        # 5. Guardar el estado y continuar.
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
        print("Números pseudoaleatorios:", numeros)

    except ValueError as error:
        print(f"Entrada inválida: {error}")


if __name__ == "__main__":
    main()

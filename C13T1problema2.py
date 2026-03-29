PARES_CIERRE = {")": "(", "]": "[", "}": "{"}
APERTURAS    = set(PARES_CIERRE.values())
CIERRES      = set(PARES_CIERRE.keys())

#pila enlazada
class NodoPila:
    def __init__(self, valor):
        self.valor     = valor
        self.siguiente = None


class Pila:
    def __init__(self):
        self.cima   = None
        self.tamano = 0

    def push(self, valor) -> None:
        nuevo           = NodoPila(valor)
        nuevo.siguiente = self.cima
        self.cima       = nuevo
        self.tamano    += 1

    def pop(self):
        if self.esta_vacia():
            raise IndexError("pop en pila vacia")
        valor      = self.cima.valor
        self.cima  = self.cima.siguiente
        self.tamano -= 1
        return valor

    def peek(self):
        if self.esta_vacia():
            raise IndexError("peek en pila vacia")
        return self.cima.valor

    def esta_vacia(self) -> bool:
        return self.cima is None

#valdiaciones
class ResultadoValidacion:
    """Encapsula el resultado de una validacion: exito, posicion del error y mensaje."""
    def __init__(self, valido: bool, posicion: int = -1, mensaje: str = ""):
        self.valido    = valido
        self.posicion  = posicion
        self.mensaje   = mensaje

    def __str__(self) -> str:
        if self.valido:
            return "OK - El codigo esta correctamente balanceado."
        return f"ERROR en posicion {self.posicion}: {self.mensaje}"


def validar_sintaxis(codigo: str) -> ResultadoValidacion:
    """
    Recorre el codigo caracter por caracter.
    Apila cada apertura encontrada. Al encontrar un cierre:
      - Si la pila esta vacia -> cierre sin apertura correspondiente.
      - Si la cima no coincide con el cierre esperado -> mal anidado.
    Al final, si la pila no quedo vacia -> hay aperturas sin cerrar.
    """
    pila = Pila()

    for i, caracter in enumerate(codigo):
        if caracter in APERTURAS:
            pila.push((caracter, i))          # apila (simbolo, posicion)

        elif caracter in CIERRES:
            esperado = PARES_CIERRE[caracter]

            if pila.esta_vacia():
                return ResultadoValidacion(
                    False, i,
                    f"'{caracter}' sin apertura correspondiente."
                )

            simbolo_apilado, pos_apertura = pila.pop()

            if simbolo_apilado != esperado:
                return ResultadoValidacion(
                    False, i,
                    f"Se esperaba cierre para '{simbolo_apilado}' "
                    f"(abierto en pos {pos_apertura}), "
                    f"pero se encontro '{caracter}'."
                )

    # Si quedo algo en la pila, hay aperturas sin cerrar
    if not pila.esta_vacia():
        simbolo_sin_cerrar, pos = pila.pop()
        return ResultadoValidacion(
            False, pos,
            f"'{simbolo_sin_cerrar}' en posicion {pos} nunca fue cerrado."
        )

    return ResultadoValidacion(True)

def mostrar_resultado(codigo: str, resultado: ResultadoValidacion) -> None:
    """Imprime el codigo con un marcador visual en la posicion del error."""
    print(f"\n  Codigo   : {codigo}")
    if not resultado.valido and resultado.posicion >= 0:
        marcador = " " * (11 + resultado.posicion) + "^"
        print(marcador)
    print(f"  {resultado}")

# funcion principal con menu para usuario
def main() -> None:
    print("  PROBLEMA 2: VALIDADOR DE SINTAXIS - PILA LIFO")
    print("=" * 58)
    print("  Caracteres verificados: () [] {}")
    print("  El resto del texto se ignora (letras, numeros, etc.)\n")

    while True:
        print("\n  1. Validar codigo")
        print("  2. Ejecutar ejemplos predefinidos")
        print("  0. Salir")

        op = input("\n  Opcion: ").strip()

        if op == "1":
            codigo = input("  Ingrese el codigo a validar:\n  > ")
            resultado = validar_sintaxis(codigo)
            mostrar_resultado(codigo, resultado)

        elif op == "2":
            ejemplos = [
                # (codigo, descripcion)
                ("int main() { return 0; }",         "correcto"),
                ("if (x > 0) { f(x[0]); }",          "anidado correcto"),
                ("([)]",                              "mal anidado"),
                ("{(})",                              "cierre incorrecto"),
                ("(((",                               "aperturas sin cerrar"),
                (")))",                               "cierres sin apertura"),
            ]
            print()
            for codigo, descripcion in ejemplos:
                resultado = validar_sintaxis(codigo)
                estado    = "OK " if resultado.valido else "ERR"
                print(f"  [{estado}] {descripcion}")
                print(f"         {codigo}")
                if not resultado.valido:
                    print(f"         -> {resultado.mensaje}")
                print()

        elif op == "0":
            print("\n  Validador cerrado.")
            break
        else:
            print("  Opcion invalida.")


if __name__ == "__main__":
    main()
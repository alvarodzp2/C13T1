#librerias
from dataclasses import dataclass

#clases apra la pila
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
        valor       = self.cima.valor
        self.cima   = self.cima.siguiente
        self.tamano -= 1
        return valor

    def peek(self):
        if self.esta_vacia():
            raise IndexError("peek en pila vacia")
        return self.cima.valor

    def esta_vacia(self) -> bool:
        return self.cima is None

    def listar(self) -> list:
        resultado, actual = [], self.cima
        while actual:
            resultado.append(actual.valor)
            actual = actual.siguiente
        return resultado


# =============================================================================
#  MODELO DE SUPERFICIE 3D
# =============================================================================

@dataclass
class Superficie:
    """
    Representa una superficie poligonal en la escena 3D.

    profundidad_z: distancia al espectador. Mayor valor = mas lejos.
    color        : color de relleno (texto libre para la simulacion).
    opaca        : si es True puede ocultar superficies detras de ella.
    """
    id_superficie : int
    nombre        : str
    profundidad_z : float   # eje Z: 0 = muy cercano, valores grandes = lejano
    color         : str
    opaca         : bool = True

    def __str__(self) -> str:
        tipo = "opaca" if self.opaca else "transparente"
        return (f"ID:{self.id_superficie:>3}  {self.nombre:<22}  "
                f"Z={self.profundidad_z:>7.2f}  {self.color:<12}  {tipo}")


# =============================================================================
#  MOTOR DE RENDERIZADO
# =============================================================================

class MotorRenderizado:
    """
    Gestiona la cola de renderizado usando una pila (algoritmo del pintor).
    """

    def __init__(self):
        self.escena           : list[Superficie] = []
        self.pila_render      : Pila             = Pila()
        self.orden_renderizado: list[Superficie] = []  # historial de lo ya dibujado

    def agregar_superficie(self, superficie: Superficie) -> None:
        self.escena.append(superficie)

    def construir_pila_renderizado(self) -> None:
   
        self.pila_render       = Pila()
        self.orden_renderizado = []

        visibles = [s for s in self.escena if s.profundidad_z > 0]

        # Ordenar de menor Z a mayor Z (cercanas primero) para que al apilar
        # la mas cercana quede al fondo y la mas lejana en la cima.
        # Al hacer pop la cima (mas lejana) se renderiza primero,
        # y la ultima en salir es la mas cercana -> queda encima de todo.
        visibles_ordenadas = sorted(visibles,
                                    key=lambda s: s.profundidad_z)

        for superficie in visibles_ordenadas:
            self.pila_render.push(superficie)

        print(f"\n  Pila construida: {self.pila_render.tamano} superficie(s).")
        print(f"  Cima (primera en renderizar): {self.pila_render.peek().nombre}")

    def renderizar_escena(self) -> list[Superficie]:
        """
        Hace pop de la pila y 'dibuja' cada superficie en orden back-to-front.
        Retorna la lista de superficies en el orden en que fueron renderizadas.
        """
        if self.pila_render.esta_vacia():
            print("  Pila vacia. Ejecute construir_pila_renderizado() primero.")
            return []

        print("\n  Iniciando renderizado (back-to-front)...")
        orden = 1

        while not self.pila_render.esta_vacia():
            superficie = self.pila_render.pop()
            self.orden_renderizado.append(superficie)

            # Verificar si esta cubierta por alguna ya dibujada mas cercana
            ocluida = self._esta_ocluida(superficie)
            estado  = "OCLUIDA (no visible)" if ocluida else "visible"

            print(f"  [{orden:>2}] Renderizando Z={superficie.profundidad_z:>7.2f}  "
                  f"{superficie.nombre:<22} [{estado}]")
            orden += 1

        return self.orden_renderizado

    def _esta_ocluida(self, superficie: Superficie) -> bool:
        """
        Verifica si la superficie esta completamente oculta por alguna
        superficie opaca ya renderizada con menor profundidad Z.
        En esta simulacion dos superficies colisionan si tienen el mismo
        nombre base (simplificacion del test de interseccion geometrica).
        """
        for ya_dibujada in self.orden_renderizado[:-1]:  # excluir la actual
            if (ya_dibujada.opaca and
                    ya_dibujada.profundidad_z < superficie.profundidad_z and
                    ya_dibujada.nombre.split()[0] == superficie.nombre.split()[0]):
                return True
        return False

    def mostrar_escena(self) -> None:
        print(f"\n  Escena actual ({len(self.escena)} superficie(s)):")
        for s in sorted(self.escena, key=lambda x: x.profundidad_z):
            print(f"  {s}")

    def mostrar_pila(self) -> None:
        elementos = self.pila_render.listar()
        if not elementos:
            print("  Pila de renderizado vacia.")
            return
        print(f"\n  Pila de renderizado ({len(elementos)} elemento(s)):")
        for i, s in enumerate(elementos):
            etiqueta = " <- cima (mas cercana)" if i == 0 else ""
            print(f"  {s}{etiqueta}")


#ingreso de datos de parte del usuario

def pedir_superficie(id_auto: int) -> Superficie:
    nombre = input("  Nombre de la superficie  : ").strip() or f"Superficie_{id_auto}"
    while True:
        try:
            z = float(input("  Profundidad Z (> 0 = frente al espectador): "))
            break
        except ValueError:
            print("  [Error] Ingrese un numero.")
    color = input("  Color                    : ").strip() or "blanco"
    opaca_inp = input("  Es opaca? (s/n)          : ").strip().lower()
    opaca = opaca_inp != "n"
    return Superficie(id_auto, nombre, z, color, opaca)


def main() -> None:
    print("  PROBLEMA 4: RENDERIZADO 3D - ALGORITMO DEL PINTOR (PILA)")
    print()

    motor    = MotorRenderizado()
    id_count = 1

    while True:
        print("\n  1. Agregar superficie a la escena")
        print("  2. Ver escena actual")
        print("  3. Construir pila de renderizado")
        print("  4. Ver pila de renderizado")
        print("  5. Renderizar escena completa")
        print("  6. Renderizar siguiente superficie (pop manual)")
        print("  0. Salir")

        op = input("\n  Opcion: ").strip()

        if op == "1":
            sup = pedir_superficie(id_count)
            motor.agregar_superficie(sup)
            print(f"  Superficie '{sup.nombre}' agregada.")
            id_count += 1

        elif op == "2":
            if not motor.escena:
                print("  La escena esta vacia.")
            else:
                motor.mostrar_escena()

        elif op == "3":
            if not motor.escena:
                print("  Agregue superficies primero.")
            else:
                motor.construir_pila_renderizado()

        elif op == "4":
            motor.mostrar_pila()

        elif op == "5":
            if motor.pila_render.esta_vacia():
                print("  Use la opcion 3 para construir la pila primero.")
            else:
                motor.renderizar_escena()

        elif op == "6":
            if motor.pila_render.esta_vacia():
                print("  Pila vacia. Construyala con la opcion 3.")
            else:
                sup = motor.pila_render.pop()
                motor.orden_renderizado.append(sup)
                print(f"\n  Renderizado: {sup}")
                if not motor.pila_render.esta_vacia():
                    print(f"  Siguiente en la pila: {motor.pila_render.peek().nombre}")
                else:
                    print("  La pila quedo vacia. Escena completa.")

        elif op == "0":
            print("\n  Motor de renderizado cerrado.")
            break
        else:
            print("  Opcion invalida.")

#llamada a la funcion principal
if __name__ == "__main__":
    main()
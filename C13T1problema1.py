#variables constantes
# Movimientos posibles del robot
AVANZAR          = "AVANZAR"
RETROCEDER       = "RETROCEDER"
GIRAR_DERECHA    = "GIRAR_DERECHA"
GIRAR_IZQUIERDA  = "GIRAR_IZQUIERDA"

MOVIMIENTOS_VALIDOS = {AVANZAR, RETROCEDER, GIRAR_DERECHA, GIRAR_IZQUIERDA}

# Inverso de cada movimiento para el retroceso
MOVIMIENTO_INVERSO = {
    AVANZAR         : RETROCEDER,
    RETROCEDER      : AVANZAR,
    GIRAR_DERECHA   : GIRAR_IZQUIERDA,
    GIRAR_IZQUIERDA : GIRAR_DERECHA,
}

# Orientaciones cardinales y sus deltas de posicion cuando el robot avanza
ORIENTACIONES = ["NORTE", "ESTE", "SUR", "OESTE"]

# Cuando el robot avanza una celda en cada orientacion
DELTA_AVANCE = {
    "NORTE": ( 0,  1),
    "SUR"  : ( 0, -1),
    "ESTE" : ( 1,  0),
    "OESTE": (-1,  0),
}

#clases
class NodoPila:
    """
    Nodo individual de la pila enlazada.

    Atributos:
        valor      (str):          Movimiento almacenado en este nivel.
        siguiente  (NodoPila|None): Enlace al nodo que estaba debajo en la pila.
                                    None indica que este era el fondo de la pila.
    """
    def __init__(self, valor: str):
        self.valor     = valor
        self.siguiente = None     # apunta al nodo inferior; None si es el fondo


class Pila:
    """
    Pila LIFO (Last In, First Out) implementada con lista enlazada simple.

    La cima de la pila es siempre el nodo mas recientemente apilado.
    No usa listas de Python internamente: cada nivel es un NodoPila.

    Atributos:
        cima   (NodoPila|None): Nodo en el tope de la pila.
        tamano (int):           Numero de elementos apilados actualmente.

    Operaciones:
        push(valor)  -> apila un nuevo elemento en la cima.
        pop()        -> desapila y retorna el elemento de la cima.
        peek()       -> consulta la cima sin desapilar.
        esta_vacia() -> True si la pila no tiene elementos.
    """

    def __init__(self):
        self.cima   = None
        self.tamano = 0

    # ------------------------------------------------------------------
    # PUSH: apilar un elemento
    # ------------------------------------------------------------------
    def push(self, valor: str) -> None:
        """
        Apila un nuevo movimiento en la cima de la pila.

        Parametros:
            valor (str): Movimiento a almacenar (AVANZAR, GIRAR_DERECHA, etc.)

        Funcionamiento:
            Crea un nuevo NodoPila. El enlace .siguiente del nuevo nodo
            apunta a la cima actual, luego la cima pasa a ser el nuevo nodo.
            Es el equivalente a apilar una ficha encima de la anterior.

            ANTES:  cima -> [B] -> [A] -> None
            push(C)
            DESPUES: cima -> [C] -> [B] -> [A] -> None
        """
        nuevo          = NodoPila(valor)
        nuevo.siguiente = self.cima     # el nuevo nodo apunta al anterior tope
        self.cima      = nuevo          # el tope ahora es el nuevo nodo
        self.tamano   += 1

    # ------------------------------------------------------------------
    # POP: desapilar el elemento de la cima
    # ------------------------------------------------------------------
    def pop(self) -> str:
        """
        Desapila y retorna el elemento en la cima de la pila.

        Retorna:
            str: Valor del elemento que estaba en la cima.

        Lanza:
            IndexError si la pila esta vacia (no hay nada que desapilar).

        Funcionamiento:
            Guarda el valor de la cima actual, luego avanza la cima al
            nodo que estaba inmediatamente debajo. El nodo desapilado
            queda sin referencias y sera recolectado por el GC.

            ANTES:  cima -> [C] -> [B] -> [A] -> None
            pop() retorna "C"
            DESPUES: cima -> [B] -> [A] -> None
        """
        if self.esta_vacia():
            raise IndexError("No se puede hacer pop: la pila esta vacia.")
        valor_extraido = self.cima.valor
        self.cima      = self.cima.siguiente   # bajar la cima un nivel
        self.tamano   -= 1
        return valor_extraido

    # ------------------------------------------------------------------
    # PEEK: consultar la cima sin modificar la pila
    # ------------------------------------------------------------------
    def peek(self) -> str:
        """
        Retorna el valor en la cima sin desapilarlo.

        Retorna:
            str: Valor del elemento en la cima.

        Lanza:
            IndexError si la pila esta vacia.

        Funcionamiento:
            Simplemente retorna .valor de la cima sin mover ningun puntero.
            La pila no se modifica en absoluto.
        """
        if self.esta_vacia():
            raise IndexError("No se puede hacer peek: la pila esta vacia.")
        return self.cima.valor

    # ------------------------------------------------------------------
    # ESTA_VACIA: verificar si la pila no tiene elementos
    # ------------------------------------------------------------------
    def esta_vacia(self) -> bool:
        """Retorna True si la pila no contiene ningun elemento."""
        return self.cima is None

    # ------------------------------------------------------------------
    # LISTAR: ver el contenido de la pila de cima a fondo
    # ------------------------------------------------------------------
    def listar(self) -> list[str]:
        """
        Retorna una lista con todos los movimientos apilados,
        del mas reciente (cima) al mas antiguo (fondo).

        Util solo para mostrar el estado de la pila en pantalla.
        No modifica la pila.
        """
        elementos = []
        actual    = self.cima
        while actual is not None:
            elementos.append(actual.valor)
            actual = actual.siguiente
        return elementos


# =============================================================================
#  MODELO DEL ROBOT
# =============================================================================

class RobotAlmacen:
    """
    Representa un robot autonomo en un almacen con movimiento en cuadricula.

    El robot mantiene su posicion (x, y) y orientacion actual.
    Cada movimiento ejecutado se apila en la pila de ruta para permitir
    el retroceso exacto cuando se encuentra un obstaculo.

    Atributos:
        x          (int):  Coordenada X actual del robot.
        y          (int):  Coordenada Y actual del robot.
        orientacion(str):  Orientacion actual: NORTE, SUR, ESTE u OESTE.
        pila_ruta  (Pila): Pila con el historial de movimientos ejecutados.
        log        (list): Registro de todos los eventos para mostrar en pantalla.
    """

    def __init__(self, x_inicial: int = 0, y_inicial: int = 0,
                 orientacion_inicial: str = "NORTE"):
        if orientacion_inicial not in ORIENTACIONES:
            raise ValueError(f"Orientacion invalida: {orientacion_inicial}. "
                             f"Use: {ORIENTACIONES}")
        self.x           = x_inicial
        self.y           = y_inicial
        self.orientacion = orientacion_inicial
        self.pila_ruta   = Pila()
        self.log         = []

    # ------------------------------------------------------------------
    # EJECUTAR MOVIMIENTO
    # ------------------------------------------------------------------
    def ejecutar_movimiento(self, movimiento: str) -> None:
        """
        Ejecuta un movimiento, actualiza el estado del robot y apila
        el movimiento en la pila de ruta.

        Parametros:
            movimiento (str): Uno de los valores en MOVIMIENTOS_VALIDOS.

        Funcionamiento:
            1. Valida que el movimiento sea reconocido.
            2. Actualiza la posicion u orientacion segun el tipo de movimiento.
            3. Apila el movimiento en la pila para poder deshacerlo despues.

        Por que se apila el movimiento ejecutado y no el inverso:
            Al retroceder, se saca el movimiento de la pila y se calcula
            su inverso en ese momento usando MOVIMIENTO_INVERSO. Esto es
            mas limpio que calcular el inverso al apilar.
        """
        if movimiento not in MOVIMIENTOS_VALIDOS:
            raise ValueError(f"Movimiento '{movimiento}' no reconocido.")

        if movimiento == AVANZAR:
            dx, dy = DELTA_AVANCE[self.orientacion]
            self.x += dx
            self.y += dy
            self.log.append(
                f"  AVANZAR -> posicion: ({self.x}, {self.y})  "
                f"orientacion: {self.orientacion}"
            )

        elif movimiento == RETROCEDER:
            dx, dy = DELTA_AVANCE[self.orientacion]
            self.x -= dx
            self.y -= dy
            self.log.append(
                f"  RETROCEDER -> posicion: ({self.x}, {self.y})  "
                f"orientacion: {self.orientacion}"
            )

        elif movimiento == GIRAR_DERECHA:
            idx_actual      = ORIENTACIONES.index(self.orientacion)
            self.orientacion = ORIENTACIONES[(idx_actual + 1) % 4]
            self.log.append(
                f"  GIRAR_DERECHA -> posicion: ({self.x}, {self.y})  "
                f"orientacion: {self.orientacion}"
            )

        elif movimiento == GIRAR_IZQUIERDA:
            idx_actual      = ORIENTACIONES.index(self.orientacion)
            self.orientacion = ORIENTACIONES[(idx_actual - 1) % 4]
            self.log.append(
                f"  GIRAR_IZQUIERDA -> posicion: ({self.x}, {self.y})  "
                f"orientacion: {self.orientacion}"
            )

        # Apilar el movimiento ejecutado para poder deshacerlo
        self.pila_ruta.push(movimiento)

    # ------------------------------------------------------------------
    # RETROCEDER UN PASO (deshacer el ultimo movimiento)
    # ------------------------------------------------------------------
    def retroceder_un_paso(self) -> str | None:
        """
        Deshace el ultimo movimiento ejecutado sacandolo de la pila
        y ejecutando su movimiento inverso.

        Retorna:
            str: El movimiento inverso que se ejecuto para retroceder.
            None: Si la pila estaba vacia (no hay pasos que deshacer).

        Funcionamiento:
            1. Hace pop del ultimo movimiento ejecutado.
            2. Calcula el inverso usando MOVIMIENTO_INVERSO.
            3. Aplica el inverso al estado del robot SIN apilar el inverso
               (no queremos deshacer el retroceso).
        """
        if self.pila_ruta.esta_vacia():
            self.log.append("  [Pila vacia] No hay movimientos que deshacer.")
            return None

        ultimo_movimiento = self.pila_ruta.pop()
        inverso           = MOVIMIENTO_INVERSO[ultimo_movimiento]

        # Aplicar el inverso directamente al estado sin pasar por ejecutar_movimiento
        # para que el inverso NO se apile de nuevo en la pila de ruta.
        if inverso == AVANZAR:
            dx, dy = DELTA_AVANCE[self.orientacion]
            self.x += dx
            self.y += dy
        elif inverso == RETROCEDER:
            dx, dy = DELTA_AVANCE[self.orientacion]
            self.x -= dx
            self.y -= dy
        elif inverso == GIRAR_DERECHA:
            idx = ORIENTACIONES.index(self.orientacion)
            self.orientacion = ORIENTACIONES[(idx + 1) % 4]
        elif inverso == GIRAR_IZQUIERDA:
            idx = ORIENTACIONES.index(self.orientacion)
            self.orientacion = ORIENTACIONES[(idx - 1) % 4]

        self.log.append(
            f"  [RETROCESO] inverso de {ultimo_movimiento} = {inverso}  "
            f"-> posicion: ({self.x}, {self.y})  orientacion: {self.orientacion}"
        )
        return inverso

    # ------------------------------------------------------------------
    # RETROCEDER TODA LA RUTA (obstaculo total)
    # ------------------------------------------------------------------
    def retroceder_ruta_completa(self) -> int:
        """
        Deshace todos los movimientos de la pila hasta dejar al robot
        en su posicion inicial.

        Retorna:
            int: Cantidad de pasos que se deshicieron.

        Caso de uso:
            El robot encuentra un obstaculo que bloquea totalmente el camino
            y debe volver al punto de partida para recalcular la ruta.
        """
        pasos_deshechos = 0
        self.log.append("\n  [OBSTACULO TOTAL] Iniciando retroceso completo de la ruta...")

        while not self.pila_ruta.esta_vacia():
            self.retroceder_un_paso()
            pasos_deshechos += 1

        self.log.append(
            f"  [RETROCESO COMPLETO] {pasos_deshechos} paso(s) deshechos. "
            f"Posicion final: ({self.x}, {self.y})"
        )
        return pasos_deshechos

    # ------------------------------------------------------------------
    # ESTADO ACTUAL
    # ------------------------------------------------------------------
    def estado(self) -> str:
        """Retorna una cadena descriptiva del estado actual del robot."""
        return (f"Posicion: ({self.x}, {self.y})  "
                f"Orientacion: {self.orientacion}  "
                f"Pasos en pila: {self.pila_ruta.tamano}")

    def mostrar_pila(self) -> None:
        """Imprime el contenido de la pila de ruta de cima a fondo."""
        elementos = self.pila_ruta.listar()
        if not elementos:
            print("    (pila vacia)")
            return
        for i, mov in enumerate(elementos):
            etiqueta = " <- cima (ultimo)" if i == 0 else ""
            fondo    = " <- fondo (primero)" if i == len(elementos) - 1 else ""
            print(f"    [{len(elementos) - i:>2}] {mov}{etiqueta}{fondo}")


# =============================================================================
#  INGRESO INTERACTIVO
# =============================================================================

def pedir_movimiento() -> str:
    """
    Solicita al usuario que seleccione un movimiento valido.

    Retorna:
        str: Codigo del movimiento seleccionado.
    """
    opciones = {
        "1": AVANZAR,
        "2": RETROCEDER,
        "3": GIRAR_DERECHA,
        "4": GIRAR_IZQUIERDA,
    }
    print("\n  Movimientos disponibles:")
    for k, v in opciones.items():
        print(f"    {k}. {v}")
    while True:
        sel = input("  Seleccione movimiento (1-4): ").strip()
        if sel in opciones:
            return opciones[sel]
        print("  [Error] Opcion invalida, intente de nuevo.")


def mostrar_log(robot: RobotAlmacen) -> None:
    """Imprime el log de eventos del robot y lo vacia."""
    if robot.log:
        print()
        for linea in robot.log:
            print(linea)
        robot.log.clear()


# funcion rincipal con menu interactivo para le usuario

def main() -> None:
    """
    Menu interactivo del sistema de navegacion del robot de almacen.
    El usuario configura el robot, ejecuta movimientos y puede simular
    la deteccion de obstaculos para observar el retroceso por la pila.
    """
    print("=" * 60)
    print("  PROBLEMA 1: NAVEGACION DE ROBOT DE ALMACEN (PILA LIFO)")
    print("=" * 60)

    # Configurar posicion e orientacion iniciales
    print("\n  Configuracion inicial del robot:")
    while True:
        try:
            x0 = int(input("  Posicion inicial X (entero): "))
            y0 = int(input("  Posicion inicial Y (entero): "))
            break
        except ValueError:
            print("  [Error] Ingrese enteros validos.")

    print(f"  Orientaciones disponibles: {ORIENTACIONES}")
    while True:
        ori = input("  Orientacion inicial         : ").strip().upper()
        if ori in ORIENTACIONES:
            break
        print("  [Error] Orientacion invalida.")

    robot = RobotAlmacen(x0, y0, ori)
    print(f"\n  Robot listo. {robot.estado()}")

    while True:
        print(f"\n{'=' * 60}")
        print(f"  MENU  |  {robot.estado()}")
        print("  1. Ejecutar movimiento")
        print("  2. Retroceder un paso (deshacer ultimo movimiento)")
        print("  3. Retroceder toda la ruta (obstaculo total)")
        print("  4. Ver pila de ruta actual")
        print("  5. Ver peek de la pila (proximo movimiento a deshacer)")
        print("  0. Salir")

        op = input("\n  Opcion: ").strip()

        # --- 1. Ejecutar movimiento ---
        if op == "1":
            movimiento = pedir_movimiento()
            try:
                robot.ejecutar_movimiento(movimiento)
                mostrar_log(robot)
            except ValueError as e:
                print(f"  [Error] {e}")

        # --- 2. Retroceder un paso ---
        elif op == "2":
            inverso = robot.retroceder_un_paso()
            if inverso:
                print(f"\n  Movimiento deshecho. Inverso aplicado: {inverso}")
            mostrar_log(robot)

        # --- 3. Retroceder toda la ruta ---
        elif op == "3":
            confirmacion = input(
                "  Confirmar retroceso completo (s/n): "
            ).strip().lower()
            if confirmacion == "s":
                pasos = robot.retroceder_ruta_completa()
                mostrar_log(robot)
                print(f"\n  Ruta completamente deshecha en {pasos} paso(s).")
            else:
                print("  Retroceso cancelado.")

        # --- 4. Ver pila ---
        elif op == "4":
            print(f"\n  Pila de ruta ({robot.pila_ruta.tamano} elemento(s), "
                  f"cima = ultimo movimiento realizado):")
            robot.mostrar_pila()

        # --- 5. Peek ---
        elif op == "5":
            try:
                tope = robot.pila_ruta.peek()
                print(f"\n  Tope de la pila (proximo a deshacer): {tope}")
            except IndexError:
                print("\n  La pila esta vacia, no hay movimientos que deshacer.")

        elif op == "0":
            print("\n  Sistema de navegacion cerrado.")
            break
        else:
            print("  Opcion invalida.")

# llamda al programa
if __name__ == "__main__":
    main()
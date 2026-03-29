#librerias
from dataclasses import dataclass, field
from datetime import datetime

#clases que forman la pila
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
#  MODELOS
# =============================================================================

@dataclass
class ContextoProcesador:
    """Snapshot del estado del procesador al momento de ser interrumpido."""
    pc          : int    # Program Counter: direccion de la siguiente instruccion
    sp          : int    # Stack Pointer del programa interrumpido
    registro_a  : int    # Registro acumulador
    registro_b  : int    # Registro de proposito general
    flags       : str    # Flags del procesador (Z, C, N, V como string)

    def __str__(self) -> str:
        return (f"PC=0x{self.pc:04X}  SP=0x{self.sp:04X}  "
                f"A=0x{self.registro_a:02X}  B=0x{self.registro_b:02X}  "
                f"FLAGS={self.flags}")


@dataclass
class Interrupcion:
    """Representa una solicitud de interrupcion (IRQ)."""
    id_irq      : int
    nombre      : str
    prioridad   : int    # 0 = maxima prioridad, valores mayores = menor prioridad
    descripcion : str
    timestamp   : str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S.%f")[:12])
    completada  : bool = False

    def __str__(self) -> str:
        estado = "COMPLETADA" if self.completada else "EN PROCESO"
        return (f"IRQ{self.id_irq}  {self.nombre:<22}  "
                f"Prioridad:{self.prioridad}  [{estado}]  @{self.timestamp}")


#clase para manejar interrupciones
class ManejadorInterrupciones:
    """
    Simula el controlador de interrupciones de un microcontrolador.
    La pila almacena pares (contexto, interrupcion) al anidar IRQs.
    """

    def __init__(self):
        # Pila de contextos guardados: cada entrada es (ContextoProcesador, Interrupcion)
        self.pila_contextos    : Pila              = Pila()
        self.irq_activa        : Interrupcion|None = None
        self.contexto_actual   : ContextoProcesador|None = None
        self.log               : list[str]         = []
        self._contador_irq     : int               = 1

    def _registrar(self, mensaje: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
        entrada = f"  [{ts}] {mensaje}"
        self.log.append(entrada)
        print(entrada)

    # funcion que simula el estado actual del procesador con valores ficticios
    def _capturar_contexto(self) -> ContextoProcesador:
        base = self.pila_contextos.tamano * 0x100
        return ContextoProcesador(
            pc         = 0x1000 + base,
            sp         = 0xFF00 - base,
            registro_a = 0x42 + base % 256,
            registro_b = 0x10 + base % 128,
            flags      = "Z0C1N0V0"
        )

    # funcion para cuando llega una nueva interrupcion
    def recibir_interrupcion(self, nombre: str, prioridad: int,
                              descripcion: str) -> bool:
    
        nueva = Interrupcion(self._contador_irq, nombre, prioridad, descripcion)
        self._contador_irq += 1

        # Rechazar si la nueva tiene menor o igual prioridad que la activa
        if self.irq_activa and nueva.prioridad >= self.irq_activa.prioridad:
            self._registrar(
                f"IRQ '{nueva.nombre}' (prio={nueva.prioridad}) IGNORADA: "
                f"'{self.irq_activa.nombre}' (prio={self.irq_activa.prioridad}) "
                f"tiene mayor o igual prioridad."
            )
            return False

        # Guardar contexto actual en la pila antes de cambiar de IRQ
        if self.irq_activa:
            contexto = self._capturar_contexto()
            self.pila_contextos.push((contexto, self.irq_activa))
            self._registrar(
                f"PUSH contexto: [{self.irq_activa.nombre}] guardado. "
                f"Pila: {self.pila_contextos.tamano} nivel(es)."
            )
            self._registrar(f"  Contexto guardado: {contexto}")

        self.irq_activa = nueva
        self._registrar(
            f"ATENDIENDO IRQ{nueva.id_irq} '{nueva.nombre}' "
            f"(prio={nueva.prioridad}): {nueva.descripcion}"
        )
        return True

    def finalizar_interrupcion_activa(self) -> bool:
    
        if not self.irq_activa:
            self._registrar("No hay interrupcion activa que finalizar.")
            return False

        self.irq_activa.completada = True
        self._registrar(
            f"COMPLETADA IRQ '{self.irq_activa.nombre}'."
        )

        if self.pila_contextos.esta_vacia():
            self._registrar("Pila vacia. Retorno al programa principal.")
            self.irq_activa = None
            return True

        # Pop: restaurar el contexto guardado
        contexto_anterior, irq_anterior = self.pila_contextos.pop()
        self._registrar(
            f"POP contexto: restaurando [{irq_anterior.nombre}]. "
            f"Pila: {self.pila_contextos.tamano} nivel(es)."
        )
        self._registrar(f"  Contexto restaurado: {contexto_anterior}")
        self.irq_activa = irq_anterior
        return True

    def mostrar_estado(self) -> None:
        print(f"\n  IRQ activa     : "
              f"{self.irq_activa.nombre if self.irq_activa else 'ninguna (programa principal)'}")
        print(f"  Niveles en pila: {self.pila_contextos.tamano}")
        niveles = self.pila_contextos.listar()
        for i, (ctx, irq) in enumerate(niveles):
            etiqueta = " <- cima" if i == 0 else ""
            print(f"  [{i+1}] {irq.nombre:<22} | {ctx}{etiqueta}")

    def mostrar_log(self) -> None:
        print(f"\n  Log de eventos ({len(self.log)} entradas):")
        for entrada in self.log:
            print(entrada)

#funcion que pide al usuario datos 

def pedir_interrupcion() -> tuple[str, int, str]:
    nombre      = input("  Nombre de la IRQ         : ").strip() or "IRQ_sin_nombre"
    while True:
        try:
            prioridad = int(input("  Prioridad (0=max, 9=min) : "))
            if 0 <= prioridad <= 9:
                break
            print("  [Error] Ingrese un valor entre 0 y 9.")
        except ValueError:
            print("  [Error] Entero requerido.")
    descripcion = input("  Descripcion              : ").strip() or "sin descripcion"
    return nombre, prioridad, descripcion

#funcion principal con menu para el usaurio
def main() -> None:
    print("  PROBLEMA 5: INTERRUPCIONES DE MICROCONTROLADOR - PILA LIFO")
    print()

    manejador = ManejadorInterrupciones()

    while True:
        print("\n  1. Recibir nueva interrupcion")
        print("  2. Finalizar interrupcion activa (pop contexto)")
        print("  3. Ver estado actual del sistema")
        print("  4. Ver log de eventos")
        print("  0. Salir")

        op = input("\n  Opcion: ").strip()

        if op == "1":
            nombre, prioridad, descripcion = pedir_interrupcion()
            print()
            aceptada = manejador.recibir_interrupcion(nombre, prioridad, descripcion)
            if aceptada:
                print(f"\n  IRQ '{nombre}' aceptada y en ejecucion.")

        elif op == "2":
            print()
            manejador.finalizar_interrupcion_activa()

        elif op == "3":
            manejador.mostrar_estado()

        elif op == "4":
            manejador.mostrar_log()

        elif op == "0":
            print("\n  Sistema cerrado.")
            break
        else:
            print("  Opcion invalida.")

#llamda a la funcion principal
if __name__ == "__main__":
    main()
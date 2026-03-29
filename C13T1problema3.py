#variables definidas
CAPAS_RED = ["Aplicacion", "Transporte", "Red", "Enlace"]

#clases para la pila enlazada

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


#modelo de paquete de red que se envia 

class Paquete:
    """
    Representa un paquete de red durante su ciclo de vida.
    La pila almacena las cabeceras agregadas por cada capa.
    Al desempaquetar se retiran en orden inverso (LIFO).
    """
    def __init__(self, datos: str):
        self.datos_originales = datos
        self.pila_capas       = Pila()   # cabeceras apiladas en orden de encapsulamiento

    def empaquetar(self, capa: str, metadata: dict) -> None:
        """Agrega la cabecera de una capa encima de las anteriores."""
        cabecera = {"capa": capa, **metadata}
        self.pila_capas.push(cabecera)

    def desempaquetar_capa(self) -> dict:
        """Retira y retorna la cabecera de la capa mas externa (cima)."""
        return self.pila_capas.pop()

    def contenido_actual(self) -> str:
        """Muestra las capas apiladas de exterior (cima) a interior (fondo)."""
        capas = self.pila_capas.listar()
        if not capas:
            return f"Datos desnudos: {self.datos_originales}"
        partes = [f"[{c['capa']}]" for c in capas]
        return " > ".join(partes) + f" > [{self.datos_originales}]"


#funciones para emisor y receptor

#simula el lado del emisor
def empaquetar_paquete(datos: str, capas: list[str]) -> Paquete:

    paquete = Paquete(datos)
    print("\n  [EMISOR] Encapsulando datos...")
    print(f"  Datos originales: \"{datos}\"")

    for numero, capa in enumerate(capas):
        metadata = _generar_metadata(capa, numero)
        paquete.empaquetar(capa, metadata)
        print(f"  + Capa {capa:<14} agregada  ->  {paquete.contenido_actual()}")

    print(f"\n  Paquete listo para envio ({paquete.pila_capas.tamano} capas).")
    return paquete

#simula el lado del receptor
def desempaquetar_paquete(paquete: Paquete, capas: list[str]) -> str:
    print("\n  [RECEPTOR] Desencapsulando paquete...")

    capas_retiradas = []
    while not paquete.pila_capas.esta_vacia():
        cabecera = paquete.desempaquetar_capa()
        capas_retiradas.append(cabecera["capa"])
        restante = paquete.contenido_actual()
        print(f"  - Capa {cabecera['capa']:<14} retirada   ->  {restante}")

    print(f"\n  Datos recuperados: \"{paquete.datos_originales}\"")
    return paquete.datos_originales


def _generar_metadata(capa: str, numero: int) -> dict:
    """Genera metadata simulada segun la capa del modelo."""
    if capa == "Aplicacion":
        return {"protocolo": "HTTP/2", "content_type": "application/json"}
    if capa == "Transporte":
        return {"protocolo": "TCP", "puerto_origen": 49152 + numero,
                "puerto_destino": 443, "numero_seq": 1000 + numero * 100}
    if capa == "Red":
        return {"protocolo": "IPv4", "ip_origen": "192.168.1.10",
                "ip_destino": "93.184.216.34", "ttl": 64}
    if capa == "Enlace":
        return {"protocolo": "Ethernet", "mac_origen": "AA:BB:CC:DD:EE:FF",
                "mac_destino": "11:22:33:44:55:66"}
    return {"protocolo": capa}


def mostrar_cabeceras(paquete: Paquete) -> None:
    """Muestra el detalle de cada cabecera apilada sin modificar la pila."""
    capas = paquete.pila_capas.listar()
    print(f"\n  Detalle de cabeceras ({len(capas)} capa(s), cima primero):")
    for i, cabecera in enumerate(capas):
        etiqueta = " <- cima (mas externa)" if i == 0 else ""
        print(f"  [{i+1}] {cabecera}{etiqueta}")


# funcion que permite al usaurio seleccionar que capas incluir o usar las predefinidas

def pedir_capas() -> list[str]:
    print(f"\n  Capas disponibles: {CAPAS_RED}")
    usar_todas = input("  Usar todas las capas? (s/n): ").strip().lower()
    if usar_todas == "s":
        return list(CAPAS_RED)

    seleccionadas = []
    print("  Ingrese capas en orden de encapsulamiento (ENTER para terminar):")
    while True:
        capa = input("  Capa: ").strip().capitalize()
        if not capa:
            break
        if capa in CAPAS_RED:
            seleccionadas.append(capa)
            print(f"  Capa '{capa}' agregada.")
        else:
            print(f"  Capa '{capa}' no reconocida.")
    return seleccionadas if seleccionadas else list(CAPAS_RED)

#funcion principal que interactua con el usuario
def main() -> None:
    print("  PROBLEMA 3: PROTOCOLOS DE RED EN CAPAS - PILA LIFO")
    print()

    paquete_activo = None

    while True:
        print("\n  1. Empaquetar nuevo mensaje")
        print("  2. Ver cabeceras del paquete actual")
        print("  3. Desempaquetar (simular recepcion)")
        print("  4. Retirar solo la siguiente capa")
        print("  0. Salir")

        op = input("\n  Opcion: ").strip()

        if op == "1":
            datos = input("\n  Datos a enviar: ").strip()
            if not datos:
                print("  [Error] Los datos no pueden estar vacios.")
                continue
            capas = pedir_capas()
            paquete_activo = empaquetar_paquete(datos, capas)

        elif op == "2":
            if not paquete_activo:
                print("  No hay paquete activo. Use la opcion 1 primero.")
            else:
                mostrar_cabeceras(paquete_activo)

        elif op == "3":
            if not paquete_activo:
                print("  No hay paquete activo.")
            elif paquete_activo.pila_capas.esta_vacia():
                print("  El paquete ya esta completamente desencapsulado.")
            else:
                desempaquetar_paquete(paquete_activo, CAPAS_RED)

        elif op == "4":
            if not paquete_activo or paquete_activo.pila_capas.esta_vacia():
                print("  No hay capas que retirar.")
            else:
                capa_retirada = paquete_activo.desempaquetar_capa()
                print(f"\n  Capa retirada: {capa_retirada['capa']}")
                print(f"  Estado actual: {paquete_activo.contenido_actual()}")

        elif op == "0":
            print("\n  Sistema cerrado.")
            break
        else:
            print("  Opcion invalida.")

#llamda a la funcion principal
if __name__ == "__main__":
    main()
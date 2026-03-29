# README - C13T1: Aplicaciones de Pilas en Problemas de Ingenieria

## Archivos

| Archivo               | Problema                                          |
|-----------------------|---------------------------------------------------|
| C13T1problema1.py     | Navegacion de robot de almacen                    |
| C13T1problema2.py     | Validador de sintaxis para compiladores           |
| C13T1problema3.py     | Protocolos de comunicacion en capas               |
| C13T1problema4.py     | Renderizado de graficos 3D                        |
| C13T1problema5.py     | Gestion de interrupciones en microcontroladores   |

## Como ejecutar

```bash
python C13T1problema1.py
python C13T1problema2.py
python C13T1problema3.py
python C13T1problema4.py
python C13T1problema5.py
```

---

## Problema 1: Navegacion de Robot de Almacen

**Como resuelve la pila el problema**

El robot necesita deshacer su ruta exactamente en orden inverso cuando encuentra un obstaculo. Cada movimiento ejecutado se apila (push). Al detectar el obstaculo se hace pop, se calcula el movimiento inverso usando el diccionario `MOVIMIENTO_INVERSO` y se aplica al estado del robot sin volver a apilar. El ultimo movimiento realizado es el primero en deshacerse, que es exactamente la propiedad LIFO.

---

## Problema 2: Validador de Sintaxis

**Como resuelve la pila el problema**

Al recorrer el codigo, cada caracter de apertura `( [ {` se apila junto con su posicion. Al encontrar un cierre se hace pop y se compara: si la pila estaba vacia hay un cierre sin apertura; si el simbolo no coincide hay mal anidado. Al terminar el recorrido, si la pila no quedo vacia hay aperturas sin cerrar. La pila mantiene el orden de anidamiento correcto: el ultimo abierto debe ser el primero en cerrarse (LIFO).

---

## Problema 3: Protocolos de Red en Capas

**Como resuelve la pila el problema**

El encapsulamiento de red agrega cabeceras de adentro hacia afuera (Aplicacion -> Transporte -> Red -> Enlace). El desencapsulamiento las retira en orden inverso, que es la definicion de LIFO. La pila modela directamente esta estructura: `push` en el emisor por cada capa, `pop` en el receptor por cada capa. La cima siempre es la capa mas externa, que es la primera que procesa el receptor.


## Problema 4: Renderizado 3D (Algoritmo del Pintor)

**Como resuelve la pila el problema**

El algoritmo del pintor requiere dibujar primero las superficies mas lejanas para que las cercanas las cubran. La pila se construye apilando las superficies ordenadas de mas cercana (fondo) a mas lejana (cima). Al hacer pop repetido, la primera en salir es la mas lejana y la ultima la mas cercana, garantizando el orden back-to-front. La cima siempre contiene la proxima superficie a renderizar en el orden correcto.

---

## Problema 5: Interrupciones de Microcontrolador

**Como resuelve la pila el problema**

Cuando llega una IRQ de mayor prioridad mientras se atiende otra, el procesador debe pausar la actual, guardar su contexto (PC, SP, registros, flags) y atender la nueva. Al terminar la nueva, debe retomar exactamente donde estaba. La pila guarda pares (contexto, IRQ) con push al interrumpir y pop al finalizar. El ultimo contexto guardado es el primero en restaurarse, reflejando exactamente el orden de anidamiento de las interrupciones.

Una IRQ se rechaza si su prioridad es menor o igual a la activa, evitando que interrupciones de baja prioridad interfieran con las de alta.


## Comparacion entre problemas

Todos los problemas comparten la misma propiedad fundamental: la operacion
mas reciente es la primera en deshacerse o procesarse.

| Problema     | Que se apila         | Cuando se hace pop              |
|--------------|----------------------|---------------------------------|
| Robot        | Movimientos          | Al encontrar obstaculo          |
| Validador    | Caracteres apertura  | Al encontrar cierre             |
| Protocolos   | Cabeceras de capa    | Al desencapsular en el receptor |
| Renderizado  | Superficies 3D       | Al renderizar cada frame        |
| Interrupciones| Contextos del CPU   | Al finalizar una IRQ anidada    |
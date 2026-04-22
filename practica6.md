# 1. El Acertijo: El Guardián del Tiempo

Lee atentamente las siguientes líneas. Cada estrofa describe un componente matemático exacto de una celda recurrente básica. ¿Puedes identificar a qué variable, matriz o función se refiere cada una antes de leer la disección?

---

## Estrofa 1

> Soy la novedad pura, el pulso del instante,  
> la matriz de características que el mundo me da en este segundo.

**Respuesta:** Vector de entrada en `X_t`.

---

## Estrofa 2

> Pero soy ciego sin mi compañero,  
> el fantasma del pasado,  
> que trae consigo el resumen de todo lo que hemos vivido hasta ayer.

**Respuesta:** `H_{t-1}`, estado oculto del paso anterior.

---

## Estrofa 3

> Para unirnos, cruzamos por peajes inmutables,  
> barreras que multiplican nuestra importancia  
> y deciden qué tanto valemos.

**Respuesta:** `W` y `U`, matrices de pesos.

---

## Estrofa 4

> Juntos, sumados a un pequeño desvío inevitable,  
> chocamos contra un muro curvo que nos comprime entre el `-1` y el `1`,  
> evitando que nuestra energía explote hacia el infinito.

**Respuesta:** `b_h` y `b_y`, vectores de sesgo.

---

## Estrofa 5

> Al salir de esa curva, nazco yo, una nueva identidad.  
> Soy tu estado actual, la respuesta de hoy,  
> y estoy listo para ser el fantasma de tu mañana.

**Respuesta:** `H_t`, estado oculto en el tiempo actual.
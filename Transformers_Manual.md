# Actividad manual — Entender Transformers sin computadora

## Actividad 1: La matriz de atención

Imagina que eres la palabra COME y quieres entender qué haces en la oración. Puntúa del 0 al 10 cuánto te “importa” cada palabra para entenderte (10 = muchísimo).

|                | EL | GATO | COME | PESCADO |
|----------------|----|------|------|---------|
| Desde COME →   |   4 |  8    | 7    |    8   |

## Paso 2 — Convertir a porcentajes (mini-softmax)

| Palabra | Puntuación | ÷ Suma | × 100 ≈ % |
|---|---:|---:|---:|
| EL | 4 |0.148 | 15% |
| GATO | 8 | 0.296 | 30% |
| COME | 7 | 0.259 | 26% |
| PESCADO | 8 | 0.296 | 30% |
| **Total** | 27 | 27 | **100 %** |

## Paso 3 — Interpretación

**Responde en una frase: ¿A quién le diste más atención? ¿Tiene sentido para el verbo “come”?**

Le di la misma importancia tanto al sujeto que es el gato, como al objeto directo que es el tipo de comida que esta comiendo el gato. Siento yo que si ya que lo mas importante es el suejeto y el objeto directo según mi perspectiva.

**Si fueras la palabra PESCADO, ¿crees que tu fila de porcentajes sería igual? ¿Por qué sí o por no?**

Lo más seguro es que no, ya que ahora tendría mas importancia el verbo que es come que en la tabla anterior, probablemente el sujeto seguiría teniendo la misma importancia.

## Hoja para alumnos — Actividad 2: La palabra ambigua (dos contextos)

La palabra BANCO aparece en dos frases. En parejas, completen solo la fila de BANCO (puntuación 0–10 y luego porcentajes) en cada caso.

Frase A
FUIMOS   AL   BANCO   DEL   RIO
Frase B
FUIMOS   AL   BANCO   A   SACAR   DINERO

**Frase A: FUIMOS AL BANCO DEL RÍO**

| Palabra | Puntuación | ÷ Suma | × 100 ≈ % |
|---|---:|---:|---:|
| FUIMOS | 1 | 1 ÷ 30 | 3.3 % |
| AL | 2 | 2 ÷ 30 | 6.7 % |
| BANCO | 10 | 10 ÷ 30 | 33.3 % |
| DEL | 7 | 7 ÷ 30 | 23.3 % |
| RÍO | 10 | 10 ÷ 30 | 33.3 % |
| **Total** | **30** |  | **100 %** |

**Frase B: FUIMOS AL BANCO A SACAR DINERO**

| Palabra | Puntuación | ÷ Suma | × 100 ≈ % |
|---|---:|---:|---:|
| FUIMOS | 1 | 1 ÷ 36 | 2.8 % |
| AL | 2 | 2 ÷ 36 | 5.6 % |
| BANCO | 10 | 10 ÷ 36 | 27.8 % |
| A | 5 | 5 ÷ 36 | 13.9 % |
| SACAR | 8 | 8 ÷ 36 | 22.2 % |
| DINERO | 10 | 10 ÷ 36 | 27.8 % |
| **Total** | **36** |  | **100 %** |

**¿En cuál frase BANCO le da más puntos a “RIO” / “DEL”?**
En la Frase A: “FUIMOS AL BANCO DEL RÍO”.
A Río ya que es la pista principal que nos dice que BANCO no significa institución financiera, sino orilla o borde del río.

**¿En cuál le da más a “DINERO” / “SACAR”?**

En la Frase B: “FUIMOS AL BANCO A SACAR DINERO”.
Le da más importacia a DINERO porque Porque SACAR DINERO indica claramente que BANCO significa institución financiera.

**Esto imita lo que hace un Transformer: la misma palabra cambia de vecinos importantes según la oración. Escríbanlo con sus palabras (3 líneas máximo).**

Un Transformer entiende una palabra según las palabras que la rodean. Por eso BANCO se relaciona más con RÍO/DEL cuando habla de un río, y con SACAR/DINERO cuando habla de dinero. La misma palabra puede cambiar de significado según su contexto.

## Hoja para alumnos — Actividad 3: Máscara causal (no hacer trampa)

| Pregunta \ Mira a | EL | GATO | COME | PESCADO |
|---|---|---|---|---|
| **EL** |  |  |  |  |
| **GATO** | ✓ |  |  |  |
| **COME** | ✓ | ✓ |  |  |
| **PESCADO** | ✓ | ✓ | ✓ |  |

**¿Cuántos ✓ hay en la fila de la última palabra** (PESCADO)?
3 palomitas

**¿Cuántos ✓ hay en la fila de la primera palabra (EL)?**
Ninguna

**La forma de ✓ que queda (triángulo abajo) se llama máscara causal. ¿Por qué creen que es necesaria para escribir texto?**

Es necesaria porque al escribir texto todavía no existen las palabras futuras.
La máscara causal hace que el modelo solo use las palabras anteriores para decidir la siguiente.
Así genera el texto en orden y no “hace trampa” mirando respuestas que aún no debería conocer.

## Actividad 4: Varias cabezas (varios criterios)

| Persona / Cabeza | Criterio                          | MARIA | NO | COMIO | PORQUE | ESTABA | ENFERMA |
| ---------------- | --------------------------------- | ----: | -: | ----: | -----: | -----: | ------: |
| A                | ¿Quién explica el porqué?         |     1 |  2 |     5 |     10 |      8 |      10 |
| B                | ¿Quién es el sujeto de la acción? |    10 |  2 |     5 |      1 |      1 |       1 |
| C                | ¿Quién está junto al verbo?       |     1 | 10 |     5 |     10 |      1 |       1 |

**Porcentajes por cabeza de atención**

| Persona / Cabeza | Criterio | MARIA | NO | COMIO | PORQUE | ESTABA | ENFERMA | Total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | ¿Quién explica el porqué? | 2.78 % | 5.56 % | 13.89 % | 27.78 % | 22.22 % | 27.78 % | 100 % |
| B | ¿Quién es el sujeto de la acción? | 50 % | 10 % | 25 % | 5 % | 5 % | 5 % | 100 % |
| C | ¿Quién está junto al verbo? | 3.57 % | 35.71 % | 17.86 % | 35.71 % | 3.57 % | 3.57 % | 100 % |

**Comparen: ¿las tres filas son iguales?**

No, las tres filas no son iguales. Cada cabeza de atención mira la frase con un criterio diferente: una se enfoca en la causa, otra en el sujeto y otra en las palabras cercanas a COMIO.

**En un Transformer real, esas “vistas” se juntan. ¿Qué ventaja tendría ver la frase desde tres criterios y no solo uno?**

Ver la frase desde tres criterios ayuda a entenderla mejor, porque el modelo no depende de una sola pista. Puede juntar información sobre quién hizo la acción, por qué ocurrió y qué palabras están cerca, logrando una comprensión más completa de la oración.

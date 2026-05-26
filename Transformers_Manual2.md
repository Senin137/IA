# Actividad manual Parte 2 — Entender Transformers

**Eladio Martinez Ambriz**

## Actividad 6 — Matriz de atención completa

### Paso 1 — Puntuar todas las filas

**Para cada palabra de la fila izquierda, puntúa 0–10 cuánto te importa cada columna (incluyéndose a sí misma si tiene sentido).**

| Desde ↓ / Hacia → | LA | NIÑA | PEQUEÑA | COME | FRUTA |
|---|---:|---:|---:|---:|---:|
| **LA** | 3 | 10 | 6 | 1 | 1 |
| **NIÑA** | 7 | 10 | 9 | 8 | 3 |
| **PEQUEÑA** | 4 | 10 | 8 | 2 | 1 |
| **COME** | 2 | 10 | 4 | 10 | 10 |
| **FRUTA** | 1 | 5 | 1 | 10 | 10 |

### Paso 2 — Normalizar cada fila por separado

| Desde ↓ / Hacia → | Suma fila | LA | NIÑA | PEQUEÑA | COME | FRUTA | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| **LA** | 21 | 14.3% | 47.6% | 28.6% | 4.8% | 4.8% | ≈ 100% |
| **NIÑA** | 37 | 18.9% | 27.0% | 24.3% | 21.6% | 8.1% | ≈ 100% |
| **PEQUEÑA** | 25 | 16.0% | 40.0% | 32.0% | 8.0% | 4.0% | 100% |
| **COME** | 36 | 5.6% | 27.8% | 11.1% | 27.8% | 27.8% | ≈ 100% |
| **FRUTA** | 27 | 3.7% | 18.5% | 3.7% | 37.0% | 37.0% | ≈ 100% |

### Paso 3 — Colorear
Pinta en rojo la celda más alta de cada fila. ¿Se forma un patrón distinto por fila?

| Desde ↓ / Hacia → | LA | NIÑA | PEQUEÑA | COME | FRUTA |
|---|---:|---:|---:|---:|---:|
| **LA** | 14.3 % | 🔴 **47.6 %** | 28.6 % | 4.8 % | 4.8 % |
| **NIÑA** | 18.9 % | 🔴 **27.0 %** | 24.3 % | 21.6 % | 8.1 % |
| **PEQUEÑA** | 16.0 % | 🔴 **40.0 %** | 32.0 % | 8.0 % | 4.0 % |
| **COME** | 5.6 % | 🔴 **27.8 %** | 11.1 % | 🔴 **27.8 %** | 🔴 **27.8 %** |
| **FRUTA** | 3.7 % | 18.5 % | 3.7 % | 🔴 **37.0 %** | 🔴 **37.0 %** |

Sí, se forma un patrón distinto por fila.  
Cada palabra mira más a las palabras que le ayudan a entender su función: **LA** mira a **NIÑA**, **PEQUEÑA** también mira a **NIÑA**, **COME** mira al sujeto y al objeto, y **FRUTA** mira mucho a **COME** porque es lo que se come.

### Preguntas de análisis

**¿La fila de COME se parece a la de FRUTA?**

Sí, se parecen un poco, porque ambas se relacionan con la acción de comer.

| Comparación | Explicación |
|---|---|
| **COME** mira a **NIÑA** y **FRUTA** | Porque necesita saber **quién come** y **qué come**. |
| **FRUTA** mira mucho a **COME** | Porque necesita saber qué acción recibe: es lo que se come. |

## ¿Por qué deberían diferir?

Aunque se parecen, no deberían ser iguales porque cada palabra cumple una función diferente en la oración.

| Palabra | Función en la oración | A qué debería mirar más |
|---|---|---|
| **COME** | Verbo / acción | A **NIÑA** y **FRUTA**, porque necesita saber quién realiza la acción y qué se come. |
| **FRUTA** | Objeto / cosa comida | A **COME**, porque depende del verbo para entender su papel. |

**Respuesta final**

La fila de **COME** y la fila de **FRUTA** se parecen porque ambas están conectadas por la acción de comer.  
Pero deberían diferir porque **COME** es la acción principal y necesita mirar al sujeto y al objeto, mientras que **FRUTA** es el objeto y necesita mirar principalmente al verbo.  
Por eso cada fila muestra una forma distinta de entender la misma oración.

**¿Alguna fila reparte atención casi pareja?**

Sí, la fila que más se acerca es la de **NIÑA**, aunque no es perfectamente pareja.

| Fila | LA | NIÑA | PEQUEÑA | COME | FRUTA |
|---|---:|---:|---:|---:|---:|
| **NIÑA** | 18.9 % | 27.0 % | 24.3 % | 21.6 % | 8.1 % |

**¿Por qué podría ser NIÑA?**

Porque **NIÑA** es una palabra central en la frase:

> **LA NIÑA PEQUEÑA COME FRUTA**

La palabra **NIÑA** se relaciona con varias partes importantes:

| Relación | Explicación |
|---|---|
| **LA** | Indica que se habla de una niña específica. |
| **PEQUEÑA** | Describe cómo es la niña. |
| **COME** | Muestra la acción que realiza la niña. |
| **FRUTA** | Se relaciona con lo que la niña come. |

**Respuesta final**

La fila de **NIÑA** es la que reparte la atención de forma más pareja, porque necesita mirar varias palabras para entenderse bien: el artículo **LA**, la descripción **PEQUEÑA**, la acción **COME** y el objeto **FRUTA**.  
Aun así, no todas quedan cerca de 20 %, porque **FRUTA** es menos directa para entender a **NIÑA** que las demás palabras.

**Si la frase tuviera 100 palabras, ¿cuántas celdas tendría la tabla? (Respuesta: 100 x 100 = 10000.) ¿Por qué eso explica que textos muy largos cuestan más memoria?**

Esto explica que los textos largos cuestan más memoria porque cada palabra necesita comparar su atención con muchas otras palabras.

| Cantidad de palabras | Tamaño de la tabla de atención |
|---:|---:|
| 5 palabras | 5 × 5 = 25 celdas |
| 10 palabras | 10 × 10 = 100 celdas |
| 100 palabras | 100 × 100 = 10,000 celdas |
| 1,000 palabras | 1,000 × 1,000 = 1,000,000 celdas |

**¿Por qué usa más memoria?**

Porque en un Transformer no solo se guarda una relación por palabra, sino una tabla donde cada palabra mira a todas las demás.

Mientras más largo es el texto, la tabla crece mucho más rápido:

> Si duplicamos las palabras, la tabla no se duplica: crece mucho más, porque se calcula palabra contra palabra.

**Respuesta final**

Los textos muy largos cuestan más memoria porque el Transformer necesita guardar muchas relaciones de atención.  
Con 100 palabras ya son 10,000 celdas, y con textos más largos el número crece de forma cuadrática.  
Por eso procesar textos grandes requiere más memoria y más cómputo.

## Actividad 7 — Softmax a mano (de puntajes a probabilidades)

### Paso 1 — Elevar a exponencial (aproximado)

En softmax:

$$
p_i = \frac{e^{s_i}}{\sum_j e^{s_j}}
$$

Use calculadora:

$$
e^3 \approx 20.09,\quad e^{0.5} \approx 1.65,\quad e^{0.2} \approx 1.22,\quad e^1 \approx 2.72
$$

| Palabra | $s_i$ | $e^{s_i} \approx$ |
|---|---:|---:|
| NIÑA | 3.0 | 20.09 |
| PEQUEÑA | 0.5 | 1.65 |
| COME | 0.2 | 1.22 |
| FRUTA | 1.0 | 2.72 |
| **Suma** |  | **25.68** |

### Paso 2 — Dividir cada uno entre la suma

Cada valor se divide entre la suma total:

$$
\text{porcentaje} = \frac{e^{s_i}}{25.68} \times 100
$$

| Palabra | $e^{s_i}$ | ÷ 25.68 | ≈ % |
|---|---:|---:|---:|
| NIÑA | 20.09 | 20.09 ÷ 25.68 | 78 % |
| PEQUEÑA | 1.65 | 1.65 ÷ 25.68 | 6 % |
| COME | 1.22 | 1.22 ÷ 25.68 | 5 % |
| FRUTA | 2.72 | 2.72 ÷ 25.68 | 11 % |
| **Total** | **25.68** |  | **100 %** |

### Paso 3 — Interpretar

- Aunque el puntaje de **COME** no era el mínimo, su porcentaje final es bajo porque **NIÑA** domina la distribución.

- Si el puntaje de **NIÑA** fuera **10** en lugar de **3**, el softmax se acercaría a “casi 100 % en una sola columna”.  
  A esto se le puede llamar **saturación**, porque una sola palabra concentra casi toda la atención.

- Por eso, en un Transformer real se divide el puntaje entre:

$$
\sqrt{d_k}
$$

Esto ayuda a que los valores no sean demasiado grandes antes de aplicar softmax, evitando que una sola palabra domine completamente la atención.

### Pregunta
**¿Por qué no basta con dividir los puntajes 0–10 entre su suma, sin exponencial? (Pista: con puntajes negativos o muy desiguales, el reparto se comporta distinto; softmax amplifica diferencias.)**

No basta porque dividir directamente solo reparte los valores de forma proporcional, pero **no cambia mucho la diferencia entre puntajes**.  
En cambio, **softmax usa exponenciales**, por eso las palabras con puntaje alto crecen mucho más que las de puntaje bajo.

Con estos puntajes:

| Palabra | Puntaje |
|---|---:|
| NIÑA | 3.0 |
| PEQUEÑA | 0.5 |
| COME | 0.2 |
| FRUTA | 1.0 |

Si solo dividimos entre la suma:

| Palabra | Cálculo simple | Resultado aprox. |
|---|---:|---:|
| NIÑA | 3.0 ÷ 4.7 | 64 % |
| PEQUEÑA | 0.5 ÷ 4.7 | 11 % |
| COME | 0.2 ÷ 4.7 | 4 % |
| FRUTA | 1.0 ÷ 4.7 | 21 % |

Pero con softmax:

| Palabra | Resultado con softmax |
|---|---:|
| NIÑA | 78 % |
| PEQUEÑA | 6 % |
| COME | 5 % |
| FRUTA | 11 % |

**Diferencia principal**

Softmax hace que **NIÑA domine más**, porque su puntaje era claramente mayor.  
Eso ayuda al modelo a concentrar más atención en las palabras realmente importantes.

Además, si hubiera puntajes negativos, dividir directamente podría dar problemas o porcentajes raros.  
Softmax convierte todos los puntajes en valores positivos usando exponenciales, por eso siempre produce una distribución válida que suma 100 %.

## Actividad 8 — Mezcla de “vectores contenido” (Values)

### Conversión de porcentajes a decimales

| Palabra | Vector V = (x, y) | % | Decimal |
|---|---:|---:|---:|
| LA | (1, 1) | 5 % | 0.05 |
| NIÑA | (4, 5) | 35 % | 0.35 |
| PEQUEÑA | (3, 4) | 10 % | 0.10 |
| COME | (5, 1) | 10 % | 0.10 |
| FRUTA | (6, 3) | 40 % | 0.40 |

### Multiplicar cada vector por su peso

| Palabra | Cálculo | Contribución |
|---|---|---:|
| LA | 0.05 × (1, 1) | (0.05, 0.05) |
| NIÑA | 0.35 × (4, 5) | (1.40, 1.75) |
| PEQUEÑA | 0.10 × (3, 4) | (0.30, 0.40) |
| COME | 0.10 × (5, 1) | (0.50, 0.10) |
| FRUTA | 0.40 × (6, 3) | (2.40, 1.20) |

### Sumar x e y por separado

| Coordenada | Suma |
|---|---:|
| x | 0.05 + 1.40 + 0.30 + 0.50 + 2.40 = **4.65** |
| y | 0.05 + 1.75 + 0.40 + 0.10 + 1.20 = **3.50** |

### Resultado final

La salida ponderada es:

**(4.65, 3.50)**

### Paso 3 — Dibuja en papel

| Palabra | Coordenadas |
|---|---:|
| LA | (1, 1) |
| NIÑA | (4, 5) |
| PEQUEÑA | (3, 4) |
| COME | (5, 1) |
| FRUTA | (6, 3) |

**Vector salida de COME**

La salida ponderada que obtuvimos fue:

**COME_salida = (4.65, 3.50)**

- Si la dibujas **desde el origen**, es una flecha de **(0, 0)** a **(4.65, 3.50)**.
- Si la dibujas **desde COME**, entonces va desde **(5, 1)** hasta **(4.65, 3.50)**.

Ese desplazamiento sería:

**(4.65 - 5,\ 3.50 - 1) = (-0.35,\ 2.50)**

**¿Queda cerca de FRUTA y NIÑA?**

Sí, la flecha queda bastante cerca de **FRUTA** y **NIÑA**.

| Comparación | Distancia aprox. |
|---|---:|
| Salida → FRUTA (6, 3) | 1.44 |
| Salida → NIÑA (4, 5) | 1.64 |
| Salida → PEQUEÑA (3, 4) | 1.72 |
| Salida → COME (5, 1) | 2.52 |

La salida de **COME** queda más cerca de **FRUTA** y **NIÑA** que de su punto original.  
Eso significa que, después de aplicar atención, **COME** mezcla información de las palabras más relevantes.  
En otras palabras: **COME entiende mejor quién come (NIÑA) y qué come (FRUTA)**.

## Actividad 9 — Máscara de padding

### Lote de dos frases

| Posición | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Frase 1 | EL | GATO | COME | PAD | PAD |
| Frase 2 | LA | NIÑA | PEQUEÑA | COME | FRUTA |

---

## Paso 1 — Matriz 5×5 solo para Frase 1

**Frase 1:** `EL GATO COME PAD PAD`

> **P** = celda anulada por padding

| Desde ↓ / Hacia → | EL | GATO | COME | PAD | PAD |
|---|---|---|---|---|---|
| **EL** |  |  |  | **P** | **P** |
| **GATO** |  |  |  | **P** | **P** |
| **COME** |  |  |  | **P** | **P** |
| **PAD** | **P** | **P** | **P** | **P** | **P** |
| **PAD** | **P** | **P** | **P** | **P** | **P** |

---

## Interpretación

Las columnas **PAD** se marcan con **P** porque ninguna palabra real debe mirar al relleno.

Las filas **PAD** también se marcan con **P** porque esas posiciones no representan palabras reales.

Así, la atención solo se calcula entre las palabras reales:

**EL**, **GATO** y **COME**.

### Paso 2 — Regla

**Regla:** La palabra real no puede prestar atención a **PAD**.

Por eso se tachan las celdas donde:

- La **fila** es una palabra real.
- La **columna** es **PAD**.

| Desde ↓ / Hacia → | EL | GATO | COME | PAD | PAD |
|---|---|---|---|---|---|
| **EL** |  |  |  | ✗ | ✗ |
| **GATO** |  |  |  | ✗ | ✗ |
| **COME** |  |  |  | ✗ | ✗ |
| **PAD** |  |  |  |  |  |
| **PAD** |  |  |  |  |  |

Las palabras reales **EL**, **GATO** y **COME** no deben mirar a las posiciones **PAD**, porque **PAD** solo es relleno y no aporta significado.

### Paso 3 — Pregunta

**¿Por qué Frase 2 no necesita tantas celdas tachadas en sus palabras reales?**

Porque la frase 2 ocupa las 5 posiciones con palabras reales:

| Posición | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Frase 2 | LA | NIÑA | PEQUEÑA | COME | FRUTA |

Como no tiene **PAD**, sus palabras reales no tienen que evitar columnas de relleno.

---

**¿Qué pasaría si el modelo atendiera mucho a PAD?**

Si el modelo prestara mucha atención a **PAD**, aprendería información falsa, porque **PAD no significa nada**; solo es relleno.

El modelo podría pensar que el relleno tiene importancia y aprender patrones incorrectos.



La frase 2 no necesita tantas celdas tachadas porque todas sus posiciones son palabras reales.  
Si el modelo atendiera mucho a **PAD**, aprendería patrones falsos del relleno y su comprensión de la frase sería peor.

## Actividad 10 — Atención cruzada (decoder mirando encoder)

### Paso 1 — Matriz rectangular 3×3

Filas: palabras del decoder.  
Columnas: palabras del encoder.

| Desde (inglés) ↓ / Español → | YO | QUIERO | CAFE |
|---|---:|---:|---:|
| I |  |  |  |
| WANT |  |  |  |
| Palabra 3 por escribir | 1 | 3 | 10 |

---

La palabra 3 por escribir en inglés debería ser **COFFEE**.

Por eso debe mirar más a **CAFE**, porque es la palabra española que da la pista principal.

### Paso 2 — Convertir a porcentajes

Fila: **Palabra 3 por escribir**  
Puntajes: YO = 1, QUIERO = 3, CAFE = 10

Suma:

**1 + 3 + 10 = 14**

| Desde (inglés) ↓ / Español → | YO | QUIERO | CAFE | Total |
|---|---:|---:|---:|---:|
| **Palabra 3 por escribir** | 1 ÷ 14 = **7.1 %** | 3 ÷ 14 = **21.4 %** | 10 ÷ 14 = **71.4 %** | **100 %** |

**¿CAFE debería ganar?** 

Sí, **CAFE debería ganar**, porque la palabra que falta en inglés es:

**COFFEE**

Entonces el decoder debe mirar principalmente a **CAFE**, ya que es la palabra española que indica qué palabra debe generar.

**¿La fila de I podría mirar mucho a YO?**

Sí, tiene sentido.

| Palabra del decoder | Palabra del encoder que debería mirar |
|---|---|
| **I** | **YO** |
| **WANT** | **QUIERO** |
| **COFFEE** | **CAFE** |

La palabra **I** puede mirar mucho a **YO**, porque son equivalentes en la traducción.

**Diferencia clave**

En **self-attention**, las filas y columnas pertenecen a la misma frase y al mismo idioma.

En **cross-attention**, las filas son palabras que el decoder está generando en otro idioma, y las columnas son palabras de la frase original del encoder.

Por eso aquí el decoder en inglés mira la frase completa en español para decidir qué palabra escribir.

## Actividad 11 — Adivinar la palabra tapada

Frase con hueco

**EL GATO ___ PESCADO**

### Paso 1 — Lista de candidatos

| Candidato | ¿Tiene sentido en la frase? | Explicación |
|---|---|---|
| **COME** | Sí | “El gato come pescado” es una oración lógica. |
| **DUERME** | No mucho | “El gato duerme pescado” no tiene sentido gramatical. |
| **VERDE** | No | “El gato verde pescado” no forma una oración correcta. |
| **RAPIDO** | No | “El gato rápido pescado” no tiene una acción clara. |

**Mejor candidato**

La palabra que mejor completa la frase es:

**COME**

Frase completa

**EL GATO COME PESCADO**

### Paso 2 — Puntuar candidatos para el hueco

Frase:

**EL GATO ___ PESCADO**

| Candidato | Puntuación 0–10 | Compatibilidad con el contexto |
|---|---:|---|
| **COME** | **10** | Tiene mucho sentido: un gato puede comer pescado. |
| **DUERME** | 2 | “El gato duerme pescado” no tiene mucho sentido con la palabra pescado. |
| **VERDE** | 1 | Puede describir algo, pero no conecta bien con gato y pescado en esta frase. |
| **RAPIDO** | 1 | Describe velocidad, pero no explica qué pasa con el pescado. |

Mejor candidato

El candidato con mayor compatibilidad es:

**COME — 10 puntos**

Porque conecta de forma lógica con **GATO** y **PESCADO**:  
el gato realiza una acción sobre el pescado.

### Paso 3 — Convertir a porcentajes

Usamos **reparto proporcional** con las puntuaciones del paso anterior.

Puntuaciones:

| Candidato | Puntuación |
|---|---:|
| COME | 10 |
| DUERME | 2 |
| VERDE | 1 |
| RAPIDO | 1 |

Suma total:

**10 + 2 + 1 + 1 = 14**

---

## Porcentajes

| Candidato | Cálculo | ≈ % |
|---|---:|---:|
| **COME** | 10 ÷ 14 × 100 | **71.4 %** |
| **DUERME** | 2 ÷ 14 × 100 | **14.3 %** |
| **VERDE** | 1 ÷ 14 × 100 | **7.1 %** |
| **RAPIDO** | 1 ÷ 14 × 100 | **7.1 %** |
| **Total** |  | **100 %** |

---

## Resultado

El candidato con mayor porcentaje es:

**COME — 71.4 %**

Por eso la frase más probable queda:

**EL GATO COME PESCADO**

### Paso 4 — Reflexión escrita

**¿Por qué COME debería superar a VERDE?
¿DUERME podría tener algo de sentido? ¿Qué atención habría entre GATO y DUERME?
¿Por qué BERT necesita ver PESCADO (derecha) aunque el hueco esté en el centro? (Bidireccional = contexto completo.)**

**COME** debería superar a **VERDE** porque conecta mejor con el sentido de la frase: un gato puede comer pescado.  
**VERDE** describe una característica, pero no explica qué relación hay entre **GATO** y **PESCADO**.  
**DUERME** podría tener algo de sentido con **GATO**, porque los gatos duermen, pero no combina bien con **PESCADO**.  
La atención entre **GATO** y **DUERME** sería media, porque sí hay relación, aunque no completa la idea de la oración.  
BERT necesita ver **PESCADO** porque usa contexto completo: mira izquierda y derecha para adivinar mejor la palabra oculta.

## Actividad 12 — Dos capas de atención (refinar la representación)

Usando los **perfiles tras capa 1**:

| Palabra | Perfil inicial | Tras capa 1 |
|---|---:|---:|
| LA | 1 | 2 |
| NIÑA | 4 | 6 |
| PEQUEÑA | 3 | 5 |
| COME | 5 | 7 |
| FRUTA | 6 | 8 |

### Paso 1 — Segunda ronda solo para FRUTA

| Desde FRUTA (capa 2) → | LA | NIÑA | PEQUEÑA | COME | FRUTA |
|---|---:|---:|---:|---:|---:|
| Puntaje 0–10 | 1 | 7 | 3 | 10 | 6 |

**FRUTA** mira más fuerte a **COME**, porque necesita saber qué acción recibe.  
También mira bastante a **NIÑA**, porque ayuda a entender quién realiza la acción de comer.  
Mira algo a sí misma porque sigue siendo importante conservar su propio significado.

**Respuesta final**

En la segunda capa, **FRUTA** debería prestar más atención a **COME**, luego a **NIÑA**, y después a sí misma.  
Esto muestra que, después de una capa, las palabras ya tienen información mezclada y pueden relacionarse mejor en la siguiente ronda.

### Paso 2 — Frase

En la segunda capa, **FRUTA** ya “sabe” que **COME** tiene perfil **7**, porque la primera capa conectó la relación **verbo–objeto**.

## Actividad 13 — RNN vs Transformer: contar conexiones

### Dibuja 5 nodos en línea

**A — B — C — D — E**

---

**Modo RNN**

Solo el vecino anterior puede pasar mensaje.

Cuenta enlaces si cada letra solo recibe mensaje directo del anterior:

**A → B, B → C, C → D, D → E**

| Camino | Enlaces |
|---|---:|
| A → B | 1 |
| B → C | 1 |
| C → D | 1 |
| D → E | 1 |
| **Total para llegar de A a E** | **4 enlaces** |

---

**Modo atención**

Una capa: todos miran a todos, sin máscara.

Cada letra puede mirar a las 5 letras:

**5 × 5 = 25 celdas**

| Modelo | Forma de conexión | Cantidad |
|---|---|---:|
| RNN | Pasa mensaje paso a paso | 4 enlaces de A a E |
| Transformer | Todos miran a todos en una capa | 25 celdas |

---

## Idea principal

En una **RNN**, la información de **A** tarda varios pasos en llegar a **E**.  
En un **Transformer**, **E** puede mirar directamente a **A** en una sola capa.  
Por eso el Transformer maneja mejor relaciones lejanas dentro de una frase.

### Preguntas

**1. Si A debe influir en E, ¿cuántos “saltos” necesita?**

| Modelo | Saltos de A a E |
|---|---:|
| **RNN** | 4 saltos: A → B → C → D → E |
| **Transformer / Atención** | 1 salto: E puede mirar directamente a A |

En una **RNN**, el mensaje pasa palabra por palabra.  
En una **capa de atención**, cualquier palabra puede mirar directamente a cualquier otra.

---

**2. ¿Qué crece más rápido con 100 palabras?**

| Modelo | Cálculo | Resultado |
|---|---:|---:|
| **RNN** | 100 enlaces secuenciales aprox. | 100 |
| **Transformer** | 100 × 100 celdas | 10,000 |

Crece más rápido la atención del **Transformer**, porque usa una tabla donde cada palabra puede mirar a todas las demás.

---

**3. ¿Por qué aun así usamos Transformers y no solo RNN?**

Usamos **Transformers** porque pueden procesar muchas palabras en paralelo y detectar relaciones lejanas de forma directa.  
Una **RNN** debe pasar la información paso a paso, lo que puede perder detalles en frases largas.  
El Transformer entiende mejor dependencias entre palabras alejadas, aunque gasta más memoria porque su tabla de atención crece mucho en textos largos.

## Actividad 14 — Escalar por $\sqrt{d_k}$

**1. Haz softmax aproximado de [8, 2, 2, 2] (cuatro palabras).
2. Haz softmax de [4, 1, 1, 1] (tras dividir entre 2).
3. Compara: ¿la palabra ganadora sigue ganando pero con menos % absoluto?**

Datos

Antes de aplicar softmax, tenemos cuatro puntajes:

| Caso | Puntajes |
|---|---|
| Sin escalar | `[8, 2, 2, 2]` |
| Escalado por $\sqrt{d_k}$ | `[4, 1, 1, 1]` |

Como:

$$
d_k = 4
$$

Entonces:

$$
\sqrt{d_k} = \sqrt{4} = 2
$$

Por eso:

$$
8 \div 2 = 4
$$

$$
2 \div 2 = 1
$$

---

1. Softmax aproximado de `[8, 2, 2, 2]`

| Puntaje | Exponencial aproximada |
|---:|---:|
| $e^8$ | 2980.96 |
| $e^2$ | 7.39 |
| $e^2$ | 7.39 |
| $e^2$ | 7.39 |

Suma:

$$
2980.96 + 7.39 + 7.39 + 7.39 = 3003.13
$$

| Palabra | Cálculo | Porcentaje aprox. |
|---|---:|---:|
| Ganadora | $2980.96 \div 3003.13$ | **99.26 %** |
| Otra | $7.39 \div 3003.13$ | **0.25 %** |
| Otra | $7.39 \div 3003.13$ | **0.25 %** |
| Otra | $7.39 \div 3003.13$ | **0.25 %** |

---

2. Softmax aproximado de `[4, 1, 1, 1]`

| Puntaje | Exponencial aproximada |
|---:|---:|
| $e^4$ | 54.60 |
| $e^1$ | 2.72 |
| $e^1$ | 2.72 |
| $e^1$ | 2.72 |

Suma:

$$
54.60 + 2.72 + 2.72 + 2.72 = 62.76
$$

| Palabra | Cálculo | Porcentaje aprox. |
|---|---:|---:|
| Ganadora | $54.60 \div 62.76$ | **87.0 %** |
| Otra | $2.72 \div 62.76$ | **4.3 %** |
| Otra | $2.72 \div 62.76$ | **4.3 %** |
| Otra | $2.72 \div 62.76$ | **4.3 %** |

---

3. Comparación

| Caso | Palabra ganadora | Reparto |
|---|---:|---|
| Sin escalar `[8, 2, 2, 2]` | **99.26 %** | Casi toda la atención se va a una sola palabra. |
| Escalado `[4, 1, 1, 1]` | **87.0 %** | La palabra ganadora sigue ganando, pero las demás aún reciben algo de atención. |

---

Sí, la palabra ganadora sigue ganando después de escalar, pero con un porcentaje menos extremo.  
Sin escalar, el softmax se satura y casi toda la atención cae en una sola palabra.  
Al dividir entre $\sqrt{d_k}$, los puntajes se reducen antes del softmax, haciendo que el reparto sea más equilibrado.
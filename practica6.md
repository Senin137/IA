# ACTIVIDAD 2: EL ENIGMA DEL ORÁCULO SECUENCIAL:
                    ANATOMÍA DE UNA VANILLA RNN
                    Eladio Martinez Ambriz

## 1. El Acertijo: El Guardián del Tiempo

Lee atentamente las siguientes líneas. Cada estrofa describe un componente matemático exacto de una celda recurrente básica. ¿Puedes identificar a qué variable, matriz o función se refiere cada una antes de leer la disección?

---

### Estrofa 1

> Soy la novedad pura, el pulso del instante,  
> la matriz de características que el mundo me da en este segundo.

**Respuesta:** Vector de entrada en `X_t`.

---

### Estrofa 2

> Pero soy ciego sin mi compañero,  
> el fantasma del pasado,  
> que trae consigo el resumen de todo lo que hemos vivido hasta ayer.

**Respuesta:** `H_{t-1}`, estado oculto del paso anterior.

---

### Estrofa 3

> Para unirnos, cruzamos por peajes inmutables,  
> barreras que multiplican nuestra importancia  
> y deciden qué tanto valemos.

**Respuesta:** `W` y `U`, matrices de pesos.

---

### Estrofa 4

> Juntos, sumados a un pequeño desvío inevitable,  
> chocamos contra un muro curvo que nos comprime entre el `-1` y el `1`,  
> evitando que nuestra energía explote hacia el infinito.

**Respuesta:** `b_h`, `b_y` y `tanh`, vectores de sesgo.

---

### Estrofa 5

> Al salir de esa curva, nazco yo, una nueva identidad.  
> Soy tu estado actual, la respuesta de hoy,  
> y estoy listo para ser el fantasma de tu mañana.

**Respuesta:** `H_t`, estado oculto en el tiempo actual.

## 2.1 Actividad 2.1: Mapeo de Variables

  Dada la ecuación fundamental de la Vanilla RNN: $$h_t = \tanh(W_{hx}
  x_t + W_{hh} h_{t-1} + b)$$

  Identifica y escribe la frase exacta del poema que hace referencia a
  cada uno de los siguientes componentes matemáticos:

  $x_t$
>  Soy la novedad pura, el pulso del instante,  
> la matriz de características que el mundo me da en este segundo.
       
  $h_{t-1}$:
> Pero soy ciego sin mi compañero,  
> el fantasma del pasado,  
> que trae consigo el resumen de todo lo que hemos vivido hasta ayer.
        
  $W_{hx}, W_{hh}$:
> Para unirnos, cruzamos por peajes inmutables,  
> barreras que multiplican nuestra importancia  
> y deciden qué tanto valemos.

  $b$:
> Juntos, sumados a un pequeño desvío inevitable,  
> chocamos contra un muro curvo que nos comprime entre el `-1` y el `1`.

$\tanh$:
>Un muro curvo que nos comprime entre el `-1` y el `1`,  
> evitando que nuestra energía explote hacia el infinito

  $h_t$:
> Al salir de esa curva, nazco yo, una nueva identidad.  
> Soy tu estado actual, la respuesta de hoy,  
> y estoy listo para ser el fantasma de tu mañana.

## 2.2 Actividad 2.2: El Análisis de Dimensionalidad (El tamaño de los peajes)

  Supón que estás diseñando esta red para procesar secuencias de
  datos. Si la "novedad pura" ($x_t$) es un vector de entrada con
  características de dimensión $\mathbb{R}^{20}$ y decides que el
  "fantasma del pasado" ($h_{t-1}$) requiere una capacidad de memoria
  representada en un espacio oculto de dimensión $\mathbb{R}^{64}$.

  Calcula y justifica matemáticamente:
  1. Las dimensiones exactas requeridas para la matriz $W_{hx}$.
  2. Las dimensiones exactas requeridas para la matriz recurrente
     $W_{hh}$.
  3. La dimensión final del vector resultante $h_t$.

**1.**
Cálculo: Para que la multiplicación sea posible, el número de columnas de $W_{hx}$ debe coincidir con la dimensión de $x_t$ ($20$). Para que el resultado pueda sumarse al estado oculto, el número de filas debe ser igual a la dimensión de dicho estado ($64$).
**Resultado: $W_{hx} \in \mathbb{R}^{64 \times 20}$.**  

**2.**
Cálculo: Como el estado oculto previo tiene dimensión $64$ y el resultado de la operación debe mantenerse en ese mismo espacio de dimensión $64$ para la suma, la matriz debe ser cuadrada.
**Resultado: $W_{hh} \in \mathbb{R}^{64 \times 64}$.**

**3.**
El vector $h_t$ es el producto de la suma interna tras pasar por la función de activación $\tanh$.Justificación: 1. El producto $W_{hx} x_t$ resulta en un vector de $(64 \times 20) \times (20 \times 1) = \mathbf{64 \times 1}$.2. El producto $W_{hh} h_{t-1}$ resulta en un vector de $(64 \times 64) \times (64 \times 1) = \mathbf{64 \times 1}$.3. Al sumar ambos vectores (y el sesgo $b$, que también debe ser $64 \times 1$), obtenemos un vector en $\mathbb{R}^{64}$.4. La función $\tanh$ se aplica elemento a elemento, por lo que no altera la forma del vector.
**Resultado: $h_t \in \mathbb{R}^{64}$**.

## 2.3 Actividad 2.3: La Estrofa Perdida (Pensamiento Lateral)

En el poema original, el vector de sesgo (bias) $b$ apenas se menciona
  como "un pequeño desvío inevitable". Sabiendo que en álgebra lineal el
  sesgo permite desplazar la función de activación para evitar que pase
  rígidamente por el origen, **redacta una estrofa corta** (manteniendo
  el tono literario del acertijo) que describa de manera exclusiva la
  función y utilidad del parámetro $b$.

**El Impulso Silencioso (El Sesgo $b$)**
Soy el leve empuje lateral, la constante que rompe la simetría,para que el muro no nos dicte un origen de rígida monotonía.Sin traer datos ni recuerdos, inclino con sutileza la balanza,dándole al cero un nuevo sitio y al aprendizaje una libre danza.

## 2.4 Actividad 2.4: El Límite del Muro Curvo (Análisis de Saturación)

El acertijo menciona que el muro curvo ($\tanh$) evita que "nuestra
  energía explote hacia el infinito".
  1. Grafica mentalmente o en papel la función $f(z) = \tanh(z)$ y su
     derivada $f'(z) = 1 - \tanh^2(z)$.
  2. Si los valores de entrada y los pesos crecen descontroladamente y
     el resultado de la suma lineal es $z = 500$, la salida del muro
     curvo será casi exactamente $1$. ¿Qué le sucede a la derivada
     $f'(500)$ en ese punto?
  3. Explica brevemente por qué este fenómeno (conocido como saturación) es catastrófico para el aprendizaje de la red.

### 1. Comportamiento de la Función y su Derivada

$f(z) = \tanh(z)$: Es una curva en forma de "S" que se estira hacia el 1 cuando $z$ es positivo y hacia el -1 cuando $z$ es negativo.
$f'(z) = 1 - \tanh^2(z)$: Es una campana centrada en el origen. Su valor máximo es 1 (cuando $z=0$) y decae rápidamente hacia 0 a medida que nos alejamos del centro.

### 2. El Cálculo en el Punto Crítico ($z = 500$)
La Salida: $\tanh(500)$ es un valor tan cercano a $1$ que, para la precisión de cualquier computadora estándar, se redondea a $1.0$.La Derivada: Aplicamos la fórmula:
$$f'(500) = 1 - \tanh^2(500)$$$$f'(500) \approx 1 - (1)^2 = 0$$
En este punto, la pendiente de la curva es prácticamente horizontal. La derivada es, para efectos prácticos, cero.

### 3. ¿Por qué es catastrófico para el aprendizaje?

El aprendizaje en una red neuronal ocurre mediante el algoritmo de Backpropagation (Propagación hacia atrás). Este proceso utiliza la Regla de la Cadena para calcular cuánto debe cambiar cada peso para reducir el error.
El cálculo del gradiente (la señal de aprendizaje) siempre incluye una multiplicación por la derivada de la función de activación:
$$\Delta W \propto \text{Error} \cdot \mathbf{f'(z)} \cdot \text{Entrada}$$
Si $f'(z)$ es 0 (o un número extremadamente pequeño):
El gradiente se desvanece: Al multiplicar por cero, todo el gradiente se vuelve cero.

Muerte de la neurona: Los pesos no reciben ninguna actualización. El "peaje" deja de ajustar su precio porque no recibe información sobre si lo está haciendo bien o mal.

Desvanecimiento del gradiente (Vanishing Gradient): En las RNN, este problema se multiplica a través del tiempo. Si la señal desaparece en un paso, el "fantasma del pasado" no puede informar a las capas anteriores, y la red pierde su capacidad de aprender dependencias a largo plazo.

## 2.5 Actividad 2.5: El Eco del Castigo (Trazo del Gradiente)

El aprendizaje en una RNN se realiza propagando el error hacia atrás en el tiempo (BPTT). Supón que la red cometió un error en su "respuesta de hoy" ($h_t$). Para corregirlo, la red debe enviar una señal de castigo hacia atrás para ajustar los pesos.  Siguiendo la narrativa del acertijo: Describe qué "peajes" y "muros" debe atravesar el error en reversa para llegar desde $h_t$ y poder modificar la percepción del "fantasma del pasado" ($h_{t-1}$). ¿Qué operación matemática del cálculo diferencial representa este viaje en reversa?

**Respuesta**
En una celda recurrente, la novedad ($x_t$) y el pasado ($h_{t-1}$) se fusionan mediante matrices de pesos que actúan como "peajes" para proyectar los datos a un espacio de memoria común (como $\mathbb{R}^{64}$), sumándose junto a un sesgo ($b$) que permite a la red desplazar su activación y no quedar anclada al origen. Esta suma atraviesa el "muro" de la función $\tanh$, que comprime los valores entre $-1$ y $1$ para mantener la estabilidad numérica, generando así la nueva identidad del sistema ($h_t$). Para aprender, la red utiliza la Regla de la Cadena en reversa (BPTT), enviando un "eco" de error que debe multiplicar la derivada de la $\tanh$ por la transpuesta de los pesos; no obstante, si los valores son muy altos o bajos, la curva se vuelve plana, la derivada se desvanece a cero y el aprendizaje se detiene, provocando que el presente sea incapaz de corregir la percepción del "fantasma" del pasado. Que es basicamente lo que hemos estado resolviendo en los ejercicios anteriores.

## 2.6 Actividad 2.6: Depuración del Oráculo (Inspección de Código NumPy)

  A continuación se presenta un intento de programar el oráculo en
  Python. Sin embargo, el programador junior cometió **un grave error
  algorítmico y matemático** en la línea 4 que provocará un colapso en
  la dimensionalidad o un cálculo erróneo.

  ┌────
  │ def paso_rnn_erroneo(x_t, h_prev, W_hx, W_hh, b):
  │     # Línea con error oculto
  │     combinacion = (W_hx * x_t) + (W_hh * h_prev) + b
  │     return np.tanh(combinacion)
  └────

  1. Identifica cuál es el error matemático exacto al usar el operador
     `*' en NumPy para este contexto matricial.
  2. Reescribe la línea de código utilizando la operación correcta
     dictada por el álgebra lineal para transformaciones afines.

**Respuestas:**
**1.**
En NumPy, el operador * realiza una multiplicación de Hadamard (elemento a elemento) y aplica broadcasting si las dimensiones lo permiten.

Lo que hace el código erróneo: Si W_hx es una matriz de $64 \times 20$ y x_t es un vector de $20$, NumPy intentará multiplicar cada fila de la matriz por el vector elemento por elemento. El resultado será una matriz de $64 \times 20$, no un vector de $64$.

El colapso: Al intentar sumar esa matriz de $64 \times 20$ con el resultado de W_hh * h_prev (que sería una matriz de $64 \times 64$), el programa lanzará un ValueError debido a la incompatibilidad de formas (shape mismatch).

La intención matemática: Lo que buscamos es una transformación afín, donde cada peso de la matriz se combine con cada característica de la entrada para colapsar en una sola neurona. Esto requiere un producto de matrices (dot product).

**2.**
Para realizar la operación correcta de acuerdo a la fórmula $z = Wx + Uh + b$, debemos usar el operador @ (introducido en Python 3.5 específicamente para esto) o la función np.dot().

***import numpy as np***

***def paso_rnn_corregido(x_t, h_prev, W_hx, W_hh, b):
    # Usamos el operador '@' para el producto punto matricial (dot product)
    combinacion = (W_hx @ x_t) + (W_hh @ h_prev) + b***
    ***return np.tanh(combinacion)***
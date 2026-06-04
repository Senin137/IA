# EDA: Clasificación de dígitos 1, 2 y 3

## 1. Descripción del problema

El objetivo de este análisis es revisar un conjunto de imágenes que contienen dígitos escritos a mano.
En este caso, solo se trabajará con tres clases:

* 1
* 2
* 3

La finalidad es preparar los datos para que posteriormente un modelo de aprendizaje automático pueda identificar correctamente qué número aparece en cada imagen.

Este problema corresponde a una tarea de **clasificación supervisada**, ya que cada imagen tiene una etiqueta conocida.

---

## 2. Variables del conjunto de datos

### Variables de entrada (X)

Las variables de entrada son los píxeles de cada imagen.
Si las imágenes tienen un tamaño de **28 x 28 píxeles**, entonces cada una contiene **784 valores**.

Cada píxel representa la intensidad de color de una parte de la imagen.

| Variable            | Descripción                           |
| ------------------- | ------------------------------------- |
| pixel_1 a pixel_784 | Intensidad de cada píxel de la imagen |

---

### Variable de salida (y)

La variable de salida indica el número que aparece en la imagen.

| Clase | Significado         |
| ----- | ------------------- |
| 1     | Imagen del número 1 |
| 2     | Imagen del número 2 |
| 3     | Imagen del número 3 |

---

## 3. Análisis visual

Al observar las imágenes, se pueden identificar características generales de cada número.

### Número 1

El número 1 normalmente tiene una forma simple, basada principalmente en una línea vertical.

Características:

* Trazo recto o ligeramente inclinado.
* Pocos píxeles activos.
* Menor complejidad visual.

### Número 2

El número 2 suele tener una curva en la parte superior y una base horizontal.

Características:

* Curva superior.
* Trazo diagonal o curvo hacia abajo.
* Línea inferior marcada.

### Número 3

El número 3 generalmente está formado por dos curvas.

Características:

* Curva superior.
* Curva inferior.
* Forma más redondeada.

---

## 4. Distribución de clases

Es importante revisar si el conjunto de datos tiene una cantidad similar de ejemplos para cada clase.

| Clase | Cantidad esperada |
| ----- | ----------------- |
| 1     | Similar           |
| 2     | Similar           |
| 3     | Similar           |

Si una clase tiene muchos más ejemplos que las demás, el modelo podría aprender mejor esa clase y cometer más errores con las clases que tengan menos datos.

---

## 5. Posibles dificultades

Durante el análisis pueden encontrarse algunos problemas que afecten la clasificación.

| Problema                        | Explicación                                              |
| ------------------------------- | -------------------------------------------------------- |
| Similitud entre 2 y 3           | Ambos números tienen curvas y pueden confundirse         |
| Imágenes borrosas               | Dificultan reconocer la forma del número                 |
| Diferentes estilos de escritura | Cada persona escribe los números de manera distinta      |
| Números mal centrados           | El modelo puede interpretar mal la imagen                |
| Ruido en los píxeles            | Algunos píxeles pueden no pertenecer realmente al número |

---

## 6. Preparación de los datos

Antes de entrenar un modelo, es recomendable realizar algunos pasos básicos:

* Revisar que las etiquetas sean correctas.
* Verificar que las imágenes sean claras.
* Normalizar los valores de los píxeles.
* Separar los datos en entrenamiento y prueba.
* Visualizar ejemplos de cada clase.

La normalización ayuda a que los valores de los píxeles estén en un rango más manejable, por ejemplo de **0 a 1**.

---

## 7. Modelos posibles

Para este problema se pueden utilizar distintos modelos de clasificación, como:

* KNN
* SVM
* Árboles de decisión
* Random Forest
* Redes neuronales
* Redes neuronales convolucionales

Para imágenes, una red neuronal convolucional puede ser una buena opción, ya que está diseñada para detectar patrones visuales.

---

## 8. Conclusión

El análisis exploratorio permite conocer mejor el conjunto de datos antes de entrenar un modelo.

En este caso, el número **1** probablemente sea el más fácil de identificar por su forma simple. En cambio, los números **2** y **3** pueden presentar más confusión debido a sus curvas y formas similares.

Revisar la distribución de clases, la calidad de las imágenes y los posibles errores ayuda a preparar mejor los datos y mejorar el desempeño del modelo de clasificación.

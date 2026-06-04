# EDA: Problema del muñeco y la bala

## 1. Descripción del problema

En este problema se analiza un sistema donde un muñeco debe reaccionar ante una bala que se aproxima.

La bala puede pasar a diferentes alturas y velocidades, por lo que el muñeco debe elegir una acción adecuada para evitar ser golpeado.

Las acciones posibles son:

* **Brincar**
* **Agacharse**
* **Quedarse quieto**

El objetivo es predecir qué acción debe realizar el muñeco según las características de la bala.

---

## 2. Objetivo del análisis

El propósito del EDA es identificar la relación entre la altura de la bala, su velocidad y la acción que debería tomar el muñeco.

Este análisis ayuda a entender los datos antes de entrenar un modelo de clasificación.

---

## 3. Variables del problema

### Variables de entrada (X)

| Variable       | Descripción                           |
| -------------- | ------------------------------------- |
| altura_bala    | Altura a la que pasa la bala          |
| velocidad_bala | Velocidad con la que se mueve la bala |
| distancia_bala | Qué tan cerca está la bala del muñeco |

Estas variables permiten saber qué tan peligrosa es la bala y cuánto tiempo tiene el muñeco para reaccionar.

---

### Variable de salida (y)

La variable de salida representa la acción que debe tomar el muñeco.

| Acción    | Significado                                         |
| --------- | --------------------------------------------------- |
| brincar   | El muñeco salta para evitar una bala baja           |
| agacharse | El muñeco se agacha para evitar una bala media      |
| quedarse  | El muñeco no se mueve porque no hay peligro directo |

---

## 4. Análisis de la altura de la bala

La altura de la bala es una de las variables más importantes, ya que determina qué parte del cuerpo podría ser alcanzada.

| Altura de la bala | Interpretación                    |
| ----------------- | --------------------------------- |
| Baja              | Puede golpear las piernas         |
| Media             | Puede golpear el torso            |
| Alta              | Puede pasar por encima del muñeco |

De acuerdo con esto, se puede establecer una acción esperada para cada caso.

---

## 5. Relación entre altura y acción

| Altura | Acción esperada |
| ------ | --------------- |
| Baja   | Brincar         |
| Media  | Agacharse       |
| Alta   | Quedarse quieto |

Esta relación puede servir como base para crear las etiquetas del conjunto de datos.

---

## 6. Importancia de la velocidad

La velocidad de la bala también influye en la decisión.
Si la bala se mueve muy rápido, el muñeco tendrá menos tiempo para reaccionar.

Por ejemplo:

* Una bala lenta permite una reacción más sencilla.
* Una bala rápida puede provocar errores en la acción.
* En velocidades muy altas, la distancia también se vuelve importante.

---

## 7. Posibles problemas en los datos

Durante el análisis pueden aparecer algunos problemas que afecten la predicción.

| Problema           | Explicación                                           |
| ------------------ | ----------------------------------------------------- |
| Altura mal medida  | Puede generar una acción incorrecta                   |
| Velocidad muy alta | Reduce el tiempo disponible para reaccionar           |
| Casos límite       | Puede haber confusión entre brincar o agacharse       |
| Datos repetidos    | Pueden afectar el entrenamiento del modelo            |
| Falta de ejemplos  | El modelo podría no aprender bien algunas situaciones |

---

## 8. Conclusión

Este problema puede tratarse como una tarea de **clasificación supervisada**, ya que se busca predecir una acción a partir de variables conocidas.

La altura de la bala es la variable principal para decidir si el muñeco debe brincar, agacharse o quedarse quieto. Sin embargo, la velocidad y la distancia también son importantes porque afectan el tiempo de reacción.

Un buen análisis de los datos permite detectar casos confusos, corregir errores y preparar mejor el conjunto de datos antes de entrenar el modelo.

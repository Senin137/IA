## Misión 1: El Lunes Increíble (El Olvido)

El sentimiento de alegría se va diluyendo rápidamente mientras los días pasan, ya que se le da más importancia al presente que al pasado cuando aparecen nuevos estímulos.

**Cálculos**

- Día 1 (Lunes):  
  $h_1 = 10 + (0.5 \times 0) = \mathbf{10}$

- Día 2 (Martes):  
  $h_2 = 0 + (0.5 \times 10) = \mathbf{5}$

- Día 3 (Miércoles):  
  $h_3 = 0 + (0.5 \times 5) = \mathbf{2.5}$

- Día 4 (Jueves):  
  $h_4 = 0 + (0.5 \times 2.5) = \mathbf{1.25}$

- Día 5 (Viernes):  
  $h_5 = 0 + (0.5 \times 1.25) = \mathbf{0.625}$

---

## Misión 2: El Rescate Emocional

Primero, calculamos el arrastre:

- Día 1:  
  $h_1 = -6$

- Día 2:  
  $h_2 = -4 + (0.5 \times -6) = -4 - 3 = \mathbf{-7}$  
  *(¡Día difícil!)*

- Día 3:  
  $h_3 = 0 + (0.5 \times -7) = \mathbf{-3.5}$

**Queremos que el Día 4 sea positivo**

$$
h_4 = x_4 + (0.5 \times -3.5) > 0
$$

$$
x_4 - 1.75 > 0
$$

$$
x_4 > 1.75
$$

El evento del Día 4 debe tener una magnitud mayor a **+1.75** para que finalmente logres irte a dormir con un estado de ánimo positivo. Cualquier cosa por debajo de eso no será suficiente para vencer el bajón acumulado.

---

## Misión 3: Constancia vs. El Pico

Ya fue calculado en la **Misión 1**.

**Estado final del Día 5:**  
$0.625$

### Escenario B: Pequeñas Alegrías

- Día 1:  
  $h_1 = 3 + 0 = \mathbf{3}$

- Día 2:  
  $h_2 = 3 + (0.5 \times 3) = \mathbf{4.5}$

- Día 3:  
  $h_3 = 3 + (0.5 \times 4.5) = \mathbf{5.25}$

- Día 4:  
  $h_4 = 3 + (0.5 \times 5.25) = \mathbf{5.625}$

- Día 5:  
  $h_5 = 3 + (0.5 \times 5.625) = \mathbf{5.8125}$

  **Conclusión**

  El escenario B gana. Como Vanilla RNN, prefiero la información reciente y constante. El pico del lunes se perdió en la coctelera del tiempo, mientras que los pequeños +3 diarios se fueron acumulando hasta estabilizarse.
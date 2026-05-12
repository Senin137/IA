# Banco de Preguntas para Evaluación de RAG: Violencia en México

Este documento contiene las consultas de prueba para el sistema RAG entrenado con el corpus sobre violencia en México. El objetivo es evaluar la precisión del vector store y la mitigación de alucinaciones del modelo base.

## Nivel 1: Extracción de Datos Directos (Factoid)

Estas preguntas evalúan si el RAG es capaz de recuperar la métrica o el dato exacto sin perderse en el ruido del corpus.

**Q1: ¿Cuáles son las tres entidades federativas con mayor índice de homicidios dolosos según los datos más recientes incluidos en el corpus?**

Según los datos más recientes del gobierno mexicano incluidos en el Corpus, las tres entidades federativas con mayor índice de homicidios dolosos son:

Chihuahua
Durango
Sinaloa

**Q2: ¿Qué organizaciones, cárteles o grupos delictivos se mencionan con mayor frecuencia operando en la región de Tierra Caliente?**

Según los datos incluidos en el corpus, las organizaciones que se mencionan con mayor frecuencia operando en la región de Tierra Caliente o en Michoacán son:

Los Caballeros Templarios
La Familia Michoacana
CJNG (Cártel Jalisco Nueva Generación)
Los Zetas

**Q3: ¿Cuáles son las cifras oficiales reportadas sobre el desplazamiento forzado interno a causa de la violencia durante el último sexenio documentado?**

Según los datos incluidos en el corpus, se menciona que alrededor del 2015 y 2020 alrededor de 1.2 millones de personas fueron desplazadas debido a la violencia.

## Nivel 2: Síntesis y Relación de Conceptos   
Estas consultas obligan al sistema a recuperar múltiples fragmentos (chunks) de diferentes documentos y fusionarlos de manera coherente.

**Q4: Según los documentos, ¿cuáles son las principales causas socioeconómicas que los autores asocian directamente al incremento de la violencia urbana?**

Según el corpus, las principales causas socioeconómicas que los autores asocian directamente al incremento de la violencia urbana son:

La falta de trabajo y bajos salarios
La pobreza
La inequidad socioeconómica

**Q5: Contrasta las estrategias de seguridad pública mencionadas en el corpus. ¿Qué diferencias de enfoque existen entre la militarización y las políticas de prevención social?**

Según el corpus, se menciona que la militarización de la seguridad pública implica:

Un enfoque más represivo y autoritario
Un énfasis en la repressión del delito a través de la fuerza militar
Una visión más estrecha del problema del delito
Por otro lado, las políticas de prevención social mencionadas en el corpus implica:

Un enfoque más integral y multidisciplinario
Un énfasis en la prevención del delito a través de programas sociales y de desarrollo comunitario
Una visión más amplia y compleja del problema del delito, que incluye factores socioeconómicos y sociales.
Se destaca que las políticas de prevención social intentan abordar las causas profundas del delito, mientras que la militarización se enfoca en los síntomas.

**Q6: ¿Cómo ha evolucionado la tasa de delitos de extorsión (cobro de piso) a nivel nacional y qué sectores económicos se reportan como los más afectados?**

Según el corpus, se menciona que:

La tasa de delitos de extorsión ha aumentado significativamente en México en los últimos años.
Los sectores económicos más afectados son:
Industrias manufactureras (como automóviles y calzado)
Sector agrícola
Sectores de hidrocarburos
Turismo
Se reporta que estos sectores han sido particularmente vulnerables a la extorsión, lo que ha llevado a una disminución en la inversión y el crecimiento económico en estas áreas.

**Q7: ¿Existe alguna diferencia significativa documentada en los tipos de violencia que experimentan las zonas rurales en comparación con las zonas metropolitanas?**

Según el corpus, se menciona que:

Las zonas rurales suelen ser afectadas por una variedad de violencias diferentes a las que enfrentan las zonas metropolitanas.
En particular, las zonas rurales están más expuestas a:
Violencia relacionada con la propiedad y el control del territorio
Violencia relacionada con los conflictos entre comunidades y bandas criminales
Violencia relacionada con la explotación laboral y la pobreza
En contraste, las zonas metropolitanas suelen ser más afectadas por:

Violencia relacionada con el tráfico de drogas y el crimen organizado
Violencia relacionada con la extorsión y el cohecho
Violencia relacionada con los conflictos internos entre grupos armados
Se destaca que las zonas rurales enfrentan una violencia más estructural y sistémica, mientras que las zonas metropolitanas se ven afectadas por una violencia más dinámica y relacionada con la delincuencia organizada.

**Q8: Con base en las posturas de las ONGs y las fuentes gubernamentales presentes en los textos, ¿cuáles son las principales contradicciones o discrepancias en el registro de víctimas?**

Según el corpus, se menciona que hay algunas contradicciones y discrepancias en el registro de víctimas relacionadas con la violencia contra las mujeres y las comunidades:

Las fuentes gubernamentales suelen subestimar la magnitud del problema de la violencia contra las mujeres, lo que lleva a una falta de priorización adecuada en los esfuerzos de prevención y atención.
Las ONGs y las organizaciones de derechos humanos argumentan que este subestimación se debe a un enfoque excesivamente legalista y no suficientemente enfocado en la prevención y el tratamiento integral de las víctimas, lo que puede llevar a una falta de resolución efectiva de los casos.
También se menciona que hay una inconsistencia en la clasificación de las víctimas, con algunas fuentes que las clasifican como “femígenas” y otras que las consideran “victimas de violencia familiar”, lo que puede llevar a una falta de coherencia en el registro y la atención de las víctimas.
En general, se destaca que hay un desafío para encontrar un registro preciso y coherente de las víctimas de violencia, debido a la complejidad del problema y la variedad de perspectivas y prioridades entre las fuentes gubernamentales y las ONGs.

**Q9: ¿Qué impacto específico tiene la violencia documentada sobre la tasa de deserción escolar en las zonas de alto conflicto? (Nota: Evalúa si el corpus cubre temas educativos o si el RAG alucina una respuesta).**

La violencia documentada en las zonas de alto conflicto puede tener un impacto significativo en la tasa de deserción escolar. Según algunos estudios, la exposición a la violencia y el miedo pueden llevar a los estudiantes a abandonar la escuela debido a la inseguridad y el estrés que conlleva la situación conflictiva.

Además, la falta de acceso a la educación de calidad en las zonas de alto conflicto puede contribuir a la tasa de deserción escolar. La violencia y el miedo pueden llevar a los padres o tutores a priorizar la seguridad de sus hijos sobre su educación, lo que puede resultar en una falta de compromiso con la escuela.

Otro factor a considerar es que la violencia puede afectar la salud mental y emocional de los estudiantes, lo que puede llevar a problemas de ansiedad, depresión y trastornos del comportamiento. Esto puede hacer más probable que los estudiantes abandonen la escuela debido a la carga emocional y psicológica.

En el caso específico del contexto proporcionado, la violencia relacionada con las drogas en México y su impacto en las zonas de alto conflicto puede estar asociado con una tasa de deserción escolar más alta. La falta de seguridad y la inseguridad pueden llevar a los estudiantes a abandonar la escuela, lo que puede tener consecuencias negativas para su futuro educativo y profesional.

Es importante destacar que la relación entre la violencia y la tasa de deserción escolar es compleja y puede variar dependiendo de factores como la gravedad de la violencia, el acceso a la educación de calidad y la capacidad del sistema educativo para adaptarse a las necesidades de los estudiantes en situaciones conflictivas.

**(El rag medio alucino la respuesta, en el corpus que agregue no venía tanta información acerca de la violencia en el ambito educativo).**

**Q10: A partir de las conclusiones de los autores en el corpus, ¿qué vacíos de información, subregistros o falta de datos fiables se identifican como el principal obstáculo para medir la violencia real en el país?**

Según la investigación realizada por Zepeda-Mercado y Montes de Oca-López (2024), los autores identifican algunos vacíos de información, subregistros o falta de datos fiables que se traducen en un principal obstáculo para medir la violencia real en el país. Algunos de estos son:

Falta de definición clara de la violencia: La investigación destaca la necesidad de una definición clara y concisa de la violencia, lo que no se encuentra en la mayoría de los estudios y reportes sobre seguridad pública.
Dificultad para cuantificar la violencia: Los autores señalan que es difícil cuantificar la violencia debido a la naturaleza desorganizada de los datos disponibles, como la falta de información completa y precisa sobre los incidentes violentos, las víctimas y los responsables.
Inconsistencia en la clasificación de los homicidios: La investigación muestra que hay inconsistencias en la clasificación de los homicidios, lo que puede llevar a malas conclusiones sobre la tasa de violencia.
Falta de datos sobre la desigualdad de género: Aunque el estudio analiza la desigualdad laboral en México desde una perspectiva de género, hay un vacío en la información sobre cómo afecta a las mujeres y niñas específicamente.
Limitaciones en la disponibilidad de datos de vigilancia policial: Los autores destacan que la mayoría de los datos sobre seguridad pública provienen de fuentes policiacas, lo que puede llevar a sesgos y falta de precisión en la información disponible.
En resumen, estos vacíos de información y subregistros pueden afectar la precisión y la confiabilidad de las estadísticas sobre violencia en México.

## Notas para la evaluación

**Medir los tiempos de latencia y mostrar los chunks de texto que el sistema recuperó para justificar cada respuesta.**

El RAG tardo aproximadamente entre 3 a 5 minutos en responder entre cada pregunta, dependiendo de la complejidad de esta. Los chunks que estoy utilizando son aproximadamente 500.
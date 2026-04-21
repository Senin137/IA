import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Generación de Datos Base (Señal Limpia)
np.random.seed(42)
tiempo = pd.date_range(start='2026-04-15', periods=500, freq='min')
# Tendencia + Oscilación + Ruido base
valores = np.linspace(10, 50, 500) + np.sin(np.linspace(0, 20, 500))*5 + np.random.normal(0, 2, 500)

df = pd.DataFrame({'Timestamp': tiempo, 'Lectura': valores})
df.set_index('Timestamp', inplace=True)

# 2. Inspección Temporal (¿Hay valores atípicos o estacionalidad?)
plt.figure(figsize=(10, 4))
plt.plot(df.index, df['Lectura'], label='Señal Cruda del Sensor', color='#2ca02c')
plt.title("Inspección Visual de la Serie de Tiempo")
plt.xlabel("Tiempo")
plt.ylabel("Amplitud")
plt.grid(True)
plt.show()

# 3. Análisis de Distribución (¿El ruido es normal?)
plt.figure(figsize=(6, 4))
sns.histplot(df['Lectura'], kde=True, bins=30)
plt.title("Histograma y Densidad de las Lecturas")
plt.show()

# 4. Estadística Descriptiva (El perfil del dataset)
print("=== Perfil Estadístico del Dataset ===")
print(df.describe())

# 2. INYECCIÓN DE ANOMALÍAS INTENCIONALES

# Anomalía A: Outliers (Picos de ruido masivo)
# Simulamos un error de voltaje que dispara la lectura a 120
df.iloc[100:105, 0] = 120 

# Anomalía B: Fallo de Sensor (Flatline / Congelamiento)
# El sensor se queda pegado en un valor fijo durante 50 minutos
df.iloc[250:300, 0] = 30.0

# Anomalía C: Datos Faltantes (Pérdida de conexión/NaN)
# Simulamos un apagón donde no se registró nada
df.iloc[400:420, 0] = np.nan

# 3. VISUALIZACIÓN Y ANÁLISIS (EDA)

# Inspección Temporal
plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Lectura'], label='Señal con Anomalías', color='#d62728', linewidth=1.5)
plt.axvspan(df.index[100], df.index[105], color='yellow', alpha=0.3, label='Outlier')
plt.axvspan(df.index[250], df.index[300], color='blue', alpha=0.1, label='Flatline')
plt.axvspan(df.index[400], df.index[420], color='gray', alpha=0.2, label='Missing Data')

plt.title("EDA: Detección Visual de Anomalías en la Serie de Tiempo")
plt.xlabel("Tiempo (HH:MM)")
plt.ylabel("Amplitud (Lectura)")
plt.legend()
plt.grid(True, linestyle='--')
plt.show()

# Análisis de Distribución (Notarás cómo el outlier de 120 deforma el histograma)
plt.figure(figsize=(8, 4))
sns.histplot(df['Lectura'].dropna(), kde=True, color='#d62728')
plt.title("Impacto de Anomalías en la Distribución de Datos")
plt.show()

# Perfil Estadístico
print("=== Perfil Estadístico con Anomalías ===")
print(df.describe())

print("\n=== Conteo de Valores Nulos (NaN) ===")
print(df.isnull().sum())
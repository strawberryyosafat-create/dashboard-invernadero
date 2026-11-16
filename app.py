import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from datos import cargar_datos

st.set_page_config(page_title="Invernadero", layout="wide")
st.title("Optimización del Rendimiento Agrícola y Eficiencia de Riego")

df_all = cargar_datos()

# --- Filtros interactivos (Paso 4.2) ---
st.sidebar.header("Filtros")
trat = st.sidebar.multiselect("Tratamiento", df_all.tipo_tratamiento.unique(),
                              default=list(df_all.tipo_tratamiento.unique()))
rmin, rmax = float(df_all.volumen_riego.min()), float(df_all.volumen_riego.max())
rango = st.sidebar.slider("Volumen de riego (m³/ha)", rmin, rmax, (rmin, rmax))

df = df_all[df_all.tipo_tratamiento.isin(trat) &
            df_all.volumen_riego.between(*rango)].copy()

if len(df) < 10 or df.tipo_tratamiento.nunique() < 2:
    st.warning("Selecciona al menos 10 parcelas y ambos tratamientos.")
    st.stop()

# --- Modelo e inferencia sobre datos filtrados ---
X = sm.add_constant(df[["volumen_riego", "fertilizante_kg"]])
modelo = sm.OLS(df.rendimiento_ton, X).fit()
df["residuos"] = df.rendimiento_ton - modelo.predict(X)

A = df[df.tipo_tratamiento == "Tratamiento_A"].rendimiento_ton
B = df[df.tipo_tratamiento == "Tratamiento_B"].rendimiento_ton
_, p_valor = stats.ttest_ind(B, A, alternative="greater")

# --- KPIs ---
k1, k2, k3 = st.columns(3)
k1.metric("Rendimiento promedio global", f"{df.rendimiento_ton.mean():.2f} t/ha")
k2.metric("R² ajustado del modelo", f"{modelo.rsquared_adj*100:.1f} %")
k3.metric("p-valor (prueba t)", f"{p_valor:.4g}")

# --- Cuadrícula 2x2 ---
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

with c1:  # Gráfica 1: heatmap
    fig, ax = plt.subplots()
    sns.heatmap(df[["volumen_riego", "fertilizante_kg", "rendimiento_ton"]].corr(),
                annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    ax.set_title("Correlación de Pearson")
    st.pyplot(fig)

with c2:  # Gráfica 2: dispersión + OLS con banda de confianza
    fig, ax = plt.subplots()
    sns.regplot(data=df, x="volumen_riego", y="rendimiento_ton", ci=95, ax=ax)
    ax.set_xlabel("Volumen de Riego (m³/ha)")
    ax.set_ylabel("Rendimiento (ton/ha)")
    ax.set_title("Regresión OLS")
    st.pyplot(fig)

with c3:  # Gráfica 3: boxplot
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x="tipo_tratamiento", y="rendimiento_ton", ax=ax)
    ax.set_xlabel("Tipo de Tratamiento (A vs B)")
    ax.set_ylabel("Rendimiento (ton/ha)")
    ax.set_title("Comparación de tratamientos")
    st.pyplot(fig)

with c4:  # Gráfica 4: histograma de residuos + KDE
    fig, ax = plt.subplots()
    sns.histplot(df["residuos"], kde=True, ax=ax)
    ax.set_xlabel("Residuo (ton/ha)")
    ax.set_title("Diagnóstico de residuos")
    st.pyplot(fig)
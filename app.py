import streamlit as st
from beambending import Beam
import matplotlib.pyplot as plt

# Título y descripción de la App web
st.title("🏗️ Calculadora Estructural: Vigas")
st.write("Generador de diagramas de Fuerza Cortante y Momento Flector.")

# 1. Sección de Entradas del Usuario (Longitud y Apoyos)
st.sidebar.header("1. Geometría de la Viga")
L = st.sidebar.number_input("Longitud total (metros)", min_value=1.0, value=10.0, step=0.5)

st.sidebar.header("2. Posición de los Apoyos")
apoyo_fijo = st.sidebar.number_input("Apoyo Fijo (m)", min_value=0.0, max_value=L, value=0.0)
apoyo_movil = st.sidebar.number_input("Apoyo Móvil (m)", min_value=0.0, max_value=L, value=L)

# 2. Sección de Cargas
st.sidebar.header("3. Cargas")
carga_puntual = st.sidebar.number_input("Carga Puntual (kN) *Usa negativo para hacia abajo*", value=-20.0)
pos_carga = st.sidebar.number_input("Posición de la carga (m)", min_value=0.0, max_value=L, value=5.0)

carga_dist = st.sidebar.number_input("Carga Distribuida (kN/m) *Negativo hacia abajo*", value=-5.0)

# Botón para calcular
if st.button("Generar Diagramas"):
    try:
        # Lógica matemática usando la librería beam_bending
        viga = Beam(L)
        viga.pinned_support = apoyo_fijo
        viga.rolling_support = apoyo_movil
        
        # Agregar cargas
        viga.add_loads((carga_puntual, pos_carga))  # Carga puntual
        if carga_dist != 0:
            viga.add_distributed_load(carga_dist, (0, L)) # Carga distribuida en toda la viga
        
        # Crear la gráfica
        fig = viga.plot()
        
        # Mostrar gráfica en la página web
        st.pyplot(fig)
        
        st.success("¡Cálculo realizado con éxito!")
        
    except Exception as e:
        st.error("Error en el cálculo. Verifica que el sistema sea estable (isostático).")

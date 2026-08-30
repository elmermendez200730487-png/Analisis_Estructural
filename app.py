import streamlit as st

st.set_page_config(layout="wide") # Hace la app más ancha
st.title("🏗️ Calculadora Estructural Avanzada")

# --- 1. GEOMETRÍA ---
st.header("1. Geometría de la Viga")
L = st.number_input("Longitud total (metros)", min_value=1.0, value=10.0)

col1, col2 = st.columns(2)

# --- 2. APOYOS Y EMPOTRAMIENTOS ---
with col1:
    st.subheader("Vínculos / Apoyos")
    
    # Empotramientos
    num_empotramientos = st.selectbox("Cantidad de Empotramientos", [0, 1, 2])
    pos_empotramientos = []
    for i in range(num_empotramientos):
        pos = st.number_input(f"Posición Empotramiento {i+1} (m)", 0.0, L, key=f"emp_{i}")
        pos_empotramientos.append(pos)

    # Soportes simples/móviles
    num_soportes = st.selectbox("Cantidad de Soportes Simples", [0, 1, 2, 3, 4], index=2)
    pos_soportes = []
    for i in range(num_soportes):
        pos = st.number_input(f"Posición Soporte {i+1} (m)", 0.0, L, key=f"sop_{i}")
        pos_soportes.append(pos)

# --- 3. CARGAS ---
with col2:
    st.subheader("Cargas")
    
    # Cargas Puntuales
    num_puntuales = st.selectbox("Cantidad de Cargas Puntuales", [0, 1, 2, 3, 4, 5], index=1)
    cargas_puntuales = []
    for i in range(num_puntuales):
        with st.expander(f"Configurar Carga Puntual {i+1}"):
            fuerza = st.number_input("Fuerza (kN) [Negativo = hacia abajo]", value=-10.0, key=f"fp_{i}")
            pos = st.number_input("Posición en X (m)", 0.0, L, key=f"posp_{i}")
            cargas_puntuales.append((fuerza, pos))

    # Cargas Distribuidas
    num_distribuidas = st.selectbox("Cantidad de Cargas Distribuidas", [0, 1, 2, 3, 4, 5], index=1)
    cargas_distribuidas = []
    for i in range(num_distribuidas):
        with st.expander(f"Configurar Carga Distribuida {i+1}"):
            tipo = st.radio("Tipo", ["Rectangular", "Triangular"], key=f"tipo_{i}")
            w_inicio = st.number_input("Magnitud Inicio (kN/m)", value=-5.0, key=f"wi_{i}")
            w_fin = st.number_input("Magnitud Fin (kN/m)", value=-5.0 if tipo == "Rectangular" else 0.0, key=f"wf_{i}")
            x_inicio = st.number_input("Desde X (m)", 0.0, L, value=0.0, key=f"xi_{i}")
            x_fin = st.number_input("Hasta X (m)", 0.0, L, value=L, key=f"xf_{i}")
            cargas_distribuidas.append((tipo, w_inicio, w_fin, x_inicio, x_fin))

# --- BOTÓN DE CÁLCULO ---
st.divider()
if st.button("Generar Diagramas", type="primary"):
    st.info("Aquí conectaremos el nuevo motor matemático hiperestático.")
    
    # Mostrar resumen de lo que el usuario ingresó (para verificar)
    st.write("### Datos ingresados para el cálculo:")
    st.write(f"- **Empotramientos en:** {pos_empotramientos} m")
    st.write(f"- **Soportes en:** {pos_soportes} m")
    st.write(f"- **Cargas Puntuales:** {cargas_puntuales}")
    st.write(f"- **Cargas Distribuidas:** {cargas_distribuidas}")

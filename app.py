import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🏗️ Motor de Análisis Hiperestático")

# --- 1. GEOMETRÍA ---
st.header("1. Geometría de la Viga")
L = st.number_input("Longitud total (metros)", min_value=1.0, value=10.0)

col1, col2 = st.columns(2)

# --- 2. APOYOS Y EMPOTRAMIENTOS ---
with col1:
    st.subheader("Vínculos / Apoyos")
    num_empotramientos = st.selectbox("Cantidad de Empotramientos", list(range(11)))
    pos_empotramientos = [st.number_input(f"Posición Emp. {i+1} (m)", 0.0, L, key=f"emp_{i}") for i in range(num_empotramientos)]

    num_soportes = st.selectbox("Cantidad de Soportes Simples", list(range(11)), index=2)
    pos_soportes = [st.number_input(f"Posición Soporte {i+1} (m)", 0.0, L, key=f"sop_{i}") for i in range(num_soportes)]

# --- 3. CARGAS ---
with col2:
    st.subheader("Cargas")
    num_puntuales = st.selectbox("Cantidad de Cargas Puntuales", list(range(11)), index=1)
    cargas_puntuales = []
    for i in range(num_puntuales):
        with st.expander(f"Carga Puntual {i+1}"):
            f = st.number_input("Fuerza (kN) [Negativo = abajo]", value=-10.0, key=f"fp_{i}")
            p = st.number_input("Posición en X (m)", 0.0, L, key=f"posp_{i}")
            cargas_puntuales.append((f, p))

    num_distribuidas = st.selectbox("Cantidad de Cargas Distribuidas", list(range(11)), index=1)
    cargas_distribuidas = []
    for i in range(num_distribuidas):
        with st.expander(f"Carga Distribuida {i+1}"):
            tipo = st.radio("Tipo", ["Rectangular", "Triangular"], key=f"tipo_{i}")
            wi = st.number_input("Magnitud Inicio (kN/m)", value=-5.0, key=f"wi_{i}")
            wf = st.number_input("Magnitud Fin (kN/m)", value=-5.0 if tipo == "Rectangular" else 0.0, key=f"wf_{i}")
            xi = st.number_input("Desde X (m)", 0.0, L, value=0.0, key=f"xi_{i}")
            xf = st.number_input("Hasta X (m)", 0.0, L, value=L, key=f"xf_{i}")
            cargas_distribuidas.append((wi, wf, xi, xf))

st.divider()

# --- 4. CONSTRUCCIÓN DEL MODELO EN TIEMPO REAL ---
# (Esto se ejecuta automáticamente en cada cambio para actualizar el dibujo)
ss = SystemElements()

# Identificar nodos
puntos = [0.0, L] + pos_empotramientos + pos_soportes + [p[1] for p in cargas_puntuales]
for c in cargas_distribuidas:
    puntos.extend([c[2], c[3]])
    
puntos = sorted(list(set([round(p, 4) for p in puntos])))

# Crear elementos
for i in range(len(puntos) - 1):
    ss.add_element(location=[[puntos[i], 0], [puntos[i+1], 0]])

def get_node(x_val):
    return puntos.index(round(x_val, 4)) + 1

# Agregar apoyos
for pos in pos_empotramientos:
    ss.add_support_fixed(node_id=get_node(pos))
for pos in pos_soportes:
    ss.add_support_hinged(node_id=get_node(pos))

# Agregar cargas
for fuerza, pos in cargas_puntuales:
    ss.point_load(node_id=get_node(pos), Fx=0, Fy=fuerza)

for wi, wf, xi, xf in cargas_distribuidas:
    if xi == xf: continue
    for i in range(len(puntos) - 1):
        x1, x2 = puntos[i], puntos[i+1]
        centro = (x1 + x2) / 2.0
        if xi - 0.001 <= centro <= xf + 0.001:
            q1 = wi + (wf - wi) * (x1 - xi) / (xf - xi)
            q2 = wi + (wf - wi) * (x2 - xi) / (xf - xi)
            ss.q_load(q=[q1, q2], element_id=i+1, direction='y')

# --- 5. VISTA PREVIA EN TIEMPO REAL ---
st.subheader("👀 Vista Previa de la Estructura")
try:
    fig_struct = ss.show_structure(show=False)
    st.pyplot(fig_struct)
except Exception as e:
    st.info("Agrega los apoyos para ver la estructura graficada.")

st.divider()

# --- 6. CÁLCULO Y DIAGRAMAS ---
if st.button("Resolver Sistema Hiperestático", type="primary"):
    try:
        ss.solve() # Aquí es donde realmente se invierte la matriz
        
        st.success("Cálculo realizado con éxito.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Fuerza Cortante")
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            
        with c2:
            st.subheader("Momento Flector")
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)
            
       st.subheader("Deformación")
        fig_d = ss.show_displacement(show=False)
        st.pyplot(fig_d)
        
        # --- NUEVO: EXTRACCIÓN Y TABLA DE DATOS DE DEFORMACIÓN ---
        st.divider()
        st.subheader("📊 Datos Numéricos de Deformación por Nodo")
        
        # Extraer los datos del motor
        desplazamientos = ss.get_node_displacements()
        datos_tabla = []
        
        for i, x_val in enumerate(puntos):
            nodo_id = i + 1
            # Buscar los datos correspondientes a este nodo en la lista
            disp = next((d for d in desplazamientos if d["id"] == nodo_id), {})
            
            if disp:
                datos_tabla.append({
                    "Nodo": nodo_id,
                    "Posición X (m)": round(x_val, 4),
                    "Deflexión Vertical Y (m)": round(disp.get('uy', 0), 6),
                    "Giro / Rotación Z (rad)": round(disp.get('phi_z', disp.get('phi_y', 0)), 6)
                })
                
        # Mostrar tabla interactiva
        st.dataframe(datos_tabla, use_container_width=True)
        
        # Opcional: Mostrar reacciones en los apoyos
        st.subheader("🛑 Reacciones en los Apoyos")
        reacciones = ss.get_node_results_system()
        st.dataframe(reacciones, use_container_width=True)

    except Exception as e:
        st.error(f"Error al resolver. Verifica que el sistema no sea inestable (necesita al menos 2 apoyos simples o 1 empotramiento). Detalle: {e}")

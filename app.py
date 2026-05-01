import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Tuple, List, Dict
from utils_acustica import *

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Simulador Acústico Pro v2.0 - Profesional", layout="wide", initial_sidebar_state="expanded")

# --- CATÁLOGO DE PARLANTES ---
CATALOGO_PARLANTES = {
    "Subwoofer": {
        "Doble 18\"": {"spl": 138},
        "18\"": {"spl": 135},
        "15\"": {"spl": 130},
        "12\"": {"spl": 126}
    },
    "Woofer / Full Range": {
        "15\"": {"spl": 132},
        "12\"": {"spl": 128},
        "10\"": {"spl": 124},
        "8\"": {"spl": 120}
    },
    "Line Array": {
        "Módulo Grande (Dual 12\")": {"spl": 140},
        "Módulo Compacto (Dual 8\")": {"spl": 134}
    },
    "Retorno / Monitor": {
        "Piso 15\"": {"spl": 130},
        "Piso 12\"": {"spl": 126}
    }
}

# --- CACHE FUNCTIONS ---
@st.cache_data
def compute_spl_map(largo: float, ancho: float, z_oyente: float, parlantes: List[Dict], resolucion: int=40) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    '''Computa mapa SPL interactivo para una lista N de parlantes.'''
    x_mesh = np.linspace(0, largo, resolucion)
    y_mesh = np.linspace(0, ancho, resolucion)
    X, Y = np.meshgrid(x_mesh, y_mesh)
    
    mapas = []
    for p in parlantes:
        dist = np.sqrt((X - p["x"])**2 + (Y - p["y"])**2 + (z_oyente - p["z"])**2)
        mapa_indiv = atenuacion_spl_array(p["spl"], dist)
        mapas.append(mapa_indiv)
        
    mapa_total = suma_spl_arrays(mapas) if mapas else np.full_like(X, 0)
    return X, Y, mapa_total

@st.cache_data
def compute_reflections(sx: float, sy: float, sz: float, rx: float, ry: float, rz: float, largo: float, ancho: float, alto: float) -> List[Tuple[List[float], List[float], List[float]]]:
    '''Cached ray reflections computation.'''
    return calcular_reflexiones_1er_orden(sx, sy, sz, rx, ry, rz, largo, ancho, alto)

# --- INTERFAZ PRINCIPAL ---

st.title("🎛️ Simulador Acústico Profesional")
st.markdown("Análisis avanzado con trazado de rayos multidireccional y configuración modular de recintos.")

# Menú Lateral para la configuración maestra
with st.sidebar:
    st.header("🏢 Propiedades de la Sala")
    largo = st.number_input("Largo de la sala (X) [m]:", value=20.0, step=0.5, min_value=1.0)
    ancho = st.number_input("Ancho de la sala (Y) [m]:", value=15.0, step=0.5, min_value=1.0)
    alto = st.number_input("Alto de la sala (Z) [m]:", value=6.0, step=0.5, min_value=2.0)
    
    st.divider()
    st.header("🌡️ Medio Ambiente")
    temp = st.number_input("Temperatura Ambiente (°C)", value=20.0, step=0.5)
    vel_sonido = velocidad_sonido(temp)
    st.info(f"Velocidad del Sonido calculada: **{vel_sonido:.2f} m/s**")
    
    st.divider()
    st.header("🔊 Sistema de Parlantes")

    if 'parlantes' not in st.session_state:
        # Empezar con 2 parlantes por defecto (L/R)
        st.session_state.parlantes = [
            {"id": 1, "cat": "Woofer / Full Range", "subcat": "15\"", "spl": 132, "x": 0.5, "y": ancho*0.3, "z": 4.0, "mostrar_rayos": False},
            {"id": 2, "cat": "Woofer / Full Range", "subcat": "15\"", "spl": 132, "x": 0.5, "y": ancho*0.7, "z": 4.0, "mostrar_rayos": False}
        ]
        st.session_state.counter = 3

    if st.button("➕ Añadir Altavoz", use_container_width=True, type="primary"):
        st.session_state.parlantes.append({
            "id": st.session_state.counter,
            "cat": "Woofer / Full Range",
            "subcat": "15\"",
            "spl": 132,
            "x": 0.5, 
            "y": ancho / 2.0, 
            "z": 2.0,
            "mostrar_rayos": False
        })
        st.session_state.counter += 1

    st.markdown("---")
    
    parlantes_actualizados = []
    
    for i, p in enumerate(st.session_state.parlantes):
        with st.expander(f"🔈 Altavoz {i+1} : {p['cat']} {p['subcat']} ({p['spl']} dB)", expanded=False):
            col_del, _ = st.columns([1, 4])
            eliminar = col_del.button("🗑️", key=f"del_{p['id']}", help="Eliminar este parlante")
            if eliminar:
                continue
            
            # Categorías
            cat_idx = list(CATALOGO_PARLANTES.keys()).index(p["cat"]) if p["cat"] in CATALOGO_PARLANTES else 0
            new_cat = st.selectbox("Categoría", list(CATALOGO_PARLANTES.keys()), index=cat_idx, key=f"cat_{p['id']}")
            
            # Dinamismo de subcategoría
            if new_cat != p["cat"]:
                # Reset subcat to first available
                new_subcat = list(CATALOGO_PARLANTES[new_cat].keys())[0]
                default_spl = CATALOGO_PARLANTES[new_cat][new_subcat]["spl"]
            else:
                subcat_list = list(CATALOGO_PARLANTES[new_cat].keys())
                subcat_idx = subcat_list.index(p["subcat"]) if p["subcat"] in subcat_list else 0
                new_subcat = st.selectbox("Subcategoría", subcat_list, index=subcat_idx, key=f"subcat_{p['id']}")
                default_spl = CATALOGO_PARLANTES[new_cat][new_subcat]["spl"]

            # Si la categoría/subcat acaba de mutar, inyectamos el SPL default de la nueva; si no, dejamos que el usuario lo modifique.
            if new_cat != p["cat"] or new_subcat != p["subcat"]:
                current_spl = default_spl
            else:
                current_spl = p["spl"]

            new_spl = st.slider("SPL @ 1m [dB]", 80, 160, int(current_spl), key=f"spl_{p['id']}")
            
            st.caption("Ubicación 3D")
            cx, cy = st.columns(2)
            new_x = cx.number_input("Posición X (m)", value=float(p["x"]), min_value=0.0, max_value=float(largo), step=0.1, key=f"x_{p['id']}")
            new_y = cy.number_input("Posición Y (m)", value=float(p["y"]), min_value=0.0, max_value=float(ancho), step=0.1, key=f"y_{p['id']}")
            new_z = st.number_input("Altura Z (m)", value=float(p["z"]), min_value=0.0, max_value=float(alto), step=0.1, key=f"z_{p['id']}")
            
            new_rayos = st.toggle("Mostrar Rayos 3D (Tab 3)", value=p.get("mostrar_rayos", False), key=f"ray_{p['id']}")
            
            parlantes_actualizados.append({
                "id": p["id"],
                "cat": new_cat,
                "subcat": new_subcat,
                "spl": new_spl,
                "x": new_x,
                "y": new_y,
                "z": new_z,
                "mostrar_rayos": new_rayos
            })
            
    st.session_state.parlantes = parlantes_actualizados

# --- CREACIÓN DE PESTAÑAS ---
tab0, tab1, tab2, tab3 = st.tabs([
    "📖 Teoría Acústica General", 
    "📐 Analítica Psicoacústica", 
    "📉 Gráficas de Atenuación 2D", 
    "🧊 Trazado de Rayos 3D y Mapa SPL"
])

with tab0:
    st.header("🎓 Fundamentos de Acústica y Psicoacústica")
    st.markdown("""
    ### **Conceptos Clave**
    - **Ley Inversa del Cuadrado**: La intensidad del sonido disminuye linealmente a factor de $1/r^2$.
    - **RT60**: Tiempo de reverberación - clave para claridad óptica de voz/música en un recinto cerrado.
    - **Efecto Haas**: El oído prefiere el sonido que llega primero (hasta ~35ms) para definir su localización.
    - **Ray Tracing**: Simulación visual computacional para evaluar rebotes y tratamiento de superficies absorbentes.
    """)
    
    st.subheader("Tabla Recomendaciones RT60 por Uso")
    data = {
        'Tipo de Espacio': ['Teatro/Voz', 'Música Clásica', 'Rock/Pop', 'Estudio Grabación'],
        'RT60 Óptimo (s)': ['0.8-1.2', '1.2-1.8', '0.6-1.0', '<0.5']
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

# ==========================================
# PESTAÑA 1: ANALÍTICA PSICOACÚSTICA
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📚 **Teoría: Modos de Resonancia Axial**", expanded=False):
            st.markdown("""
            Los **modos axiales** son las frecuencias fundamentales donde el sonido forma ondas estacionarias entre paredes paralelas.
            **Fórmula**: $$ f = \\frac{c}{2L} $$
            Evite ubicar componentes muy empotrados a las esquinas si excitan estos modos de baja frecuencia.
            """)
        
        st.subheader("Modos de Resonancia")
        
        st.write(f"👉 Piso a Techo: **{frec_resonancia_axial(alto, vel_sonido):.1f} Hz**")
        st.write(f"👉 De Pared a Pared (Ancho): **{frec_resonancia_axial(ancho, vel_sonido):.1f} Hz**")
        st.write(f"👉 De Pared a Pared (Largo): **{frec_resonancia_axial(largo, vel_sonido):.1f} Hz**")
        
        st.divider()
        with st.expander("🧠 **Teoría: Efecto Haas (Precedencia)**", expanded=False):
            st.markdown("""
            Para "inclinar" la imagen acústica hacia la tarima frontal principal aunque usemos altavoces de relevo (delay towers),
            se añade un **Delay Haas** (normalmente entre 12 y 20 milisegundos extra a la alineación física).
            """)
        
        dist_relevo = st.number_input("Distancia entre Altavoz Principal y Altavoz Relevo (m)", value=10.0, step=0.5, min_value=0.0)
        delay_base = calcular_delay(dist_relevo, vel_sonido)
        delay_haas = delay_base + 15.0 
        
        st.success(f"⏳ **Delay Físico Teórico:** {delay_base:.2f} ms")
        st.info(f"🧠 **Delay Psicoacústico (Haas):** {delay_haas:.2f} ms")

    with col2:
        with st.expander("📐 **Teoría: Estimación RT60 Sabine**", expanded=False):
            st.markdown("""
            Fórmula de **Sabine**: $$ RT_{60} = 0.161 \\frac{V}{A} $$ 
            ($V$=volumen interior m³, $A$=absorción equivalente).
            """)
        
        st.subheader("Tiempo de Reverberación Estimado (RT60)")
        
        mat_paredes = st.selectbox("Material Principal Paredes", list(MATERIALES.keys()), index=0)
        mat_techo = st.selectbox("Material del Techo", list(MATERIALES.keys()), index=1)
        mat_suelo = st.selectbox("Material del Suelo", list(MATERIALES.keys()), index=0)
        
        area_paredes = 2 * (largo * alto) + 2 * (ancho * alto)
        area_suelo = largo * ancho
        area_techo = largo * ancho
        volumen = largo * ancho * alto
        
        absorcion_total = (area_paredes * MATERIALES[mat_paredes] +
                           area_suelo * MATERIALES[mat_suelo] +
                           area_techo * MATERIALES[mat_techo])
        
        rt60 = calcular_rt60_sabine(volumen, absorcion_total)
        
        st.metric("Volumen Activo", f"{volumen:.1f} m³")
        st.metric("Estimación RT60 (Media de Frecuencias)", f"{rt60:.2f} s")
        
        if rt60 > 2.5:
            st.error("⚠️ Muy reverberante. Integibilidad pobre. Requiere paneles acústicos absorbentes.")
        elif rt60 > 1.2:
            st.warning("⚠️ Reverberación moderada alta. (Ideal sólo música sinfónica).")
        elif rt60 > 0.6:
            st.success("✅ Acústica controlada. Cine, auditorios.")
        else:
            st.info("⏺ Sala ultra-seca / Studio.")

# ==========================================
# PESTAÑA 2: CURVA DE ATENUACIÓN 2D
# ==========================================
with tab2:
    st.header("Leyes Físicas: Atenuación Lineal P.A.")
    
    if len(st.session_state.parlantes) == 0:
        st.warning("No hay parlantes en la simulación. Agregue uno desde el menú lateral.")
    else:
        dist_max = st.slider("Distancia de simulación lineal (m)", min_value=10, max_value=int(max(10, largo*2)), value=int(largo))
        distancias = np.linspace(1, dist_max, 200)
        
        fig2d = go.Figure()
        
        # Paleta de colores para trazados
        colores = ['orange', 'cyan', 'magenta', 'lightgreen', 'yellow', 'pink']
        
        list_spl_valores = []
        for i, p in enumerate(st.session_state.parlantes):
            vals = [atenuacion_spl(p["spl"], d) for d in distancias]
            list_spl_valores.append(vals)
            c = colores[i % len(colores)]
            fig2d.add_trace(go.Scatter(
                x=distancias, y=vals, 
                mode='lines', name=f'Altavoz {i+1} ({p["cat"]})', line=dict(color=c, width=2),
                hovertemplate='Distancia: %{x:.1f} m<br>Nivel: %{y:.1f} dB'
            ))
            
        if len(list_spl_valores) > 1:
            # Suma Total Incoherente
            # Conversion a array
            stack = np.array(list_spl_valores)
            suma_total = 10 * np.log10(np.sum(10**(stack / 10), axis=0))
            
            fig2d.add_trace(go.Scatter(
                x=distancias, y=suma_total, 
                mode='lines', name='Sumatoria Total SPL', line=dict(color='white', width=4, dash='dash'),
                hovertemplate='Distancia: %{x:.1f} m<br>SPL Total Combinado: %{y:.1f} dB'
            ))
            
        fig2d.update_layout(
            title="Atenuación Lineal frente Distancia en campo libre",
            xaxis_title="Distancia (m)",
            yaxis_title="Presión Sonora (dB SPL)",
            hovermode="x unified",
            template='plotly_dark'
        )
        st.plotly_chart(fig2d, use_container_width=True)

# ==========================================
# PESTAÑA 3: VISUALIZACIÓN 3D Y EXPORTACIÓN
# ==========================================
with tab3:
    st.header("Entorno de Trazado de Rayos (Ray Tracing) y SPL 3D")
    
    col_oyente, _, _ = st.columns(3)
    z_oyente = col_oyente.slider("Altura de los oídos de la audiencia (m)", 0.0, float(alto), 1.7)
    
    if len(st.session_state.parlantes) == 0:
        st.warning("⚠️ Añada altavoces para inicializar el motor de render 3D.")
    else:
        # Calcular mapa de calor combinando n parlantes
        X, Y, mapa_spl = compute_spl_map(largo, ancho, z_oyente, st.session_state.parlantes, resolucion=40)
        
        fig3d = go.Figure()
        
        # Plano Térmico de Predicción
        max_spl_system = max([p["spl"] for p in st.session_state.parlantes])
        
        fig3d.add_trace(go.Surface(
            z=np.full_like(X, z_oyente),
            x=X, y=Y,
            surfacecolor=mapa_spl,
            colorscale='Jet',
            colorbar_title="SPL (dB)",
            cmin=min(80, np.min(mapa_spl)), cmax=max(max_spl_system, np.max(mapa_spl)),
            hovertemplate='X (m): %{x:.1f}<br>Y (m): %{y:.1f}<br>Nivel: %{surfacecolor:.1f} dB<extra></extra>',
            opacity=0.8
        ))
        
        rx, ry, rz = largo/2, ancho/2, z_oyente
        fig3d.add_trace(go.Scatter3d(
            x=[rx], y=[ry], z=[rz],
            mode='markers', name='Centroide Focal (Audiencia)',
            marker=dict(size=4, color='white', symbol='cross')
        ))

        # Iterar sobre cada parlante para dibujar componente físico y geométrico
        colores = ['orange', 'cyan', 'magenta', 'lime', 'yellow', 'pink']
        
        for i, p in enumerate(st.session_state.parlantes):
            c = colores[i % len(colores)]
            
            # Altavoz (Punto físico)
            fig3d.add_trace(go.Scatter3d(
                x=[p["x"]], y=[p["y"]], z=[p["z"]],
                mode='markers+text', name=f'Altavoz {i+1} {p["subcat"]}',
                marker=dict(size=7, color=c, symbol='square'),
                text=[f"A{i+1}"], textposition="top center"
            ))
            
            if p.get("mostrar_rayos", False):
                # Generar Ray Tracing
                rayos = compute_reflections(p["x"], p["y"], p["z"], rx, ry, rz, largo, ancho, alto)
                # Directo
                fig3d.add_trace(go.Scatter3d(
                    x=[p["x"], rx], y=[p["y"], ry], z=[p["z"], rz],
                    mode='lines', line=dict(color=c, width=4), name=f"Directo A{i+1}",
                    hoverinfo='none'
                ))
                # Rebotes
                for r_idx, (rx_cam, ry_cam, rz_cam) in enumerate(rayos):
                    fig3d.add_trace(go.Scatter3d(
                        x=rx_cam, y=ry_cam, z=rz_cam,
                        mode='lines', line=dict(color=c, width=1.5, dash='dot'), 
                        name=f"Rebote A{i+1} ({r_idx+1})",
                        hoverinfo='none', showlegend=False
                    ))

        fig3d.update_layout(
            scene=dict(
                xaxis=dict(title='Largo (X)', range=[0, largo]),
                yaxis=dict(title='Ancho (Y)', range=[0, ancho]),
                zaxis=dict(title='Alto (Z)', range=[0, alto]),
                aspectmode='data',
                camera=dict(
                    eye=dict(x=-1.5, y=-2.0, z=1.8),
                    center=dict(x=0, y=0, z=-0.2)
                )
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            template='plotly_dark',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        st.plotly_chart(fig3d, use_container_width=True, height=750)
        
        st.divider()
        st.subheader("Bandeja de Exportables HTML Web")
        html_data = fig3d.to_html(full_html=True, include_plotlyjs='cdn')
        st.download_button(
            label="⚡ Descargar Interfaz 3D HTML Interractiva",
            data=html_data,
            file_name="Proyecto_Acustico_Profesional_3D.html",
            mime="text/html"
        )
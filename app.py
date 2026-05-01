import streamlit as st
import pandas as pd

# Configuración de la página (para que ocupe toda la pantalla y tenga un emoji de detective)
st.set_page_config(page_title="Auditoría de Diseño DP 2026", page_icon="🕵️‍♂️", layout="wide")

# Caché de Streamlit: La clave del éxito. 
# Esto evita que el servidor explote recargando el Excel cada vez que das un clic.
@st.cache_data
def cargar_datos(archivo_excel):
    try:
        # sheet_name=None obliga a Pandas a leer TODAS las pestañas.
        diccionario_hojas = pd.read_excel(archivo_excel, sheet_name=None)
        
        lista_dfs = []
        
        # Iteramos sobre cada pestaña
        for nombre_pestaña, df_temp in diccionario_hojas.items():
            # Inyectamos el mes basado en el nombre de la pestaña
            df_temp.insert(0, 'Mes', nombre_pestaña)
            lista_dfs.append(df_temp)
                
        # Unimos el Frankenstein
        df_completo = pd.concat(lista_dfs, ignore_index=True)
        
        # Limpiamos los nombres de las columnas de esos malditos espacios en blanco ocultos
        df_completo.columns = df_completo.columns.str.strip()
        
        # Llenamos vacíos. Porque la falta de fechas es una ofensa.
        df_completo.fillna("NO REGISTRA", inplace=True)
        
        return df_completo
        
    except Exception as e:
        # Si algo sale mal, se lo escupimos al usuario en rojo pasión
        st.error(f"Uy, el Excel explotó en mis manos. Detalles del desastre: {e}")
        st.stop() # Detiene la ejecución de la app aquí mismo

# --- INTERFAZ DE USUARIO (El chisme visual) ---

st.title("🕵️‍♂️ Auditoría de Diseño DP 2026")
st.markdown("Bienvenidos al centro de comando. Sube tu Excel y empecemos a buscar culpables.")

# Widget para subir el archivo (mucho más seguro y dinámico que dejar la ruta fija)
archivo_subido = st.file_uploader("Arrastra tu Excel masivo aquí (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    # Mostramos un spinner mientras lee todo
    with st.spinner("Asimilando datos y juzgando fechas de entrega..."):
        df = cargar_datos(archivo_subido)
    
    st.success("¡Boom! Excel cargado y procesado. Todas las pestañas han sido asimiladas.")
    
    st.markdown("---")
    st.header("Filtros de Búsqueda")
    
    # Creamos columnas para que el menú se vea más pro
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # El selectbox reemplaza tu menú de consola (1, 2 o 3)
        opcion_busqueda = st.selectbox(
            "¿A quién o qué le vamos a hacer cacería hoy?",
            options=[
                "Solicitud (Qué pidieron)", 
                "Solicitante (Quién molestó)", 
                "Diseñador (Quién lo sufrió)"
            ]
        )
    
    # Mapeamos la opción visual a la columna real del DataFrame
    mapa_columnas = {
        "Solicitud (Qué pidieron)": "solicitud",
        "Solicitante (Quién molestó)": "solicitante",
        "Diseñador (Quién lo sufrió)": "diseñador"
    }
    columna_real = mapa_columnas[opcion_busqueda]
    
    with col2:
        # Aquí el usuario escribe en vivo
        termino_busqueda = st.text_input(f"Escribe tu término de búsqueda para '{columna_real}':")

    # Si el usuario escribió algo, filtramos
    if termino_busqueda:
        # Filtramos ignorando mayúsculas y minúsculas (case=False)
        resultados = df[df[columna_real].astype(str).str.contains(termino_busqueda, case=False, na=False)]
        
        if resultados.empty:
            st.warning(f"Nada. Cero. No encontré '{termino_busqueda}' en la columna '{columna_real}'. O lo escribiste mal, o esa persona/solicitud no existió.")
        else:
            # Las columnas del chisme
            columnas_a_mostrar = [
                'Mes', 
                'solicitud', 
                'solicitante', 
                'diseñador', 
                'fecha recepción solicitud', 
                'fecha solicitada de entrega', 
                'fecha entrega final'
            ]
            
            # Nos aseguramos de que existan para no romper la app
            columnas_disponibles = [col for col in columnas_a_mostrar if col in df.columns]
            df_final = resultados[columnas_disponibles]
            
            st.markdown(f"### 🎯 Resultados Encontrados ({len(df_final)} registros hallados en el fango de tu Excel)")
            
            # st.dataframe permite ordenar por columnas, hacer scroll y se ve hermoso
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Un pequeño extra: un botón para descargar el filtro como CSV
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar esta evidencia (CSV)",
                data=csv,
                file_name=f"evidencia_{termino_busqueda}.csv",
                mime="text/csv",
            )
else:
    st.info("Estoy esperando... Pon el Excel ahí arriba y deja de jugar con mis sentimientos.")
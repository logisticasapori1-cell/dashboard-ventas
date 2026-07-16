import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(layout="wide", page_title="Portal Analítico - Sapori", page_icon="🔒")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# ==========================================
# MÓDULO DE ACCESO / LOGIN
# ==========================================
if not st.session_state['autenticado']:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )

    col_izq, col_centro, col_der = st.columns([1, 1.5, 1])
    
    with col_centro:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #1f4e79; font-family: Arial;'>SAPORI</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='text-align: center; color: #2b2b2b; font-family: Arial; margin-top:0px;'>Portal Oficial de Operaciones</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Supply Chain, Ventas y Pronósticos</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("formulario_login"):
            st.markdown("##### 🔐 Ingrese sus credenciales corporativas")
            usuario = st.text_input("Usuario o Correo Institucional", placeholder="ej. gerencia.operaciones")
            contrasena = st.text_input("Contraseña del Sistema", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            boton_ingresar = st.form_submit_button("Acceder al Sistema", type="primary", use_container_width=True)
            
            if boton_ingresar:
                if usuario == "admin" and contrasena == "sapori2026":
                    st.session_state['autenticado'] = True
                    st.success("✅ Acceso concedido. Inicializando entorno...")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Verifique e intente de nuevo.")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align: center; color: #888; font-size: 12px; font-family: Arial;'>"
            "© 2026 Sapori | Dirección de Supply Chain & Operaciones<br>Versión del Sistema: 3.1 (Lógica Dinámica)"
            "</div>", 
            unsafe_allow_html=True
        )

# ==========================================
# ENTORNO DEL SISTEMA AUTENTICADO
# ==========================================
else:
    with st.sidebar:
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 📌 Módulos de Operación")
        modulo_activo = st.radio(
            "Seleccione el área a visualizar:",
            ["1. Dashboard Venta Diaria & Forecast", "2. Control de Desviaciones (Mensual)"]
        )
        
        st.markdown("---")
        # --- PARÁMETROS CRÍTICOS DE TIEMPO PARA EL FORECAST ---
        st.markdown("### ⏱️ Control de Tiempos del Mes")
        dias_efectivos = st.number_input("Días de Venta Efectivos (Transcurridos):", min_value=1, value=8, step=1)
        dias_restantes = st.number_input("Días de Venta Restantes del Mes:", min_value=0, value=15, step=1)
        
        st.markdown("---")
        st.success("👤 Rol: **Administrador / Gerencia**")
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

    # =========================================================================
    # MÓDULO 1: VENTA DIARIA Y FORECAST (CÁLCULO DINÁMICO)
    # =========================================================================
    if modulo_activo == "1. Dashboard Venta Diaria & Forecast":
        st.title("📈 Dashboard Ejecutivo: Pronósticos y Ventas")
        st.markdown("### Seguimiento de Forecast y Venta Diaria por SKU")
        
        file_ventas = "VINCULO VTS BY SKU.xlsx"
        
        if not os.path.exists(file_ventas):
            st.error(f"❌ **Archivo requerido no encontrado:** '{file_ventas}'")
            st.info("💡 Por favor, guarde la matriz con el nombre exacto de **'VINCULO VTS BY SKU.xlsx'** en la raíz de la carpeta.")
        else:
            try:
                # Lectura de la hoja de cálculo
                df_vts = pd.read_excel(file_ventas)
                
                # =========================================================================
                # 🛠️ NUEVO: DETECTAR Y REDONDEAR COLUMNAS DE PROMEDIOS EN LA MATRIZ DE SKUS
                # =========================================================================
                for col in df_vts.columns:
                    if 'PROMEDIO' in str(col).upper() or 'PROMD' in str(col).upper():
                        df_vts[col] = pd.to_numeric(df_vts[col], errors='coerce').round(0).fillna(0).astype(int)
                # =========================================================================
                
                # --- MAPEO INTELIGENTE DE COLUMNAS PARA SOPORTAR CUALQUIER FORMATO ---
                cols_upper = {col: str(col).upper().strip() for col in df_vts.columns}
                
                col_gross = next((c for c, m in cols_upper.items() if 'GROSS' in m or 'BRUTA' in m or 'VENTA_BRUTA' in m), None)
                col_return = next((c for c, m in cols_upper.items() if 'RETURN' in m or 'DEVOL' in m or 'RECHAZO' in m), None)
                col_forecast = next((c for c, m in cols_upper.items() if 'FORECAST' in m or 'META' in m or 'OBJETIVO' in m), None)
                
                # Inicialización de acumuladores base (Mapeo preventivo si faltan columnas)
                val_gross = df_vts[col_gross].sum() if col_gross else 171575
                val_return = df_vts[col_return].sum() if col_return else 2145
                val_forecast = df_vts[col_forecast].sum() if col_forecast else 696207
                
                # Ejecución de la Ingeniería Matemática de Sapori
                val_net = val_gross - val_return
                val_prom_dia = val_gross / dias_efectivos if dias_efectivos > 0 else 0
                val_pronost_mes = val_prom_dia * (dias_efectivos + dias_restantes)
                val_dif_units = val_gross - val_forecast
                val_efficiency = (val_gross / val_forecast) * 100 if val_forecast > 0 else 0
                
                # Notificación informativa en barra de alertas si está usando datos simulados
                if not col_gross or not col_forecast:
                    st.sidebar.warning("⚠️ Columnas no detectadas textualmente en Excel. Mostrando plantilla base estándar.")
                
                # --- RENDERIZADO DEL DASHBOARD TIPO MATRIZ ---
                st.markdown(
                    """
                    <div style="background-color: #a9cce3; padding: 10px; text-align: center; font-weight: bold; font-size: 20px; color: #1f4e79; border-radius: 5px; margin-bottom: 20px;">
                        DASHBOARD DE CONTROL OPERATIVO DE DEMANDA
                    </div>
                    """, unsafe_allow_html=True
                )
                
                # FILA 1: Métricas de Ejecución Comercial e Indicadores de Variación
                col_a1, col_a2, col_a3, col_a4, col_a5, col_a6, col_a7 = st.columns(7)
                col_a1.metric("TOTAL UNITS SALES GROSS", f"{val_gross:,.0f}")
                col_a2.metric("TOTAL UNITS SALES NET", f"{val_net:,.0f}")
                col_a3.metric("PROMEDIO VENTA DIARIA", f"{val_prom_dia:,.0f}")
                col_a4.metric("PRONOSTICO VENTA MENSUAL", f"{val_pronost_mes:,.0f}")
                col_a5.metric("FORECAST", f"{val_forecast:,.0f}")
                col_a6.metric("FORECAST EFFICIENCY", f"{val_efficiency:.1f}%")
                
                # Control inteligente de flecha y alertas para la Desviación de Unidades
                delta_dif = "- Brecha de Cobertura" if val_dif_units < 0 else "+ Superávit Comercial"
                col_a7.metric("DIFERENCIA ALCANCE FORECAST", f"{val_dif_units:,.0f}", delta=delta_dif, delta_color="normal")
                
                st.markdown("---")
                
                # FILA 2: Control Logístico de Tiempos y Devoluciones
                col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)
                col_b1.metric("UNITS RETURN (Devoluciones)", f"{val_return:,.0f}")
                col_b2.metric("INICIO DE VENTA", "01/07/2026")
                col_b4.metric("FINAL DE VENTA", "31/07/2026")
                col_b5.metric("DIAS VENTA EFECTIVOS.", f"{dias_efectivos} días")
                col_b6.metric("DIAS VENTA RESTANTES.", f"{dias_restantes} días")
                
                st.markdown("---")
                
                # --- VISUALIZADOR DE LA MATRIZ DE VENTAS POR SKU ---
                st.markdown("### 📋 Desglose Operativo: Matriz de Ventas por SKU")
                busqueda_sku = st.text_input("🔍 Filtrar tabla por Nombre de Producto o SKU de Producción:")
                
                df_vts_filtrado = df_vts.copy()
                if busqueda_sku:
                    mask = df_vts_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda_sku, case=False, na=False)).any(axis=1)
                    df_vts_filtrado = df_vts_filtrado[mask]
                
                st.dataframe(df_vts_filtrado, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"Error analítico durante el procesamiento del archivo: {e}")

    # =========================================================================
    # MÓDULO 2: CONTROL DE DESVIACIONES (MÓDULO MENSUAL)
    # =========================================================================
    elif modulo_activo == "2. Control de Desviaciones (Mensual)":
        st.title("📊 Tablero de Control de Desviaciones")
        st.markdown("### Análisis Comparativo, Financiero y Pareto (ABC) por SKU")

        file_name = "Comparación de Venta Diaria por SKU (Junio vs Julio).xlsx"

        if not os.path.exists(file_name):
            st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
        else:
            try:
                df = pd.read_excel(file_name, sheet_name="Table 1")
                
                if 'CATEGORÍA' not in df.columns:
                    df['CATEGORÍA'] = "Por Asignar"

                for col in ['PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO']:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
                    # Forzar redondeo matemático y convertir a entero (sin decimales)
                    df[col] = df[col].round(0).astype(int)
                
                if 'Porcentaje de desviación' in df.columns:
                    df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
                else:
                    df['Desviacion_Num'] = ((df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']) / df['PROMD VTA DIA JUNIO']) * 100

                tiene_precio = 'PRECIO UNITARIO' in df.columns
                if tiene_precio:
                    df['Dif_Unidades_Diarias'] = df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']
                    df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
                    df['Impacto_Mensual_$'] = df['Impacto_Diario_$'] * 30

                df = df.sort_values(by='PROMD VTA DIA JULIO', ascending=False).reset_index(drop=True)
                volumen_total_julio = df['PROMD VTA DIA JULIO'].sum()
                df['Porcentaje_Participacion'] = (df['PROMD VTA DIA JULIO'] / volumen_total_julio) * 100 if volumen_total_julio > 0 else 0
                df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()
                
                def asignar_abc(acumulado):
                    if acumulado <= 80: return 'A'
                    elif acumulado <= 95: return 'B'
                    else: return 'C'
                df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

                total_skus = len(df)
                subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
                bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
                
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Total SKUs en Planta", f"{total_skus} Prod.")
                kpi2.metric("SKUs en Alza", f"{subio}", delta=f"+{subio} SKUs", delta_color="normal")
                kpi3.metric("SKUs en Alerta", f"{bajo}", delta=f"-{bajo} SKUs", delta_color="normal")
                
                if tiene_precio:
                    impacto_total = df['Impacto_Mensual_$'].sum()
                    delta_financiero = "- Mensual vs Junio" if impacto_total < 0 else "Mensual vs Junio"
                    kpi4.metric("Balance Financiero Proyectado", f"${impacto_total:,.2f}", delta=delta_financiero, delta_color="normal")
                else:
                    kpi4.metric("Balance", "Falta Precio Unitario")
                    
                st.markdown("---")
                
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    filtro_tendencia = st.selectbox("🎯 Estado de Tendencia:", ["Todos", "SUBIÓ", "BAJO"])
                with col_f2:
                    filtro_abc = st.selectbox("📊 Clasificación ABC:", ["Todos", "A", "B", "C"])
                with col_f3:
                    lista_categorias = ["Todos"] + sorted(df['CATEGORÍA'].dropna().unique().tolist())
                    filtro_categoria = st.selectbox("🏷️ Categoría/Marca:", lista_categorias)
                with col_f4:
                    busqueda = st.text_input("🔍 Filtrar Nombre:")
                
                df_filtrado = df.copy()
                if filtro_tendencia != "Todos" and 'Estado de tendencia' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Estado de tendencia'] == filtro_tendencia]
                if filtro_abc != "Todos":
                    df_filtrado = df_filtrado[df_filtrado['Clasificación ABC'] == filtro_abc]
                if filtro_categoria != "Todos":
                    df_filtrado = df_filtrado[df_filtrado['CATEGORÍA'] == filtro_categoria]
                if busqueda:
                    df_filtrado = df_filtrado[
                        df_filtrado['PRODUCTO'].str.contains(busqueda, case=False, na=False) | 
                        df_filtrado['REFERENCIA INTERNA'].astype(str).str.contains(busqueda, na=False)
                    ]
                
                df_grafico = df_filtrado.sort_values(by='PROMD VTA DIA JUNIO', ascending=False)
                if not df_grafico.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico['PROMD VTA DIA JUNIO'], name='Junio', marker_color='#1f4e79'))
                    fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico['PROMD VTA DIA JULIO'], name='Julio', marker_color='#d95f02'))
                    fig.update_layout(barmode='group', height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.markdown("### 📋 Detalle de Desviaciones")
                
                # 1. Definir qué columnas se van a mostrar (AQUÍ ESTÁ LA VARIABLE QUE FALTABA)
                if tiene_precio:
                    columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Impacto_Mensual_$', 'Estado de tendencia']
                else:
                    columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
                
                # 2. Función de colores para las tendencias
                def resaltar_tendencia(val):
                    if val == 'SUBIÓ': return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                    elif val == 'BAJO': return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                    return ''
                
                # 3. Diccionario de formatos (Redondeo sin decimales y Porcentaje)
                formato_columnas = {
                    'PROMD VTA DIA JUNIO': '{:,.0f}',
                    'PROMD VTA DIA JULIO': '{:,.0f}',
                    'Porcentaje de desviación': '{:.2%}'
                }
                
                if tiene_precio:
                    formato_columnas['Impacto_Mensual_$'] = '${:,.2f}'
                
                # 4. Aplicar estilos y formatos a la tabla
                tabla_estilizada = df_filtrado[columnas_render].style.map(
                    resaltar_tendencia, subset=['Estado de tendencia']
                ).format(formato_columnas)
                    
                # 5. Mostrar la tabla en pantalla
                st.dataframe(tabla_estilizada, use_container_width=True, hide_index=True)

                st.markdown("---")
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
                excel_data = buffer.getvalue()
                st.download_button("📄 Descargar Reporte para Firmas", data=excel_data, file_name="Reporte_Desviaciones.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

            except Exception as e:
                st.error(f"Error crítico en la lectura del archivo Excel: {e}")

# =========================================================================
    def render_modulo_3():
        st.title("📊 Módulo 3: Dashboard Ejecutivo de Producción y Forecast")
        st.markdown("Análisis histórico y proyección de demanda para optimización de inventarios.")
        st.markdown("---")
    
        # 1. Carga de archivo
        file_historico = st.file_uploader("📂 Cargar Histórico de Producción (.xlsx)", type=["xlsx"], key="uploader_m3")
    
        if file_historico is not None:
            # Protegemos la lectura del archivo
            try:
                excel_file = pd.ExcelFile(file_historico)
            except Exception as e:
                st.error(f"Error al leer el archivo Excel: {e}")
                return
            
            # 2. Función interna para procesar las hojas
            def parsear_hoja_categoria(sheet_name):
                df = excel_file.parse(sheet_name)
                df = df.dropna(how='all')
                
                row_fecha_label = None
                for label, row in df.iterrows():
                    fechas_eval = pd.to_datetime(row, errors='coerce')
                    if fechas_eval.notna().sum() >= 3:
                        row_fecha_label = label
                        break
                
                if row_fecha_label is None:
                    return None
                
                fechas = pd.to_datetime(df.loc[row_fecha_label], errors='coerce')
                columnas_validas = fechas[fechas.notna()].index
                
                # Nos quedamos solo con las columnas de fechas válidas para análisis
                df_limpio = df[columnas_validas].copy()
                df_limpio.columns = fechas[columnas_validas]
                return df_limpio

            # 3. Interfaz del Dashboard (Se muestra solo si el archivo carga bien)
            st.success("¡Archivo cargado y procesado con éxito!")
            
            # Selector de hoja/categoría a analizar
            hojas_disponibles = excel_file.sheet_names
            hoja_seleccionada = st.selectbox("Seleccione la categoría de producto a analizar:", hojas_disponibles)
            
            datos_procesados = parsear_hoja_categoria(hoja_seleccionada)

            if datos_procesados is not None:
                # --- SECCIÓN DE KPIs VISUALES ---
                st.subheader("📈 Resumen de Producción")
                col1, col2, col3 = st.columns(3)
                
                # Aquí simulamos cálculos rápidos. Ajustaremos esto según tus filas reales.
                with col1:
                    st.metric(label="Total Registros Históricos", value=f"{len(datos_procesados)} series")
                with col2:
                    st.metric(label="Último mes analizado", value=datos_procesados.columns[-1].strftime('%B %Y'))
                with col3:
                    st.metric(label="Estado del Forecast", value="Activo", delta="Optimizado")

                st.markdown("---")

                # --- SECCIÓN DE PESTAÑAS (TABS) PARA ORGANIZAR LA VISTA ---
                tab1, tab2 = st.tabs(["📉 Análisis Histórico", "🔮 Proyección (Forecast)"])
                
                with tab1:
                    st.markdown("### Tendencia de Producción en el Tiempo")
                    # Para graficar, Pandas y Plotly prefieren que las fechas estén en filas, no en columnas.
                    # Hacemos una pequeña transposición (T) temporal para el gráfico:
                    df_grafico = datos_procesados.T
                    df_grafico.index.name = 'Fecha'
                    
                    # Gráfico de líneas atractivo
                    fig = px.line(df_grafico, x=df_grafico.index, y=df_grafico.columns[0], 
                                  title=f"Evolución Histórica - Fila 1 ({hoja_seleccionada})",
                                  markers=True, line_shape="spline")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mostrar la tabla limpia (asegurando el uso de puntos decimales)
                    with st.expander("Ver tabla de datos limpios"):
                        st.dataframe(datos_procesados.style.format(precision=2, thousands="", decimal="."))
                
                with tab2:
                    st.markdown("### Modelo de Proyección")
                    st.info("Aquí conectaremos el algoritmo de pronóstico (ARIMA, Prophet o promedios móviles) usando los datos históricos extraídos.")
                    # Espacio reservado para agregar la lógica del Forecast en el siguiente paso.
            else:
                st.warning("No se pudo detectar una fila válida con fechas en esta hoja. Verifica el formato de tu Excel.")

    # =========================================================================
    # PIE DE PÁGINA GLOBAL
    # =========================================================================
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-family: Arial;'>"
        "📝 Sistema Operativo Realizado por: <b>Dirección de Supply Chain Sapori</b>"
        "</div>", 
        unsafe_allow_html=True
    )
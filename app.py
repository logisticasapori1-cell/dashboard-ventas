import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
            usuario = st.text_input("Usuario o Correo Institucional")
            contrasena = st.text_input("Contraseña del Sistema", type="password")
            
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
            "© 2026 Sapori | Dirección de Supply Chain & Operaciones<br>Versión del Sistema: 3.0 (Multi-Módulo)"
            "</div>", 
            unsafe_allow_html=True
        )

# ==========================================
# ENTORNO DEL SISTEMA AUTENTICADO
# ==========================================
else:
    # --- MENÚ DE NAVEGACIÓN LATERAL ---
    with st.sidebar:
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)
        st.markdown("---")
        
        # Selector de Módulo Principal
        st.markdown("### 📌 Módulos de Operación")
        modulo_activo = st.radio(
            "Seleccione el área a visualizar:",
            ["1. Dashboard Venta Diaria & Forecast", "2. Control de Desviaciones (Mensual)"]
        )
        
        st.markdown("---")
        st.success("👤 Rol: **Administrador / Gerencia**")
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

    # =========================================================================
    # MÓDULO 1: VENTA DIARIA Y FORECAST (NUEVO DESARROLLO)
    # =========================================================================
    if modulo_activo == "1. Dashboard Venta Diaria & Forecast":
        st.title("📈 Dashboard Ejecutivo: Pronósticos y Ventas")
        st.markdown("### Seguimiento de Forecast Efficiency y Ejecución Diaria por SKU")
        
        file_ventas = "VINCULO VTS BY SKU.xlsx"
        
        if not os.path.exists(file_ventas):
            st.error(f"❌ **Archivo requerido no encontrado:** '{file_ventas}'")
            st.info("💡 Por favor, asegúrate de subir o guardar este archivo en la misma carpeta para visualizar los datos.")
        else:
            try:
                # Lectura de la matriz de ventas (asume que la hoja principal tiene los datos)
                df_vts = pd.read_excel(file_ventas)
                
                # --- RÉPLICA DEL DASHBOARD GERENCIAL (KPIs SUPERIORES) ---
                st.markdown(
                    """
                    <div style="background-color: #a9cce3; padding: 10px; text-align: center; font-weight: bold; font-size: 20px; color: #1f4e79; border-radius: 5px;">
                        DASHBOARD
                    </div>
                    """, unsafe_allow_html=True
                )
                st.markdown("<br>", unsafe_allow_html=True)
                
                # FILA 1: Métricas de Venta y Pronóstico
                col_a1, col_a2, col_a3, col_a4, col_a5, col_a6, col_a7 = st.columns(7)
                col_a1.metric("SALES GROSS", "171,575")
                col_a2.metric("SALES NET", "169,430")
                col_a3.metric("PROMD VTA DIA", "21,447")
                col_a4.metric("PRONOST VTA MES", "493,278")
                col_a5.metric("FORECAST", "696,207")
                col_a6.metric("FORECAST EFFICIENCY", "25%")
                col_a7.metric("DIF UNITS", "-524,632", delta="- Riesgo Volumétrico", delta_color="normal")
                
                st.markdown("---")
                
                # FILA 2: Control Operativo y Tiempos
                col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)
                col_b1.metric("UNITS RETURN (Devoluciones)", "2,145")
                col_b2.metric("INICIO DE VENTA", "01/07/2026")
                col_b3.metric("TRANSC. VENTA", "13/07/2026")
                col_b4.metric("FINAL DE VENTA", "31/07/2026")
                col_b5.metric("DIAS VENTA EFECT.", "8")
                col_b6.metric("DIAS VENTA RESTA.", "15")
                
                st.markdown("---")
                
                # --- VENTA DIARIA POR SKU (TABLA DETALLADA) ---
                st.markdown("### 📋 Desglose Operativo: Venta Diaria por SKU")
                
                # Filtros interactivos para la tabla de ventas
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    busqueda_sku = st.text_input("🔍 Buscar SKU específico en ventas diarias:")
                
                df_vts_filtrado = df_vts.copy()
                if busqueda_sku:
                    # Busca en todas las columnas de texto por si el nombre del producto o SKU coincide
                    mask = df_vts_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda_sku, case=False, na=False)).any(axis=1)
                    df_vts_filtrado = df_vts_filtrado[mask]
                
                st.dataframe(df_vts_filtrado, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error al leer el archivo {file_ventas}: {e}")

    # =========================================================================
    # MÓDULO 2: CONTROL DE DESVIACIONES (EL DESARROLLO ANTERIOR)
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
                
                if tiene_precio:
                    columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Impacto_Mensual_$', 'Estado de tendencia']
                else:
                    columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
                
                def resaltar_tendencia(val):
                    if val == 'SUBIÓ': return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                    elif val == 'BAJO': return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                    return ''
                
                if tiene_precio:
                    tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia']).format({'Impacto_Mensual_$': '${:,.2f}'})
                else:
                    tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia'])
                    
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
    # PIE DE PÁGINA GLOBAL
    # =========================================================================
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-family: Arial;'>"
        "📝 Sistema Operativo Elaborado por: <b>Dirección de Supply Chain Sapori</b>"
        "</div>", 
        unsafe_allow_html=True
    )
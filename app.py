import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io
import re

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Portal de Supply Chain & S&OP - Sapori",
    page_icon="🟢"
)

# ==========================================
# SISTEMA DE DISEÑO GLOBAL
# ==========================================
st.markdown("""
<style>
    :root {
        --primary: #1a3a5c;
        --primary-light: #2c5a8a;
        --accent: #e8a317;
        --bg-card: #ffffff;
        --bg-soft: #f4f7fb;
        --text-main: #1e293b;
        --text-muted: #64748b;
        --border: #e2e8f0;
        --success: #16a34a;
        --warning: #d97706;
        --danger: #dc2626;
    }

    .stApp {
        background-color: #f8fafc;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3a5c 0%, #0f2744 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.93rem;
        padding: 4px 0;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.2);
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.15);
        border-color: rgba(255,255,255,0.35);
    }
    [data-testid="stSidebar"] .stNumberInput input {
        background: rgba(255,255,255,0.08) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }

    /* Títulos */
    h1, h2, h3, h4 {
        color: var(--primary) !important;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Cards de métricas */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }

    /* Botones */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"] {
        background: var(--primary);
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-light);
        box-shadow: 0 4px 12px rgba(26,58,92,0.25);
    }

    /* Inputs y selects */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stNumberInput input {
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
    }

    /* Separadores */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #cbd5e1, transparent);
        margin: 1.4rem 0;
    }

    /* Tablas */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    /* Login card */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 85vh;
    }
    .login-card {
        background: white;
        border-radius: 16px;
        padding: 2.5rem 2.2rem;
        box-shadow: 0 12px 40px rgba(26,58,92,0.12);
        border: 1px solid #e2e8f0;
        max-width: 420px;
        width: 100%;
        margin: 0 auto;
    }

    /* Header de módulo */
    .module-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8a 100%);
        color: white;
        padding: 14px 24px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.12rem;
        letter-spacing: 0.02em;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 12px rgba(26,58,92,0.18);
    }

    /* Sección de KPIs */
    .kpi-section-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin: 0.8rem 0 0.5rem 0;
    }

    /* Footer */
    .footer-custom {
        margin-top: 2.5rem;
        padding: 1.2rem 0.5rem;
        border-top: 1px solid var(--border);
        font-size: 0.82rem;
        color: var(--text-muted);
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# ==========================================
# MÓDULO DE ACCESO / LOGIN
# ==========================================
if not st.session_state['autenticado']:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_allow_html=True)

    if os.path.exists("logo_empresa.png"):
        st.image("logo_empresa.png", width=180)
    else:
        st.markdown(
            "<h1 style='text-align:center; color:#1a3a5c; margin:0; font-size:2rem; letter-spacing:0.04em;'>SAPORI</h1>",
            unsafe_allow_html=True
        )

    st.markdown("""
        <p style='text-align:center; color:#64748b; margin:0.4rem 0 1.6rem 0; font-size:0.95rem;'>
            Portal de Supply Chain &amp; S&amp;OP
        </p>
    """, unsafe_allow_html=True)

    with st.form("formulario_login"):
        st.markdown("##### 🔐 Credenciales corporativas")
        usuario = st.text_input("Usuario o Correo Institucional", placeholder="ej. gerencia.operaciones")
        contrasena = st.text_input("Contraseña del Sistema", type="password", placeholder="••••••••")
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        boton_ingresar = st.form_submit_button("Acceder al Sistema", type="primary", use_container_width=True)

        if boton_ingresar:
            usuarios_autorizados = {
                "admin": "sapori2026",
                "Jair Ramos": "1402",
                "Romulo Delgado": "gerencia123",
                "logistica": "logistica2026"
            }
            if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == contrasena:
                st.session_state['autenticado'] = True
                st.success("✅ Acceso concedido. Inicializando entorno...")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas. Verifique e intente de nuevo.")

    st.markdown("""
        <p style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:1.6rem; line-height:1.5;'>
            © 2026 Sapori · Dirección de Supply Chain &amp; Operaciones<br>
            Versión 3.1 (Lógica Dinámica)
        </p>
    """, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

# ==========================================
# ENTORNO DEL SISTEMA AUTENTICADO
# ==========================================
else:
    # ----- SIDEBAR -----
    with st.sidebar:
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)

        st.markdown("### Módulos de Operación")
        modulo_activo = st.radio(
            "Área a visualizar",
            [
                "1. Control Operativo de Ventas y Forecast",
                "2. Tablero de Desviaciones y Tendencias",
                "3. Control y Análisis de Producción Mensual"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Control de Tiempos")
        dias_efectivos = st.number_input("Días de Venta Efectivos", min_value=1, value=8, step=1)
        dias_restantes = st.number_input("Días de Venta Restantes", min_value=0, value=15, step=1)

        st.markdown("---")
        st.caption("👤 Rol: Administrador / Gerencia")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

    # =========================================================================
    # MÓDULO 1: VENTA DIARIA Y FORECAST
    # =========================================================================
    if modulo_activo == "1. Control Operativo de Ventas y Forecast":
        st.title("📈 Rendimiento Comercial y Proyecciones de Demanda")
        st.caption("Ventas diarias · Forecast · Alcance")

        file_ventas = "VINCULO VTS BY SKU.xlsx"

        if not os.path.exists(file_ventas):
            st.error(f"❌ **Archivo requerido no encontrado:** '{file_ventas}'")
            st.info("💡 Guarde la matriz con el nombre exacto **'VINCULO VTS BY SKU.xlsx'** en la raíz de la carpeta.")
        else:
            try:
                df_kpis = pd.read_excel(file_ventas, sheet_name="DASHBOARD", header=None)

                val_gross = pd.to_numeric(df_kpis.iloc[2, 0], errors='coerce')
                val_net = pd.to_numeric(df_kpis.iloc[2, 1], errors='coerce')
                val_prom_dia = pd.to_numeric(df_kpis.iloc[2, 2], errors='coerce')
                val_pronost_mes = pd.to_numeric(df_kpis.iloc[2, 3], errors='coerce')
                val_forecast = pd.to_numeric(df_kpis.iloc[2, 4], errors='coerce')
                val_efficiency = df_kpis.iloc[2, 5]
                val_dif_units = pd.to_numeric(df_kpis.iloc[2, 6], errors='coerce')

                val_return = pd.to_numeric(df_kpis.iloc[4, 0], errors='coerce')
                fecha_inicio = df_kpis.iloc[4, 1]
                fecha_final = df_kpis.iloc[4, 3]

                val_gross = val_gross if pd.notna(val_gross) else 0
                val_net = val_net if pd.notna(val_net) else 0
                val_prom_dia = val_prom_dia if pd.notna(val_prom_dia) else 0
                val_pronost_mes = val_pronost_mes if pd.notna(val_pronost_mes) else 0
                val_forecast = val_forecast if pd.notna(val_forecast) else 0
                val_dif_units = val_dif_units if pd.notna(val_dif_units) else 0
                val_return = val_return if pd.notna(val_return) else 0

                if isinstance(val_efficiency, str):
                    val_efficiency = float(val_efficiency.replace('%', '').replace(',', '.').strip())
                elif isinstance(val_efficiency, (int, float)):
                    val_efficiency = val_efficiency * 100 if val_efficiency <= 1.0 else val_efficiency
                val_efficiency = val_efficiency if pd.notna(val_efficiency) else 0

                fecha_inicio_str = (
                    pd.to_datetime(fecha_inicio).strftime('%d/%m/%Y')
                    if pd.notna(pd.to_datetime(fecha_inicio, errors='coerce'))
                    else "01/07/2026"
                )
                fecha_final_str = (
                    pd.to_datetime(fecha_final).strftime('%d/%m/%Y')
                    if pd.notna(pd.to_datetime(fecha_final, errors='coerce'))
                    else "31/07/2026"
                )

                st.markdown(
                    '<div class="module-header">DASHBOARD DE CONTROL OPERATIVO DE DEMANDA</div>',
                    unsafe_allow_html=True
                )

                # --- KPIs de Volumen ---
                st.markdown('<p class="kpi-section-label">Indicadores de Volumen</p>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Units Sales Gross", f"{val_gross:,.0f}".replace(",", "."))
                c2.metric("Total Units Sales Net", f"{val_net:,.0f}".replace(",", "."))
                c3.metric("Promedio Venta Diaria", f"{val_prom_dia:,.0f}".replace(",", "."))
                c4.metric("Pronóstico Venta Mensual", f"{val_pronost_mes:,.0f}".replace(",", "."))

                # --- KPIs de Forecast ---
                st.markdown('<p class="kpi-section-label">Forecast & Alcance</p>', unsafe_allow_html=True)
                c5, c6, c7 = st.columns(3)
                c5.metric("Forecast", f"{val_forecast:,.0f}".replace(",", "."))
                c6.metric("Forecast Efficiency", f"{val_efficiency:,.0f}%")
                delta_dif = "- Brecha de Cobertura" if val_dif_units < 0 else "+ Superávit Comercial"
                c7.metric(
                    "Diferencia Alcance Forecast",
                    f"{val_dif_units:,.0f}".replace(",", "."),
                    delta=delta_dif,
                    delta_color="normal"
                )

                st.markdown("---")

                # --- KPIs de contexto ---
                st.markdown('<p class="kpi-section-label">Contexto Operativo</p>', unsafe_allow_html=True)
                b1, b2, b3, b4, b5 = st.columns(5)
                b1.metric("Units Return", f"{val_return:,.0f}".replace(",", "."))
                b2.metric("Inicio de Venta", fecha_inicio_str)
                b3.metric("Final de Venta", fecha_final_str)
                b4.metric("Días Efectivos", f"{dias_efectivos} días")
                b5.metric("Días Restantes", f"{dias_restantes} días")

                st.markdown("---")

                # --- Tabla SKUs ---
                st.markdown("### 📋 Desglose Operativo: Matriz de Ventas por SKU")
                busqueda_sku = st.text_input(
                    "🔍 Filtrar por Nombre de Producto o SKU de Producción",
                    placeholder="Escriba para filtrar..."
                )

                df_vts = pd.read_excel(file_ventas, sheet_name="file_ventas")
                df_vts_filtrado = df_vts.copy()

                formatos_columnas = {}
                for col in df_vts_filtrado.columns:
                    col_str = str(col).upper()
                    if 'REFERENCIA' in col_str:
                        df_vts_filtrado[col] = (
                            pd.to_numeric(df_vts_filtrado[col], errors='coerce')
                            .fillna(0).astype(int).astype(str)
                        )
                        df_vts_filtrado[col] = df_vts_filtrado[col].replace('0', '')
                    elif 'PROMEDIO' in col_str or 'PROMD' in col_str or 'VENTA' in col_str:
                        df_vts_filtrado[col] = (
                            pd.to_numeric(df_vts_filtrado[col], errors='coerce')
                            .fillna(0).astype(int)
                        )
                        formatos_columnas[col] = lambda x: f"{x:,.0f}".replace(",", ".")

                if busqueda_sku:
                    mask = (
                        df_vts_filtrado.astype(str)
                        .apply(lambda x: x.str.contains(busqueda_sku, case=False, na=False))
                        .any(axis=1)
                    )
                    df_vts_filtrado = df_vts_filtrado[mask]

                if formatos_columnas:
                    st.dataframe(
                        df_vts_filtrado.style.format(formatos_columnas),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.dataframe(df_vts_filtrado, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"Error analítico durante el procesamiento del archivo: {e}")

    # =========================================================================
    # MÓDULO 2: CONTROL DE DESVIACIONES
    # =========================================================================
    elif modulo_activo == "2. Tablero de Desviaciones y Tendencias":
        st.title("📊 Impacto Financiero y Desviaciones Estratégicas")
        st.caption("Análisis Comparativo · Financiero · Pareto (ABC) por SKU")

        file_name = "Comparación de Venta Diaria por SKU (Julio vs Agosto).xlsx"

        if not os.path.exists(file_name):
            st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
        else:
            try:
                df = pd.read_excel(file_name, sheet_name="Table 1")

                if 'CATEGORÍA' not in df.columns:
                    df['CATEGORÍA'] = "Por Asignar"

                for col in ['PROMD VTA DIA JULIO', 'PROMD VTA DIA AGOSTO']:
                    if df[col].dtype == 'object':
                        df[col] = (
                            df[col].astype(str)
                            .str.replace('.', '', regex=False)
                            .str.replace(',', '.', regex=False)
                            .astype(float)
                        )
                    df[col] = df[col].round(0).astype(int)

                if 'Porcentaje de desviación' in df.columns:
                    df['Desviacion_Num'] = (
                        df['Porcentaje de desviación']
                        .astype(str).str.rstrip('%')
                        .str.replace(',', '.', regex=False)
                        .astype(float)
                    )
                else:
                    df['Desviacion_Num'] = (
                        (df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA AGOSTO'])
                        / df['PROMD VTA DIA AGOSTO']
                    ) * 100

                tiene_precio = 'PRECIO UNITARIO' in df.columns
                if tiene_precio:
                    df['Dif_Unidades_Diarias'] = df['PROMD VTA DIA AGOSTO'] - df['PROMD VTA DIA JULIO']
                    df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
                    df['Impacto Mensual $'] = df['Impacto_Diario_$'] * 30

                df = df.sort_values(by='PROMD VTA DIA JULIO', ascending=False).reset_index(drop=True)
                volumen_total_julio = df['PROMD VTA DIA JULIO'].sum()
                df['Porcentaje_Participacion'] = (
                    (df['PROMD VTA DIA JULIO'] / volumen_total_julio) * 100
                    if volumen_total_julio > 0 else 0
                )
                df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()

                def asignar_abc(acumulado):
                    if acumulado <= 80:
                        return 'A'
                    elif acumulado <= 95:
                        return 'B'
                    return 'C'

                df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

                total_skus = len(df)
                subio = (
                    len(df[df['Estado de tendencia'] == 'SUBIÓ'])
                    if 'Estado de tendencia' in df.columns
                    else len(df[df['Desviacion_Num'] > 0])
                )
                bajo = (
                    len(df[df['Estado de tendencia'] == 'BAJO'])
                    if 'Estado de tendencia' in df.columns
                    else len(df[df['Desviacion_Num'] < 0])
                )

                st.markdown(
                    '<div class="module-header">TABLERO DE DESVIACIONES Y TENDENCIAS</div>',
                    unsafe_allow_html=True
                )

                st.markdown('<p class="kpi-section-label">Resumen Ejecutivo</p>', unsafe_allow_html=True)
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Total SKUs en Planta", f"{total_skus} Prod.")
                kpi2.metric("SKUs en Alza", f"{subio}", delta=f"+{subio} SKUs", delta_color="normal")
                kpi3.metric("SKUs en Alerta", f"{bajo}", delta=f"-{bajo} SKUs", delta_color="normal")

                if tiene_precio:
                    impacto_total = df['Impacto Mensual $'].sum()
                    delta_financiero = (
                        "- Mensual (Agosto) vs Julio" if impacto_total < 0
                        else "Mensual (Agosto) vs Julio"
                    )
                    kpi4.metric(
                        "Balance Financiero Proyectado",
                        f"${impacto_total:,.2f}",
                        delta=delta_financiero,
                        delta_color="normal"
                    )
                else:
                    kpi4.metric("Balance", "Falta Precio Unitario")

                st.markdown("---")

                # --- Filtros ---
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    filtro_tendencia = st.selectbox(
                        "🎯 Estado de Tendencia",
                        ["Todos", "SUBIÓ", "BAJO"]
                    )
                with col_f2:
                    filtro_abc = st.selectbox(
                        "📊 Clasificación ABC",
                        ["Todos", "A", "B", "C"]
                    )
                with col_f3:
                    lista_categorias = ["Todos"] + sorted(df['CATEGORÍA'].dropna().unique().tolist())
                    filtro_categoria = st.selectbox("🏷️ Categoría / Marca", lista_categorias)
                with col_f4:
                    busqueda = st.text_input("🔍 Filtrar Nombre", placeholder="Producto o referencia...")

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

                # --- Gráfico ---
                df_grafico = df_filtrado.sort_values(by='PROMD VTA DIA AGOSTO', ascending=False)
                if not df_grafico.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_grafico['PRODUCTO'],
                        y=df_grafico['PROMD VTA DIA JULIO'],
                        name='Julio',
                        marker_color='#1a3a5c'
                    ))
                    fig.add_trace(go.Bar(
                        x=df_grafico['PRODUCTO'],
                        y=df_grafico['PROMD VTA DIA AGOSTO'],
                        name='Agosto',
                        marker_color='#d95f02'
                    ))
                    fig.update_layout(
                        barmode='group',
                        height=500,
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                st.markdown("### 📋 Detalle de Desviaciones")

                if tiene_precio:
                    columnas_render = [
                        'REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC',
                        'PROMD VTA DIA JULIO', 'PROMD VTA DIA AGOSTO',
                        'Porcentaje de desviación', 'Impacto Mensual $', 'Estado de tendencia'
                    ]
                else:
                    columnas_render = [
                        'REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC',
                        'PROMD VTA DIA JULIO', 'PROMD VTA DIA AGOSTO',
                        'Porcentaje de desviación', 'Estado de tendencia'
                    ]

                def resaltar_tendencia(val):
                    if val == 'SUBIÓ':
                        return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                    if val == 'BAJO':
                        return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                    return ''

                formato_columnas = {
                    'PROMD VTA DIA JULIO': '{:,.0f}',
                    'PROMD VTA DIA AGOSTO': '{:,.0f}',
                    'Porcentaje de desviación': '{:.2%}'
                }
                if tiene_precio:
                    formato_columnas['Impacto Mensual $'] = (
                        lambda x: f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )

                tabla_estilizada = (
                    df_filtrado[columnas_render]
                    .style.map(resaltar_tendencia, subset=['Estado de tendencia'])
                    .format(formato_columnas)
                )
                st.dataframe(tabla_estilizada, use_container_width=True, hide_index=True)

                st.markdown("---")
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
                excel_data = buffer.getvalue()
                st.download_button(
                    "📄 Descargar Reporte para Firmas",
                    data=excel_data,
                    file_name="Reporte_Desviaciones.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

            except Exception as e:
                st.error(f"Error crítico en la lectura del archivo Excel: {e}")

    # =========================================================================
    # MÓDULO 3: DASHBOARD DE CONTROL DE PRODUCCIÓN
    # =========================================================================
    elif modulo_activo == "3. Control y Análisis de Producción Mensual":

        def render_modulo_analisis_produccion(file_historico):
            st.title("🏭 Tablero de Control de Producción Mensual")
            st.caption("Monitoreo de Volúmenes de Producción por Categoría · Feb-26 hasta Mes Actual")

            try:
                xls = pd.ExcelFile(file_historico)
                nombres_hojas = xls.sheet_names

                st.markdown(
                    '<div class="module-header">CONTROL Y ANÁLISIS DE PRODUCCIÓN MENSUAL</div>',
                    unsafe_allow_html=True
                )

                st.markdown("### 🎛️ Filtros de Análisis")
                col_filtro1, col_filtro2 = st.columns(2)

                with col_filtro1:
                    categoria_seleccionada = st.selectbox(
                        "🏷️ Categoría (Hoja)",
                        options=nombres_hojas,
                        index=0
                    )

                df = pd.read_excel(xls, sheet_name=categoria_seleccionada)

                # --- Extracción horizontal inteligente ---
                meses_patrones = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
                                  'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
                pairs = []

                def es_celda_fecha(val):
                    if hasattr(val, 'strftime'):
                        return True
                    val_str = str(val).lower().strip()
                    return any(m in val_str for m in meses_patrones)

                conteo_cols = sum(1 for col in df.columns if es_celda_fecha(col))
                if conteo_cols >= 2:
                    for idx, row in df.iterrows():
                        fila_pairs = []
                        for i, col in enumerate(df.columns):
                            if es_celda_fecha(col):
                                val_num = pd.to_numeric(row.iloc[i], errors='coerce')
                                if pd.notna(val_num) and val_num > 0:
                                    fila_pairs.append((col, val_num))
                        if len(fila_pairs) >= 2:
                            pairs = fila_pairs
                            break

                if len(pairs) == 0:
                    for idx, row in df.iterrows():
                        conteo_fila = sum(1 for val in row if es_celda_fecha(val))
                        if conteo_fila >= 2:
                            if idx + 1 < len(df):
                                fila_valores = df.iloc[idx + 1]
                                for i in range(len(row)):
                                    f_val = row.iloc[i]
                                    if es_celda_fecha(f_val):
                                        val_num = pd.to_numeric(fila_valores.iloc[i], errors='coerce')
                                        if pd.notna(val_num) and val_num > 0:
                                            pairs.append((f_val, val_num))
                            break

                if len(pairs) == 0:
                    st.warning("⚠️ No se detectó la secuencia horizontal de meses o valores en esta hoja. Verifica la estructura.")
                    return

                meses_espanol = {
                    'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
                    'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
                    'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
                }

                clean_data = []
                for f_val, val in pairs:
                    if hasattr(f_val, 'strftime'):
                        dt = pd.to_datetime(f_val)
                        if pd.notna(dt):
                            clean_data.append({'Fecha': dt, 'Real': val})
                    else:
                        m_str = str(f_val).lower().strip()
                        for m_letra, m_num in meses_espanol.items():
                            if m_letra in m_str:
                                year_match = re.search(r'(\d{2,4})$', m_str)
                                if year_match:
                                    year_part = year_match.group(1)
                                    m_str_numeric = f"{m_num}-{year_part}"
                                    fmt = '%m-%y' if len(year_part) == 2 else '%m-%Y'
                                    dt = pd.to_datetime(m_str_numeric, format=fmt, errors='coerce')
                                    if pd.notna(dt):
                                        clean_data.append({'Fecha': dt, 'Real': val})
                                break

                df_final = pd.DataFrame(clean_data)
                if df_final.empty:
                    st.warning("⚠️ Las celdas de fecha detectadas no pudieron ser procesadas correctamente.")
                    return

                df_final = df_final.sort_values(by='Fecha').reset_index(drop=True)

                meses_display = {
                    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
                }
                df_final['Mes_Filtro'] = (
                    df_final['Fecha'].dt.month.map(meses_display)
                    + "-"
                    + df_final['Fecha'].dt.strftime('%Y')
                )

                meses_disponibles = ["Todos los meses"] + df_final['Mes_Filtro'].unique().tolist()

                with col_filtro2:
                    mes_seleccionado = st.selectbox(
                        "📅 Mes",
                        options=meses_disponibles
                    )

                if mes_seleccionado != "Todos los meses":
                    df_final = df_final[df_final['Mes_Filtro'] == mes_seleccionado]

                if df_final.empty:
                    st.info("No hay registros para mostrar con el filtro seleccionado.")
                    return

                # --- KPIs ---
                st.markdown("---")
                st.markdown('<p class="kpi-section-label">Indicadores de Producción</p>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)

                total_prod = df_final['Real'].sum()
                promedio_prod = df_final['Real'].mean()
                max_idx = df_final['Real'].idxmax()
                max_row = df_final.loc[max_idx]

                with col1:
                    st.metric("Total Volumen Producido", f"{total_prod:,.0f}".replace(",", "."))
                with col2:
                    st.metric("Promedio Mensual", f"{promedio_prod:,.0f}".replace(",", "."))
                with col3:
                    st.metric(
                        "Pico Más Alto",
                        f"{max_row['Real']:,.0f}".replace(",", "."),
                        f"Mes: {max_row['Mes_Filtro']}"
                    )

                # --- Gráfico ---
                st.markdown("---")
                st.subheader(f"Tendencia de Producción · {categoria_seleccionada}")

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_final['Mes_Filtro'],
                    y=df_final['Real'],
                    name='Producción (Unidades)',
                    marker_color='#1a3a5c',
                    text=[f"{v:,.0f}".replace(",", ".") for v in df_final['Real']],
                    textposition='auto'
                ))
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=20, b=20),
                    hovermode="x unified",
                    yaxis=dict(title="Unidades"),
                    xaxis=dict(title="Meses"),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- Tabla ---
                st.subheader("📋 Resumen de Datos Analizados")
                df_tabla = df_final[['Mes_Filtro', 'Real']].copy()
                df_tabla.columns = ['Mes / Período', 'Producción Real (Unidades)']

                st.dataframe(
                    df_tabla.style.format({
                        'Producción Real (Unidades)': lambda x: f"{x:,.0f}".replace(",", ".")
                    }),
                    use_container_width=True,
                    hide_index=True
                )

            except Exception as e:
                st.error(f"Error analítico durante el procesamiento horizontal: {e}")

        # --- Ejecución del módulo ---
        file_historico_path = "Historico_Produccion_CREMIGURT.xlsx"

        if os.path.exists(file_historico_path):
            render_modulo_analisis_produccion(file_historico_path)
        else:
            st.error(f"❌ **Archivo requerido no encontrado:** '{file_historico_path}'")
            st.info(
                "💡 Asegúrate de que el archivo **'Historico_Produccion_CREMIGURT.xlsx'** "
                "esté guardado en la raíz junto al código."
            )

    # =========================================================================
    # PIE DE PÁGINA GLOBAL
    # =========================================================================
    st.markdown("""
    <div class="footer-custom">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <strong>Plataforma de Inteligencia Operativa</strong><br>
                <span style="font-size:0.75rem; color:#94a3b8;">Versión 3.1 · Entorno Seguro</span>
            </div>
            <div style="text-align:right;">
                Desarrollado por <strong>Jair Ramos</strong><br>
                <span style="color:#1a3a5c; font-weight:600; font-size:0.82rem;">
                    Dirección de Supply Chain Sapori
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

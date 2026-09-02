import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

@st.cache_data
def _cargar_kpis_financieros(path):
    return pd.read_excel(path, sheet_name='Hoja1', header=None)

def renderizar():
    st.markdown("# 🛡️ Salud Financiera y Riesgo de Suministro")
    st.caption("Activos Inventario · Fill Rate · Riesgo Operativo (Quiebre de Stock)")

    file_path = "data/Kpis Financieros Inventario.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_path}'")
        return
        
    try:
        # Cargar datos sin cabecera para extraer por coordenadas exactas
        df_raw = _cargar_kpis_financieros(file_path)
        
        # --- 1. EXTRACCIÓN DE DATOS MACRO ---
        capital_inmovilizado = pd.to_numeric(df_raw.iloc[23, 2], errors='coerce')
        
        # Cálculo de Fill Rate Ponderado
        recepcion_mp = pd.to_numeric(df_raw.iloc[13, 1], errors='coerce')
        recepcion_me = pd.to_numeric(df_raw.iloc[14, 1], errors='coerce')
        req_mp = pd.to_numeric(df_raw.iloc[13, 2], errors='coerce')
        req_me = pd.to_numeric(df_raw.iloc[14, 2], errors='coerce')
        fill_rate_global = (recepcion_mp + recepcion_me) / (req_mp + req_me) if (req_mp + req_me) > 0 else 0
        
        # Cálculo de DIO Global
        inv_mp_tr = pd.to_numeric(df_raw.iloc[8, 1], errors='coerce')
        inv_me_tr = pd.to_numeric(df_raw.iloc[9, 1], errors='coerce')
        cons_mp_tr = pd.to_numeric(df_raw.iloc[8, 2], errors='coerce')
        cons_me_tr = pd.to_numeric(df_raw.iloc[9, 2], errors='coerce')
        dio_global = (inv_mp_tr + inv_me_tr) / (cons_mp_tr + cons_me_tr) if (cons_mp_tr + cons_me_tr) > 0 else 0

        formato_dinero = lambda x: f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # --- SECCIÓN 1: CABECERA ESTRATÉGICA ---
        st.markdown('<div class="module-header">VISIÓN GLOBAL DE RIESGO Y LIQUIDEZ</div>', unsafe_allow_html=True)
        
        # Reducimos a 2 columnas para centrar perfectamente los 2 KPIs restantes
        col1, col2 = st.columns(2)
        
        col1.metric("Capital de Activos Inventario", formato_dinero(capital_inmovilizado))
        col2.metric("Cobertura Global Promedio", f"{dio_global:.1f} Días", "Días de Inventario (DIO)", delta_color="off")

        # --- SECCIÓN 3: GRÁFICOS DE CAPITAL ALLOCATION ---
        st.markdown("---")
        st.subheader("Estructura de Activos Inventario")
        
        val_inicio_mp = pd.to_numeric(df_raw.iloc[18, 1], errors='coerce')
        val_inicio_me = pd.to_numeric(df_raw.iloc[19, 1], errors='coerce')

        col_dona1, col_dona2 = st.columns(2)
        colores_dona = ['#1a3a5c', '#fa7d2a'] # Azul corporativo y Naranja Sapori

        with col_dona1:
            fig1 = go.Figure(data=[go.Pie(labels=["Materia Prima", "Empaque"], values=[val_inicio_mp, val_inicio_me], hole=.5, marker_colors=colores_dona, textinfo='percent+label')])
            fig1.update_layout(title_text="Distribución a Inicio de Mes", showlegend=False, margin=dict(t=40, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig1, use_container_width=True)

        with col_dona2:
            fig2 = go.Figure(data=[go.Pie(labels=["Materia Prima", "Empaque"], values=[inv_mp_tr, inv_me_tr], hole=.5, marker_colors=colores_dona, textinfo='percent+label')])
            fig2.update_layout(title_text="Distribución en Tiempo Real", showlegend=False, margin=dict(t=40, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig2, use_container_width=True)

        # --- SECCIÓN 4: SUPPLIER FILL RATE ---
        st.markdown("---")
        st.subheader("🚚 Presupuesto Compras MPS (Proyección 100% vs Real)")
        
        fill_mp = pd.to_numeric(df_raw.iloc[13, 3], errors='coerce')
        fill_me = pd.to_numeric(df_raw.iloc[14, 3], errors='coerce')

        fig_fill = go.Figure(go.Bar(
            y=['Material Empaque', 'Materia Prima'],
            x=[fill_me, fill_mp],
            orientation='h',
            marker=dict(color=['#dc2626' if v < 0.5 else '#d97706' if v < 0.8 else '#16a34a' for v in [fill_me, fill_mp]]),
            text=[f"{v:.2%}" for v in [fill_me, fill_mp]], textposition='auto'
        ))
        fig_fill.update_layout(xaxis=dict(tickformat=".0%", range=[0, 1]), height=220, margin=dict(t=20, b=20, l=20, r=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_fill, use_container_width=True)

        # --- SECCIÓN 5: MOVIMIENTOS DEL MES ---    
        st.markdown("---")
        st.subheader("📋 Conciliación: Movimientos del Mes Actual")

        # 1. Cálculos de variación (Disponible Actual vs Valor Inicial)
        var_mp_usd = inv_mp_tr - val_inicio_mp
        var_me_usd = inv_me_tr - val_inicio_me
        
        var_mp_pct = (var_mp_usd / val_inicio_mp) if val_inicio_mp > 0 else 0
        var_me_pct = (var_me_usd / val_inicio_me) if val_inicio_me > 0 else 0
        
        # 2. Función para formatear el texto de la tendencia ej: "+$13.602,04 (+9.05%)"
        def format_tendencia(usd, pct):
            if pd.isna(usd) or pd.isna(pct):
                return "Sin datos"
            signo = "+" if usd > 0 else "-"
            # Formateamos el valor absoluto con el estándar de Sapori
            usd_str = f"{abs(usd):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{signo}${usd_str} ({signo}{abs(pct):.2%})"
            
        tendencia_mp = format_tendencia(var_mp_usd, var_mp_pct)
        tendencia_me = format_tendencia(var_me_usd, var_me_pct)

        consumo_mp_val = pd.to_numeric(df_raw.iloc[33, 3], errors='coerce')
        consumo_me_val = pd.to_numeric(df_raw.iloc[34, 3], errors='coerce')

        # 3. Construcción del DataFrame actualizado (Añadido Saldo Inicial)
        data_mov = {
            "Categoría": ["MATERIA PRIMA", "MATERIAL EMPAQUE"],
            "Saldo Inicial (USD)": [val_inicio_mp, val_inicio_me],
            "Recepción/Compras del Mes": [recepcion_mp, recepcion_me],
            "Consumo del Mes": [consumo_mp_val, consumo_me_val],
            "Inventario Final (Hoy)": [inv_mp_tr, inv_me_tr],
            "Tendencia vs Inicio Mes": [tendencia_mp, tendencia_me]
        }
        
        df_movimientos = pd.DataFrame(data_mov)
        
        # --- GRÁFICO DE BARRAS AGRUPADAS (FLUJO CONTABLE DEL MES) ---
        fig_mov = go.Figure()
        
        # 0. Saldo Inicial - Gris neutral corporativo
        fig_mov.add_trace(go.Bar(
            x=df_movimientos['Categoría'],
            y=df_movimientos['Saldo Inicial (USD)'],
            name='Saldo Inicial (Día 1)',
            marker_color='#64748b', 
            text=[f"${v:,.0f}".replace(",", ".") for v in df_movimientos['Saldo Inicial (USD)']],
            textposition='auto'
        ))

        # 1. Recepción (Entradas de Capital) - Verde
        fig_mov.add_trace(go.Bar(
            x=df_movimientos['Categoría'],
            y=df_movimientos['Recepción/Compras del Mes'],
            name='Recepción / Compras',
            marker_color='#16a34a', 
            text=[f"${v:,.0f}".replace(",", ".") for v in df_movimientos['Recepción/Compras del Mes']],
            textposition='auto'
        ))
        
        # 2. Consumo (Salidas de Capital) - Rojo
        fig_mov.add_trace(go.Bar(
            x=df_movimientos['Categoría'],
            y=df_movimientos['Consumo del Mes'],
            name='Consumo del Mes',
            marker_color='#dc2626', 
            text=[f"${v:,.0f}".replace(",", ".") for v in df_movimientos['Consumo del Mes']],
            textposition='auto'
        ))

        # 3. Inventario Disponible (Saldo Final) - Azul Sapori
        fig_mov.add_trace(go.Bar(
            x=df_movimientos['Categoría'],
            y=df_movimientos['Inventario Final (Hoy)'],
            name='Inventario Final (Hoy)',
            marker_color='#1a3a5c', 
            text=[f"${v:,.0f}".replace(",", ".") for v in df_movimientos['Inventario Final (Hoy)']],
            textposition='auto'
        ))
        
        fig_mov.update_layout(
            barmode='group',
            height=420,
            margin=dict(t=30, b=20, l=20, r=20),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Valor en USD ($)", gridcolor='#e2e8f0', zeroline=False)
        )
        
        st.plotly_chart(fig_mov, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # -----------------------------------------------------------

        # 4. Semáforo para la columna de tendencia (Lógica Financiera Invertida)
        def color_tendencia(val):
            val_str = str(val)
            if val_str.startswith('-'):
                # Si baja el inventario: Verde (Favorable, liberamos capital)
                return 'color: #385723; font-weight: bold; background-color: #e2f0d9;' 
            elif val_str.startswith('+'):
                # Si sube el inventario: Naranja/Rojo (Alerta, inmovilizamos capital)
                return 'color: #c65911; font-weight: bold; background-color: #fce4d6;' 
            return ''
            
        # 5. Renderizado de la tabla final
        st.dataframe(
            df_movimientos.style.map(color_tendencia, subset=['Tendencia vs Inicio Mes']).format({
                "Saldo Inicial (USD)": formato_dinero,
                "Recepción/Compras del Mes": formato_dinero,
                "Consumo del Mes": formato_dinero,
                "Inventario Final (Hoy)": formato_dinero
            }),
            use_container_width=True, hide_index=True
        )   
    except Exception as e:
        st.error(f"Error procesando los KPIs Financieros: {e}")
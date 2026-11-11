import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io
from utils import datos

PREFIJO_COL_MES = "PROMD VTA DIA"

def _cargar_desviaciones(path=None):
    return datos.leer_hoja(datos.HOJA_DESVIACIONES)

def preparar(df):
    """Prepara la tabla de desviaciones: columnas de mes, impacto, ABC y conteos. También lo usa el Resumen ejecutivo."""
    if 'CATEGORÍA' not in df.columns:
        df['CATEGORÍA'] = "Por Asignar"

    # Columnas de mes detectadas por nombre: 'PROMD VTA DIA <MES>'.
    # La primera es el mes anterior y la segunda el mes actual (orden del Excel).
    cols_mes = [c for c in df.columns if str(c).strip().upper().startswith(PREFIJO_COL_MES)]
    if len(cols_mes) != 2:
        raise ValueError(
            f"Se esperaban 2 columnas que empiecen por '{PREFIJO_COL_MES}' en la hoja "
            f"'{datos.HOJA_DESVIACIONES}' y se encontraron {len(cols_mes)}: {cols_mes}"
        )
    COL_ANT, COL_ACT = cols_mes
    MES_ANT = str(COL_ANT).strip()[len(PREFIJO_COL_MES):].strip().capitalize()
    MES_ACT = str(COL_ACT).strip()[len(PREFIJO_COL_MES):].strip().capitalize()

    for col in [COL_ANT, COL_ACT]:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        if col in df.columns:
            df[col] = df[col].round(0).astype(int)

    if 'Porcentaje de desviación' in df.columns:
        df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
    else:
        df['Desviacion_Num'] = ((df[COL_ACT] - df[COL_ANT]) / df[COL_ANT]) * 100

    tiene_precio = 'PRECIO UNITARIO' in df.columns
    if tiene_precio:
        df['Dif_Unidades_Diarias'] = df[COL_ACT] - df[COL_ANT]
        df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
        df['Impacto Mensual $'] = df['Impacto_Diario_$'] * 30

    df = df.sort_values(by=COL_ANT, ascending=False).reset_index(drop=True)
    volumen_total_ant = df[COL_ANT].sum()
    df['Porcentaje_Participacion'] = (df[COL_ANT] / volumen_total_ant) * 100 if volumen_total_ant > 0 else 0
    df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()

    def asignar_abc(acumulado):
        if acumulado <= 80: return 'A'
        elif acumulado <= 95: return 'B'
        return 'C'

    df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

    total_skus = len(df)
    subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
    bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
    return {"df": df, "COL_ANT": COL_ANT, "COL_ACT": COL_ACT, "MES_ANT": MES_ANT, "MES_ACT": MES_ACT, "tiene_precio": tiene_precio, "total_skus": total_skus, "subio": subio, "bajo": bajo}


def renderizar():
    st.markdown("# 📊 Impacto Financiero y Desviaciones Estratégicas")
    st.caption("Análisis Comparativo · Financiero · Pareto (ABC) por SKU")

    file_name = datos.ARCHIVO_DATOS

    if not os.path.exists(file_name):
        st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
    else:
        try:
            df = _cargar_desviaciones(file_name)

            _r = preparar(df)
            df = _r["df"]
            COL_ANT = _r["COL_ANT"]
            COL_ACT = _r["COL_ACT"]
            MES_ANT = _r["MES_ANT"]
            MES_ACT = _r["MES_ACT"]
            tiene_precio = _r["tiene_precio"]
            total_skus = _r["total_skus"]
            subio = _r["subio"]
            bajo = _r["bajo"]

            st.markdown('<div class="module-header">TABLERO DE DESVIACIONES Y TENDENCIAS</div>', unsafe_allow_html=True)
            st.markdown('<p class="kpi-section-label">Resumen Ejecutivo</p>', unsafe_allow_html=True)
            
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total SKUs en Planta", f"{total_skus} Prod.")
            kpi2.metric("SKUs en Alza", f"{subio}", delta=f"+{subio} SKUs", delta_color="normal")
            kpi3.metric("SKUs en Alerta", f"{bajo}", delta=f"-{bajo} SKUs", delta_color="normal")

            if tiene_precio:
                impacto_total = df['Impacto Mensual $'].sum()
                delta_financiero = f"- Mensual vs {MES_ANT}" if impacto_total < 0 else f"+ Mensual vs {MES_ANT}"
                impacto_str = f"${impacto_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                kpi4.metric("Balance Financiero Proyectado", impacto_str, delta=delta_financiero, delta_color="normal")
            else:
                kpi4.metric("Balance", "Falta Precio Unitario")

            st.markdown("---")

            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1: filtro_tendencia = st.selectbox("🎯 Estado de Tendencia", ["Todos", "SUBIÓ", "BAJO"])
            with col_f2: filtro_abc = st.selectbox("📊 Clasificación ABC", ["Todos", "A", "B", "C"])
            with col_f3: 
                lista_categorias = ["Todos"] + sorted(df['CATEGORÍA'].dropna().unique().tolist())
                filtro_categoria = st.selectbox("🏷️ Categoría / Marca", lista_categorias)
            with col_f4: busqueda = st.text_input("🔍 Filtrar Nombre", placeholder="Producto o referencia...")

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

            df_grafico = df_filtrado.sort_values(by=COL_ACT, ascending=False)
            if not df_grafico.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico[COL_ANT], name=MES_ANT, marker_color='#1a3a5c'))
                fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico[COL_ACT], name=MES_ACT, marker_color='#d95f02'))
                fig.update_layout(barmode='group', height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, width="stretch")

            st.markdown("---")
            st.markdown("### 📋 Detalle de Desviaciones")

            if tiene_precio:
                columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', COL_ANT, COL_ACT, 'Porcentaje de desviación', 'Impacto Mensual $', 'Estado de tendencia']
            else:
                columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', COL_ANT, COL_ACT, 'Porcentaje de desviación', 'Estado de tendencia']

            def resaltar_tendencia(val):
                if val == 'SUBIÓ': return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                if val == 'BAJO': return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                return ''

            formato_columnas = {
                COL_ANT: lambda x: f"{x:,.0f}".replace(",", "."),
                COL_ACT: lambda x: f"{x:,.0f}".replace(",", "."),
                'Porcentaje de desviación': '{:.2%}'
            }
            
            if tiene_precio:
                formato_columnas['Impacto Mensual $'] = lambda x: f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia']).format(formato_columnas)
            st.dataframe(tabla_estilizada, width="stretch", hide_index=True)

            st.markdown("---")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
            st.download_button("📄 Descargar Reporte para Firmas", data=buffer.getvalue(), file_name="Reporte_Desviaciones.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

        except Exception as e:
            st.error(f"Error crítico en la lectura del archivo Excel: {e}")
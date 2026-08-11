import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import re

def renderizar():
    st.title("🏭 Tablero de Control de Producción Mensual")
    st.caption("Monitoreo de Volúmenes de Producción por Categoría · Feb-26 hasta Mes Actual")

    # NUEVA RUTA
    file_historico_path = "data/Historico_Produccion_CREMIGURT.xlsx"

    if os.path.exists(file_historico_path):
        try:
            xls = pd.ExcelFile(file_historico_path)
            nombres_hojas = xls.sheet_names

            st.markdown('<div class="module-header">CONTROL Y ANÁLISIS DE PRODUCCIÓN MENSUAL</div>', unsafe_allow_html=True)
            st.markdown("### 🎛️ Filtros de Análisis")
            col_filtro1, col_filtro2 = st.columns(2)

            with col_filtro1:
                categoria_seleccionada = st.selectbox("🏷️ Categoría (Hoja)", options=nombres_hojas, index=0)

            df = pd.read_excel(xls, sheet_name=categoria_seleccionada)

            meses_patrones = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
            pairs = []

            def es_celda_fecha(val):
                if hasattr(val, 'strftime'): return True
                val_str = str(val).lower().strip()
                return any(m in val_str for m in meses_patrones)

            conteo_cols = sum(1 for col in df.columns if es_celda_fecha(col))
            if conteo_cols >= 2:
                for idx, row in df.iterrows():
                    fila_pairs = []
                    for i, col in enumerate(df.columns):
                        if es_celda_fecha(col):
                            val_num = pd.to_numeric(row.iloc[i], errors='coerce')
                            if pd.notna(val_num) and val_num > 0: fila_pairs.append((col, val_num))
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
                                    if pd.notna(val_num) and val_num > 0: pairs.append((f_val, val_num))
                        break

            if len(pairs) == 0:
                st.warning("⚠️ No se detectó la secuencia horizontal de meses o valores en esta hoja. Verifica la estructura.")
                return

            meses_espanol = {'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'}
            clean_data = []
            
            for f_val, val in pairs:
                if hasattr(f_val, 'strftime'):
                    dt = pd.to_datetime(f_val)
                    if pd.notna(dt): clean_data.append({'Fecha': dt, 'Real': val})
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
                                if pd.notna(dt): clean_data.append({'Fecha': dt, 'Real': val})
                            break

            df_final = pd.DataFrame(clean_data)
            if df_final.empty:
                st.warning("⚠️ Las celdas de fecha detectadas no pudieron ser procesadas correctamente.")
                return

            df_final = df_final.sort_values(by='Fecha').reset_index(drop=True)
            meses_display = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
            df_final['Mes_Filtro'] = df_final['Fecha'].dt.month.map(meses_display) + "-" + df_final['Fecha'].dt.strftime('%Y')

            meses_disponibles = ["Todos los meses"] + df_final['Mes_Filtro'].unique().tolist()
            with col_filtro2: mes_seleccionado = st.selectbox("📅 Mes", options=meses_disponibles)

            if mes_seleccionado != "Todos los meses":
                df_final = df_final[df_final['Mes_Filtro'] == mes_seleccionado]

            if df_final.empty:
                st.info("No hay registros para mostrar con el filtro seleccionado.")
                return

            st.markdown("---")
            st.markdown('<p class="kpi-section-label">Indicadores de Producción</p>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            total_prod = df_final['Real'].sum()
            promedio_prod = df_final['Real'].mean()
            max_idx = df_final['Real'].idxmax()
            max_row = df_final.loc[max_idx]

            with col1: st.metric("Total Volumen Producido", f"{total_prod:,.0f}".replace(",", "."))
            with col2: st.metric("Promedio Mensual", f"{promedio_prod:,.0f}".replace(",", "."))
            with col3: st.metric("Pico Más Alto", f"{max_row['Real']:,.0f}".replace(",", "."), f"Mes: {max_row['Mes_Filtro']}")

            st.markdown("---")
            st.subheader(f"Tendencia de Producción · {categoria_seleccionada}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_final['Mes_Filtro'], y=df_final['Real'], name='Producción (Unidades)', mode='lines+markers+text',
                line=dict(color='#1a3a5c', width=3), marker=dict(size=9, color='#1a3a5c', line=dict(width=2, color='white')),
                text=[f"{v:,.0f}".replace(",", ".") for v in df_final['Real']], textposition='top center', textfont=dict(size=11, color='#1a3a5c')
            ))
            fig.update_layout(height=450, margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified", yaxis=dict(title="Unidades", gridcolor='#e2e8f0', zeroline=False), xaxis=dict(title="Meses", gridcolor='#f1f5f9'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Resumen de Datos Analizados")
            df_tabla = df_final[['Mes_Filtro', 'Real']].copy()
            df_tabla.columns = ['Mes / Período', 'Producción Real (Unidades)']

            st.dataframe(df_tabla.style.format({'Producción Real (Unidades)': lambda x: f"{x:,.0f}".replace(",", ".")}), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error analítico durante el procesamiento horizontal: {e}")
    else:
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_historico_path}'")
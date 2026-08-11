import streamlit as st
import pandas as pd
import os

def renderizar(dias_efectivos, dias_restantes):
    st.title("📈 Rendimiento Comercial y Proyecciones de Demanda")
    st.caption("Ventas diarias · Forecast · Alcance")

    # NUEVA RUTA
    file_ventas = "data/VINCULO VTS BY SKU.xlsx"

    if not os.path.exists(file_ventas):
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_ventas}'")
    else:
        try:
            df_kpis = pd.read_excel(file_ventas, sheet_name="DASHBOARD", header=None)

            val_gross = pd.to_numeric(df_kpis.iloc[2, 0], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[2, 0], errors='coerce')) else 0
            val_net = pd.to_numeric(df_kpis.iloc[2, 1], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[2, 1], errors='coerce')) else 0
            val_prom_dia = pd.to_numeric(df_kpis.iloc[2, 2], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[2, 2], errors='coerce')) else 0
            val_pronost_mes = pd.to_numeric(df_kpis.iloc[2, 3], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[2, 3], errors='coerce')) else 0
            val_forecast = pd.to_numeric(df_kpis.iloc[2, 4], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[2, 4], errors='coerce')) else 0
            val_efficiency = df_kpis.iloc[2, 5]
            val_dif_units = pd.to_numeric(df_kpis.iloc[2, 6], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[2, 6], errors='coerce')) else 0
            val_return = pd.to_numeric(df_kpis.iloc[4, 0], errors='coerce') if pd.notna(pd.to_numeric(df_kpis.iloc[4, 0], errors='coerce')) else 0
            
            fecha_inicio = df_kpis.iloc[4, 1]
            fecha_final = df_kpis.iloc[4, 3]

            if isinstance(val_efficiency, str):
                val_efficiency = float(val_efficiency.replace('%', '').replace(',', '.').strip())
            elif isinstance(val_efficiency, (int, float)):
                val_efficiency = val_efficiency * 100 if val_efficiency <= 1.0 else val_efficiency
            val_efficiency = val_efficiency if pd.notna(val_efficiency) else 0

            fecha_inicio_str = pd.to_datetime(fecha_inicio).strftime('%d/%m/%Y') if pd.notna(pd.to_datetime(fecha_inicio, errors='coerce')) else "01/07/2026"
            fecha_final_str = pd.to_datetime(fecha_final).strftime('%d/%m/%Y') if pd.notna(pd.to_datetime(fecha_final, errors='coerce')) else "31/07/2026"

            st.markdown('<div class="module-header">DASHBOARD DE CONTROL OPERATIVO DE DEMANDA</div>', unsafe_allow_html=True)

            st.markdown('<p class="kpi-section-label">Indicadores de Volumen</p>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Units Sales Gross", f"{val_gross:,.0f}".replace(",", "."))
            c2.metric("Total Units Sales Net", f"{val_net:,.0f}".replace(",", "."))
            c3.metric("Promedio Venta Diaria", f"{val_prom_dia:,.0f}".replace(",", "."))
            c4.metric("Pronóstico Venta Mensual", f"{val_pronost_mes:,.0f}".replace(",", "."))

            st.markdown('<p class="kpi-section-label">Forecast & Alcance</p>', unsafe_allow_html=True)
            c5, c6, c7 = st.columns(3)
            c5.metric("Forecast", f"{val_forecast:,.0f}".replace(",", "."))
            c6.metric("Forecast Efficiency", f"{val_efficiency:,.0f}%")
            delta_dif = "- Brecha de Cobertura" if val_dif_units < 0 else "+ Superávit Comercial"
            c7.metric("Diferencia Alcance Forecast", f"{val_dif_units:,.0f}".replace(",", "."), delta=delta_dif, delta_color="normal")

            st.markdown("---")
            st.markdown('<p class="kpi-section-label">Contexto Operativo</p>', unsafe_allow_html=True)
            b1, b2, b3, b4, b5 = st.columns(5)
            b1.metric("Units Return", f"{val_return:,.0f}".replace(",", "."))
            b2.metric("Inicio de Venta", fecha_inicio_str)
            b3.metric("Final de Venta", fecha_final_str)
            b4.metric("Días Efectivos", f"{dias_efectivos} días")
            b5.metric("Días Restantes", f"{dias_restantes} días")

            st.markdown("---")
            st.markdown("### 📋 Desglose Operativo: Matriz de Ventas por SKU")
            busqueda_sku = st.text_input("🔍 Filtrar por Nombre de Producto o SKU de Producción", placeholder="Escriba para filtrar...")

            df_vts = pd.read_excel(file_ventas, sheet_name="file_ventas")
            df_vts_filtrado = df_vts.copy()

            formatos_columnas = {}
            for col in df_vts_filtrado.columns:
                col_str = str(col).upper()
                if 'REFERENCIA' in col_str:
                    df_vts_filtrado[col] = pd.to_numeric(df_vts_filtrado[col], errors='coerce').fillna(0).astype(int).astype(str).replace('0', '')
                elif 'PROMEDIO' in col_str or 'PROMD' in col_str or 'VENTA' in col_str:
                    df_vts_filtrado[col] = pd.to_numeric(df_vts_filtrado[col], errors='coerce').fillna(0).astype(int)
                    formatos_columnas[col] = lambda x: f"{x:,.0f}".replace(",", ".")

            if busqueda_sku:
                mask = df_vts_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda_sku, case=False, na=False)).any(axis=1)
                df_vts_filtrado = df_vts_filtrado[mask]

            if formatos_columnas:
                st.dataframe(df_vts_filtrado.style.format(formatos_columnas), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_vts_filtrado, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error analítico durante el procesamiento del archivo: {e}")
import streamlit as st
import pandas as pd
import plotly.express as px
import os

def renderizar():
    st.markdown("# 🗺️ Desempeño Regional de Ventas (CEDIs)")
    st.caption("Análisis de Venta Bruta y Proyección por Centro de Distribución")

    # Ruta del archivo
    file_path = "data/Ventas por cides AGOSTO.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ **No se encontró el archivo:** '{file_path}'")
        return

    try:
        # Extraer nombres de las hojas (filtrando la pestaña de consolidado y CEDIs)
        xls = pd.ExcelFile(file_path)
        hojas = [h for h in xls.sheet_names if "VENTAS CONSOLIDADA" in h]

        # Interfaz de selección de región
        st.markdown("### Seleccione el CEDI a analizar")
        hoja_seleccionada = st.selectbox(
            "Centro de Distribución", 
            hojas, 
            label_visibility="collapsed"
        )

        # Leer la hoja seleccionada (saltamos las primeras 5 filas de metadata)
        df = pd.read_excel(file_path, sheet_name=hoja_seleccionada, skiprows=5)
        
        # Estructurar columnas: Referencia (Código), Producto, Venta Bruta, Venta Diaria, Venta Mes
        df.columns = ["Referencia", "Producto", "Venta_Bruta", "Venta_Diaria", "Venta_Mes", "Vacio"]
        
        # Limpiar datos (quitar filas vacías o de totales)
        df = df.dropna(subset=['Producto', 'Venta_Bruta'])
        df = df[df['Producto'] != "Total general"]
        
        # Asegurar tipos numéricos y limpiar referencias
        df['Referencia'] = df['Referencia'].astype(str).str.replace(".0", "", regex=False)
        df['Venta_Bruta'] = pd.to_numeric(df['Venta_Bruta'], errors='coerce').fillna(0)
        df['Venta_Mes'] = pd.to_numeric(df['Venta_Mes'], errors='coerce').fillna(0)

        # ==========================================
        # SECCIÓN DE KPIs
        # ==========================================
        total_bruta = df['Venta_Bruta'].sum()
        total_mes = df['Venta_Mes'].sum()
        cumplimiento = (total_bruta / total_mes * 100) if total_mes > 0 else 0

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📦 Venta Bruta Actual (Unidades)", f"{total_bruta:,.0f}".replace(",", "."))
        with c2:
            st.metric("🎯 Proyección Fin de Mes (Unidades)", f"{total_mes:,.0f}".replace(",", "."))
        with c3:
            st.metric("📈 Avance de Proyección", f"{cumplimiento:.1f}%")

        st.markdown("---")

        # ==========================================
        # GRÁFICA Y TABLA
        # ==========================================
        col_grafica, col_tabla = st.columns([6, 4])

        with col_grafica:
            st.markdown("##### 🏆 Top 10 Productos Más Vendidos")
            df_top = df.sort_values(by="Venta_Bruta", ascending=False).head(10)
            
            fig = px.bar(
                df_top, 
                x='Venta_Bruta', 
                y='Producto', 
                orientation='h',
                text_auto='.0f',
                color='Venta_Bruta',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_tabla:
            st.markdown("##### 📋 Detalle por SKU (Referencia y Venta)")
            # Seleccionamos únicamente Referencia, Producto y Venta Bruta como pediste
            df_mostrar = df[['Referencia', 'Producto', 'Venta_Bruta']].sort_values(by="Venta_Bruta", ascending=False)
            
            st.dataframe(
                df_mostrar.style.format({
                    "Venta_Bruta": "{:,.0f}"
                }),
                hide_index=True,
                height=400,
                use_container_width=True
            )

    except Exception as e:
        st.error(f"⚠️ **Error al procesar el archivo:** {e}")
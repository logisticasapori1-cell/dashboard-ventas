import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

def renderizar():
    st.title("📦 Cierre de Inventario Valorizado")
    st.caption("Evolución financiera de Materia Prima, Material de Empaque y Producto Terminado")

    file_path = "data/Historico Cierre Inventario Valorizado.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_path}'")
        return

    try:
        # 1. Extracción y Consolidación de Datos
        xls = pd.ExcelFile(file_path)
        data = []
        
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            if not df.empty:
                # Extraemos los valores. Si la columna no existe (ej. Producto Terminado en Enero), asignamos None
                val_mp = df['VALOR $ MATERIA PRIMA'].iloc[0] if 'VALOR $ MATERIA PRIMA' in df.columns else None
                val_me = df['VALOR $ MATERIAL EMPAQUE'].iloc[0] if 'VALOR $ MATERIAL EMPAQUE' in df.columns else None
                val_pt = df['VALOR $ PRODUCTO TERMINADO'].iloc[0] if 'VALOR $ PRODUCTO TERMINADO' in df.columns else None
                
                data.append({"Mes": sheet, "Categoría": "MATERIA PRIMA", "Valor $": val_mp})
                data.append({"Mes": sheet, "Categoría": "MATERIAL EMPAQUE", "Valor $": val_me})
                data.append({"Mes": sheet, "Categoría": "PRODUCTO TERMINADO", "Valor $": val_pt})

        df_consolidado = pd.DataFrame(data)
        
        # 2. Interfaz de Filtros
        st.markdown('<div class="module-header">MÉTRICAS DE CAPITAL DE INVENTARIO</div>', unsafe_allow_html=True)
        st.markdown("### 🎛️ Parámetros de Consulta")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            meses_opciones = ["Todos los meses"] + list(xls.sheet_names)
            filtro_mes = st.selectbox("📅 Seleccione el Mes", meses_opciones)
            
        with col_f2:
            categorias_opciones = ["Todas las Categorías", "MATERIA PRIMA", "MATERIAL EMPAQUE", "PRODUCTO TERMINADO"]
            filtro_categoria = st.selectbox("🏷️ Seleccione la Categoría", categorias_opciones)

        # 3. Aplicación de Filtros
        df_filtrado = df_consolidado.copy()
        
        if filtro_mes != "Todos los meses":
            df_filtrado = df_filtrado[df_filtrado["Mes"] == filtro_mes]
            
        if filtro_categoria != "Todas las Categorías":
            df_filtrado = df_filtrado[df_filtrado["Categoría"] == filtro_categoria]

        # 4. Renderizado de KPIs (NUEVA ESTRUCTURA JERÁRQUICA)
        st.markdown("---")
        st.markdown('<p class="kpi-section-label">Resumen de Valorización</p>', unsafe_allow_html=True)
        
        # Excluimos nulos para la suma total
        valor_total = df_filtrado["Valor $"].sum(skipna=True)
        
        # Función rápida para formato monetario corporativo
        formato_dinero = lambda x: f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # 4.1. Tarjeta Principal (Padre) - Cúspide
        st.markdown(f"""
            <div style="background-color: #1a3a5c; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: center; margin-bottom: 25px;">
                <p style="margin:0; color: #ffffff; font-size: 14px; font-weight: bold; letter-spacing: 1.5px;">VALOR TOTAL DEL INVENTARIO</p>
                <h1 style="margin:0; color: white; font-size: 42px; font-weight: 800;">{formato_dinero(valor_total)}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # 4.2. Sub-clasificaciones (Hijos) - Base de 3 columnas
        if filtro_categoria == "Todas las Categorías":
            mp_total = df_filtrado[df_filtrado["Categoría"] == "MATERIA PRIMA"]["Valor $"].sum(skipna=True)
            me_total = df_filtrado[df_filtrado["Categoría"] == "MATERIAL EMPAQUE"]["Valor $"].sum(skipna=True)
            pt_total = df_filtrado[df_filtrado["Categoría"] == "PRODUCTO TERMINADO"]["Valor $"].sum(skipna=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("TOTAL MATERIA PRIMA", formato_dinero(mp_total))
            c2.metric("TOTAL MATERIAL EMPAQUE", formato_dinero(me_total))
            c3.metric("TOTAL PRODUCTO TERMINADO", formato_dinero(pt_total))
        else:
            promedio = df_filtrado["Valor $"].mean(skipna=True)
            st.metric("Promedio en el Período", formato_dinero(promedio) if pd.notna(promedio) else "$0,00")

        # 5. Gráfica Lineal de Tendencias (Si se seleccionan varios meses)
        st.markdown("---")
        if filtro_mes == "Todos los meses":
            st.subheader("📈 Tendencia Lineal de Cierre Valorizado")
            
            fig = go.Figure()
            
            # Definir colores corporativos para cada línea
            colores = {
                "MATERIA PRIMA": "#1a3a5c",
                "MATERIAL EMPAQUE": "#e8a317",
                "PRODUCTO TERMINADO": "#16a34a"
            }

            categorias_a_graficar = [filtro_categoria] if filtro_categoria != "Todas las Categorías" else ["MATERIA PRIMA", "MATERIAL EMPAQUE", "PRODUCTO TERMINADO"]
            
            for cat in categorias_a_graficar:
                df_cat = df_filtrado[df_filtrado["Categoría"] == cat]
                # Conectamos solo los puntos que existen (ignora nulos visualmente)
                df_cat_plot = df_cat.dropna(subset=["Valor $"])
                
                if not df_cat_plot.empty:
                    fig.add_trace(go.Scatter(
                        x=df_cat_plot["Mes"], 
                        y=df_cat_plot["Valor $"],
                        mode='lines+markers',
                        name=cat,
                        line=dict(color=colores[cat], width=3),
                        marker=dict(size=8, color=colores[cat])
                    ))
                    
            fig.update_layout(
                height=450, 
                margin=dict(l=20, r=20, t=30, b=20), 
                hovermode="x unified", 
                yaxis=dict(title="Valor Total ($)", gridcolor='#e2e8f0'), 
                xaxis=dict(title="Período de Cierre", gridcolor='#f1f5f9'), 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
            )
            st.plotly_chart(fig, use_container_width=True)

        # 6. Tabla Detallada
        st.subheader("📋 Desglose de Registros")
        
        # Preparamos tabla pivotada o directa según el filtro para que se vea más limpia
        if filtro_categoria == "Todas las Categorías":
            tabla_mostrar = df_filtrado.pivot(index='Mes', columns='Categoría', values='Valor $').reset_index()
            # Respetamos el orden cronológico de los meses originales
            tabla_mostrar['Mes'] = pd.Categorical(tabla_mostrar['Mes'], categories=xls.sheet_names, ordered=True)
            tabla_mostrar = tabla_mostrar.sort_values('Mes')
        else:
            tabla_mostrar = df_filtrado.dropna(subset=["Valor $"])
            
        # Aplicamos el formato con puntos y comas a todas las columnas numéricas
        columnas_numericas = tabla_mostrar.select_dtypes(include=['float64', 'int64']).columns
        formato_diccionario = {col: formato_dinero for col in columnas_numericas}
        
        st.dataframe(
            tabla_mostrar.style.format(formato_diccionario, na_rep="No registrado"), 
            use_container_width=True, 
            hide_index=True
        )

    except Exception as e:
        st.error(f"Error procesando el histórico de inventarios: {e}")
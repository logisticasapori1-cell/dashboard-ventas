import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

@st.cache_data
def _cargar_cierre_inventario(path):
    """Lee todas las hojas del histórico de cierre y retorna sheet_names + dict de DataFrames."""
    xls = pd.ExcelFile(path)
    hojas = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}
    return xls.sheet_names, hojas


def _renderizar_tendencia_total(df_consolidado, sheet_names, formato_dinero):
    """Gráfica de línea con el Valor Total del inventario (MP + ME + PT) desde abril hasta el último mes."""
    st.subheader("📊 Tendencia del Valor Total del Inventario (desde Abril)")
    st.caption("Suma de Materia Prima + Material de Empaque + Producto Terminado. Cifras en USD. No depende de los filtros superiores.")

    # Ubicar la hoja de abril (se toma la más reciente si hubiera varias)
    indices_abril = [
        i for i, s in enumerate(sheet_names)
        if "ABR" in str(s).upper() or "APR" in str(s).upper()
    ]
    if not indices_abril:
        st.info("No se encontró una hoja de Abril en el archivo; no es posible construir la tendencia.")
        return

    meses = list(sheet_names[indices_abril[-1]:])

    df = df_consolidado[df_consolidado["Mes"].isin(meses)].copy()
    df["Valor $"] = pd.to_numeric(df["Valor $"], errors="coerce")

    agrupado = df.groupby("Mes")["Valor $"]
    resumen = pd.DataFrame({
        "Mes": meses,
        "Valor_Total": agrupado.sum(min_count=1).reindex(meses).values,
        "Categorias": agrupado.count().reindex(meses).fillna(0).astype(int).values,
    })
    resumen["Var_%"] = resumen["Valor_Total"].pct_change(fill_method=None) * 100

    df_plot = resumen.dropna(subset=["Valor_Total"])
    if df_plot.empty:
        st.info("No hay valores registrados desde Abril.")
        return

    # KPI: variación entre el primer y el último mes del rango
    v_ini, v_fin = df_plot["Valor_Total"].iloc[0], df_plot["Valor_Total"].iloc[-1]
    var_total = ((v_fin - v_ini) / v_ini * 100) if v_ini else 0
    k1, k2, k3 = st.columns(3)
    k1.metric(f"Valor {df_plot['Mes'].iloc[0]} (USD)", formato_dinero(v_ini))
    k2.metric(f"Valor {df_plot['Mes'].iloc[-1]} (USD)", formato_dinero(v_fin))
    k3.metric("Variación en el período", f"{var_total:+.1f}%".replace(".", ","))

    # Textos de hover con formato local
    def _hover(fila):
        texto = f"<b>{fila['Mes']}</b><br>Valor total: {formato_dinero(fila['Valor_Total'])}"
        if pd.notna(fila["Var_%"]):
            texto += f"<br>Var. vs mes anterior: {fila['Var_%']:+.1f}%".replace(".", ",")
        if fila["Categorias"] < 3:
            texto += f"<br>⚠️ Incompleto: {fila['Categorias']}/3 categorías registradas"
        return texto

    incompletos = df_plot["Categorias"] < 3
    colores_marcador = ["#fa7d2a" if inc else "#1a3a5c" for inc in incompletos]

    fig = go.Figure(go.Scatter(
        x=df_plot["Mes"],
        y=df_plot["Valor_Total"],
        mode="lines+markers+text",
        name="Valor Total",
        line=dict(color="#1a3a5c", width=3),
        marker=dict(size=10, color=colores_marcador),
        text=[formato_dinero(v).split(",")[0] for v in df_plot["Valor_Total"]],
        textposition="top center",
        customdata=df_plot.apply(_hover, axis=1),
        hovertemplate="%{customdata}<extra></extra>",
    ))
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(title="Valor Total (USD)", gridcolor="#e2e8f0"),
        xaxis=dict(title="Período de Cierre", gridcolor="#f1f5f9"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    if incompletos.any():
        st.caption("🟠 Los puntos naranjas son meses con alguna categoría sin registrar; su total puede estar subestimado.")

def renderizar():
    st.markdown("# 📦 Cierre de Inventario Valorizado")
    st.caption("Evolución financiera de Materia Prima, Material de Empaque y Producto Terminado")

    file_path = "data/Historico Cierre Inventario Valorizado.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_path}'")
        return

    try:
        # 1. Extracción y Consolidación de Datos
        sheet_names, hojas_dict = _cargar_cierre_inventario(file_path)
        data = []
        
        for sheet in sheet_names:
            df = hojas_dict[sheet]
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
            meses_opciones = ["Todos los meses"] + list(sheet_names)
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
            <div style="background-color: #d1e0f0; padding: 25px; border-radius: 8px; border: 1px solid #d1e0f0; text-align: center; margin-bottom: 25px;">
                <p style="margin:0; color: #94a3b8; font-size: 14px; font-weight: bold; letter-spacing: 1.5px;">VALOR TOTAL DEL INVENTARIO</p>
                <p style="margin:0; font-size: 42px; font-weight: 800;"><span style="color: #ffffff !important;">{formato_dinero(valor_total)}</span></p>
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
                "MATERIAL EMPAQUE": "#fa7d2a",
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

        # 5.1 Tendencia del Valor Total (Abril → último mes)
        st.markdown("---")
        _renderizar_tendencia_total(df_consolidado, sheet_names, formato_dinero)
        st.markdown("---")

        # 6. Tabla Detallada
        st.subheader("📋 Desglose de Registros")
        
        # Preparamos tabla pivotada o directa según el filtro para que se vea más limpia
        if filtro_categoria == "Todas las Categorías":
            tabla_mostrar = df_filtrado.pivot(index='Mes', columns='Categoría', values='Valor $').reset_index()
            # Respetamos el orden cronológico de los meses originales
            tabla_mostrar['Mes'] = pd.Categorical(tabla_mostrar['Mes'], categories=sheet_names, ordered=True)
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
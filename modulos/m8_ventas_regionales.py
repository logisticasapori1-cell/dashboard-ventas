import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

PREFIJO_HOJA = "VENTAS CONSOLIDADA"
HOJA_NACIONAL = "VENTAS CONSOLIDADA"  # Hoja con el total nacional (se excluye del comparativo)


def _es_nacional(hoja):
    return hoja.strip().upper() == HOJA_NACIONAL


@st.cache_data
def _cargar_hojas_regionales(path):
    """Retorna la lista de hojas con 'VENTAS CONSOLIDADA' en el nombre."""
    xls = pd.ExcelFile(path)
    return [h for h in xls.sheet_names if PREFIJO_HOJA in h]


@st.cache_data
def _cargar_hoja_regional(path, hoja):
    return pd.read_excel(path, sheet_name=hoja, skiprows=5)


def _limpiar_df(df):
    """Estandariza columnas y limpia filas vacías / totales."""
    df = df.copy()
    df.columns = ["Referencia", "Producto", "Venta_Bruta", "Venta_Diaria", "Venta_Mes"]
    df = df.dropna(subset=["Producto", "Venta_Bruta"])
    df = df[df["Producto"] != "Total general"]
    # Quita solo el ".0" final (evita dañar referencias como "1.05")
    df["Referencia"] = df["Referencia"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["Venta_Bruta"] = pd.to_numeric(df["Venta_Bruta"], errors="coerce").fillna(0)
    df["Venta_Mes"] = pd.to_numeric(df["Venta_Mes"], errors="coerce").fillna(0)
    return df


def _nombre_cedi(hoja):
    """Obtiene un nombre corto del CEDI a partir del nombre de la hoja."""
    if _es_nacional(hoja):
        return "TOTAL NACIONAL"
    nombre = hoja.replace(PREFIJO_HOJA, "").strip(" -_")
    return nombre if nombre else hoja


@st.cache_data
def _resumen_cedis(path, hojas):
    """Consolida Venta Bruta y Proyección de todos los CEDIs en un solo DataFrame."""
    filas = []
    for hoja in hojas:
        df = _limpiar_df(_cargar_hoja_regional(path, hoja))
        bruta = df["Venta_Bruta"].sum()
        mes = df["Venta_Mes"].sum()
        filas.append({
            "CEDI": _nombre_cedi(hoja),
            "Venta_Bruta": bruta,
            "Venta_Mes": mes,
            "Avance_%": (bruta / mes * 100) if mes > 0 else 0,
            "SKUs": len(df),
        })
    resumen = pd.DataFrame(filas)
    total_bruta = resumen["Venta_Bruta"].sum()
    resumen["Participacion_%"] = (
        resumen["Venta_Bruta"] / total_bruta * 100 if total_bruta > 0 else 0
    )
    return resumen.sort_values("Venta_Bruta", ascending=False)


def _fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def _renderizar_comparativo(file_path, hojas, hoja_nacional=None):
    st.markdown("### 📊 Comparativo entre CEDIs")
    st.caption("Venta Bruta actual vs. Proyección fin de mes por Centro de Distribución (unidades)")

    resumen = _resumen_cedis(file_path, tuple(hojas))

    if resumen.empty:
        st.info("No hay datos disponibles para comparar.")
        return

    tab_vol, tab_avance, tab_part = st.tabs(
        ["Volumen", "Avance de proyección", "Participación"]
    )

    # --- Volumen: barras agrupadas ---
    with tab_vol:
        fig = go.Figure()
        fig.add_bar(
            x=resumen["CEDI"], y=resumen["Venta_Bruta"], name="Venta Bruta",
            marker_color="#1f77b4",
            text=resumen["Venta_Bruta"].map(_fmt), textposition="outside",
        )
        fig.add_bar(
            x=resumen["CEDI"], y=resumen["Venta_Mes"], name="Proyección Mes",
            marker_color="#aec7e8",
            text=resumen["Venta_Mes"].map(_fmt), textposition="outside",
        )
        fig.update_layout(
            barmode="group", height=450,
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis_title="Unidades", xaxis_title="",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Avance %: barras horizontales con línea de meta ---
    with tab_avance:
        df_av = resumen.sort_values("Avance_%")
        fig_av = px.bar(
            df_av, x="Avance_%", y="CEDI", orientation="h",
            color="Avance_%", color_continuous_scale="Blues",
            text=df_av["Avance_%"].map(lambda v: f"{v:.1f}%"),
        )
        fig_av.add_vline(x=100, line_dash="dash", line_color="gray",
                         annotation_text="100%")
        fig_av.update_traces(textposition="outside", cliponaxis=False)
        fig_av.update_layout(
            coloraxis_showscale=False, height=max(350, len(df_av) * 45),
            margin=dict(l=0, r=40, t=30, b=0),
            xaxis_title="% de avance vs. proyección", yaxis_title="",
        )
        st.plotly_chart(fig_av, use_container_width=True)

    # --- Participación: dona ---
    with tab_part:
        fig_pie = px.pie(
            resumen, names="CEDI", values="Venta_Bruta", hole=0.45,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(height=450, margin=dict(l=0, r=0, t=30, b=0),
                              showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Tabla resumen ---
    st.dataframe(
        resumen.style.format({
            "Venta_Bruta": "{:,.0f}",
            "Venta_Mes": "{:,.0f}",
            "Avance_%": "{:.1f}%",
            "Participacion_%": "{:.1f}%",
        }),
        hide_index=True,
        use_container_width=True,
    )

    # --- Cuadre: suma de CEDIs vs. hoja nacional ---
    if hoja_nacional:
        df_nac = _limpiar_df(_cargar_hoja_regional(file_path, hoja_nacional))
        total_nac = df_nac["Venta_Bruta"].sum()
        total_cedis = resumen["Venta_Bruta"].sum()
        diferencia = total_cedis - total_nac
        if abs(diferencia) < 1:
            st.caption(f"✅ La suma de los CEDIs cuadra con el Total Nacional ({_fmt(total_nac)} unidades).")
        else:
            st.warning(
                f"⚠️ La suma de los CEDIs ({_fmt(total_cedis)}) no cuadra con el Total Nacional "
                f"({_fmt(total_nac)}). Diferencia: {_fmt(diferencia)} unidades."
            )


def renderizar():
    st.markdown("# 🗺️ Desempeño Regional de Ventas (CEDIs)")
    st.caption("Análisis de Venta Bruta y Proyección por Centro de Distribución")

    # Ruta del archivo
    file_path = "data/Ventas por cides.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ **No se encontró el archivo:** '{file_path}'")
        return

    try:
        hojas = _cargar_hojas_regionales(file_path)
        hojas_cedis = [h for h in hojas if not _es_nacional(h)]
        hoja_nacional = next((h for h in hojas if _es_nacional(h)), None)

        # ==========================================
        # COMPARATIVO ENTRE CEDIs (sin la hoja nacional)
        # ==========================================
        _renderizar_comparativo(file_path, hojas_cedis, hoja_nacional)
        st.markdown("---")

        # ==========================================
        # DETALLE POR CEDI
        # ==========================================
        st.markdown("### Seleccione el CEDI a analizar")
        opciones = hojas_cedis + ([hoja_nacional] if hoja_nacional else [])
        hoja_seleccionada = st.selectbox(
            "Centro de Distribución",
            opciones,
            format_func=_nombre_cedi,
            label_visibility="collapsed"
        )

        df = _limpiar_df(_cargar_hoja_regional(file_path, hoja_seleccionada))

        # KPIs
        total_bruta = df["Venta_Bruta"].sum()
        total_mes = df["Venta_Mes"].sum()
        cumplimiento = (total_bruta / total_mes * 100) if total_mes > 0 else 0

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📦 Venta Bruta Actual (Unidades)", _fmt(total_bruta))
        with c2:
            st.metric("🎯 Proyección Fin de Mes (Unidades)", _fmt(total_mes))
        with c3:
            st.metric("📈 Avance de Proyección", f"{cumplimiento:.1f}%")

        st.markdown("---")

        # Gráfica y tabla
        col_grafica, col_tabla = st.columns([6, 4])

        with col_grafica:
            st.markdown("##### 🏆 Top 10 Productos Más Vendidos")
            df_top = df.sort_values(by="Venta_Bruta", ascending=False).head(10)

            fig = px.bar(
                df_top,
                x="Venta_Bruta",
                y="Producto",
                orientation="h",
                text_auto=".0f",
                color="Venta_Bruta",
                color_continuous_scale="Blues"
            )
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_tabla:
            st.markdown("##### 📋 Detalle por SKU (Referencia y Venta)")
            df_mostrar = df[["Referencia", "Producto", "Venta_Bruta"]].sort_values(
                by="Venta_Bruta", ascending=False
            )
            st.dataframe(
                df_mostrar.style.format({"Venta_Bruta": "{:,.0f}"}),
                hide_index=True,
                height=400,
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("##### Participación % por SKU — Venta del Mes")
        st.caption("Todos los productos. Cada barra es el peso del SKU sobre el total de Venta Mes del CEDI.")

        df_pct = df.copy()
        df_pct["Pct_Mes"] = (df_pct["Venta_Mes"] / total_mes * 100) if total_mes > 0 else 0
        df_pct = df_pct.sort_values(by="Pct_Mes", ascending=False)

        fig_pct = px.bar(
            df_pct,
            x="Pct_Mes",
            y="Producto",
            orientation="h",
            color="Pct_Mes",
            color_continuous_scale="Blues",
            text=df_pct["Pct_Mes"].map(lambda v: f"{v:.1f}%"),
        )
        fig_pct.update_traces(textposition="outside", cliponaxis=False)
        fig_pct.update_layout(
            yaxis={"categoryorder": "total ascending"},
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=40, t=30, b=0),
            height=max(400, len(df_pct) * 28),
            xaxis_title="% de la venta del mes",
            yaxis_title="",
        )
        st.plotly_chart(fig_pct, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ **Error al procesar el archivo:** {e}")
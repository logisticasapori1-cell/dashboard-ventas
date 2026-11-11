import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import datos, ui
from utils.formato import num, pct, con_signo

PREFIJO_HOJA = datos.PREFIJO_CEDIS
HOJA_NACIONAL = "VENTAS CONSOLIDADA"  # Hoja con el total nacional (se excluye del comparativo)


def _es_nacional(hoja):
    return hoja.strip().upper() == HOJA_NACIONAL


def _cargar_hojas_regionales(path=None):
    """Retorna la lista de hojas que empiezan por 'VENTAS CONSOLIDADA'."""
    return datos.hojas_con_prefijo(PREFIJO_HOJA)


def _cargar_hoja_regional(path, hoja):
    return datos.leer_hoja(hoja, skiprows=5)


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
def _resumen_cedis(path, hojas, ver=None):
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
    return num(n)


def _titulo(hoja):
    return _nombre_cedi(hoja).title()


def _nacional(hoja_nacional):
    if not hoja_nacional:
        return None
    return _limpiar_df(_cargar_hoja_regional(datos.ARCHIVO_DATOS, hoja_nacional))


# ══════════════════════════════════════════════════════════
# 1. VISTA NACIONAL
# ══════════════════════════════════════════════════════════
def _kpis_nacionales(resumen, df_nac):
    suma_bruta = resumen["Venta_Bruta"].sum()
    if df_nac is not None:
        bruta, mes = df_nac["Venta_Bruta"].sum(), df_nac["Venta_Mes"].sum()
        etiqueta = "Venta bruta · total nacional"
    else:
        bruta, mes = suma_bruta, resumen["Venta_Mes"].sum()
        etiqueta = "Venta bruta · suma de CEDIs"
    avance = (bruta / mes * 100) if mes > 0 else 0

    tarjetas = [
        ui.kpi_html(etiqueta, num(bruta), "unid.", nota=f"{len(resumen)} CEDIs"),
        ui.kpi_html("Proyección fin de mes", num(mes), "unid."),
        ui.kpi_html("Avance de proyección", pct(avance), progreso=(avance, "Venta bruta vs. proyección", "")),
    ]
    if df_nac is not None:
        diferencia = suma_bruta - bruta
        cuadra = abs(diferencia) < 1
        tarjetas.append(ui.kpi_html(
            "Cuadre CEDIs vs. nacional", "Cuadra" if cuadra else con_signo(diferencia), "" if cuadra else "unid.",
            delta=None if cuadra else ("Diferencia por revisar", None),
            nota=f"Suma CEDIs {num(suma_bruta)} · Nacional {num(bruta)}"))
    ui.kpis(tarjetas)


def _grafico_volumen(resumen):
    fig = go.Figure()
    fig.add_bar(x=resumen["CEDI"].str.title(), y=resumen["Venta_Bruta"], name="Venta bruta",
                marker_color=ui.NAVY, text=resumen["Venta_Bruta"].map(num), textposition="outside",
                hovertemplate="%{x}<br>Venta bruta: %{text} unid.<extra></extra>")
    fig.add_bar(x=resumen["CEDI"].str.title(), y=resumen["Venta_Mes"], name="Proyección fin de mes",
                marker_color=ui.LIGHTBLUE, text=resumen["Venta_Mes"].map(num), textposition="outside",
                hovertemplate="%{x}<br>Proyección: %{text} unid.<extra></extra>")
    fig.update_traces(cliponaxis=False, textfont=dict(size=11, color=ui.INK))
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.08)
    ui.estilo_grafico(fig, alto=380)
    ui.ejes_miles(fig)
    ui.grafico(fig, clave="cedi_volumen")


def _grafico_avance(resumen):
    df_av = resumen.sort_values("Avance_%")
    colores = [ui.ORANGE if v < 100 else ui.NAVY for v in df_av["Avance_%"]]
    fig = go.Figure(go.Bar(
        x=df_av["Avance_%"], y=df_av["CEDI"].str.title(), orientation="h", marker_color=colores,
        text=df_av["Avance_%"].map(pct), textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>Avance: %{text}<extra></extra>"))
    fig.add_vline(x=100, line_dash="dash", line_color=ui.MUTED, line_width=1.2,
                  annotation_text="Meta 100%", annotation_position="top", annotation_font=dict(color=ui.MUTED, size=11))
    ui.estilo_grafico(fig, alto=max(300, len(df_av) * 56))
    fig.update_xaxes(ticksuffix="%", range=[0, max(110, df_av["Avance_%"].max() * 1.12)], showgrid=True, gridcolor=ui.BORDER)
    fig.update_yaxes(showgrid=False)
    ui.grafico(fig, clave="cedi_avance")


def _tabla_resumen(resumen):
    tabla = resumen.rename(columns={
        "CEDI": "CEDI", "Venta_Bruta": "Venta bruta (unid.)", "Venta_Mes": "Proyección mes (unid.)",
        "Avance_%": "Avance", "SKUs": "SKUs", "Participacion_%": "Participación"})
    tabla["CEDI"] = tabla["CEDI"].str.title()
    st.dataframe(tabla.style.format({
        "Venta bruta (unid.)": num, "Proyección mes (unid.)": num,
        "Avance": pct, "Participación": pct}), hide_index=True, width="stretch")


def _renderizar_comparativo(file_path, hojas, hoja_nacional=None):
    resumen = _resumen_cedis(file_path, tuple(hojas), datos.version())
    if resumen.empty:
        st.info("No hay datos disponibles para comparar.")
        return

    df_nac = _nacional(hoja_nacional)
    _kpis_nacionales(resumen, df_nac)

    with ui.tarjeta("cedi_comparativo", "Comparativo entre CEDIs", "Unidades"):
        vista = st.segmented_control("Vista", ["Volumen", "Avance de proyección", "Participación"],
                                     default="Volumen", required=True, key="cedi_vista",
                                     label_visibility="collapsed")
        if vista == "Volumen":
            ui.leyenda([("Venta bruta", ui.NAVY), ("Proyección fin de mes", ui.LIGHTBLUE)])
            _grafico_volumen(resumen)
        elif vista == "Avance de proyección":
            ui.leyenda([("Avance ≥ 100%", ui.NAVY), ("Avance < 100%", ui.ORANGE)])
            _grafico_avance(resumen)
        else:
            r = resumen.sort_values("Participacion_%", ascending=False)
            ui.barras([(c.title(), b, [pct(p)]) for c, b, p in zip(r["CEDI"], r["Venta_Bruta"], r["Participacion_%"])],
                      columnas_extra=(64,))
        _tabla_resumen(resumen)

        if df_nac is not None:
            total_nac = df_nac["Venta_Bruta"].sum()
            total_cedis = resumen["Venta_Bruta"].sum()
            diferencia = total_cedis - total_nac
            if abs(diferencia) < 1:
                ui.alerta("check", "pos", "La suma de los CEDIs cuadra con el total nacional",
                          f"{num(total_nac)} unidades.")
            else:
                ui.alerta("alert", "aviso", f"La suma de los CEDIs no cuadra con el total nacional",
                          f"Suma CEDIs {num(total_cedis)} · Total nacional {num(total_nac)} · "
                          f"Diferencia {con_signo(diferencia)} unidades.")


# ══════════════════════════════════════════════════════════
# 2. DETALLE POR CEDI
# ══════════════════════════════════════════════════════════
def _excel(df):
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Detalle CEDI")
    return buffer.getvalue()


def _renderizar_detalle(file_path, opciones):
    ui.seccion("Detalle por CEDI", "Seleccione el centro de distribución")
    hoja = st.segmented_control("Centro de distribución", opciones, default=opciones[0], required=True,
                                format_func=_titulo, key="cedi_detalle", label_visibility="collapsed")

    df = _limpiar_df(_cargar_hoja_regional(file_path, hoja))
    total_bruta = df["Venta_Bruta"].sum()
    total_mes = df["Venta_Mes"].sum()
    cumplimiento = (total_bruta / total_mes * 100) if total_mes > 0 else 0
    nombre = _titulo(hoja)

    ui.kpis([
        ui.kpi_html(f"Venta bruta actual · {nombre}", num(total_bruta), "unid.", nota=f"{len(df)} SKU"),
        ui.kpi_html("Proyección fin de mes", num(total_mes), "unid."),
        ui.kpi_html("Avance de proyección", pct(cumplimiento), progreso=(cumplimiento, "Venta bruta vs. proyección", "")),
    ], minimo=260)

    col_top, col_tabla = st.columns([3, 2], gap="medium")
    with col_top:
        with ui.tarjeta("cedi_top", f"Top 10 productos · {nombre}", "Venta bruta · unidades · % del CEDI"):
            top = df.sort_values(by="Venta_Bruta", ascending=False).head(10)
            ui.barras([(p, v, [pct(v / total_bruta * 100) if total_bruta else "–"])
                       for p, v in zip(top["Producto"], top["Venta_Bruta"])], columnas_extra=(56,))
    with col_tabla:
        with ui.tarjeta("cedi_tabla", "Detalle por SKU", "Referencia y venta bruta"):
            df_mostrar = df[["Referencia", "Producto", "Venta_Bruta"]].sort_values(by="Venta_Bruta", ascending=False)
            df_mostrar = df_mostrar.rename(columns={"Venta_Bruta": "Venta bruta (unid.)"})
            st.dataframe(df_mostrar.style.format({"Venta bruta (unid.)": num}), hide_index=True, height=360, width="stretch",
                         column_config={"Referencia": st.column_config.TextColumn("Ref.", width=70),
                                        "Producto": st.column_config.TextColumn("Producto", width="medium"),
                                        "Venta bruta (unid.)": st.column_config.NumberColumn("Venta bruta", width=90)})
            st.download_button("Descargar Excel", data=_excel(df_mostrar), file_name=f"Venta_{nombre.replace(' ', '_')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               icon=":material/download:", width="stretch", key="cedi_descarga")

    with ui.tarjeta("cedi_participacion", f"Participación por SKU en la venta del mes · {nombre}",
                    "Peso de cada SKU sobre la proyección del mes del CEDI · todos los productos"):
        df_pct = df.copy()
        df_pct["Pct_Mes"] = (df_pct["Venta_Mes"] / total_mes * 100) if total_mes > 0 else 0
        df_pct = df_pct.sort_values(by="Pct_Mes", ascending=False)
        with st.container(height=440, border=False):
            ui.barras([(p, m, [pct(x)]) for p, m, x in zip(df_pct["Producto"], df_pct["Venta_Mes"], df_pct["Pct_Mes"])],
                      columnas_extra=(56,))


# ══════════════════════════════════════════════════════════
# PÁGINA
# ══════════════════════════════════════════════════════════
def renderizar():
    ui.encabezado("Comercial › Desempeño por CEDI", "Desempeño por CEDI",
                  "Venta bruta y proyección de fin de mes por centro de distribución · Cifras en unidades")

    file_path = datos.ARCHIVO_DATOS
    if not datos.existe():
        datos.mostrar_error_archivo()
        return

    try:
        hojas = _cargar_hojas_regionales(file_path)
        hojas_cedis = [h for h in hojas if not _es_nacional(h)]
        hoja_nacional = next((h for h in hojas if _es_nacional(h)), None)

        _renderizar_comparativo(file_path, hojas_cedis, hoja_nacional)

        opciones = hojas_cedis + ([hoja_nacional] if hoja_nacional else [])
        if opciones:
            _renderizar_detalle(file_path, opciones)

    except Exception as e:
        st.error(f"No se pudo procesar la venta por CEDI: {e}")

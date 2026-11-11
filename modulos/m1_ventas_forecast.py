import io

import pandas as pd
import streamlit as st

from utils import datos, ui
from utils.formato import num, pct, con_signo


def _cargar_kpis(path=None):
    return datos.leer_hoja(datos.HOJA_VENTAS_KPIS, header=None)


def _cargar_ventas_sku(path=None):
    return datos.leer_hoja(datos.HOJA_VENTAS_SKU)


def _numero(valor):
    v = pd.to_numeric(valor, errors="coerce")
    return v if pd.notna(v) else 0


def calcular():
    """KPIs de la hoja 'VTS DASHBOARD' (sin dibujar nada). También lo usa el Resumen ejecutivo."""
    df = _cargar_kpis()

    eficiencia = df.iloc[2, 5]
    if isinstance(eficiencia, str):
        eficiencia = float(eficiencia.replace("%", "").replace(",", ".").strip())
    elif isinstance(eficiencia, (int, float)):
        eficiencia = eficiencia * 100 if eficiencia <= 1.0 else eficiencia
    eficiencia = eficiencia if pd.notna(eficiencia) else 0

    def _fecha(valor, respaldo):
        f = pd.to_datetime(valor, errors="coerce")
        return f if pd.notna(f) else pd.to_datetime(respaldo, dayfirst=True)

    inicio = _fecha(df.iloc[4, 1], "01/07/2026")
    final = _fecha(df.iloc[4, 3], "31/07/2026")

    return {
        "venta_bruta": _numero(df.iloc[2, 0]),
        "venta_neta": _numero(df.iloc[2, 1]),
        "promedio_diario": _numero(df.iloc[2, 2]),
        "pronostico_mes": _numero(df.iloc[2, 3]),
        "forecast": _numero(df.iloc[2, 4]),
        "eficiencia": eficiencia,
        "diferencia": _numero(df.iloc[2, 6]),
        "devoluciones": _numero(df.iloc[4, 0]),
        "inicio": inicio,
        "final": final,
        "inicio_str": inicio.strftime("%d/%m/%Y"),
        "final_str": final.strftime("%d/%m/%Y"),
    }


def _tabla_sku():
    df = _cargar_ventas_sku().copy()
    formatos = {}
    for col in df.columns:
        nombre = str(col).upper()
        if "REFERENCIA" in nombre:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).astype(str).replace("0", "")
        elif "PROMEDIO" in nombre or "PROMD" in nombre or "VENTA" in nombre:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            formatos[col] = lambda x: num(x)
    return df, formatos


def _excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ventas por SKU")
    return buffer.getvalue()


def renderizar(dias_efectivos, dias_restantes):
    ui.encabezado("Comercial › Ventas & Forecast", "Ventas & Forecast",
                  "Ventas diarias, forecast y alcance del período · Cifras en unidades")

    if not datos.existe():
        datos.mostrar_error_archivo()
        return

    try:
        k = calcular()
    except Exception as e:
        st.error(f"No se pudieron leer los indicadores de ventas: {e}")
        return

    devol_pct = (k["devoluciones"] / k["venta_bruta"] * 100) if k["venta_bruta"] else 0

    ui.kpis([
        ui.grupo_html("Venta", principal=(num(k["venta_bruta"]), "unid. brutas"), stats=[
            ui.stat_html("Venta neta", num(k["venta_neta"]), "unid."),
            ui.stat_html("Devoluciones", num(k["devoluciones"]), "unid.", f"{pct(devol_pct)} de la venta bruta"),
        ]),
        ui.grupo_html("Forecast", insignia=f"Eficiencia {k['eficiencia']:,.0f}%",
                      progreso=(k["eficiencia"], f"Pronóstico mensual {num(k['pronostico_mes'])}", f"Forecast {num(k['forecast'])}"),
                      stats=[
                          ui.stat_html("Diferencia de alcance", con_signo(k["diferencia"]), "unid.",
                                       "Brecha de cobertura" if k["diferencia"] < 0 else "Superávit comercial"),
                          ui.stat_html("Promedio venta diaria", num(k["promedio_diario"]), "unid."),
                      ]),
        ui.grupo_html("Período", principal=f"{k['inicio_str']} – {k['final_str']}", stats=[
            ui.stat_html("Días efectivos", str(dias_efectivos), "días"),
            ui.stat_html("Días restantes", str(dias_restantes), "días"),
        ]),
    ], minimo=300)

    try:
        df_vts, formatos = _tabla_sku()
    except Exception as e:
        st.error(f"No se pudo leer la matriz de ventas por SKU: {e}")
        return

    col_prod = next((c for c in df_vts.columns if "PRODUCTO" in str(c).upper()), None)
    col_venta = next((c for c in df_vts.columns if str(c).upper() == "VENTA BRUTA"), None)
    if col_prod and col_venta:
        total = df_vts[col_venta].sum()
        top = df_vts.sort_values(col_venta, ascending=False).head(10)
        with ui.tarjeta("top_sku", "Top 10 SKU por venta bruta", "Unidades · % de la venta bruta total"):
            ui.barras([(r[col_prod], r[col_venta], [pct(r[col_venta] / total * 100) if total else "–"])
                       for _, r in top.iterrows()], columnas_extra=(64,))

    with ui.tarjeta("detalle_sku", "Detalle por SKU"):
        c_busq, c_desc = st.columns([3, 1], vertical_alignment="bottom")
        with c_busq:
            busqueda = st.text_input("Buscar SKU", placeholder="Buscar por producto o referencia",
                                     label_visibility="collapsed", icon=":material/search:")
        df_filtrado = df_vts
        if busqueda:
            mascara = df_vts.astype(str).apply(lambda x: x.str.contains(busqueda, case=False, na=False)).any(axis=1)
            df_filtrado = df_vts[mascara]
        with c_desc:
            st.download_button("Descargar Excel", data=_excel(df_filtrado), file_name="Ventas_por_SKU.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               icon=":material/download:", width="stretch")
        if formatos:
            st.dataframe(df_filtrado.style.format(formatos), width="stretch", hide_index=True)
        else:
            st.dataframe(df_filtrado, width="stretch", hide_index=True)
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_vts)} SKU")

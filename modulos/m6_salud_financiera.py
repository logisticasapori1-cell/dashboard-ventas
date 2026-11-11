import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from utils import datos, ui
from utils.formato import num, usd, pct

def _cargar_kpis_financieros(path=None):
    return datos.leer_hoja(datos.HOJA_KPIS_FINANCIEROS, header=None)

def extraer_kpis(df_raw):
    """Valores base de la hoja de KPIs financieros (sin dibujar nada). También lo usa el Resumen ejecutivo."""
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
    return {"capital_inmovilizado": capital_inmovilizado, "recepcion_mp": recepcion_mp, "recepcion_me": recepcion_me, "req_mp": req_mp, "req_me": req_me, "fill_rate_global": fill_rate_global, "inv_mp_tr": inv_mp_tr, "inv_me_tr": inv_me_tr, "cons_mp_tr": cons_mp_tr, "cons_me_tr": cons_me_tr, "dio_global": dio_global}


GRIS = "#b8c4d0"


def movimientos(df_raw, k):
    """Tabla de conciliación del mes (sin dibujar nada). k = extraer_kpis(df_raw)."""
    val_inicio_mp = pd.to_numeric(df_raw.iloc[18, 1], errors='coerce')
    val_inicio_me = pd.to_numeric(df_raw.iloc[19, 1], errors='coerce')
    consumo_mp = pd.to_numeric(df_raw.iloc[33, 3], errors='coerce')
    consumo_me = pd.to_numeric(df_raw.iloc[34, 3], errors='coerce')
    var_mp = k["inv_mp_tr"] - val_inicio_mp
    var_me = k["inv_me_tr"] - val_inicio_me
    return pd.DataFrame({
        "Categoría": ["MATERIA PRIMA", "MATERIAL EMPAQUE"],
        "Saldo Inicial (USD)": [val_inicio_mp, val_inicio_me],
        "Recepción/Compras del Mes": [k["recepcion_mp"], k["recepcion_me"]],
        "Consumo del Mes": [consumo_mp, consumo_me],
        "Inventario Final (Hoy)": [k["inv_mp_tr"], k["inv_me_tr"]],
        "Var_USD": [var_mp, var_me],
        "Var_%": [(var_mp / val_inicio_mp) if val_inicio_mp > 0 else 0, (var_me / val_inicio_me) if val_inicio_me > 0 else 0],
    })


def format_tendencia(v_usd, v_pct):
    if pd.isna(v_usd) or pd.isna(v_pct):
        return "Sin datos"
    signo = "+" if v_usd > 0 else "-"
    return f"{signo}{usd(abs(v_usd))} ({signo}{num(abs(v_pct) * 100, 2)}%)"


def color_tendencia(val):
    """Lógica financiera invertida: bajar inventario libera capital (favorable)."""
    s = str(val)
    if s.startswith('-'):
        return "background-color:#e3f1e8;color:#17734a;font-weight:600;"
    if s.startswith('+'):
        return "background-color:#fde7d9;color:#a84b0b;font-weight:600;"
    return ""


def _estado_compras(v):
    if pd.isna(v):
        return ("Sin datos", None)
    if v < 0.5:
        return ("Crítico (< 50%)", False)
    if v < 0.8:
        return ("En riesgo (50% a 80%)", None)
    return ("Adecuado (≥ 80%)", True)


def _grafico_estructura(inicio, hoy):
    fig = go.Figure()
    for nombre, idx, color in (("Materia prima", 0, ui.NAVY), ("Material de empaque", 1, ui.ORANGE)):
        vals = [hoy[idx], inicio[idx]]
        totales = [sum(hoy), sum(inicio)]
        fig.add_bar(y=["Hoy", "Inicio de mes"], x=vals, name=nombre, orientation="h", marker_color=color,
                    text=[f"{pct(v / t * 100 if t else 0)}" for v, t in zip(vals, totales)], textposition="inside",
                    insidetextanchor="middle", textfont=dict(color="#ffffff", size=13),
                    customdata=[usd(v) for v in vals],
                    hovertemplate="%{y} · " + nombre + "<br>%{customdata} (%{text})<extra></extra>")
    fig.update_layout(barmode="stack", barnorm="percent", bargap=0.35)
    ui.estilo_grafico(fig, alto=220)
    fig.update_xaxes(ticksuffix="%", range=[0, 100], showgrid=True, gridcolor=ui.BORDER)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=13, color=ui.INK))
    ui.grafico(fig, clave="fin_estructura")


def _grafico_movimientos(df):
    fig = go.Figure()
    series = [("Saldo Inicial (USD)", "Saldo inicial (día 1)", GRIS), ("Recepción/Compras del Mes", "Recepción / compras", ui.LIGHTBLUE),
              ("Consumo del Mes", "Consumo del mes", ui.ORANGE), ("Inventario Final (Hoy)", "Inventario final (hoy)", ui.NAVY)]
    etiquetas = [c.capitalize() for c in df["Categoría"]]
    for col, nombre, color in series:
        fig.add_bar(x=etiquetas, y=df[col], name=nombre, marker_color=color,
                    text=[usd(v, dec=0) for v in df[col]], textposition="outside", cliponaxis=False,
                    textfont=dict(size=11, color=ui.INK), hovertemplate="%{x} · " + nombre + "<br>%{text}<extra></extra>")
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.06)
    ui.estilo_grafico(fig, alto=400)
    ui.ejes_miles(fig)
    ui.grafico(fig, clave="fin_movimientos")


def renderizar():
    ui.encabezado("Finanzas › Salud financiera", "Salud financiera y riesgo de suministro",
                  "Capital en inventario, cumplimiento del presupuesto de compras (MPS) y movimientos del mes · Cifras en USD")

    if not datos.existe():
        datos.mostrar_error_archivo()
        return

    try:
        df_raw = _cargar_kpis_financieros()
        k = extraer_kpis(df_raw)
        fill_mp = pd.to_numeric(df_raw.iloc[13, 3], errors='coerce')
        fill_me = pd.to_numeric(df_raw.iloc[14, 3], errors='coerce')
        df_mov = movimientos(df_raw, k)

        # ── 1. Visión global de riesgo y liquidez ───
        e_mp, e_me = _estado_compras(fill_mp), _estado_compras(fill_me)
        ui.kpis([
            ui.kpi_html("Capital de activos inventario", usd(k["capital_inmovilizado"], simbolo=""), "USD"),
            ui.kpi_html("Cobertura global promedio", num(k["dio_global"], 1), "días", nota="Días de inventario (DIO)"),
            ui.kpi_html("Compras MPS · Materia prima", pct(fill_mp * 100, 2) if pd.notna(fill_mp) else "–",
                        progreso=((0 if pd.isna(fill_mp) else fill_mp) * 100, "Real vs. proyección 100%", ""), delta=e_mp),
            ui.kpi_html("Compras MPS · Material de empaque", pct(fill_me * 100, 2) if pd.notna(fill_me) else "–",
                        progreso=((0 if pd.isna(fill_me) else fill_me) * 100, "Real vs. proyección 100%", ""), delta=e_me),
        ], minimo=230)

        # ── 2. Estructura de activos ────────────────
        inicio = [df_mov["Saldo Inicial (USD)"].iloc[0], df_mov["Saldo Inicial (USD)"].iloc[1]]
        hoy = [k["inv_mp_tr"], k["inv_me_tr"]]
        with ui.tarjeta("fin_estructura", "Estructura de activos de inventario",
                        "Participación de materia prima y empaque · inicio de mes vs. hoy"):
            ui.leyenda([("Materia prima", ui.NAVY), ("Material de empaque", ui.ORANGE)])
            _grafico_estructura(inicio, hoy)
            ui.linea_resumen([("Inicio de mes", usd(sum(inicio)), False), ("Hoy", usd(sum(hoy)), False)])

        # ── 3. Conciliación del mes ─────────────────
        with ui.tarjeta("fin_movimientos", "Conciliación: movimientos del mes actual", "USD"):
            ui.leyenda([("Saldo inicial", GRIS), ("Recepción / compras", ui.LIGHTBLUE),
                        ("Consumo", ui.ORANGE), ("Inventario final (hoy)", ui.NAVY)])
            _grafico_movimientos(df_mov)

            tabla = df_mov.drop(columns=["Var_USD", "Var_%"]).copy()
            tabla["Tendencia vs Inicio Mes"] = [format_tendencia(u, p) for u, p in zip(df_mov["Var_USD"], df_mov["Var_%"])]
            tabla["Categoría"] = tabla["Categoría"].str.capitalize()
            dinero = ["Saldo Inicial (USD)", "Recepción/Compras del Mes", "Consumo del Mes", "Inventario Final (Hoy)"]
            st.dataframe(tabla.style.map(color_tendencia, subset=["Tendencia vs Inicio Mes"]).format({c: usd for c in dinero}),
                         width="stretch", hide_index=True, column_config={
                             "Saldo Inicial (USD)": st.column_config.Column("Saldo inicial"),
                             "Recepción/Compras del Mes": st.column_config.Column("Recepción / compras"),
                             "Consumo del Mes": st.column_config.Column("Consumo"),
                             "Inventario Final (Hoy)": st.column_config.Column("Inventario final (hoy)"),
                             "Tendencia vs Inicio Mes": st.column_config.Column("Variación vs. inicio de mes")})
            st.caption("Variación en verde: el inventario bajó y se liberó capital. En naranja: subió y se inmovilizó capital.")

    except Exception as e:
        st.error(f"Error procesando los KPIs Financieros: {e}")

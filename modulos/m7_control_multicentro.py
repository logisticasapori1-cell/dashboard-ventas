import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from utils import datos, ui
from utils.formato import num, usd, pct

def _cargar_sici(path=None):
    return datos.leer_hoja(datos.HOJA_SICI, header=None)

def extraer_totales(df_raw):
    """Totales valorizados y de inventario por CEDI (sin dibujar nada). También lo usa el Resumen ejecutivo."""
    idx_val = df_raw[df_raw[1] == 'VALORIZADO'].index[0]
    idx_inv = df_raw[df_raw[1] == 'INVENTARIO'].index[0]

    val_ccs = pd.to_numeric(df_raw.iloc[idx_val+1, 3], errors='coerce')
    val_car = pd.to_numeric(df_raw.iloc[idx_val+2, 3], errors='coerce')
    val_ori = pd.to_numeric(df_raw.iloc[idx_val+3, 3], errors='coerce')
    val_lar = pd.to_numeric(df_raw.iloc[idx_val+4, 3], errors='coerce')
    val_zul = pd.to_numeric(df_raw.iloc[idx_val+5, 3], errors='coerce')
    val_total = pd.to_numeric(df_raw.iloc[idx_val+6, 3], errors='coerce')

    inv_ccs = pd.to_numeric(df_raw.iloc[idx_inv+1, 3], errors='coerce')
    inv_car = pd.to_numeric(df_raw.iloc[idx_inv+2, 3], errors='coerce')
    inv_ori = pd.to_numeric(df_raw.iloc[idx_inv+3, 3], errors='coerce')
    inv_lar = pd.to_numeric(df_raw.iloc[idx_inv+4, 3], errors='coerce')
    inv_zul = pd.to_numeric(df_raw.iloc[idx_inv+5, 3], errors='coerce')
    inv_total = pd.to_numeric(df_raw.iloc[idx_inv+6, 3], errors='coerce')
    return {"idx_val": idx_val, "idx_inv": idx_inv, "val_ccs": val_ccs, "val_car": val_car, "val_ori": val_ori, "val_lar": val_lar, "val_zul": val_zul, "val_total": val_total, "inv_ccs": inv_ccs, "inv_car": inv_car, "inv_ori": inv_ori, "inv_lar": inv_lar, "inv_zul": inv_zul, "inv_total": inv_total}


CEDIS = ["Caracas", "Carabobo", "Oriente", "Lara", "Zulia"]
VISTA_GLOBAL = "Visión global"
# Columnas de cada CEDI en la hoja SICI (existencia, valor, cobertura, demanda, balance)
MAPA_COLS = {"Caracas": [4, 5, 6, 7, 8], "Carabobo": [9, 10, 11, 12, 13], "Oriente": [14, 15, 16, 17, 18],
             "Lara": [19, 20, 21, 22, 23], "Zulia": [24, 25, 26, 27, 28]}

# Semáforos (mismos umbrales de siempre)
def _rojo(): return f"background-color:{ui.ROJO_BG};color:{ui.ROJO_TX};font-weight:600;"
def _ambar(): return f"background-color:{ui.AMBAR_BG};color:{ui.AMBAR_TX};font-weight:600;"
def _verde(): return f"background-color:{ui.VERDE_BG};color:{ui.VERDE_TX};font-weight:600;"


def semaforo_cobertura(val):
    try:
        v = float(val)
        return _rojo() if v < 7 else (_ambar() if v <= 15 else _verde())
    except (TypeError, ValueError):
        return ""


def semaforo_eficiencia(val):
    try:
        v = float(val)
        return _rojo() if v < 0.70 else (_ambar() if v <= 0.95 else _verde())
    except (TypeError, ValueError):
        return ""


def tabla_vista(df_raw, idx_val, vista):
    """Tabla de productos para la vista elegida (global o un CEDI). Sin dibujar nada."""
    df_tabla_raw = df_raw.iloc[12:idx_val - 2].copy()
    if vista == VISTA_GLOBAL:
        df = df_tabla_raw[[1, 2, 29, 30, 31, 32, 33]].copy()
        df.columns = ["SKU", "Producto", "Existencia Total", "Valor Total ($)", "Demanda Promedio", "Cobertura (Días)", "Eficiencia SICI"]
        numericas = ["Existencia Total", "Valor Total ($)", "Demanda Promedio", "Cobertura (Días)", "Eficiencia SICI"]
    else:
        df = df_tabla_raw[[1, 2] + MAPA_COLS[vista]].copy()
        df.columns = ["SKU", "Producto", "Existencia Local", "Valor Local ($)", "Cobertura (Días)", "Demanda Mensual", "Balance"]
        numericas = ["Existencia Local", "Valor Local ($)", "Cobertura (Días)", "Demanda Mensual", "Balance"]
    for col in numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _excel(df, hoja):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=hoja[:31])
    return buffer.getvalue()


def _usd(x):
    return usd(x) if pd.notna(x) else "–"


def renderizar():
    ui.encabezado("Operaciones › Control Multicentro", "Control Multicentro (SICI)",
                  "Inventario de producto terminado por CEDI · Valor en USD y existencia en unidades")

    if not datos.existe():
        datos.mostrar_error_archivo()
        return

    try:
        df_raw = _cargar_sici()
        t = extraer_totales(df_raw)
        valores = dict(zip(CEDIS, [t["val_ccs"], t["val_car"], t["val_ori"], t["val_lar"], t["val_zul"]]))
        unidades = dict(zip(CEDIS, [t["inv_ccs"], t["inv_car"], t["inv_ori"], t["inv_lar"], t["inv_zul"]]))
        val_total, inv_total = t["val_total"], t["inv_total"]

        # ── 1. Síntesis ──────────────────────────────
        mayor = max(valores, key=lambda k: valores[k] if pd.notna(valores[k]) else -1)
        ui.kpis([
            ui.kpi_html("Inventario total en CEDIs", usd(val_total, simbolo=""), "USD",
                        nota="Producto terminado valorizado"),
            ui.kpi_html("Existencia total", num(inv_total), "unid.", nota="5 CEDIs"),
            ui.kpi_html(f"Mayor concentración · {mayor}",
                        pct(valores[mayor] / val_total * 100) if val_total else "–", "del capital",
                        nota=f"{_usd(valores[mayor])} · {num(unidades[mayor])} unid."),
        ], minimo=260)

        with ui.tarjeta("sici_cedis", "Inventario por CEDI", "Valor (USD) · % del capital · unidades · % de la existencia"):
            orden = sorted(CEDIS, key=lambda c: valores[c] if pd.notna(valores[c]) else -1, reverse=True)
            ui.barras([(c, valores[c], [pct(valores[c] / val_total * 100) if val_total else "–",
                                        num(unidades[c]), pct(unidades[c] / inv_total * 100) if inv_total else "–"])
                       for c in orden], columnas_extra=(60, 72, 60), fmt=_usd, ancho_valor=120)
            ui.linea_resumen([("Total CEDIs", _usd(val_total), False), ("Unidades", num(inv_total), False)])

        # ── 2. Centro de mando logístico ─────────────
        ui.seccion("Centro de mando logístico", "Existencia, valor, cobertura y demanda por producto")
        vista = st.segmented_control("Vista operativa", [VISTA_GLOBAL] + CEDIS, default=VISTA_GLOBAL, required=True,
                                     key="sici_vista", label_visibility="collapsed")
        df_render = tabla_vista(df_raw, t["idx_val"], vista)

        cob = df_render["Cobertura (Días)"]
        criticos, medios, sanos = int((cob < 7).sum()), int(((cob >= 7) & (cob <= 15)).sum()), int((cob > 15).sum())
        ui.kpis([
            ui.kpi_html("Cobertura < 7 días", str(criticos), "SKU", nota="Riesgo de quiebre"),
            ui.kpi_html("Cobertura 7 a 15 días", str(medios), "SKU", nota="Vigilar"),
            ui.kpi_html("Cobertura > 15 días", str(sanos), "SKU", nota="Cubierto"),
        ], minimo=200)

        titulo = "Consolidado SICI" if vista == VISTA_GLOBAL else f"CEDI {vista}"
        with ui.tarjeta("sici_tabla", f"Detalle por producto · {titulo}", f"{len(df_render)} productos"):
            ui.leyenda([("Cobertura < 7 días / eficiencia < 70%", ui.ROJO_BG),
                        ("7 a 15 días / 70% a 95%", ui.AMBAR_BG), ("> 15 días / > 95%", ui.VERDE_BG)])
            estilo = df_render.style.map(semaforo_cobertura, subset=["Cobertura (Días)"])
            if vista == VISTA_GLOBAL:
                estilo = estilo.map(semaforo_eficiencia, subset=["Eficiencia SICI"]).format({
                    "Existencia Total": num, "Valor Total ($)": _usd, "Demanda Promedio": num,
                    "Cobertura (Días)": lambda x: num(x, 1), "Eficiencia SICI": lambda x: pct(x * 100, 0)})
            else:
                estilo = estilo.format({
                    "Existencia Local": num, "Valor Local ($)": _usd, "Cobertura (Días)": lambda x: num(x, 1),
                    "Demanda Mensual": num, "Balance": num})
            st.dataframe(estilo, width="stretch", hide_index=True)
            st.download_button("Descargar Excel", data=_excel(df_render, titulo), file_name=f"SICI_{titulo.replace(' ', '_')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               icon=":material/download:", key="sici_descarga")

    except Exception as e:
        st.error(f"Error analizando la estructura del Excel SICI: {e}")

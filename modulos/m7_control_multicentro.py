"""
Control Multicentro (SICI) · hoja "SICI Inventarios" con formato Odoo + Notas.

Estructura esperada de la hoja (se ubica por TEXTO, no por posición, para que
agregar o mover columnas no rompa el módulo):
  - Fila de encabezado cuya primera celda es "Código": Código | Producto | Línea | Precio unitario | UNIDADES … | VALORIZACIÓN …
  - Debajo, una fila con la sucursal (Barcelona/Oriente, Barquisimeto, Carabobo, Distrito Capital, Maracaibo, Total)
  - Debajo, una fila con el origen (Odoo, Notas, Total)
  - Filas de producto hasta "TOTAL PRODUCTO TERMINADO"
  - Bloque opcional "VERIFICACIÓN DE SUMAS"

La cobertura en días NO viene en la hoja: se calcula por CEDI con la proyección
mensual de venta de cada CEDI (hojas "VENTAS CONSOLIDADA <CEDI>"):
    cobertura (días) = existencia total ÷ (proyección mensual ÷ días calendario del mes del período)
"""
import io
import re
import unicodedata
from calendar import monthrange

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import datos, ui
from utils.formato import num, usd, pct

CEDIS = ["Caracas", "Carabobo", "Oriente", "Lara", "Zulia"]
VISTA_GLOBAL = "Visión global"
# Nombre de la sucursal en la hoja SICI -> nombre del CEDI en el portal
SUCURSALES = {"barcelona/oriente": "Oriente", "oriente": "Oriente", "barquisimeto": "Lara", "lara": "Lara",
              "carabobo": "Carabobo", "distrito capital": "Caracas", "caracas": "Caracas",
              "maracaibo": "Zulia", "zulia": "Zulia", "total": "Total"}
UMBRAL_CRITICO, UMBRAL_VIGILAR = 7, 15   # días de cobertura (mismos umbrales de siempre)


def _cargar_sici(path=None):
    return datos.leer_hoja(datos.HOJA_SICI, header=None)


def _norm(x):
    s = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().strip().lower()
    return re.sub(r"\s+", " ", s)


def _codigo(x):
    return re.sub(r"\.0$", "", str(x).strip())


# ══════════════════════════════════════════════════════════
# LECTURA DE LA HOJA (sin dibujar nada)
# ══════════════════════════════════════════════════════════
def leer_sici(df_raw):
    """Convierte la hoja SICI en datos ordenados.

    Retorna dict:
      productos: DataFrame con Código, Producto, Línea, Precio y columnas "u|<CEDI>|<origen>" / "v|<CEDI>|<origen>"
                 (u = unidades, v = valor; CEDI en CEDIS + "Total"; origen Odoo / Notas / Total)
      total_hoja: dict con la fila TOTAL PRODUCTO TERMINADO (mismas claves que las columnas), si existe
      verificacion: DataFrame del bloque VERIFICACIÓN DE SUMAS, si existe
      fecha_reporte: texto dd/mm/aaaa hh:mm encontrado en el título, o None
    """
    col0 = df_raw[0].map(_norm)
    filas_h = col0[col0.isin(["codigo", "cod", "sku"])].index
    if len(filas_h) == 0:
        raise ValueError("No se encontró la fila de encabezado 'Código' en la hoja SICI.")
    fh = filas_h[0]

    # Encabezados combinados: el grupo (UNIDADES / VALORIZACIÓN) y la sucursal se escriben solo en la
    # primera columna de cada bloque, así que se completan hacia la derecha.
    grupo = df_raw.iloc[fh].copy()
    grupo.iloc[4:] = grupo.iloc[4:].ffill()
    sucursal = df_raw.iloc[fh + 1].copy()
    sucursal.iloc[4:] = sucursal.iloc[4:].ffill()
    origen = df_raw.iloc[fh + 2]

    columnas = {}
    for c in df_raw.columns:
        g, sc, o = _norm(grupo[c]), _norm(sucursal[c]), _norm(origen[c])
        if g.startswith("unidades") or g.startswith("valoriz"):
            cedi = SUCURSALES.get(sc)
            if cedi and o in ("odoo", "notas", "total"):
                columnas[c] = f"{'u' if g.startswith('unidades') else 'v'}|{cedi}|{o.capitalize()}"
            continue
        if g == "producto": columnas[c] = "Producto"
        elif g.startswith("codigo"): columnas[c] = "Código"
        elif g.startswith("linea"): columnas[c] = "Línea"
        elif g.startswith("precio"): columnas[c] = "Precio"
    if "Código" not in columnas.values() or not any(k.startswith("u|") for k in columnas.values()):
        raise ValueError("La hoja SICI no tiene las columnas esperadas (Código, UNIDADES por sucursal y origen).")

    cuerpo = df_raw.iloc[fh + 3:]
    fin = cuerpo.index[cuerpo[0].map(_norm).str.startswith("total")]
    corte = fin[0] if len(fin) else cuerpo.index[-1] + 1
    prod = cuerpo.loc[:corte - 1, list(columnas)].rename(columns=columnas)
    prod = prod[pd.to_numeric(prod["Código"], errors="coerce").notna()].copy()
    prod["Código"] = prod["Código"].map(_codigo)
    numericas = [c for c in prod.columns if c.startswith(("u|", "v|"))] + (["Precio"] if "Precio" in prod else [])
    for c in numericas:
        prod[c] = pd.to_numeric(prod[c], errors="coerce").fillna(0)
    if "Línea" not in prod:
        prod["Línea"] = "Sin línea"
    prod["Línea"] = prod["Línea"].fillna("Sin línea")

    total_hoja = None
    if len(fin):
        fila = df_raw.loc[fin[0]]
        total_hoja = {columnas[c]: pd.to_numeric(fila[c], errors="coerce") for c in columnas if columnas[c].startswith(("u|", "v|"))}

    verificacion = None
    fv = df_raw.index[col0.str.startswith("verificacion")]
    if len(fv):
        bloque = df_raw.loc[fv[0] + 1:]
        vacias = bloque.index[bloque[0].isna()]
        bloque = bloque.loc[:vacias[0] - 1] if len(vacias) else bloque
        if len(bloque) > 1:
            cab = [str(x) for x in bloque.iloc[0] if pd.notna(x)]
            verificacion = bloque.iloc[1:, :len(cab)].copy()
            verificacion.columns = cab

    fecha = None
    for txt in df_raw.iloc[:max(fh, 1), 0].dropna().astype(str):
        m = re.search(r"\d{1,2}/\d{1,2}/\d{4}(?:\s+\d{1,2}:\d{2})?", txt)
        if m:
            fecha = m.group(0)
            break

    return {"productos": prod.reset_index(drop=True), "total_hoja": total_hoja,
            "verificacion": verificacion, "fecha_reporte": fecha}


def extraer_totales(df_raw):
    """Totales por CEDI (mismas claves de siempre; las usa el Resumen ejecutivo)."""
    s = leer_sici(df_raw)
    p = s["productos"]
    def v(cedi): return p.get(f"v|{cedi}|Total", pd.Series(dtype=float)).sum()
    def u(cedi): return p.get(f"u|{cedi}|Total", pd.Series(dtype=float)).sum()
    return {
        "val_ccs": v("Caracas"), "val_car": v("Carabobo"), "val_ori": v("Oriente"), "val_lar": v("Lara"), "val_zul": v("Zulia"),
        "val_total": v("Total") or sum(v(c) for c in CEDIS),
        "inv_ccs": u("Caracas"), "inv_car": u("Carabobo"), "inv_ori": u("Oriente"), "inv_lar": u("Lara"), "inv_zul": u("Zulia"),
        "inv_total": u("Total") or sum(u(c) for c in CEDIS),
    }


# ══════════════════════════════════════════════════════════
# DEMANDA Y COBERTURA POR CEDI
# ══════════════════════════════════════════════════════════
def dias_del_mes():
    """Días de venta del mes: los mismos con que las hojas de CEDI arman la proyección (venta diaria × 21)."""
    return 21


def demanda_mensual_por_cedi():
    """{CEDI: Serie(proyección mensual por Código)} desde las hojas VENTAS CONSOLIDADA <CEDI>."""
    from modulos import m8_ventas_regionales as m8
    out = {}
    for h in m8._cargar_hojas_regionales():
        if m8._es_nacional(h):
            continue
        cedi = SUCURSALES.get(_norm(m8._nombre_cedi(h)))
        if cedi in CEDIS:
            df = m8._limpiar_df(m8._cargar_hoja_regional(None, h))
            out[cedi] = df.groupby(df["Referencia"].map(_codigo))["Venta_Mes"].sum()
    return out


def tabla_vista(productos, demanda, dias, vista):
    """Tabla de productos para la vista elegida, con demanda mensual y cobertura en días."""
    base = productos[["Código", "Producto", "Línea", "Precio"]].copy()
    cedi = "Total" if vista == VISTA_GLOBAL else vista
    base["Odoo"] = productos.get(f"u|{cedi}|Odoo", 0)
    base["Notas"] = productos.get(f"u|{cedi}|Notas", 0)
    base["Existencia"] = productos.get(f"u|{cedi}|Total", 0)
    base["Valor"] = productos.get(f"v|{cedi}|Total", 0)
    if vista == VISTA_GLOBAL:
        demanda_mes = sum((productos["Código"].map(d).fillna(0) for d in demanda.values()), pd.Series(0.0, index=productos.index))
        sin_dato = productos["Código"].map(lambda c: not any(c in d.index for d in demanda.values()))
    else:
        d = demanda.get(vista, pd.Series(dtype=float))
        demanda_mes = productos["Código"].map(d).fillna(0)
        sin_dato = ~productos["Código"].isin(d.index)
    base["Demanda mensual"] = demanda_mes.where(~sin_dato)
    diaria = base["Demanda mensual"] / dias
    base["Cobertura (Días)"] = (base["Existencia"] / diaria).where(diaria > 0)
    return base


def estado_cobertura(fila):
    if pd.isna(fila["Demanda mensual"]):
        return "Sin proyección"
    if fila["Demanda mensual"] <= 0:
        return "Sin venta proyectada"
    v = fila["Cobertura (Días)"]
    return "Crítico" if v < UMBRAL_CRITICO else ("Vigilar" if v <= UMBRAL_VIGILAR else "Cubierto")


# ══════════════════════════════════════════════════════════
# ESTILOS
# ══════════════════════════════════════════════════════════
def _rojo(): return f"background-color:{ui.ROJO_BG};color:{ui.ROJO_TX};font-weight:600;"
def _ambar(): return f"background-color:{ui.AMBAR_BG};color:{ui.AMBAR_TX};font-weight:600;"
def _verde(): return f"background-color:{ui.VERDE_BG};color:{ui.VERDE_TX};font-weight:600;"


def semaforo_cobertura(val):
    try:
        v = float(val)
        if pd.isna(v):
            return ""
        return _rojo() if v < UMBRAL_CRITICO else (_ambar() if v <= UMBRAL_VIGILAR else _verde())
    except (TypeError, ValueError):
        return ""


def _usd(x):
    return usd(x, simbolo=f"{datos.MONEDA_SICI} ") if pd.notna(x) else "–"


def _excel(df, hoja):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=hoja[:31])
    return buffer.getvalue()


def _grafico_origen(productos):
    filas = [(c, productos.get(f"u|{c}|Odoo", pd.Series(dtype=float)).sum(), productos.get(f"u|{c}|Notas", pd.Series(dtype=float)).sum()) for c in CEDIS]
    filas.sort(key=lambda x: x[1] + x[2])
    nombres = [f[0] for f in filas]
    fig = go.Figure()
    for etiqueta, idx, color in (("Odoo", 1, ui.NAVY), ("Notas", 2, ui.ORANGE)):
        vals = [f[idx] for f in filas]
        fig.add_bar(y=nombres, x=vals, name=etiqueta, orientation="h", marker_color=color,
                    customdata=[num(v) for v in vals],
                    hovertemplate="%{y} · " + etiqueta + "<br>%{customdata} unid.<extra></extra>")
    totales = [f[1] + f[2] for f in filas]
    fig.add_scatter(y=nombres, x=totales, mode="text", text=[num(t) for t in totales], textposition="middle right",
                    textfont=dict(size=12, color=ui.INK), hoverinfo="skip", showlegend=False, cliponaxis=False)
    fig.update_layout(barmode="stack", bargap=0.35)
    ui.estilo_grafico(fig, alto=280)
    fig.update_xaxes(showgrid=True, gridcolor=ui.BORDER, range=[0, max(totales) * 1.15 if totales else 1], tickformat=",.0f")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=13, color=ui.INK))
    ui.grafico(fig, clave="sici_origen")


# ══════════════════════════════════════════════════════════
# RESUMEN EN TEXTO (para el Asistente IA)
# ══════════════════════════════════════════════════════════
def resumen_texto(df_raw):
    s = leer_sici(df_raw)
    p = s["productos"]
    dias = dias_del_mes()
    demanda = demanda_mensual_por_cedi()
    lineas = [f"Corte del reporte: {s['fecha_reporte'] or 'sin fecha'} · Moneda: {datos.MONEDA_SICI} · "
              f"Cobertura = existencia ÷ (proyección mensual del CEDI ÷ {dias} días)"]
    for c in CEDIS + ["Total"]:
        u = p.get(f"u|{c}|Total", pd.Series(dtype=float)).sum()
        lineas.append(f"{c}: {num(u)} unid. (Odoo {num(p.get(f'u|{c}|Odoo', pd.Series(dtype=float)).sum())} · "
                      f"Notas {num(p.get(f'u|{c}|Notas', pd.Series(dtype=float)).sum())}) · valor {_usd(p.get(f'v|{c}|Total', pd.Series(dtype=float)).sum())}")
    g = tabla_vista(p, demanda, dias, VISTA_GLOBAL)
    criticos = g[g["Cobertura (Días)"] < UMBRAL_CRITICO].sort_values("Cobertura (Días)")
    lineas.append("SKU con cobertura nacional < 7 días: " + (", ".join(
        f"{r['Producto']} ({num(r['Cobertura (Días)'], 1)} d)" for _, r in criticos.iterrows()) or "ninguno"))
    top = g.sort_values("Valor", ascending=False).head(15)
    lineas.append("Top 15 SKU por valor:\n" + top[["Código", "Producto", "Línea", "Existencia", "Valor", "Cobertura (Días)"]].to_string(index=False))
    sin_precio = p[p["Precio"] <= 0]["Producto"].tolist() if "Precio" in p else []
    if sin_precio:
        lineas.append("SKU sin precio en el maestro: " + ", ".join(sin_precio))
    return "\n".join(lineas)


# ══════════════════════════════════════════════════════════
# PÁGINA
# ══════════════════════════════════════════════════════════
def renderizar():
    if not datos.existe():
        ui.encabezado("Operaciones › Control Multicentro", "Control Multicentro (SICI)")
        datos.mostrar_error_archivo()
        return

    try:
        s = leer_sici(_cargar_sici())
    except Exception as e:
        ui.encabezado("Operaciones › Control Multicentro", "Control Multicentro (SICI)")
        st.error(f"Error analizando la estructura del Excel SICI: {e}")
        return

    p = s["productos"]
    moneda = datos.MONEDA_SICI
    corte = f"Corte {s['fecha_reporte']} · " if s["fecha_reporte"] else ""
    ui.encabezado("Operaciones › Control Multicentro", "Control Multicentro (SICI)",
                  f"{corte}Inventario de producto terminado por CEDI (Odoo + Notas) · Valor en {moneda} y existencia en unidades")

    t = extraer_totales(_cargar_sici())
    valores = dict(zip(CEDIS, [t["val_ccs"], t["val_car"], t["val_ori"], t["val_lar"], t["val_zul"]]))
    unidades = dict(zip(CEDIS, [t["inv_ccs"], t["inv_car"], t["inv_ori"], t["inv_lar"], t["inv_zul"]]))
    val_total, inv_total = t["val_total"], t["inv_total"]
    odoo_total = p.get("u|Total|Odoo", pd.Series(dtype=float)).sum()
    notas_total = p.get("u|Total|Notas", pd.Series(dtype=float)).sum()

    dias = dias_del_mes()
    try:
        demanda = demanda_mensual_por_cedi()
    except Exception as e:
        demanda = {}
        ui.estado("aviso", "No se pudo leer la proyección de venta por CEDI", f"La cobertura no se calculará: {e}")

    # ── 1. Síntesis ──────────────────────────────
    mayor = max(valores, key=lambda k: valores[k])
    g = tabla_vista(p, demanda, dias, VISTA_GLOBAL)
    demanda_total = g["Demanda mensual"].sum()
    cobertura_global = inv_total / (demanda_total / dias) if demanda_total > 0 else None
    ui.kpis([
        ui.kpi_html("Inventario total en CEDIs", usd(val_total, simbolo=""), moneda, nota="Producto terminado valorizado"),
        ui.kpi_html("Existencia total", num(inv_total), "unid.",
                    nota=f"Odoo {pct(odoo_total / inv_total * 100) if inv_total else '–'} · Notas {pct(notas_total / inv_total * 100) if inv_total else '–'}"),
        ui.kpi_html(f"Mayor concentración · {mayor}", pct(valores[mayor] / val_total * 100) if val_total else "–", "del capital",
                    nota=f"{_usd(valores[mayor])} · {num(unidades[mayor])} unid."),
        ui.kpi_html("Cobertura global", num(cobertura_global, 1) if cobertura_global else "–", "días",
                    nota=f"Existencia ÷ proyección de venta de los 5 CEDIs ({dias} días)"),
    ], minimo=230)

    sin_precio = p[p["Precio"] <= 0]["Producto"].tolist() if "Precio" in p else []
    if sin_precio:
        ui.estado("aviso", f"{len(sin_precio)} SKU sin precio en el maestro",
                  f"{', '.join(sin_precio)}: su valor aparece en 0. Revisa la hoja Maestro de precios.")

    if True:
        with ui.tarjeta("sici_cedis", "Inventario por CEDI", f"Valor ({moneda}) · % del capital · unidades · % de la existencia"):
            orden = sorted(CEDIS, key=lambda c: valores[c], reverse=True)
            ui.barras([(c, valores[c], [pct(valores[c] / val_total * 100) if val_total else "–",
                                        num(unidades[c]), pct(unidades[c] / inv_total * 100) if inv_total else "–"])
                       for c in orden], columnas_extra=(56, 64, 56), fmt=_usd, ancho_valor=118)
            ui.linea_resumen([("Total CEDIs", _usd(val_total), False), ("Unidades", num(inv_total), False)])
        with ui.tarjeta("sici_origen", "Origen del inventario por CEDI", "Unidades · Odoo vs. Notas"):
            ui.leyenda([("Odoo (reporte Quants)", ui.NAVY), ("Notas (estado de almacenes)", ui.ORANGE)])
            _grafico_origen(p)

    # ── 2. Centro de mando logístico ─────────────
    ui.seccion("Centro de mando logístico",
               f"Existencia, valor, demanda y cobertura por producto · Cobertura = existencia ÷ (proyección mensual del CEDI ÷ {dias} días)")
    f1, f2 = st.columns([3, 1], vertical_alignment="bottom")
    with f1:
        vista = st.segmented_control("Vista operativa", [VISTA_GLOBAL] + CEDIS, default=VISTA_GLOBAL, required=True,
                                     key="sici_vista", label_visibility="collapsed")
    with f2:
        lineas = ["Todas las líneas"] + sorted(p["Línea"].astype(str).unique().tolist())
        linea = st.selectbox("Línea", lineas, key="sici_linea", label_visibility="collapsed")

    df_render = tabla_vista(p, demanda, dias, vista)
    if linea != "Todas las líneas":
        df_render = df_render[df_render["Línea"].astype(str) == linea]
    estados = df_render.apply(estado_cobertura, axis=1)
    ui.kpis([
        ui.kpi_html("Cobertura < 7 días", str(int((estados == "Crítico").sum())), "SKU", nota="Riesgo de quiebre"),
        ui.kpi_html("Cobertura 7 a 15 días", str(int((estados == "Vigilar").sum())), "SKU", nota="Vigilar"),
        ui.kpi_html("Cobertura > 15 días", str(int((estados == "Cubierto").sum())), "SKU", nota="Cubierto"),
        ui.kpi_html("Sin venta proyectada", str(int(estados.isin(["Sin venta proyectada", "Sin proyección"]).sum())), "SKU",
                    nota="Sin proyección de venta en el CEDI"),
    ], minimo=200)

    titulo = "Consolidado SICI" if vista == VISTA_GLOBAL else f"CEDI {vista}"
    with ui.tarjeta("sici_tabla", f"Detalle por producto · {titulo}", f"{len(df_render)} productos"):
        ui.leyenda([("Cobertura < 7 días", ui.ROJO_BG), ("7 a 15 días", ui.AMBAR_BG), ("> 15 días", ui.VERDE_BG)])
        # Streamlit muestra 'None' en celdas vacías (y el traductor del navegador lo cambiaba):
        # la proyección y la cobertura se entregan ya como texto; el Excel descargado conserva los números.
        cob = df_render["Cobertura (Días)"].tolist()
        tabla_vis = df_render.copy()
        tabla_vis["Demanda mensual"] = [num(x) if pd.notna(x) else "Sin proyección" for x in df_render["Demanda mensual"]]
        tabla_vis["Cobertura (Días)"] = ["Sin proyección" if pd.isna(d) else ("Sin venta" if d <= 0 else num(c, 1))
                                         for d, c in zip(df_render["Demanda mensual"], cob)]
        estilo = tabla_vis.style.apply(lambda _: [semaforo_cobertura(v) for v in cob], subset=["Cobertura (Días)"]).format({
            "Precio": lambda x: _usd(x) if x > 0 else "Sin precio", "Odoo": num, "Notas": num, "Existencia": num,
            "Valor": _usd})
        st.dataframe(estilo, width="stretch", hide_index=True, column_config={
            "Cobertura (Días)": st.column_config.TextColumn("Cobertura (días de venta)", alignment="right"),
            "Código": st.column_config.Column("SKU", width=72), "Producto": st.column_config.Column(width="medium"),
            "Precio": st.column_config.Column(f"Precio ({moneda})"), "Valor": st.column_config.Column(f"Valor ({moneda})"),
            "Existencia": st.column_config.Column("Existencia total"),
            "Demanda mensual": st.column_config.TextColumn("Proyección mensual" if vista != VISTA_GLOBAL else "Proyección mensual (5 CEDIs)", alignment="right")})
        st.download_button("Descargar Excel", data=_excel(df_render, titulo), file_name=f"SICI_{titulo.replace(' ', '_')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           icon=":material/download:", key="sici_descarga")

    # ── 3. Verificación de la hoja ───────────────
    if s["verificacion"] is not None and not s["verificacion"].empty:
        ver = s["verificacion"]
        estados_ver = ver[[c for c in ver.columns if _norm(c).startswith("estado")]]
        todo_ok = estados_ver.astype(str).apply(lambda col: col.str.upper().eq("OK")).all().all() if not estados_ver.empty else None
        with ui.tarjeta("sici_verificacion", "Verificación de sumas del reporte", "Odoo vs. reporte Quants · Notas vs. su detalle"):
            if todo_ok:
                ui.estado("pos", "Todas las sumas cuadran", "Odoo, Notas, total en unidades y valor por sucursal.")
            elif todo_ok is False:
                ui.estado("aviso", "Hay sumas que no cuadran", "Revisa las filas marcadas en la tabla.")
            formato = {}
            for c in ver.columns:
                if pd.to_numeric(ver[c], errors="coerce").notna().all():
                    formato[c] = (lambda x: _usd(float(x))) if _norm(c).startswith("valor") else (lambda x: num(float(x)))
            st.dataframe(ver.style.format(formato), width="stretch", hide_index=True)

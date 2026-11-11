"""
Resumen ejecutivo: 1 o 2 cifras de cada módulo, calculadas con las MISMAS
funciones que usa cada módulo (no hay cálculos paralelos que se desalineen).
Si una sección falla, solo esa sección muestra el aviso; el resto de la página sigue.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modulos import m1_ventas_forecast as m1
from modulos import m2_desviaciones as m2
from modulos import m3_produccion as m3
from modulos import m5_cierre_inventario as m5
from modulos import m6_salud_financiera as m6
from modulos import m7_control_multicentro as m7
from modulos import m8_ventas_regionales as m8
from utils import datos, ui
from utils.formato import num, usd, pct

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_CORTOS = {m.upper(): m[:3] for m in MESES}


def _seguro(funcion):
    try:
        return funcion(), None
    except Exception as e:
        return None, str(e)


# ══════════════════════════════════════════════════════════
# DATOS (cada uno reutiliza las funciones de su módulo)
# ══════════════════════════════════════════════════════════
def _inventario():
    sheet_names, hojas = m5._cargar_cierre_inventario()
    dfc = m5.consolidar(sheet_names, hojas)
    t, aviso = m5.tendencia_total(dfc, sheet_names)
    if aviso:
        raise ValueError(aviso)
    return {"consolidado": dfc, "meses": sheet_names, **t}


def _finanzas():
    return m6.extraer_kpis(m6._cargar_kpis_financieros())


def _produccion():
    nombres, hojas = m3._cargar_hojas_produccion()
    serie, aviso = m3.serie_produccion(hojas[nombres[0]])
    if aviso:
        raise ValueError(aviso)
    return serie


def _cedis():
    hojas = m8._cargar_hojas_regionales()
    regionales = [h for h in hojas if not m8._es_nacional(h)]
    nacional = next((h for h in hojas if m8._es_nacional(h)), None)
    resumen = m8._resumen_cedis(datos.ARCHIVO_DATOS, tuple(regionales), datos.version())
    total_nacional = None
    if nacional:
        total_nacional = m8._limpiar_df(m8._cargar_hoja_regional(datos.ARCHIVO_DATOS, nacional))["Venta_Bruta"].sum()
    return resumen, total_nacional


def _desviaciones():
    return m2.preparar(m2._cargar_desviaciones())


def _multicentro():
    return m7.extraer_totales(m7._cargar_sici())


# ══════════════════════════════════════════════════════════
# SECCIONES
# ══════════════════════════════════════════════════════════
def _no_disponible(etiqueta, error):
    return ui.kpi_html(etiqueta, "No disponible", nota=f"Revisa la hoja de origen: {error}")


def _fila_kpis(v, inv, fin, prod):
    tarjetas = []

    if v:
        mes = MESES[v["inicio"].month - 1]
        tarjetas.append(ui.kpi_html(
            f"Venta neta · {mes}", num(v["venta_neta"]), "unid.",
            progreso=(v["eficiencia"], f"{v['eficiencia']:,.0f}% del forecast", f"Meta {num(v['forecast'])}")))
    else:
        tarjetas.append(_no_disponible("Venta neta", "VTS DASHBOARD"))

    if inv:
        p = inv["df_plot"]
        mes_fin = MESES_CORTOS.get(str(p["Mes"].iloc[-1]).split()[0].upper(), p["Mes"].iloc[-1])
        mes_ini = str(p["Mes"].iloc[0]).split()[0].capitalize()
        tarjetas.append(ui.kpi_html(
            f"Inventario valorizado · Cierre {mes_fin}", usd(inv["v_fin"], simbolo=""), "USD",
            delta=(f"{pct(inv['var_total'])} vs. {mes_ini.lower()}", inv["var_total"] >= 0),
            spark=list(p["Valor_Total"])))
    else:
        tarjetas.append(_no_disponible("Inventario valorizado", "hojas CIERRE"))

    if fin:
        tarjetas.append(ui.kpi_html(
            "Capital de activos inventario", usd(fin["capital_inmovilizado"], simbolo=""), "USD",
            extra=(num(fin["dio_global"], 1), "días de cobertura global")))
    else:
        tarjetas.append(_no_disponible("Capital de activos inventario", "FIN KPIs Inventario"))

    if prod is not None and len(prod) >= 1:
        ultimo = prod.iloc[-1]
        mes = MESES[ultimo["Fecha"].month - 1]
        delta = None
        if len(prod) >= 2 and prod.iloc[-2]["Real"]:
            var = (ultimo["Real"] - prod.iloc[-2]["Real"]) / prod.iloc[-2]["Real"] * 100
            delta = (f"{pct(var)} vs. {MESES[prod.iloc[-2]['Fecha'].month - 1].lower()}", var >= 0)
        tarjetas.append(ui.kpi_html(
            f"Producción · {mes}", num(ultimo["Real"]), "unid.", delta=delta,
            nota=f"Promedio mensual {num(prod['Real'].mean())} unid."))
    else:
        tarjetas.append(_no_disponible("Producción", "Produccion Total Mensual"))

    ui.kpis(tarjetas)


def _seccion_cedis(cedis, err):
    with ui.tarjeta("res_cedis", "Venta bruta por CEDI", "Unidades · % del total · avance de proyección"):
        if err:
            st.warning(f"No se pudo leer la venta por CEDI: {err}")
            return None
        resumen, total_nacional = cedis
        r = resumen.sort_values("Venta_Bruta", ascending=False)
        base = total_nacional or r["Venta_Bruta"].sum()
        ui.barras([(f["CEDI"].title(), f["Venta_Bruta"],
                    [pct(f["Venta_Bruta"] / base * 100) if base else "–", pct(f["Avance_%"])])
                   for _, f in r.iterrows()], columnas_extra=(56, 56))
        suma = r["Venta_Bruta"].sum()
        pares = [("Suma CEDIs", num(suma), False)]
        diferencia = None
        if total_nacional is not None:
            diferencia = total_nacional - suma
            pares += [("Total nacional", num(total_nacional), False),
                      ("Diferencia de cuadre", f"{num(diferencia)} unid.", abs(diferencia) > 0)]
        ui.linea_resumen(pares)
        return diferencia


def _seccion_alertas(paginas, v, desv, multi, diferencia, dias_restantes):
    with ui.tarjeta("res_alertas", "Puntos de atención"):
        hubo = False

        if desv:
            hubo = True
            texto = f"Comparado con {desv['MES_ANT'].lower()}."
            if desv["tiene_precio"]:
                impacto = desv["df"]["Impacto Mensual $"].sum()
                texto += f" Balance financiero proyectado: {'+' if impacto >= 0 else ''}{usd(impacto)} / mes."
            ui.alerta("arrow_down", "neg", f"{desv['bajo']} de {desv['total_skus']} SKUs bajaron su venta diaria", texto)
            st.page_link(paginas["desviaciones"], label="Ver desviaciones", icon=":material/arrow_forward:")

        if v and v["diferencia"] < 0:
            hubo = True
            ui.alerta("trend", "aviso", f"Faltan {num(abs(v['diferencia']))} unid. para el forecast",
                      f"Venta bruta {num(v['venta_bruta'])} de {num(v['forecast'])} ({v['eficiencia']:,.0f}%). "
                      f"Quedan {dias_restantes} días de venta.")
            st.page_link(paginas["ventas"], label="Ver ventas", icon=":material/arrow_forward:")

        if multi and multi["val_total"]:
            cedis = {"Caracas": multi["val_ccs"], "Carabobo": multi["val_car"], "Oriente": multi["val_ori"],
                     "Lara": multi["val_lar"], "Zulia": multi["val_zul"]}
            cedis = {k: x for k, x in cedis.items() if pd.notna(x)}
            if cedis:
                hubo = True
                mayor = max(cedis, key=cedis.get)
                ui.alerta("building", "info",
                          f"{mayor} concentra el {pct(cedis[mayor] / multi['val_total'] * 100, 0)} del inventario en CEDIs",
                          f"{usd(cedis[mayor])} de {usd(multi['val_total'])}.")
                st.page_link(paginas["multicentro"], label="Ver multicentro", icon=":material/arrow_forward:")

        if diferencia:
            hubo = True
            ui.alerta("alert", "aviso", f"{num(abs(diferencia))} unid. sin asignar a un CEDI",
                      "La suma por CEDI no cuadra con el total nacional.")
            st.page_link(paginas["cedis"], label="Ver CEDIs", icon=":material/arrow_forward:")

        if not hubo:
            ui.alerta("check", "pos", "Sin alertas", "No hay puntos de atención con los datos actuales.")


def _grafico_inventario(inv):
    dfc = inv["consolidado"].copy()
    dfc["Valor $"] = pd.to_numeric(dfc["Valor $"], errors="coerce")
    meses = list(inv["meses"])
    etiquetas = [MESES_CORTOS.get(str(m).split()[0].upper(), m) for m in meses]
    fig = go.Figure()
    for cat, color in (("MATERIA PRIMA", ui.NAVY), ("MATERIAL EMPAQUE", ui.LIGHTBLUE), ("PRODUCTO TERMINADO", ui.ORANGE)):
        serie = dfc[dfc["Categoría"] == cat].set_index("Mes")["Valor $"].reindex(meses)
        fig.add_bar(x=etiquetas, y=serie.values, name=cat.capitalize(), marker_color=color,
                    hovertemplate="%{x} · " + cat.capitalize() + "<br>USD %{y:,.2f}<extra></extra>")
    fig.update_layout(barmode="stack", bargap=0.45)
    ui.estilo_grafico(fig, alto=300)
    ui.ejes_miles(fig)
    ui.grafico(fig, clave="res_inv")


def _grafico_produccion(prod):
    etiquetas = [MESES[f.month - 1][:3] for f in prod["Fecha"]]
    promedio = prod["Real"].mean()
    fig = go.Figure()
    fig.add_scatter(x=etiquetas, y=prod["Real"], mode="lines+markers", name="Producción",
                    line=dict(color=ui.NAVY, width=2.5),
                    marker=dict(size=[7] * (len(prod) - 1) + [11], color=["#ffffff"] * (len(prod) - 1) + [ui.ORANGE],
                                line=dict(width=2, color=[ui.NAVY] * (len(prod) - 1) + [ui.ORANGE])),
                    hovertemplate="%{x}<br>%{y:,.0f} unid.<extra></extra>")
    fig.add_hline(y=promedio, line_dash="dash", line_color=ui.MUTED, line_width=1.2,
                  annotation_text=f"Promedio {num(promedio)}", annotation_position="top right",
                  annotation_font=dict(color=ui.MUTED, size=11))
    ui.estilo_grafico(fig, alto=300)
    ui.ejes_miles(fig, desde_cero=False)
    ui.grafico(fig, clave="res_prod")


# ══════════════════════════════════════════════════════════
# PÁGINA
# ══════════════════════════════════════════════════════════
def renderizar(paginas, dias_efectivos, dias_restantes):
    if not datos.existe():
        ui.encabezado("Inicio", "Resumen ejecutivo")
        datos.mostrar_error_archivo()
        return

    v, _ = _seguro(m1.calcular)
    inv, _ = _seguro(_inventario)
    fin, _ = _seguro(_finanzas)
    prod, _ = _seguro(_produccion)
    cedis, err_cedis = _seguro(_cedis)
    desv, _ = _seguro(_desviaciones)
    multi, _ = _seguro(_multicentro)

    periodo = f"Período {v['inicio_str']} – {v['final_str']} · " if v else ""
    ui.encabezado("Inicio", "Resumen ejecutivo", f"{periodo}Cifras en unidades y USD")

    _fila_kpis(v, inv, fin, prod)

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        diferencia = _seccion_cedis(cedis, err_cedis)
    with c2:
        _seccion_alertas(paginas, v, desv, multi, diferencia, dias_restantes)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        with ui.tarjeta("res_inv", "Valor de inventario por cierre", "USD"):
            if inv:
                ui.leyenda([("Materia prima", ui.NAVY), ("Material de empaque", ui.LIGHTBLUE), ("Producto terminado", ui.ORANGE)])
                _grafico_inventario(inv)
            else:
                st.warning("No se pudo leer el histórico de cierres.")
    with c4:
        with ui.tarjeta("res_prod", "Producción total mensual", "Unidades"):
            if prod is not None:
                ui.leyenda([("Producción", ui.NAVY), ("Último mes", ui.ORANGE)])
                _grafico_produccion(prod)
            else:
                st.warning("No se pudo leer la producción mensual.")

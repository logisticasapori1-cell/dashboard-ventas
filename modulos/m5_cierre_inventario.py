import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from utils import datos, ui
from utils.formato import usd, pct

def _cargar_cierre_inventario(path=None):
    """Lee las hojas 'CIERRE <MES> <AÑO>' y retorna (meses, dict de DataFrames), sin el prefijo."""
    return datos.leer_grupo(datos.PREFIJO_CIERRE, quitar_prefijo=True)


def tendencia_total(df_consolidado, sheet_names):
    """Serie del valor total (MP+ME+PT) desde abril. Retorna (dict, aviso)."""
    # Ubicar la hoja de abril (se toma la más reciente si hubiera varias)
    indices_abril = [
        i for i, s in enumerate(sheet_names)
        if "ABR" in str(s).upper() or "APR" in str(s).upper()
    ]
    if not indices_abril:
        return None, "No se encontró una hoja de Abril en el archivo; no es posible construir la tendencia."

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
        return None, "No hay valores registrados desde Abril."

    # KPI: variación entre el primer y el último mes del rango
    v_ini, v_fin = df_plot["Valor_Total"].iloc[0], df_plot["Valor_Total"].iloc[-1]
    var_total = ((v_fin - v_ini) / v_ini * 100) if v_ini else 0
    return {"resumen": resumen, "df_plot": df_plot, "v_ini": v_ini, "v_fin": v_fin, "var_total": var_total}, None



CATEGORIAS = ["MATERIA PRIMA", "MATERIAL EMPAQUE", "PRODUCTO TERMINADO"]
COLORES = {"MATERIA PRIMA": ui.NAVY, "MATERIAL EMPAQUE": ui.LIGHTBLUE, "PRODUCTO TERMINADO": ui.ORANGE}
MESES_CORTOS = {m: m[:3].capitalize() for m in ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
                                               "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]}


def etiqueta_mes(mes):
    """'OCTUBRE 2026' -> 'Oct-2026'."""
    partes = str(mes).split()
    corto = MESES_CORTOS.get(partes[0].upper(), partes[0].capitalize()) if partes else str(mes)
    return f"{corto}-{partes[1]}" if len(partes) > 1 else corto


def _usd(x):
    return usd(x) if pd.notna(x) else "No registrado"


def _excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cierres")
    return buffer.getvalue()


# ══════════════════════════════════════════════════════════
# 1. TENDENCIA DEL VALOR TOTAL (no depende de los filtros)
# ══════════════════════════════════════════════════════════
def _renderizar_tendencia_total(df_consolidado, sheet_names, formato_dinero=None):
    ui.seccion("Tendencia del valor total", "Materia prima + material de empaque + producto terminado, desde abril · No depende de los filtros")

    _t, _aviso = tendencia_total(df_consolidado, sheet_names)
    if _aviso:
        st.info(_aviso)
        return
    df_plot, v_ini, v_fin, var_total = _t["df_plot"], _t["v_ini"], _t["v_fin"], _t["var_total"]

    ui.kpis([
        ui.kpi_html(f"Valor {etiqueta_mes(df_plot['Mes'].iloc[0])}", usd(v_ini, simbolo=""), "USD"),
        ui.kpi_html(f"Valor {etiqueta_mes(df_plot['Mes'].iloc[-1])}", usd(v_fin, simbolo=""), "USD",
                    spark=list(df_plot["Valor_Total"])),
        ui.kpi_html("Variación en el período", pct(var_total, signo=True),
                    delta=(f"{etiqueta_mes(df_plot['Mes'].iloc[0])} → {etiqueta_mes(df_plot['Mes'].iloc[-1])}", var_total >= 0)),
    ], minimo=240)

    def _hover(fila):
        texto = f"<b>{etiqueta_mes(fila['Mes'])}</b><br>Valor total: {usd(fila['Valor_Total'])}"
        if pd.notna(fila["Var_%"]):
            texto += f"<br>Var. vs mes anterior: {pct(fila['Var_%'], signo=True)}"
        if fila["Categorias"] < 3:
            texto += f"<br>Incompleto: {fila['Categorias']}/3 categorías registradas"
        return texto

    incompletos = df_plot["Categorias"] < 3
    with ui.tarjeta("cierre_total", "Valor total del inventario por cierre", "USD"):
        leyenda = [("Valor total", ui.NAVY)]
        if incompletos.any():
            leyenda.append(("Mes con alguna categoría sin registrar (total subestimado)", ui.ORANGE))
        ui.leyenda(leyenda)
        fig = go.Figure(go.Scatter(
            x=[etiqueta_mes(m) for m in df_plot["Mes"]], y=df_plot["Valor_Total"], mode="lines+markers+text",
            line=dict(color=ui.NAVY, width=2.5),
            marker=dict(size=10, color=[ui.ORANGE if inc else ui.NAVY for inc in incompletos]),
            text=[usd(v, dec=0) for v in df_plot["Valor_Total"]], textposition=ui.posiciones_etiquetas(df_plot["Valor_Total"]),
            textfont=dict(size=11, color=ui.INK), cliponaxis=False,
            customdata=df_plot.apply(_hover, axis=1), hovertemplate="%{customdata}<extra></extra>"))
        ui.estilo_grafico(fig, alto=360)
        ui.ejes_miles(fig, desde_cero=False)
        ui.grafico(fig, clave="cierre_total")


def consolidar(sheet_names, hojas_dict):
    """Une las hojas de cierre en una tabla larga (Mes, Categoría, Valor $)."""
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
    return df_consolidado


# ══════════════════════════════════════════════════════════
# PÁGINA
# ══════════════════════════════════════════════════════════
def renderizar():
    ui.encabezado("Supply › Cierre de inventario", "Cierre de inventario valorizado",
                  "Materia prima, material de empaque y producto terminado al cierre de cada mes · Cifras en USD")

    if not datos.existe():
        datos.mostrar_error_archivo()
        return

    try:
        sheet_names, hojas_dict = _cargar_cierre_inventario()
        df_consolidado = consolidar(sheet_names, hojas_dict)

        _renderizar_tendencia_total(df_consolidado, sheet_names)

        # ══ 2. CONSULTA POR MES Y CATEGORÍA ══
        ui.seccion("Consulta por mes y categoría")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_mes = st.selectbox("Mes", ["Todos los meses"] + list(sheet_names), key="cierre_mes",
                                      format_func=lambda m: m if m == "Todos los meses" else etiqueta_mes(m))
        with col_f2:
            filtro_categoria = st.selectbox("Categoría", ["Todas las Categorías"] + CATEGORIAS, key="cierre_categoria",
                                            format_func=lambda c: "Todas las categorías" if c == "Todas las Categorías" else c.capitalize())

        df_filtrado = df_consolidado.copy()
        if filtro_mes != "Todos los meses":
            df_filtrado = df_filtrado[df_filtrado["Mes"] == filtro_mes]
        if filtro_categoria != "Todas las Categorías":
            df_filtrado = df_filtrado[df_filtrado["Categoría"] == filtro_categoria]

        valor_total = df_filtrado["Valor $"].sum(skipna=True)
        n_meses = df_filtrado["Mes"].nunique()
        etiqueta_total = (f"Cierre {etiqueta_mes(filtro_mes)}" if filtro_mes != "Todos los meses"
                          else f"Suma de {n_meses} cierres mensuales")
        tarjetas = [ui.kpi_html(etiqueta_total, usd(valor_total, simbolo=""), "USD",
                                nota=None if filtro_mes != "Todos los meses" else "Suma de saldos de cierre; no es el inventario de un mes")]
        if filtro_categoria == "Todas las Categorías":
            for cat in CATEGORIAS:
                tarjetas.append(ui.kpi_html(cat.capitalize(), usd(df_filtrado[df_filtrado["Categoría"] == cat]["Valor $"].sum(skipna=True), simbolo=""), "USD"))
        else:
            promedio = df_filtrado["Valor $"].mean(skipna=True)
            tarjetas.append(ui.kpi_html("Promedio en el período", usd(promedio if pd.notna(promedio) else 0, simbolo=""), "USD"))
        ui.kpis(tarjetas, minimo=220)

        if filtro_mes == "Todos los meses":
            categorias_a_graficar = [filtro_categoria] if filtro_categoria != "Todas las Categorías" else CATEGORIAS
            with ui.tarjeta("cierre_categorias", "Cierre valorizado por categoría", "USD por mes"):
                ui.leyenda([(c.capitalize(), COLORES[c]) for c in categorias_a_graficar])
                fig = go.Figure()
                for cat in categorias_a_graficar:
                    df_cat_plot = df_filtrado[df_filtrado["Categoría"] == cat].dropna(subset=["Valor $"])
                    if not df_cat_plot.empty:
                        fig.add_scatter(x=[etiqueta_mes(m) for m in df_cat_plot["Mes"]], y=df_cat_plot["Valor $"],
                                        mode="lines+markers", name=cat.capitalize(),
                                        line=dict(color=COLORES[cat], width=2.5), marker=dict(size=8, color=COLORES[cat]),
                                        hovertemplate="%{x} · " + cat.capitalize() + "<br>USD %{y:,.2f}<extra></extra>")
                fig.update_layout(hovermode="x unified")
                ui.estilo_grafico(fig, alto=380)
                ui.ejes_miles(fig)
                ui.grafico(fig, clave="cierre_categorias")

        with ui.tarjeta("cierre_tabla", "Desglose de registros", "USD"):
            if filtro_categoria == "Todas las Categorías":
                tabla_mostrar = df_filtrado.pivot(index='Mes', columns='Categoría', values='Valor $').reset_index()
                tabla_mostrar['Mes'] = pd.Categorical(tabla_mostrar['Mes'], categories=sheet_names, ordered=True)
                tabla_mostrar = tabla_mostrar.sort_values('Mes')
            else:
                tabla_mostrar = df_filtrado.dropna(subset=["Valor $"])
            columnas_numericas = list(tabla_mostrar.select_dtypes(include=['float64', 'int64']).columns)
            # Streamlit muestra 'None' en celdas vacías: la tabla visible se entrega ya formateada
            vista = tabla_mostrar.copy()
            vista["Mes"] = [etiqueta_mes(m) for m in vista["Mes"]]
            for c in columnas_numericas:
                vista[c] = [_usd(v) for v in vista[c]]
            vista = vista.rename(columns={c: c.capitalize() for c in columnas_numericas if c in CATEGORIAS})
            st.dataframe(vista, width="stretch", hide_index=True, column_config={
                c: st.column_config.TextColumn(alignment="right") for c in vista.columns if c not in ("Mes", "Categoría")})
            st.download_button("Descargar Excel", data=_excel(tabla_mostrar.astype({"Mes": str}) if "Mes" in tabla_mostrar else tabla_mostrar),
                               file_name="Cierre_Inventario.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               icon=":material/download:", key="cierre_descarga")

    except Exception as e:
        st.error(f"Error procesando el histórico de inventarios: {e}")

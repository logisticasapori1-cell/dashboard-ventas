import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io
from utils import datos, ui
from utils.formato import num, usd, pct

PREFIJO_COL_MES = "PROMD VTA DIA"

def _cargar_desviaciones(path=None):
    return datos.leer_hoja(datos.HOJA_DESVIACIONES)

def preparar(df):
    """Prepara la tabla de desviaciones: columnas de mes, impacto, ABC y conteos. También lo usa el Resumen ejecutivo."""
    if 'CATEGORÍA' not in df.columns:
        df['CATEGORÍA'] = "Por Asignar"

    # Columnas de mes detectadas por nombre: 'PROMD VTA DIA <MES>'.
    # La primera es el mes anterior y la segunda el mes actual (orden del Excel).
    cols_mes = [c for c in df.columns if str(c).strip().upper().startswith(PREFIJO_COL_MES)]
    if len(cols_mes) != 2:
        raise ValueError(
            f"Se esperaban 2 columnas que empiecen por '{PREFIJO_COL_MES}' en la hoja "
            f"'{datos.HOJA_DESVIACIONES}' y se encontraron {len(cols_mes)}: {cols_mes}"
        )
    COL_ANT, COL_ACT = cols_mes
    MES_ANT = str(COL_ANT).strip()[len(PREFIJO_COL_MES):].strip().capitalize()
    MES_ACT = str(COL_ACT).strip()[len(PREFIJO_COL_MES):].strip().capitalize()

    for col in [COL_ANT, COL_ACT]:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        if col in df.columns:
            df[col] = df[col].round(0).astype(int)

    if 'Porcentaje de desviación' in df.columns:
        df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
    else:
        df['Desviacion_Num'] = ((df[COL_ACT] - df[COL_ANT]) / df[COL_ANT]) * 100

    tiene_precio = 'PRECIO UNITARIO' in df.columns
    if tiene_precio:
        df['Dif_Unidades_Diarias'] = df[COL_ACT] - df[COL_ANT]
        df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
        df['Impacto Mensual $'] = df['Impacto_Diario_$'] * 30

    df = df.sort_values(by=COL_ANT, ascending=False).reset_index(drop=True)
    volumen_total_ant = df[COL_ANT].sum()
    df['Porcentaje_Participacion'] = (df[COL_ANT] / volumen_total_ant) * 100 if volumen_total_ant > 0 else 0
    df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()

    def asignar_abc(acumulado):
        if acumulado <= 80: return 'A'
        elif acumulado <= 95: return 'B'
        return 'C'

    df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

    total_skus = len(df)
    subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
    bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
    return {"df": df, "COL_ANT": COL_ANT, "COL_ACT": COL_ACT, "MES_ANT": MES_ANT, "MES_ACT": MES_ACT, "tiene_precio": tiene_precio, "total_skus": total_skus, "subio": subio, "bajo": bajo}




def resaltar_tendencia(val):
    if val == 'SUBIÓ':
        return f"background-color:{ui.VERDE_BG};color:{ui.VERDE_TX};font-weight:600;"
    if val == 'BAJO':
        return f"background-color:{ui.ROJO_BG};color:{ui.ROJO_TX};font-weight:600;"
    return ''


def filtrar(df, tendencia="Todos", abc="Todos", categoria="Todos", busqueda=""):
    """Mismos filtros de siempre, sin dibujar nada."""
    out = df.copy()
    if tendencia != "Todos" and 'Estado de tendencia' in out.columns:
        out = out[out['Estado de tendencia'] == tendencia]
    if abc != "Todos":
        out = out[out['Clasificación ABC'] == abc]
    if categoria != "Todos":
        out = out[out['CATEGORÍA'] == categoria]
    if busqueda:
        out = out[out['PRODUCTO'].str.contains(busqueda, case=False, na=False) |
                  out['REFERENCIA INTERNA'].astype(str).str.contains(busqueda, na=False)]
    return out


def _grafico_comparativo(df_grafico, COL_ANT, COL_ACT, MES_ANT, MES_ACT):
    fig = go.Figure()
    fig.add_bar(x=df_grafico['PRODUCTO'], y=df_grafico[COL_ANT], name=MES_ANT, marker_color=ui.NAVY,
                hovertemplate="%{x}<br>" + MES_ANT + ": %{y:,.0f} unid./día<extra></extra>")
    fig.add_bar(x=df_grafico['PRODUCTO'], y=df_grafico[COL_ACT], name=MES_ACT, marker_color=ui.ORANGE,
                hovertemplate="%{x}<br>" + MES_ACT + ": %{y:,.0f} unid./día<extra></extra>")
    fig.update_layout(barmode='group', bargap=0.25, bargroupgap=0.05, hovermode="x unified")
    ui.estilo_grafico(fig, alto=460)
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=10))
    fig.update_yaxes(tickformat=",.0f")
    ui.grafico(fig, clave="desv_comparativo")


def _grafico_impacto(df_filtrado):
    d = df_filtrado.dropna(subset=['Impacto Mensual $'])
    if d.empty:
        return
    negativos = d.nsmallest(8, 'Impacto Mensual $')
    negativos = negativos[negativos['Impacto Mensual $'] < 0]
    positivos = d.nlargest(8, 'Impacto Mensual $')
    positivos = positivos[positivos['Impacto Mensual $'] > 0]
    top = pd.concat([negativos, positivos]).drop_duplicates().sort_values('Impacto Mensual $')
    if top.empty:
        return
    colores = [ui.ORANGE if v < 0 else ui.NAVY for v in top['Impacto Mensual $']]
    fig = go.Figure(go.Bar(
        x=top['Impacto Mensual $'], y=top['PRODUCTO'], orientation="h", marker_color=colores,
        text=[usd(v) for v in top['Impacto Mensual $']], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>%{text} / mes<extra></extra>"))
    ui.estilo_grafico(fig, alto=max(300, len(top) * 30))
    rango = top['Impacto Mensual $'].abs().max() * 1.45
    fig.update_xaxes(range=[-rango if (top['Impacto Mensual $'] < 0).any() else 0, rango if (top['Impacto Mensual $'] > 0).any() else 0],
                     zeroline=True, zerolinecolor=ui.MUTED, showgrid=True, gridcolor=ui.BORDER, tickformat=",.0f")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11, color=ui.INK))
    ui.grafico(fig, clave="desv_impacto")


def renderizar():
    if not datos.existe():
        ui.encabezado("Supply › Desviaciones", "Desviaciones")
        datos.mostrar_error_archivo()
        return

    try:
        _r = preparar(_cargar_desviaciones())
    except Exception as e:
        ui.encabezado("Supply › Desviaciones", "Desviaciones")
        st.error(f"No se pudo leer la hoja de desviaciones: {e}")
        return

    df = _r["df"]
    COL_ANT, COL_ACT, MES_ANT, MES_ACT = _r["COL_ANT"], _r["COL_ACT"], _r["MES_ANT"], _r["MES_ACT"]
    tiene_precio, total_skus, subio, bajo = _r["tiene_precio"], _r["total_skus"], _r["subio"], _r["bajo"]

    ui.encabezado("Supply › Desviaciones", "Desviaciones",
                  f"Venta diaria promedio por SKU: {MES_ACT} vs. {MES_ANT} · Pareto ABC e impacto financiero (USD)")

    # ── KPIs ─────────────────────────────────────────
    tarjetas = [
        ui.kpi_html("SKUs en planta", str(total_skus), "prod."),
        ui.kpi_html("SKUs en alza", str(subio), "SKU", delta=(f"{pct(subio / total_skus * 100, 0)} del total", True) if total_skus else None),
        ui.kpi_html("SKUs en alerta", str(bajo), "SKU", delta=(f"{pct(bajo / total_skus * 100, 0)} del total", False) if total_skus else None),
    ]
    if tiene_precio:
        impacto_total = df['Impacto Mensual $'].sum()
        tarjetas.append(ui.kpi_html("Balance financiero proyectado", ("+" if impacto_total >= 0 else "") + usd(impacto_total, simbolo=""),
                                    "USD", delta=(f"Por mes vs. {MES_ANT.lower()}", impacto_total >= 0)))
    else:
        tarjetas.append(ui.kpi_html("Balance financiero proyectado", "Falta precio unitario",
                                    nota="Agrega la columna PRECIO UNITARIO en la hoja"))
    ui.kpis(tarjetas, minimo=220)

    # ── Filtros ──────────────────────────────────────
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filtro_tendencia = st.selectbox("Estado de tendencia", ["Todos", "SUBIÓ", "BAJO"], key="desv_tendencia")
    with col_f2:
        filtro_abc = st.selectbox("Clasificación ABC", ["Todos", "A", "B", "C"], key="desv_abc")
    with col_f3:
        lista_categorias = ["Todos"] + sorted(df['CATEGORÍA'].dropna().unique().tolist())
        filtro_categoria = st.selectbox("Categoría / marca", lista_categorias, key="desv_categoria")
    with col_f4:
        busqueda = st.text_input("Buscar", placeholder="Producto o referencia", key="desv_busqueda", icon=":material/search:")

    df_filtrado = filtrar(df, filtro_tendencia, filtro_abc, filtro_categoria, busqueda)

    # ── Gráficos ─────────────────────────────────────
    df_grafico = df_filtrado.sort_values(by=COL_ACT, ascending=False)
    with ui.tarjeta("desv_comparativo", f"Venta diaria promedio por SKU · {MES_ANT} vs. {MES_ACT}",
                    f"Unidades por día · {len(df_filtrado)} de {total_skus} SKU"):
        if df_grafico.empty:
            st.info("No hay SKUs con los filtros seleccionados.")
        else:
            ui.leyenda([(MES_ANT, ui.NAVY), (MES_ACT, ui.ORANGE)])
            _grafico_comparativo(df_grafico, COL_ANT, COL_ACT, MES_ANT, MES_ACT)

    if tiene_precio and not df_filtrado.empty:
        with ui.tarjeta("desv_impacto", "Mayor impacto financiero", "USD por mes · hasta 8 SKU que más suman y 8 que más restan"):
            ui.leyenda([("Suma al balance", ui.NAVY), ("Resta al balance", ui.ORANGE)])
            _grafico_impacto(df_filtrado)

    # ── Tabla ────────────────────────────────────────
    if tiene_precio:
        columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', COL_ANT, COL_ACT, 'Porcentaje de desviación', 'Impacto Mensual $', 'Estado de tendencia']
    else:
        columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', COL_ANT, COL_ACT, 'Porcentaje de desviación', 'Estado de tendencia']

    with ui.tarjeta("desv_tabla", "Detalle de desviaciones", f"{len(df_filtrado)} SKU"):
        conteo = df['Clasificación ABC'].value_counts()
        ui.linea_resumen([(f"Clase {c}", f"{int(conteo.get(c, 0))} SKU", False) for c in ("A", "B", "C")]
                         + [("Criterio", "A ≤ 80% · B ≤ 95% del volumen acumulado", False)])
        formato_columnas = {COL_ANT: num, COL_ACT: num, 'Porcentaje de desviación': lambda x: pct(x * 100, 2)}
        if tiene_precio:
            formato_columnas['Impacto Mensual $'] = usd
        tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia']).format(formato_columnas)
        cc = st.column_config
        st.dataframe(tabla_estilizada, width="stretch", hide_index=True, column_config={
            "REFERENCIA INTERNA": cc.Column("Ref.", width=72), "PRODUCTO": cc.Column("Producto", width="medium"),
            "CATEGORÍA": cc.Column("Categoría"), "Clasificación ABC": cc.Column("ABC", width=56),
            COL_ANT: cc.Column(f"Prom. diario {MES_ANT[:3]}."), COL_ACT: cc.Column(f"Prom. diario {MES_ACT[:3]}."),
            "Porcentaje de desviación": cc.Column("Desviación"), "Impacto Mensual $": cc.Column("Impacto mensual"),
            "Estado de tendencia": cc.Column("Tendencia")})

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
        st.download_button("Descargar reporte para firmas", data=buffer.getvalue(), file_name="Reporte_Desviaciones.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary",
                           icon=":material/download:", key="desv_descarga")

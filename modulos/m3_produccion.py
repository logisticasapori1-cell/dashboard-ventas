import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import re
from utils import datos, ui
from utils.formato import num, pct

def _cargar_hojas_produccion(path=None):
    """Retorna (nombres, {nombre_hoja: DataFrame}) de las hojas de producción."""
    return datos.leer_grupo(datos.PREFIJO_PRODUCCION)

def serie_produccion(df):
    """Convierte una hoja de producción en la serie mensual (Fecha, Real). Retorna (df, aviso)."""
    meses_patrones = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    pairs = []

    def es_celda_fecha(val):
        if hasattr(val, 'strftime'): return True
        val_str = str(val).lower().strip()
        return any(m in val_str for m in meses_patrones)

    conteo_cols = sum(1 for col in df.columns if es_celda_fecha(col))
    if conteo_cols >= 2:
        for idx, row in df.iterrows():
            fila_pairs = []
            for i, col in enumerate(df.columns):
                if es_celda_fecha(col):
                    val_num = pd.to_numeric(row.iloc[i], errors='coerce')
                    if pd.notna(val_num) and val_num > 0: fila_pairs.append((col, val_num))
            if len(fila_pairs) >= 2:
                pairs = fila_pairs
                break

    if len(pairs) == 0:
        for idx, row in df.iterrows():
            conteo_fila = sum(1 for val in row if es_celda_fecha(val))
            if conteo_fila >= 2:
                if idx + 1 < len(df):
                    fila_valores = df.iloc[idx + 1]
                    for i in range(len(row)):
                        f_val = row.iloc[i]
                        if es_celda_fecha(f_val):
                            val_num = pd.to_numeric(fila_valores.iloc[i], errors='coerce')
                            if pd.notna(val_num) and val_num > 0: pairs.append((f_val, val_num))
                break

    if len(pairs) == 0:
        return None, "⚠️ No se detectó la secuencia horizontal de meses o valores en esta hoja. Verifica la estructura."

    meses_espanol = {'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'}
    clean_data = []

    for f_val, val in pairs:
        if hasattr(f_val, 'strftime'):
            dt = pd.to_datetime(f_val)
            if pd.notna(dt): clean_data.append({'Fecha': dt, 'Real': val})
        else:
            m_str = str(f_val).lower().strip()
            for m_letra, m_num in meses_espanol.items():
                if m_letra in m_str:
                    year_match = re.search(r'(\d{2,4})$', m_str)
                    if year_match:
                        year_part = year_match.group(1)
                        m_str_numeric = f"{m_num}-{year_part}"
                        fmt = '%m-%y' if len(year_part) == 2 else '%m-%Y'
                        dt = pd.to_datetime(m_str_numeric, format=fmt, errors='coerce')
                        if pd.notna(dt): clean_data.append({'Fecha': dt, 'Real': val})
                    break

    df_final = pd.DataFrame(clean_data)
    if df_final.empty:
        return None, "⚠️ Las celdas de fecha detectadas no pudieron ser procesadas correctamente."

    df_final = df_final.sort_values(by='Fecha').reset_index(drop=True)
    return df_final, None


MESES_DISPLAY = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
PREFIJO = "Produccion Total"


def nombre_categoria(hoja):
    """'Produccion Total Cremigurt 150g' -> 'Cremigurt 150g'; la hoja mensual general -> 'Todas las líneas'."""
    resto = str(hoja)[len(PREFIJO):].strip() if str(hoja).startswith(PREFIJO) else str(hoja)
    return "Todas las líneas" if resto.lower() in ("", "mensual") else resto


def _excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Producción")
    return buffer.getvalue()


def _posiciones(vals):
    """Etiqueta debajo de los valles y arriba del resto, para que no la tape la línea."""
    pos = []
    for i, v in enumerate(vals):
        izq = vals[i - 1] if i > 0 else None
        der = vals[i + 1] if i < len(vals) - 1 else None
        valle = (izq is None or v < izq) and (der is None or v < der) and (izq is not None or der is not None)
        pos.append("bottom center" if valle else "top center")
    return pos


def _grafico(df_final):
    promedio = df_final["Real"].mean()
    n = len(df_final)
    pico = df_final["Real"].idxmax()
    colores = [ui.ORANGE if i == df_final.index[-1] else ui.NAVY for i in df_final.index]
    fig = go.Figure(go.Scatter(
        x=df_final["Mes_Filtro"], y=df_final["Real"], mode="lines+markers+text" if n > 1 else "markers+text",
        line=dict(color=ui.NAVY, width=2.5),
        marker=dict(size=[12 if i == pico else 8 for i in df_final.index], color=["#ffffff" if c == ui.NAVY else c for c in colores],
                    line=dict(width=2, color=colores)),
        text=[num(v) for v in df_final["Real"]], textposition=_posiciones(list(df_final["Real"])), textfont=dict(size=11, color=ui.INK),
        cliponaxis=False, hovertemplate="%{x}<br>%{text} unid.<extra></extra>"))
    if n > 1:
        fig.add_hline(y=promedio, line_dash="dash", line_color=ui.MUTED, line_width=1.2,
                      annotation_text=f"Promedio {num(promedio)}", annotation_position="bottom right",
                      annotation_font=dict(color=ui.MUTED, size=11))
    ui.estilo_grafico(fig, alto=400)
    ui.ejes_miles(fig, desde_cero=False)
    ui.grafico(fig, clave="prod_tendencia")


def renderizar():
    ui.encabezado("Operaciones › Producción", "Producción",
                  "Volumen producido por línea y mes · Cifras en unidades")

    if not datos.existe():
        datos.mostrar_error_archivo()
        return

    try:
        nombres_hojas, hojas_dict = _cargar_hojas_produccion()

        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            categoria_seleccionada = st.selectbox("Línea de producción", options=nombres_hojas, index=0,
                                                  format_func=nombre_categoria, key="prod_categoria")
        nombre = nombre_categoria(categoria_seleccionada)

        df_final, _aviso = serie_produccion(hojas_dict[categoria_seleccionada])
        if _aviso:
            st.warning(_aviso)
            return
        df_final['Mes_Filtro'] = df_final['Fecha'].dt.month.map(MESES_DISPLAY) + "-" + df_final['Fecha'].dt.strftime('%Y')
        df_final["Var_%"] = df_final["Real"].pct_change() * 100

        meses_disponibles = ["Todos los meses"] + df_final['Mes_Filtro'].unique().tolist()
        with col_filtro2:
            mes_seleccionado = st.selectbox("Mes", options=meses_disponibles, key="prod_mes")

        if mes_seleccionado != "Todos los meses":
            df_final = df_final[df_final['Mes_Filtro'] == mes_seleccionado]
        if df_final.empty:
            st.info("No hay registros para mostrar con el filtro seleccionado.")
            return

        total_prod = df_final['Real'].sum()
        promedio_prod = df_final['Real'].mean()
        max_row = df_final.loc[df_final['Real'].idxmax()]
        ultimo = df_final.iloc[-1]

        tarjetas = [
            ui.kpi_html(f"Total producido · {nombre}", num(total_prod), "unid.",
                        nota=f"{len(df_final)} {'mes' if len(df_final) == 1 else 'meses'} · {df_final['Mes_Filtro'].iloc[0]}"
                             + (f" a {ultimo['Mes_Filtro']}" if len(df_final) > 1 else "")),
            ui.kpi_html("Promedio mensual", num(promedio_prod), "unid."),
            ui.kpi_html("Pico más alto", num(max_row['Real']), "unid.", nota=f"Mes: {max_row['Mes_Filtro']}"),
        ]
        if pd.notna(ultimo["Var_%"]):
            tarjetas.append(ui.kpi_html(f"Último mes · {ultimo['Mes_Filtro']}", num(ultimo["Real"]), "unid.",
                                        delta=(f"{pct(ultimo['Var_%'])} vs. mes anterior", ultimo["Var_%"] >= 0)))
        ui.kpis(tarjetas, minimo=220)

        with ui.tarjeta("prod_grafico", f"Tendencia de producción · {nombre}", "Unidades por mes"):
            ui.leyenda([("Producción", ui.NAVY), ("Último mes", ui.ORANGE)])
            _grafico(df_final)

        with ui.tarjeta("prod_tabla", "Datos del período", nombre):
            df_tabla = df_final[['Mes_Filtro', 'Real', 'Var_%']].copy()
            df_tabla.columns = ['Mes / Período', 'Producción Real (Unidades)', 'Var. vs mes anterior']
            vista = df_tabla.copy()
            # Streamlit muestra 'None' en celdas vacías: la variación se entrega ya como texto
            vista['Var. vs mes anterior'] = [pct(x, signo=True) if pd.notna(x) else "–" for x in vista['Var. vs mes anterior']]
            st.dataframe(vista.style.format({'Producción Real (Unidades)': num}), width="stretch", hide_index=True,
                         column_config={'Var. vs mes anterior': st.column_config.TextColumn(alignment="right")})
            st.download_button("Descargar Excel", data=_excel(df_tabla), file_name=f"Produccion_{nombre.replace(' ', '_')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               icon=":material/download:", key="prod_descarga")

    except Exception as e:
        st.error(f"No se pudo procesar la producción: {e}")

"""
Componentes visuales del Portal v2.0.

Todas las páginas usan la misma estructura:
    encabezado()  ->  fila de KPIs (kpis / grupos)  ->  tarjeta() con gráfico  ->  tarjeta() con tabla

Los estilos de las clases `sp-*` están en utils/estilos.py.
"""
import html as _html
from contextlib import contextmanager

import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════
# TOKENS
# ══════════════════════════════════════════════════════════
# Los colores dependen del modo activo (claro u oscuro): ver utils/tema.py.
# `ui.NAVY`, `ui.INK`, etc. siguen funcionando: se resuelven en cada uso con __getattr__.
from utils import tema as _tema


def _c(nombre):
    return _tema.color(nombre)


def __getattr__(nombre):
    if nombre in _tema.CLARO:
        return _tema.color(nombre)
    raise AttributeError(nombre)


FUENTE = "Inter, 'Segoe UI', system-ui, sans-serif"

_ICONOS = {
    "arrow_up": '<path d="M12 19V5"/><path d="M6 11l6-6 6 6"/>',
    "arrow_down": '<path d="M12 5v14"/><path d="M6 13l6 6 6-6"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1"/>',
    "alert": '<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "box": '<path d="M3 7l9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7"/><path d="M12 11v10"/>',
}


def _e(x):
    return _html.escape(str(x), quote=True)


def _svg_img(svg, ancho, alto, estilo=""):
    """st.html elimina <svg> en línea; se entrega como imagen (data URI), que sí se conserva."""
    from urllib.parse import quote
    return (f'<img src="data:image/svg+xml;utf8,{quote(svg)}" width="{ancho}" height="{alto}" alt="" '
            f'aria-hidden="true" style="display:block;flex:none;{estilo}">')


def icono(nombre, size=16, color=None, grosor=2.0):
    color = color or _c("INK")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
           f'stroke="{color}" stroke-width="{grosor}" stroke-linecap="round" stroke-linejoin="round">{_ICONOS[nombre]}</svg>')
    return _svg_img(svg, size, size)


def _render(html):
    """Inserta HTML sin pasar por Markdown (evita que la indentación se vuelva código)."""
    st.html("".join(linea.strip() for linea in html.splitlines()))


# ══════════════════════════════════════════════════════════
# ESTRUCTURA DE PÁGINA
# ══════════════════════════════════════════════════════════
def encabezado(ruta, titulo, subtitulo=None):
    sub = f'<p class="sp-sub">{_e(subtitulo)}</p>' if subtitulo else ""
    _render(f'''
        <header class="sp-head">
          <p class="sp-crumb">{_e(ruta)}</p>
          <h1 class="sp-title">{_e(titulo)}</h1>
          {sub}
        </header>''')


def seccion(titulo, subtitulo=None):
    """Título de una sección dentro de la página (debajo del encabezado principal)."""
    sub = f'<p class="sp-sub">{_e(subtitulo)}</p>' if subtitulo else ""
    _render(f'<div class="sp-section"><h2 class="sp-section-title">{_e(titulo)}</h2>{sub}</div>')


@contextmanager
def tarjeta(clave, titulo=None, nota=None):
    """Contenedor blanco con borde. Uso:  with ui.tarjeta("cedis", "Venta por CEDI", "Unidades"): ..."""
    with st.container(border=True, key=f"sp_card_{clave}"):
        if titulo:
            nota_html = f'<span class="sp-card-note">{_e(nota)}</span>' if nota else ""
            _render(f'<div class="sp-card-head"><h2 class="sp-card-title">{_e(titulo)}</h2>{nota_html}</div>')
        yield


def pie(version="v2.0"):
    _render(f'''
        <footer class="sp-foot">
          <span>Plataforma de Inteligencia Operativa · {version} · Sapori, C.A.</span>
          <span>Desarrollado por Jair Ramos · KaisenYork | Software</span>
        </footer>''')


# ══════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════
def _delta_html(texto, positivo):
    if positivo is None:
        return f'<span class="sp-delta">{_e(texto)}</span>'
    color = _c("POS") if positivo else _c("NEG")
    flecha = icono("arrow_up" if positivo else "arrow_down", 14, color, 2.2)
    return f'<span class="sp-delta" style="color:{color}">{flecha}{_e(texto)}</span>'


def _barra_html(pct, izq=None, der=None, alto=8):
    pct = max(0.0, min(float(pct or 0), 100.0))
    etiquetas = ""
    if izq or der:
        etiquetas = f'<span class="sp-bar-labels"><span>{_e(izq or "")}</span><span>{_e(der or "")}</span></span>'
    return (f'<div class="sp-bar-wrap"><span class="sp-track" style="height:{alto}px">'
            f'<span class="sp-fill" style="width:{pct:.1f}%;height:{alto}px"></span></span>{etiquetas}</div>')


def _sparkline(valores, ancho=220, alto=44):
    vals = [float(v) for v in valores]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rango = (hi - lo) or 1
    pts = [(6 + i * (ancho - 12) / (len(vals) - 1), alto - 6 - (v - lo) / rango * (alto - 12)) for i, v in enumerate(vals)]
    linea = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    lx, ly = pts[-1]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="none">'
           f'<polyline points="{linea}" fill="none" stroke="{_c("NAVY")}" stroke-width="2" vector-effect="non-scaling-stroke"/>'
           f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.5" fill="{_c("ORANGE")}"/></svg>')
    return _svg_img(svg, "100%", alto, "width:100%")


def kpi_html(etiqueta, valor, unidad="", delta=None, nota=None, progreso=None, spark=None, extra=None):
    """Una tarjeta KPI.
    delta: (texto, positivo)  · positivo=None => neutro
    progreso: (pct, texto_izq, texto_der)
    spark: lista de valores para la mini tendencia
    extra: (valor_grande, texto) => cifra secundaria bajo una línea
    """
    partes = [f'<p class="sp-label">{_e(etiqueta)}</p>',
              f'<p class="sp-big">{_e(valor)}<span class="sp-unit">{_e(unidad)}</span></p>']
    if progreso:
        partes.append(_barra_html(*progreso))
    if delta:
        partes.append(f'<div class="sp-row">{_delta_html(*delta)}</div>')
    if spark:
        partes.append(_sparkline(spark))
    if extra:
        partes.append(f'<div class="sp-extra"><span class="sp-extra-val">{_e(extra[0])}</span><span class="sp-extra-txt">{_e(extra[1])}</span></div>')
    if nota:
        partes.append(f'<p class="sp-note">{_e(nota)}</p>')
    return f'<div class="sp-kpi">{"".join(partes)}</div>'


def kpis(tarjetas_html, minimo=240):
    """Fila de KPIs que se acomoda sola al ancho (en teléfono se apilan)."""
    _render(f'<div class="sp-grid" style="grid-template-columns:repeat(auto-fit,minmax({minimo}px,1fr))">{"".join(tarjetas_html)}</div>')


def stat_html(etiqueta, valor, unidad="", nota=None):
    n = f'<p class="sp-note">{_e(nota)}</p>' if nota else ""
    u = f'<span class="sp-unit">{_e(unidad)}</span>' if unidad else ""
    return f'<div class="sp-stat"><p class="sp-stat-label">{_e(etiqueta)}</p><p class="sp-stat-val">{_e(valor)}{u}</p>{n}</div>'


def grupo_html(titulo, principal=None, stats=(), insignia=None, progreso=None):
    """Tarjeta que agrupa varias métricas relacionadas (ej. bloque Venta / Forecast / Período).
    principal: (valor, unidad) o texto
    """
    cab = f'<div class="sp-group-head"><p class="sp-label">{_e(titulo)}</p>'
    cab += f'<span class="sp-badge">{_e(insignia)}</span>' if insignia else ""
    cab += "</div>"
    cuerpo = ""
    if isinstance(principal, tuple):
        cuerpo += f'<p class="sp-big">{_e(principal[0])}<span class="sp-unit">{_e(principal[1])}</span></p>'
    elif principal:
        cuerpo += f'<p class="sp-period">{_e(principal)}</p>'
    if progreso:
        cuerpo += _barra_html(*progreso, alto=10)
    if stats:
        cuerpo += f'<div class="sp-stats">{"".join(stats)}</div>'
    return f'<div class="sp-kpi sp-group">{cab}{cuerpo}</div>'


# ══════════════════════════════════════════════════════════
# BARRAS HORIZONTALES (comparativos simples, sin Plotly)
# ══════════════════════════════════════════════════════════
def barras(filas, columnas_extra=(), resaltar_primero=True, fmt=None, ancho_valor=72):
    """filas: [(nombre, valor, [textos extra...])] ya ordenadas.
    columnas_extra: anchos en px de las columnas de texto extra."""
    if not filas:
        return
    maximo = max(float(v) for _, v, *_ in filas) or 1
    from utils.formato import num
    fmt = fmt or num
    plantilla = f"minmax(90px,200px) minmax(60px,1fr) {ancho_valor}px" + "".join(f" {w}px" for w in columnas_extra)
    out = []
    for i, fila in enumerate(filas):
        nombre, valor = fila[0], float(fila[1])
        extras = fila[2] if len(fila) > 2 else []
        color = _c("ORANGE") if (resaltar_primero and i == 0) else _c("NAVY")
        celdas = "".join(f'<span class="sp-hb-extra">{_e(x)}</span>' for x in extras)
        out.append(
            f'<div class="sp-hb" style="grid-template-columns:{plantilla}">'
            f'<span class="sp-hb-name" title="{_e(nombre)}">{_e(nombre)}</span>'
            f'<span class="sp-track" style="height:12px"><span class="sp-fill" style="width:{valor / maximo * 100:.1f}%;height:12px;background:{color}"></span></span>'
            f'<span class="sp-hb-val">{fmt(valor)}</span>{celdas}</div>')
    _render(f'<div class="sp-hbars">{"".join(out)}</div>')


def linea_resumen(pares):
    """Fila de 'etiqueta valor' bajo un gráfico. pares: [(etiqueta, valor, destacado_bool)]"""
    items = "".join(
        f'<span>{_e(e)} <strong style="color:{_c("ORANGE_TXT") if d else _c("INK")}">{_e(v)}</strong></span>' for e, v, d in pares)
    _render(f'<div class="sp-summary">{items}</div>')


def leyenda(items):
    _render('<div class="sp-legend">' + "".join(
        f'<span><i style="background:{c}"></i>{_e(t)}</span>' for t, c in items) + '</div>')


def estado(tono, titulo, texto=""):
    """Franja de estado compacta (conexión, configuración, avisos de la página)."""
    color = {"neg": _c("NEG"), "aviso": _c("ORANGE_TXT"), "info": _c("NAVY"), "pos": _c("POS")}[tono]
    ico = {"neg": "alert", "aviso": "alert", "info": "trend", "pos": "check"}[tono]
    t = f'<span class="sp-status-text">{_e(texto)}</span>' if texto else ""
    _render(f'<div class="sp-status" style="border-color:{color}55;background:{color}0f">'
            f'{icono(ico, 16, color)}<strong style="color:{color}">{_e(titulo)}</strong>{t}</div>')


def alerta(icono_nombre, tono, titulo, texto):
    """Punto de atención (icono + título + texto). Debajo se puede poner un st.page_link."""
    color = {"neg": _c("NEG"), "aviso": _c("ORANGE_TXT"), "info": _c("NAVY"), "pos": _c("POS")}[tono]
    _render(f'''
        <div class="sp-alert">
          <span class="sp-alert-ico" style="color:{color};background:{color}1f">{icono(icono_nombre, 16, color)}</span>
          <div class="sp-alert-body"><p class="sp-alert-title">{_e(titulo)}</p><p class="sp-alert-text">{_e(texto)}</p></div>
        </div>''')


# ══════════════════════════════════════════════════════════
# GRÁFICOS (Plotly)
# ══════════════════════════════════════════════════════════
def estilo_grafico(fig: go.Figure, alto=320, leyenda_visible=False):
    """Aplica el estilo común a un gráfico Plotly."""
    fig.update_layout(
        height=alto,
        margin=dict(l=8, r=8, t=12, b=8),
        font=dict(family=FUENTE, size=12, color=_c("MUTED")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=leyenda_visible,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(bgcolor=_c("SURFACE"), bordercolor=_c("BORDER"), font=dict(family=FUENTE, color=_c("INK"), size=13)),
        separators=",.",
    )
    fig.update_xaxes(showgrid=False, linecolor=_c("BORDER"), tickfont=dict(color=_c("MUTED")), title=None, automargin=True)
    fig.update_yaxes(gridcolor=_c("BORDER"), zeroline=False, tickfont=dict(color=_c("MUTED")), title=None, automargin=True)
    return fig


def ejes_miles(fig, desde_cero=True, pasos=5):
    """Eje Y con etiquetas '250 k' en formato local (sin depender del locale de Plotly)."""
    valores = []
    for tr in fig.data:
        if getattr(tr, "y", None) is not None:
            valores.append([float(v) for v in tr.y if v is not None and v == v])
    if not valores:
        return fig
    if fig.layout.barmode == "stack":
        n = max(len(v) for v in valores)
        alto = max(sum(v[i] for v in valores if i < len(v)) for i in range(n))
        bajo = 0
    else:
        planos = [x for v in valores for x in v]
        alto, bajo = max(planos), (0 if desde_cero else min(planos))
    import math
    bruto = (alto - bajo) / pasos or 1
    mag = 10 ** math.floor(math.log10(bruto))
    paso = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= bruto)
    inicio = math.floor(bajo / paso) * paso
    ticks = [inicio + i * paso for i in range(int((alto - inicio) / paso) + 2)]
    from utils.formato import num
    textos = [f"{num(t / 1e6, 1)} M" if paso >= 1e6 else (f"{num(t / 1e3)} k" if t else "0") for t in ticks]
    fig.update_yaxes(tickvals=ticks, ticktext=textos, range=[ticks[0], ticks[-1]])
    return fig


def posiciones_etiquetas(valores):
    """Etiqueta debajo de los valles y arriba del resto, para que la línea no la tape."""
    vals = list(valores)
    pos = []
    for i, v in enumerate(vals):
        izq = vals[i - 1] if i > 0 else None
        der = vals[i + 1] if i < len(vals) - 1 else None
        valle = (izq is None or v < izq) and (der is None or v < der) and (izq is not None or der is not None)
        pos.append("bottom center" if valle else "top center")
    return pos


def grafico(fig, clave=None):
    st.plotly_chart(fig, width="stretch", theme=None, key=clave,
                    config={"displayModeBar": False})

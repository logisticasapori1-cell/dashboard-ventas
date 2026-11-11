"""
Paletas de color del portal (modo claro y modo oscuro).

Streamlit pinta sus propios controles con .streamlit/config.toml ([theme.light] y
[theme.dark]). Este archivo define los colores de los componentes propios
(tarjetas, KPIs, barras, gráficos, semáforos) para que coincidan con el modo activo.

Todas las parejas texto/fondo cumplen WCAG AA (4,5:1). Se verifican con
`python -m utils.tema` (imprime la tabla de contrastes).
"""
import streamlit as st

CLARO = {
    "BG": "#f4f6f9",          # fondo de la página
    "SURFACE": "#ffffff",     # tarjetas
    "TRACK": "#eef1f5",       # fondo de barras de progreso
    "BORDER": "#e2e6ec",
    "INK": "#13263a",         # texto principal
    "MUTED": "#556677",       # texto secundario
    "NAVY": "#1a3a5c",        # serie principal de gráficos / acento institucional
    "LIGHTBLUE": "#8fb0d3",   # serie secundaria
    "GRIS": "#b8c4d0",        # serie neutra
    "ORANGE": "#fa7d2a",      # naranja Sapori: solo rellenos (barras, puntos)
    "ORANGE_TXT": "#a84b0b",  # naranja para texto
    "POS": "#17734a",
    "NEG": "#b42318",
    "ON_PRIMARY": "#ffffff",  # texto sobre botón principal
    "PRIMARY": "#b5500a",     # botón principal (naranja oscuro, contraste AA con blanco)
    # Semáforos de tablas (fondo / texto)
    "ROJO_BG": "#fde7d9", "ROJO_TX": "#8f3f09",
    "AMBAR_BG": "#fff4cc", "AMBAR_TX": "#6b5000",
    "VERDE_BG": "#e3f1e8", "VERDE_TX": "#145f3e",
}

OSCURO = {
    "BG": "#0e1621",
    "SURFACE": "#16212e",
    "TRACK": "#243446",
    "BORDER": "#2a3a4c",
    "INK": "#e6edf5",
    "MUTED": "#a3b3c4",
    "NAVY": "#8fb4e0",        # en oscuro la serie principal es un azul claro
    "LIGHTBLUE": "#3f6590",
    "GRIS": "#8593a3",
    "ORANGE": "#fa7d2a",
    "ORANGE_TXT": "#ffa366",
    "POS": "#4cc38a",
    "NEG": "#ff8a7a",
    "ON_PRIMARY": "#13263a",
    "PRIMARY": "#fa7d2a",
    "ROJO_BG": "#4a2416", "ROJO_TX": "#ffc2a3",
    "AMBAR_BG": "#40360f", "AMBAR_TX": "#f6dc85",
    "VERDE_BG": "#123826", "VERDE_TX": "#8fe0b4",
}

PALETAS = {"light": CLARO, "dark": OSCURO}


def tipo():
    """'light' o 'dark' según el modo que el navegador está mostrando."""
    try:
        t = st.context.theme.type
    except Exception:
        t = None
    return t if t in PALETAS else "light"


def paleta():
    return PALETAS[tipo()]


def color(nombre):
    return paleta()[nombre]


# ══════════════════════════════════════════════════════════
# Verificación de contraste (python -m utils.tema)
# ══════════════════════════════════════════════════════════
def _lum(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


PAREJAS_TEXTO = [
    ("INK", "SURFACE"), ("INK", "BG"), ("MUTED", "SURFACE"), ("MUTED", "BG"),
    ("ORANGE_TXT", "SURFACE"), ("POS", "SURFACE"), ("NEG", "SURFACE"), ("NAVY", "SURFACE"),
    ("ON_PRIMARY", "PRIMARY"), ("ROJO_TX", "ROJO_BG"), ("AMBAR_TX", "AMBAR_BG"), ("VERDE_TX", "VERDE_BG"),
]

if __name__ == "__main__":
    for nombre, p in (("CLARO", CLARO), ("OSCURO", OSCURO)):
        print(f"\n{nombre}")
        for t, f in PAREJAS_TEXTO:
            c = contraste(p[t], p[f])
            print(f"  {t:11s} sobre {f:9s} {c:5.2f}:1  {'OK' if c >= 4.5 else 'FALLA'}")

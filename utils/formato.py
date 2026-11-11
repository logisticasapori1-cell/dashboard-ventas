"""
Formato numérico único del portal (convención es-VE):
punto para miles, coma para decimales. Úsalo en vez de formatear a mano.

    num(636395)          -> "636.395"
    num(15.2, 1)         -> "15,2"
    usd(835072.92)       -> "USD 835.072,92"
    usd(835072.92, simbolo="$")  -> "$835.072,92"
    pct(15.13, signo=True)       -> "+15,1%"
"""
import math


def _es_vacio(x):
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False


def num(x, dec=0, vacio="–"):
    if _es_vacio(x):
        return vacio
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def usd(x, dec=2, simbolo="USD ", vacio="–"):
    if _es_vacio(x):
        return vacio
    signo = "−" if float(x) < 0 else ""
    return f"{signo}{simbolo}{num(abs(float(x)), dec)}"


def pct(x, dec=1, signo=False, vacio="–"):
    if _es_vacio(x):
        return vacio
    s = num(abs(float(x)), dec)
    if signo:
        return f"{'+' if float(x) >= 0 else '−'}{s}%"
    return f"{'−' if float(x) < 0 else ''}{s}%"


def con_signo(x, dec=0, vacio="–"):
    """Número con signo explícito: +1.234 / −1.234."""
    if _es_vacio(x):
        return vacio
    return f"{'+' if float(x) >= 0 else '−'}{num(abs(float(x)), dec)}"

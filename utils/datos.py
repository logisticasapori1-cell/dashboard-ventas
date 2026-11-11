"""
Fuente única de datos del Portal Supply Chain & S&OP.

Todos los módulos leen del mismo archivo Excel (ARCHIVO_DATOS).
Si cambias el nombre de una hoja en el Excel, cámbialo solo aquí.

Grupos de hojas: los módulos de Producción, Cierre de Inventario y Ventas
por CEDI leen TODAS las hojas cuyo nombre empiece por su prefijo, en el
orden en que aparecen en el Excel. Para agregar un mes o un CEDI nuevo,
basta con crear la hoja con el prefijo correcto (sin tocar el código).
"""
import os

import pandas as pd
import streamlit as st

# ══════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════
ARCHIVO_DATOS = os.path.join("data", "Sapori_Datos.xlsx")

# Hojas individuales (nombre exacto de la pestaña)
HOJA_VENTAS_SKU = "VTS file_ventas"          # m1, m4
HOJA_VENTAS_KPIS = "VTS DASHBOARD"           # m1, m4
HOJA_DESVIACIONES = "DESV Venta Diaria SKU"  # m2, m4
HOJA_KPIS_FINANCIEROS = "FIN KPIs Inventario"  # m6, m4
HOJA_SICI = "SICI Inventarios"               # m7, m4

# Grupos de hojas (inicio del nombre de la pestaña)
PREFIJO_PRODUCCION = "Produccion Total"      # m3, m4 -> una hoja por categoría
PREFIJO_CIERRE = "CIERRE "                   # m5, m4 -> una hoja por mes, en orden cronológico
PREFIJO_CEDIS = "VENTAS CONSOLIDADA"         # m8     -> una hoja por CEDI + la nacional


class HojaNoEncontrada(Exception):
    pass


# ══════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════
def existe():
    return os.path.exists(ARCHIVO_DATOS)


def version():
    """Fecha de modificación del archivo. Se usa como llave de caché:
    al subir un Excel nuevo, el portal lo relee sin reiniciar."""
    return os.path.getmtime(ARCHIVO_DATOS) if existe() else 0.0


def mostrar_error_archivo():
    st.error(f"❌ **Archivo de datos no encontrado:** '{ARCHIVO_DATOS}'")


@st.cache_data(show_spinner=False)
def _nombres_hojas(path, ver):
    return list(pd.ExcelFile(path).sheet_names)


@st.cache_data(show_spinner=False)
def _leer(path, ver, hoja, header, skiprows):
    return pd.read_excel(path, sheet_name=hoja, header=header, skiprows=skiprows)


def listar_hojas():
    """Todas las pestañas del Excel, en su orden."""
    return _nombres_hojas(ARCHIVO_DATOS, version())


def hojas_con_prefijo(prefijo):
    """Pestañas cuyo nombre empieza por `prefijo`, en el orden del Excel."""
    return [h for h in listar_hojas() if h.startswith(prefijo)]


def leer_hoja(hoja, header=0, skiprows=None):
    """Lee una pestaña por nombre exacto (resultado en caché)."""
    if hoja not in listar_hojas():
        raise HojaNoEncontrada(
            f"No existe la hoja '{hoja}' en {ARCHIVO_DATOS}. "
            f"Revisa el nombre de la pestaña (ver utils/datos.py)."
        )
    return _leer(ARCHIVO_DATOS, version(), hoja, header, skiprows)


def leer_grupo(prefijo, quitar_prefijo=False, header=0, skiprows=None):
    """Lee todas las pestañas de un grupo.

    Retorna (nombres, dict {nombre: DataFrame}) en el orden del Excel.
    Con quitar_prefijo=True, 'CIERRE ENERO 2026' se entrega como 'ENERO 2026'.
    """
    hojas = hojas_con_prefijo(prefijo)
    if not hojas:
        raise HojaNoEncontrada(
            f"No hay hojas que empiecen por '{prefijo}' en {ARCHIVO_DATOS}."
        )
    nombres, dfs = [], {}
    for h in hojas:
        nombre = h[len(prefijo):].strip() if quitar_prefijo else h
        nombres.append(nombre)
        dfs[nombre] = leer_hoja(h, header=header, skiprows=skiprows)
    return nombres, dfs


@st.cache_data(show_spinner=False)
def _fecha_guardado(path, ver):
    """Fecha en que se guardó el Excel (propiedades del archivo, la escribe Excel al guardar)."""
    import openpyxl
    try:
        wb = openpyxl.load_workbook(path, read_only=True)
        fecha = wb.properties.modified
        wb.close()
        return fecha
    except Exception:
        return None


def fecha_actualizacion(zona="America/Caracas"):
    """Fecha y hora (hora de Venezuela) en que se guardó el Excel de datos, o None.

    Se lee de las propiedades del archivo y no de la fecha del sistema, porque al
    desplegar en Render la fecha del sistema es la del despliegue, no la del Excel.
    """
    if not existe():
        return None
    fecha = _fecha_guardado(ARCHIVO_DATOS, version())
    if fecha is None:
        return None
    from datetime import timezone
    from zoneinfo import ZoneInfo
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)  # Excel la guarda en UTC
    return fecha.astimezone(ZoneInfo(zona))

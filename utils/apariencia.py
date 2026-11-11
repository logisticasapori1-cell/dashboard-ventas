"""
Selector de apariencia: Sistema / Claro / Oscuro.

Cómo funciona
- Streamlit ya trae un tema claro y uno oscuro (.streamlit/config.toml) y sigue el
  modo del sistema operativo. El cambio de tema nativo vive en su menú (⋮), que el
  portal mantiene oculto.
- Este selector, al elegir una opción, activa ese mismo cambio nativo (sin recargar la
  página ni cerrar la sesión) y luego pide una nueva ejecución para que los
  componentes propios (tarjetas, gráficos, semáforos) tomen la paleta correcta.
- La preferencia se guarda en el navegador (localStorage "sapori_tema"), así se
  conserva al volver a entrar.

Requiere `toolbarMode = "viewer"` en config.toml (para que exista el menú nativo).
"""
import json

import streamlit as st
import streamlit.components.v1 as components

from utils import tema

OPCIONES = {"sistema": "Sistema", "claro": "Claro", "oscuro": "Oscuro"}
_ETIQUETAS = {"sistema": "Sistema", "claro": "Claro", "oscuro": "Oscuro"}

_JS = """
<script>
(function () {
  const P = window.parent, D = P.document;
  const deseado = __DESEADO__;          // "sistema" | "claro" | "oscuro" | null (pantalla de acceso)
  const tipoPython = "__TIPO__";        // modo con el que Python pintó esta ejecución
  const primera = __PRIMERA__;          // primera ejecución de la sesión
  const etiquetas = __ETIQUETAS__;
  const LS = "sapori_tema";
  let guardado = null;
  try { guardado = P.localStorage.getItem(LS); } catch (e) {}

  // 1. Al entrar, el selector arranca en "Sistema": si hay una preferencia guardada, se selecciona
  //    (se reintenta unos instantes porque el selector puede terminar de dibujarse después).
  if (primera && deseado !== null && guardado && guardado !== deseado && etiquetas[guardado]) {
    let intentos = 0;
    (function sincronizar() {
      const cont = D.querySelector(".st-key-sp_tema");
      const btn = cont && [...cont.querySelectorAll("button")].find(b => b.innerText.includes(etiquetas[guardado]));
      if (btn) { btn.click(); return; }
      if (++intentos < 30) setTimeout(sincronizar, 100); else continuar();
    })();
    return;
  }
  continuar();

  function continuar() {
  const pref = deseado !== null ? deseado : (guardado || "sistema");
  if (deseado !== null) { try { P.localStorage.setItem(LS, deseado); } catch (e) {} }

  const objetivo = { sistema: "System", claro: "Light", oscuro: "Dark" }[pref] || "System";
  const oscuroSO = P.matchMedia("(prefers-color-scheme: dark)").matches;
  const efectivo = pref === "sistema" ? (oscuroSO ? "dark" : "light") : (pref === "oscuro" ? "dark" : "light");

  function recargar() {
    const b = D.querySelector(".st-key-sp_tema_rerun button");
    if (b) b.click();
  }
  // Repite la recarga hasta que los colores propios coincidan con el modo visible (máx. 4 intentos).
  const TINTA = __TINTA__;   // color de texto principal de cada paleta: {light: "...", dark: "..."}
  function modoVisible(p) {
    if (p === "claro") return "light";
    if (p === "oscuro") return "dark";
    return P.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function asegurar(p, intentos, espera) {
    setTimeout(function () {
      const tinta = getComputedStyle(D.documentElement).getPropertyValue("--ink").trim().toLowerCase();
      if (tinta !== TINTA[modoVisible(p)] && intentos > 0) { recargar(); asegurar(p, intentos - 1, 900); }
    }, espera);
  }

  // 2. Aplicar el tema con el menú nativo de Streamlit (sin recargar la página).
  function aplicar() {
    let actual = null;
    try {
      const k = Object.keys(P.localStorage).find(x => x.startsWith("stActiveTheme-" + P.location.pathname + "-"));
      actual = k ? JSON.parse(P.localStorage.getItem(k)) : null;
    } catch (e) {}
    if (actual === objetivo) return false;
    const menu = D.querySelector('[data-testid="stMainMenuButton"]');
    if (!menu) return false;
    const oculto = D.createElement("style");
    oculto.textContent = '[data-baseweb="popover"]{opacity:0 !important; pointer-events:none !important}';
    D.head.appendChild(oculto);
    menu.click();
    setTimeout(function () {
      const item = D.querySelector('[data-testid="stMainMenuItem-theme-' + objetivo + '"]');
      if (item) item.click(); else D.body.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      setTimeout(function () { oculto.remove(); }, 300);
    }, 150);
    return true;
  }

  const cambio = aplicar();
  // 3. Si Python pintó con otro modo, volver a ejecutar para que tarjetas y gráficos usen la paleta correcta.
  if (efectivo !== tipoPython) { setTimeout(recargar, cambio ? 600 : 60); }
  asegurar(pref, 4, cambio ? 1500 : 900);

  // 4. En "Sistema", si el usuario cambia el modo del sistema operativo, repintar.
  //    Cada ejecución reemplaza el escucha anterior: el iframe viejo se destruye y sus funciones dejan de correr.
  const mq = P.__spTemaMQ || (P.__spTemaMQ = P.matchMedia("(prefers-color-scheme: dark)"));
  if (P.__spTemaEscucha) { try { mq.removeEventListener("change", P.__spTemaEscucha); } catch (e) {} }
  P.__spTemaEscucha = function () {
    let p = null; try { p = P.localStorage.getItem(LS); } catch (e) {}
    if (!p || p === "sistema") { setTimeout(recargar, 300); asegurar("sistema", 4, 1200); }
  };
  mq.addEventListener("change", P.__spTemaEscucha);
  }
})();
</script>
"""


def _motor(deseado, primera, clave):
    """Botón técnico de recarga + script, dentro de un contenedor invisible."""
    with st.container(key=f"sp_tema_js_{clave}"):
        st.button("Actualizar colores", key="sp_tema_rerun")
        html = (_JS.replace("__DESEADO__", json.dumps(deseado))
                   .replace("__TIPO__", tema.tipo())
                   .replace("__PRIMERA__", "true" if primera else "false")
                   .replace("__ETIQUETAS__", json.dumps(_ETIQUETAS))
                   .replace("__TINTA__", json.dumps({k: v["INK"].lower() for k, v in tema.PALETAS.items()})))
        components.html(html, height=0)


def selector():
    """Control de apariencia para la barra lateral."""
    primera = "sp_tema_iniciado" not in st.session_state
    st.session_state["sp_tema_iniciado"] = True
    st.html('<p class="sp-side-label">Apariencia</p>')
    deseado = st.segmented_control("Apariencia", list(OPCIONES), default="sistema", required=True,
                                   help="Sistema sigue el modo claro u oscuro de tu computador.",
                                   format_func=OPCIONES.get, key="sp_tema", label_visibility="collapsed",
                                   width="stretch")
    _motor(deseado, primera, "barra")


def aplicar_guardado():
    """En la pantalla de acceso (sin barra lateral): aplica la preferencia guardada en el navegador."""
    _motor(None, False, "acceso")

#!/usr/bin/env python3
"""Genera planificador.html autocontenido (sin servidor) entre preparar-video y montar-video.

Lee base-palabras.json (obligatorio) e informe.json (opcional, usa sus `paletas` si existen)
y arma un HTML local con el guion linea por linea (L01, L02...), el video base.mp4 embebido,
selector de paleta y par tipografico, tipo de escena, nota libre, pegado/arrastre de capturas
de referencia y boton "Guardar plan" que descarga plan-escenas.json.
"""
import argparse
import json
import os


PALETAS_DEFAULT = [
    {
        "nombre": "Editorial neutro + rojo señal",
        "colores": ["#EAE9E5", "#111111", "#E30613", "#6B6B65"],
    },
    {
        "nombre": "Oscuro estudio + lima cálido",
        "colores": ["#0E1116", "#F4F3EE", "#D9E86F", "#2D3B45"],
    },
    {
        "nombre": "Crema cálido + azul petróleo",
        "colores": ["#F5F1E8", "#18242E", "#2B6CB0", "#C9A25B"],
    },
]

TIPOGRAFIAS_OFL = [
    {
        "id": "inter-instrument",
        "nombre": "Inter + Instrument Serif Italic",
        "detalle": "Sans limpia + serif editorial en cursiva para la palabra clave",
        "base": "Inter",
        "realce": "Instrument Serif",
    },
    {
        "id": "jakarta-cormorant",
        "nombre": "Plus Jakarta Sans + Cormorant Garamond Italic",
        "detalle": "Geométrica moderna + serif elegante de alto contraste",
        "base": "Plus Jakarta Sans",
        "realce": "Cormorant Garamond",
    },
    {
        "id": "solo-inter",
        "nombre": "Solo Sans · Inter",
        "detalle": "Regular para relleno y ExtraBold con acento en la clave",
        "base": "Inter",
        "realce": "Inter",
    },
    {
        "id": "archivo-mono",
        "nombre": "Archivo + IBM Plex Mono",
        "detalle": "Titular suizo/técnico con datos y notas en monoespaciada",
        "base": "Archivo",
        "realce": "IBM Plex Mono",
    },
]


def agrupar_lineas(palabras, max_palabras=10, pausa_corte=0.38):
    lineas = []
    cur = []
    for p in palabras:
        if cur:
            prev = cur[-1]
            gap = float(p["s"]) - float(prev["e"])
            termina_frase = prev["w"][-1:] in ".?!"
            termina_coma = prev["w"][-1:] in ",;:" and len(cur) >= 5
            if termina_frase or termina_coma or gap > pausa_corte or len(cur) >= max_palabras:
                lineas.append(cur)
                cur = []
        cur.append(p)
    if cur:
        lineas.append(cur)

    salida = []
    for idx, grupo in enumerate(lineas, start=1):
        salida.append(
            {
                "id": f"L{idx:02d}",
                "inicio": round(float(grupo[0]["s"]), 3),
                "fin": round(float(grupo[-1]["e"]), 3),
                "palabras_indices": [int(grupo[0]["i"]), int(grupo[-1]["i"])],
                "texto": " ".join(x["w"] for x in grupo),
            }
        )
    return salida


def extraer_paletas(informe_path):
    if not informe_path or not os.path.exists(informe_path):
        return PALETAS_DEFAULT
    try:
        with open(informe_path, encoding="utf-8") as f:
            info = json.load(f)
    except Exception:
        return PALETAS_DEFAULT

    raw = info.get("paletas")
    if not raw:
        return PALETAS_DEFAULT

    normalizadas = []
    if isinstance(raw, list):
        for i, item in enumerate(raw, start=1):
            if isinstance(item, dict):
                nombre = item.get("nombre") or item.get("name") or f"Paleta {i}"
                cols = item.get("colores") or item.get("colors")
                if not cols:
                    cols = [
                        v
                        for k, v in item.items()
                        if isinstance(v, str) and v.startswith("#") and len(v) in (4, 7, 9)
                    ]
                if cols:
                    normalizadas.append({"nombre": str(nombre), "colores": cols[:5]})
            elif isinstance(item, list) and item:
                normalizadas.append({"nombre": f"Paleta {i}", "colores": item[:5]})
    elif isinstance(raw, dict):
        for nombre, cols in raw.items():
            if isinstance(cols, list) and cols:
                normalizadas.append({"nombre": str(nombre), "colores": cols[:5]})

    return normalizadas if normalizadas else PALETAS_DEFAULT


def construir_html(titulo, video_src, lineas, paletas):
    datos = {
        "titulo": titulo,
        "video_src": video_src,
        "paletas": paletas,
        "tipografias": TIPOGRAFIAS_OFL,
        "lineas": lineas,
    }
    datos_json = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{titulo} · Planificador</title>
<style>
  :root {{
    --bg: #f6f6f3;
    --card: #ffffff;
    --ink: #141413;
    --muted: #686862;
    --line: #e4e3dc;
    --accent: #1d4ed8;
    --accent-soft: #eff4ff;
    --radius: 12px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.45;
    padding: 28px 32px 64px;
  }}
  .wrap {{ max-width: 1320px; margin: 0 auto; }}
  header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 20px;
    margin-bottom: 22px;
    flex-wrap: wrap;
  }}
  h1 {{ font-size: 28px; font-weight: 800; letter-spacing: -0.02em; }}
  h1 span {{ color: var(--muted); font-weight: 400; }}
  .sub {{ color: var(--muted); font-size: 14px; margin-top: 4px; }}
  .actions {{ display: flex; gap: 10px; align-items: center; }}
  button {{
    font: inherit;
    font-size: 14px;
    font-weight: 600;
    border-radius: 9px;
    padding: 10px 16px;
    cursor: pointer;
    border: 1px solid var(--line);
    background: var(--card);
    color: var(--ink);
  }}
  button.primary {{
    background: var(--ink);
    color: #fff;
    border-color: var(--ink);
  }}
  button.primary:hover {{ background: #2c2c29; }}
  button:hover {{ border-color: #bcbab0; }}
  .sec-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 22px 0 8px;
  }}
  .panel {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 18px 20px;
    margin-bottom: 14px;
  }}
  .panel h2 {{ font-size: 16px; font-weight: 700; margin-bottom: 3px; }}
  .panel .hint {{ font-size: 13px; color: var(--muted); margin-bottom: 14px; }}
  .grid-opts {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 10px;
  }}
  .opt {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 11px 14px;
    cursor: pointer;
    background: #fff;
  }}
  .opt:has(input:checked) {{
    border-color: var(--accent);
    background: var(--accent-soft);
  }}
  .opt-left {{ display: flex; align-items: center; gap: 9px; font-size: 14px; font-weight: 500; }}
  .opt-sub {{ font-size: 12px; color: var(--muted); font-weight: 400; display: block; }}
  .swatches {{ display: flex; gap: 4px; flex-shrink: 0; }}
  .sw {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid rgba(0,0,0,0.14);
  }}
  .main-grid {{
    display: grid;
    grid-template-columns: minmax(0, 1fr) 360px;
    gap: 22px;
    align-items: start;
  }}
  @media (max-width: 980px) {{
    .main-grid {{ grid-template-columns: 1fr; }}
  }}
  .line-card {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: border-color 0.15s;
  }}
  .line-card.active {{
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(29, 78, 216, 0.12);
  }}
  .line-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 10px;
    cursor: pointer;
  }}
  .line-code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    font-weight: 700;
    color: var(--accent);
    background: var(--accent-soft);
    padding: 2px 8px;
    border-radius: 6px;
    margin-right: 8px;
  }}
  .line-time {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    color: var(--muted);
  }}
  .line-text {{
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    cursor: pointer;
  }}
  .line-text:hover {{ color: var(--accent); }}
  .tipo-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
  }}
  .tipo-btn {{
    font-size: 12px;
    font-weight: 600;
    padding: 5px 11px;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: #fafaf7;
    color: var(--muted);
    cursor: pointer;
  }}
  .tipo-btn.sel {{
    background: var(--ink);
    color: #fff;
    border-color: var(--ink);
  }}
  .line-inputs {{
    display: grid;
    grid-template-columns: 1fr 210px;
    gap: 10px;
  }}
  @media (max-width: 680px) {{
    .line-inputs {{ grid-template-columns: 1fr; }}
  }}
  textarea {{
    width: 100%;
    min-height: 76px;
    resize: vertical;
    font: inherit;
    font-size: 14px;
    padding: 10px 12px;
    border: 1px solid var(--line);
    border-radius: 9px;
    background: #fcfcfa;
    color: var(--ink);
  }}
  textarea:focus {{ outline: 2px solid rgba(29,78,216,0.22); border-color: var(--accent); background: #fff; }}
  .dropzone {{
    border: 1.5px dashed #cfcdc4;
    border-radius: 9px;
    padding: 10px;
    min-height: 76px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 12px;
    color: var(--muted);
    background: #fafaf7;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }}
  .dropzone.over {{ border-color: var(--accent); background: var(--accent-soft); color: var(--accent); }}
  .dropzone img {{
    max-width: 100%;
    max-height: 92px;
    border-radius: 6px;
    object-fit: contain;
    display: block;
  }}
  .dropzone .rm-img {{
    position: absolute;
    top: 4px;
    right: 4px;
    padding: 2px 7px;
    font-size: 11px;
    border-radius: 6px;
    background: rgba(20,20,19,0.82);
    color: #fff;
    border: none;
  }}
  .player-box {{
    position: sticky;
    top: 20px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 14px;
  }}
  .player-box video {{
    width: 100%;
    aspect-ratio: 9 / 16;
    max-height: 580px;
    background: #0b0d10;
    border-radius: 9px;
    display: block;
  }}
  .player-meta {{
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--muted);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }}
  .status-bar {{
    margin-top: 12px;
    font-size: 13px;
    color: var(--muted);
  }}
  #status-msg {{ color: #166534; font-weight: 600; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1 id="titulo"></h1>
      <p class="sub">Hacé clic en cualquier línea para saltar en el video. Elegí paleta, tipografía y qué se ve en cada línea; pegá (Ctrl+V) o arrastrá capturas de referencia donde quieras.</p>
    </div>
    <div class="actions">
      <input type="file" id="cargar-plan-input" accept="application/json" style="display:none" />
      <button type="button" id="btn-cargar">Cargar plan</button>
      <button type="button" class="primary" id="btn-guardar">Guardar plan</button>
    </div>
  </header>

  <div class="sec-label">El look</div>
  <section class="panel">
    <h2>Paleta de colores</h2>
    <p class="hint">Una paleta para todo el clip (tomada de <code>informe.json</code> si existe).</p>
    <div id="paletas-grid" class="grid-opts"></div>
  </section>

  <section class="panel">
    <h2>Par tipográfico</h2>
    <p class="hint">Fuentes OFL locales: una base limpia y un realce para la palabra clave.</p>
    <div id="tipos-grid" class="grid-opts"></div>
  </section>

  <div class="sec-label">El guion, línea por línea</div>
  <div class="main-grid">
    <div id="lineas-col"></div>
    <aside class="player-box">
      <video id="player" controls playsinline preload="metadata"></video>
      <div class="player-meta">
        <span id="cur-linea">L01</span>
        <span id="cur-tiempo">00:00.0</span>
      </div>
      <div class="status-bar">
        <span id="resumen-plan"></span><br />
        <span id="status-msg"></span>
      </div>
    </aside>
  </div>
</div>

<script>
const DATA = {datos_json};
const TIPOS_ESCENA = ["A-roll", "Gráfico encima", "B-roll", "Pantalla completa", "Lemo"];

const state = {{
  paletaIdx: 0,
  tipoIdx: 0,
  lineas: DATA.lineas.map((l) => ({{
    ...l,
    tipo: "A-roll",
    nota: "",
    referencia_img: null,
    referencia_nombre: null
  }}))
}};

document.getElementById("titulo").innerHTML = escapeHtml(DATA.titulo) + " <span>· Plan</span>";
const player = document.getElementById("player");
player.src = DATA.video_src;

function escapeHtml(s) {{
  return String(s).replace(/[&<>"']/g, (c) => ({{ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }}[c]));
}}
function fmtTime(sec) {{
  const m = Math.floor(sec / 60);
  const s = (sec % 60).toFixed(2).padStart(5, "0");
  return m + ":" + s;
}}

function renderPaletas() {{
  const root = document.getElementById("paletas-grid");
  root.innerHTML = "";
  DATA.paletas.forEach((p, idx) => {{
    const lab = document.createElement("label");
    lab.className = "opt";
    const sw = (p.colores || []).map((c) => '<span class="sw" style="background:' + escapeHtml(c) + '" title="' + escapeHtml(c) + '"></span>').join("");
    lab.innerHTML =
      '<span class="opt-left"><input type="radio" name="paleta" value="' + idx + '"' + (idx === state.paletaIdx ? " checked" : "") + ' /><span>' + escapeHtml(p.nombre) + '</span></span>' +
      '<span class="swatches">' + sw + '</span>';
    lab.querySelector("input").addEventListener("change", () => {{ state.paletaIdx = idx; actualizarResumen(); }});
    root.appendChild(lab);
  }});
}}

function renderTipos() {{
  const root = document.getElementById("tipos-grid");
  root.innerHTML = "";
  DATA.tipografias.forEach((t, idx) => {{
    const lab = document.createElement("label");
    lab.className = "opt";
    lab.innerHTML =
      '<span class="opt-left"><input type="radio" name="tipografia" value="' + idx + '"' + (idx === state.tipoIdx ? " checked" : "") + ' />' +
      '<span>' + escapeHtml(t.nombre) + '<span class="opt-sub">' + escapeHtml(t.detalle) + '</span></span></span>';
    lab.querySelector("input").addEventListener("change", () => {{ state.tipoIdx = idx; actualizarResumen(); }});
    root.appendChild(lab);
  }});
}}

function leerImagenEnLinea(idx, file) {{
  if (!file || !file.type.startsWith("image/")) return;
  const reader = new FileReader();
  reader.onload = () => {{
    state.lineas[idx].referencia_img = reader.result;
    state.lineas[idx].referencia_nombre = file.name || (state.lineas[idx].id + "-ref.png");
    renderDropzone(idx);
    actualizarResumen();
  }};
  reader.readAsDataURL(file);
}}

function renderDropzone(idx) {{
  const dz = document.getElementById("dz-" + idx);
  if (!dz) return;
  const l = state.lineas[idx];
  if (l.referencia_img) {{
    dz.innerHTML = '<img src="' + l.referencia_img + '" alt="Referencia ' + l.id + '" /><button type="button" class="rm-img" title="Quitar">×</button>';
    dz.querySelector(".rm-img").addEventListener("click", (ev) => {{
      ev.stopPropagation();
      state.lineas[idx].referencia_img = null;
      state.lineas[idx].referencia_nombre = null;
      renderDropzone(idx);
      actualizarResumen();
    }});
  }} else {{
    dz.innerHTML = '<span>Pegar (Ctrl+V), arrastrar<br />o elegir captura</span>';
  }}
}}

function saltarALinea(idx, reproducir) {{
  const l = state.lineas[idx];
  if (!l) return;
  try {{
    player.currentTime = l.inicio;
    if (reproducir) player.play().catch(() => {{}});
  }} catch (_) {{}}
  marcarActiva(idx);
}}

function marcarActiva(idx) {{
  document.querySelectorAll(".line-card").forEach((el, i) => {{
    el.classList.toggle("active", i === idx);
  }});
  if (state.lineas[idx]) {{
    document.getElementById("cur-linea").textContent = state.lineas[idx].id;
  }}
}}

function renderLineas() {{
  const root = document.getElementById("lineas-col");
  root.innerHTML = "";
  state.lineas.forEach((l, idx) => {{
    const card = document.createElement("article");
    card.className = "line-card" + (idx === 0 ? " active" : "");
    card.dataset.lineId = l.id;

    const head = document.createElement("div");
    head.className = "line-head";
    head.innerHTML = '<div><span class="line-code">' + l.id + '</span><span class="line-time">' + fmtTime(l.inicio) + ' – ' + fmtTime(l.fin) + ' · pal. ' + l.palabras_indices[0] + '–' + l.palabras_indices[1] + '</span></div>';
    head.addEventListener("click", () => saltarALinea(idx, true));

    const txt = document.createElement("div");
    txt.className = "line-text";
    txt.textContent = l.texto;
    txt.addEventListener("click", () => saltarALinea(idx, true));

    const tipoRow = document.createElement("div");
    tipoRow.className = "tipo-row";
    TIPOS_ESCENA.forEach((tipo) => {{
      const b = document.createElement("button");
      b.type = "button";
      b.className = "tipo-btn" + (l.tipo === tipo ? " sel" : "");
      b.textContent = tipo;
      b.dataset.tipo = tipo;
      b.addEventListener("click", () => {{
        state.lineas[idx].tipo = tipo;
        tipoRow.querySelectorAll(".tipo-btn").forEach((x) => x.classList.toggle("sel", x.dataset.tipo === tipo));
        actualizarResumen();
      }});
      tipoRow.appendChild(b);
    }});

    const inputs = document.createElement("div");
    inputs.className = "line-inputs";

    const ta = document.createElement("textarea");
    ta.placeholder = "Qué va en pantalla en esta línea…";
    ta.value = l.nota;
    ta.dataset.noteFor = l.id;
    ta.addEventListener("input", () => {{ state.lineas[idx].nota = ta.value; actualizarResumen(); }});
    ta.addEventListener("paste", (ev) => {{
      const items = ev.clipboardData && ev.clipboardData.items;
      if (!items) return;
      for (const it of items) {{
        if (it.type.startsWith("image/")) {{
          ev.preventDefault();
          leerImagenEnLinea(idx, it.getAsFile());
          break;
        }}
      }}
    }});

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.style.display = "none";
    fileInput.id = "file-" + idx;
    fileInput.addEventListener("change", () => {{
      if (fileInput.files && fileInput.files[0]) leerImagenEnLinea(idx, fileInput.files[0]);
    }});

    const dz = document.createElement("div");
    dz.className = "dropzone";
    dz.id = "dz-" + idx;
    dz.tabIndex = 0;
    dz.addEventListener("click", () => fileInput.click());
    dz.addEventListener("dragover", (ev) => {{ ev.preventDefault(); dz.classList.add("over"); }});
    dz.addEventListener("dragleave", () => dz.classList.remove("over"));
    dz.addEventListener("drop", (ev) => {{
      ev.preventDefault();
      dz.classList.remove("over");
      const f = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
      if (f) leerImagenEnLinea(idx, f);
    }});
    dz.addEventListener("paste", (ev) => {{
      const items = ev.clipboardData && ev.clipboardData.items;
      if (!items) return;
      for (const it of items) {{
        if (it.type.startsWith("image/")) {{
          ev.preventDefault();
          leerImagenEnLinea(idx, it.getAsFile());
          break;
        }}
      }}
    }});

    inputs.appendChild(ta);
    inputs.appendChild(dz);
    inputs.appendChild(fileInput);

    card.appendChild(head);
    card.appendChild(txt);
    card.appendChild(tipoRow);
    card.appendChild(inputs);
    root.appendChild(card);
    renderDropzone(idx);
  }});
}}

function construirPlanJson() {{
  return {{
    version: 1,
    titulo: DATA.titulo,
    fuente_video: DATA.video_src,
    paleta: DATA.paletas[state.paletaIdx],
    tipografia: DATA.tipografias[state.tipoIdx],
    lineas: state.lineas.map((l) => ({{
      id: l.id,
      inicio: l.inicio,
      fin: l.fin,
      palabras_indices: l.palabras_indices,
      texto: l.texto,
      tipo: l.tipo,
      nota: l.nota.trim(),
      ...(l.referencia_img ? {{ referencia_img: l.referencia_img, referencia_nombre: l.referencia_nombre }} : {{}})
    }}))
  }};
}}

function actualizarResumen() {{
  const conNota = state.lineas.filter((l) => l.nota.trim() || l.tipo !== "A-roll").length;
  const conImg = state.lineas.filter((l) => l.referencia_img).length;
  document.getElementById("resumen-plan").textContent =
    state.lineas.length + " líneas · " + conNota + " con escena/nota · " + conImg + " captura(s)";
}}

player.addEventListener("timeupdate", () => {{
  const t = player.currentTime || 0;
  document.getElementById("cur-tiempo").textContent = fmtTime(t);
  const idx = state.lineas.findIndex((l) => t >= l.inicio && t <= l.fin + 0.15);
  if (idx >= 0) marcarActiva(idx);
}});

document.getElementById("btn-guardar").addEventListener("click", () => {{
  const plan = construirPlanJson();
  const blob = new Blob([JSON.stringify(plan, null, 2)], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "plan-escenas.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  document.getElementById("status-msg").textContent = "Descargado plan-escenas.json (" + plan.lineas.length + " líneas).";
}});

const cargarInput = document.getElementById("cargar-plan-input");
document.getElementById("btn-cargar").addEventListener("click", () => cargarInput.click());
cargarInput.addEventListener("change", () => {{
  const f = cargarInput.files && cargarInput.files[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = () => {{
    try {{
      const prev = JSON.parse(r.result);
      if (prev.paleta) {{
        const pi = DATA.paletas.findIndex((p) => p.nombre === prev.paleta.nombre);
        if (pi >= 0) state.paletaIdx = pi;
      }}
      if (prev.tipografia) {{
        const ti = DATA.tipografias.findIndex((t) => t.id === prev.tipografia.id);
        if (ti >= 0) state.tipoIdx = ti;
      }}
      if (Array.isArray(prev.lineas)) {{
        const byId = new Map(prev.lineas.map((x) => [x.id, x]));
        state.lineas.forEach((l) => {{
          const hit = byId.get(l.id);
          if (hit) {{
            if (TIPOS_ESCENA.includes(hit.tipo)) l.tipo = hit.tipo;
            l.nota = hit.nota || "";
            l.referencia_img = hit.referencia_img || null;
            l.referencia_nombre = hit.referencia_nombre || null;
          }}
        }});
      }}
      renderPaletas();
      renderTipos();
      renderLineas();
      actualizarResumen();
      document.getElementById("status-msg").textContent = "Plan cargado: " + f.name;
    }} catch (e) {{
      document.getElementById("status-msg").textContent = "Error al leer el JSON.";
    }}
  }};
  r.readAsText(f);
}});

// Exponer helper solo para inspección/pruebas automatizadas
window.__PLANIFICADOR = {{ construirPlanJson, state }};

renderPaletas();
renderTipos();
renderLineas();
actualizarResumen();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Genera planificador.html local a partir de base-palabras.json")
    ap.add_argument("palabras_json", help="Ruta a base-palabras.json")
    ap.add_argument("--video", default="base.mp4", help="Ruta relativa del video desde planificador.html (default base.mp4)")
    ap.add_argument("--informe", help="Ruta a informe.json de preparar-video (opcional, lee `paletas`)")
    ap.add_argument("--titulo", default="Mi reel", help="Título mostrado arriba del planificador")
    ap.add_argument("--out", default="planificador.html", help="Ruta del HTML de salida")
    args = ap.parse_args()

    with open(args.palabras_json, encoding="utf-8") as f:
        palabras = json.load(f)

    lineas = agrupar_lineas(palabras)
    informe = args.informe
    if not informe:
        cand = os.path.join(os.path.dirname(os.path.abspath(args.palabras_json)), "informe.json")
        if os.path.exists(cand):
            informe = cand
    paletas = extraer_paletas(informe)
    html = construir_html(args.titulo, args.video, lineas, paletas)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generado {args.out} ({len(lineas)} líneas, {len(paletas)} paletas)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Genera la landing de magaiba.xyz en /es/ y /en/.

Un solo archivo de contenido, dos salidas. URLs separadas por idioma en vez del
toggle por spans que usan las cartas: ese método deja un solo URL para los dos
idiomas y Google indexa uno solo.

  python3 landing.py            escribe landing/es/ y landing/en/
  python3 landing.py --datos    sólo muestra los números que va a usar

Los números salen de la chain y de data/pulso.jsonl, no se escriben a mano.
"""
import json, os, sys, datetime

# Vive en web/generadores/ pero opera sobre la raíz del proyecto.
AQUI = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEST = os.path.join(AQUI, "landing")
SITIO = "https://magaiba.xyz"
CA = "A6rSPi9JmJgVkW6BatsA6MjFYLseizPM2Fnt92coFjf4"
POOL = "5Pxv2S1XjNTHCSHKPTfHiFinTeENfViHo8UgvkTaptoA"


def supply_onchain():
    """Lo pregunta a la chain. Si no hay red, cae al último valor conocido."""
    import urllib.request
    key = os.environ.get("HELIUS_KEY")
    url = (f"https://mainnet.helius-rpc.com/?api-key={key}" if key
           else "https://api.mainnet-beta.solana.com")
    cuerpo = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getTokenSupply",
                         "params": [CA]}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, cuerpo, {"content-type": "application/json"}), timeout=25)
        return float(json.load(r)["result"]["value"]["uiAmountString"])
    except Exception as e:
        print(f"  (sin red, uso el último conocido: {e})")
        return 876_204_995.49


def datos():
    """Números reales. El sitio viejo decía 70% en el pool: eran de 2024."""
    d = [json.loads(l) for l in open(f"{AQUI}/data/pulso.jsonl") if '"px_usd"' in l][-1]
    # El supply se lee de la chain, no de un snapshot: cada carta acuñada lo baja.
    supply = supply_onchain()
    return {
        "supply": supply,
        "quemado": 1_000_000_000 - supply,
        "quemado_pct": (1_000_000_000 - supply) / 1_000_000_000 * 100,
        "pool_tok": d["res_tok"],
        "pool_pct": d["res_tok"] / supply * 100,
        "pool_sol": d["res_sol"],
        "precio": d["px_usd"],
        "mc": d["mc"],
        "liq": d["liq_usd"],
        "fecha": d["t"][:10],
    }


PRENSA = [
    ("Vorterix", "https://www.youtube.com/watch?v=XlE8r-wHUE4"),
    ("RT", "https://actualidad.rt.com/actualidad/502277-criptomoneda-argentina-magaiba-surgir-meme-valor-subir-350-por-ciento"),
    ("Ámbito", "https://www.ambito.com/finanzas/magaiba-joya-cripto-todo-lo-que-tienes-que-saber-la-memecoin-argentina-que-es-furor-n5965693"),
    ("A24", "https://www.a24.com/crypto/magaiba-la-historia-la-memecoin-argentina-que-sacudio-el-mercado-criptomonedas-pocos-dias-n1306321"),
    ("iProUP", "https://www.iproup.com/economia-digital/46400-magaiba-la-memecoin-argentina-surgida-de-un-podcast-que-es-furor"),
    ("El Litoral", "https://www.ellitoral.com/internet-y-tecnologia/memecoin-creado-argentinos-base-lagarto-nacional-vale-peso-magaiba-bitcoin-criptomoneda-cotizacion-vale-dolar-precio-circulo-vicioso_0_nFGoEaQC11.html"),
    ("El Planteo", "https://elplanteo.com/magaiba/"),
    ("Corta", "https://corta.com/economia/que-magaiba-memecoin-argentina-n22698"),
    ("Más Industrias", "https://masindustrias.com.ar/que-es-magaiba-la-criptomoneda-argentina-que-se-volvio-furor/"),
    ("421", "https://www.421.news/es/magaiba-memecoin-argentina/"),
]

T = {
 "es": {
  "lang": "es", "otro": "en", "otro_nom": "EN",
  "title": "MAGAIBA · So gentle, so good · Memecoin argentina",
  "desc": "La memecoin argentina del lagarto overo, nacida en vivo en el podcast Círculo Vicioso en marzo de 2024. Token SPL en Solana, sin autoridad de emisión.",
  "hero_bajada": "La memecoin argentina del lagarto overo. Nació en vivo, al aire, en el episodio 171 de <a href=\"https://www.youtube.com/@CirculoVicioso8\">Círculo Vicioso</a>, el 7 de marzo de 2024.",
  "cta": "Comprar en Jupiter", "cta2": "Ver las cartas",
  "ca": "Contrato", "copiar": "Copiar", "copiado": "Copiado",
  "h_que": "Qué es",
  "p_que": "Un video de 2017 donde una mujer presenta a su lagarto overo, <i>McGyver</i>, y lo pronuncia «magaiba». El chiste sobrevivió siete años en los rincones raros de internet hasta que dos tipos hicieron una moneda con él, al aire, sin plan de negocios. La comunidad juntó los 10 SOL de liquidez inicial en menos de doce horas.",
  "hitos": [("2017","Se viraliza el video de McGyver."),
            ("7 mar 2024","Se anuncia al aire en el episodio 171."),
            ("8 mar 2024","Sale a Solana con tope fijo de 1.000 millones."),
            ("13 mar 2024","Pico histórico: $0,02179, unas 363 veces el precio de salida.")],
  "h_num": "Los números, hoy",
  "n_supply": "Supply", "n_quemado": "Quemado para siempre",
  "n_pool": "En el pool de liquidez", "n_mc": "Market cap", "n_precio": "Precio", "n_liq": "Liquidez",
  "p_num": "El tope es fijo: el contrato no puede emitir un token más. <b>Las autoridades de emisión y de congelamiento están revocadas</b>, verificado en la chain. Los LP tokens del pool están quemados, así que esa liquidez no la puede retirar nadie.",
  "p_ojo": "El resto del supply está en manos privadas. Eso es lo que hay: no hay bloqueo ni cronograma que lo retenga.",
  "h_prensa": "En los medios",
  "p_prensa": "Marzo de 2024, cuando el token pasó de un chiste de podcast a tapa de la sección de economía.",
  "h_riesgo": "Leé esto antes de comprar",
  "p_riesgo": "Esto es un chiste con una blockchain atada. No tiene utilidad, no tiene equipo de desarrollo, no promete nada. El precio cayó más del 99% desde el pico de 2024 y el volumen diario se mide en miles de dólares, así que una orden mediana mueve el precio. Comprá plata que puedas perder entera, porque es el resultado más probable. Nada de esto es consejo de inversión.",
  "h_com": "Comunidad",
  "pie_lic": "Sitio bajo CC BY-SA 4.0 · Datos on-chain al",
 },
 "en": {
  "lang": "en", "otro": "es", "otro_nom": "ES",
  "title": "MAGAIBA · So gentle, so good · Argentine memecoin",
  "desc": "The Argentine tegu-lizard memecoin, born live on the Círculo Vicioso podcast in March 2024. SPL token on Solana, mint authority revoked.",
  "hero_bajada": "The Argentine lizard memecoin. Born live on air, in episode 171 of <a href=\"https://www.youtube.com/@CirculoVicioso8\">Círculo Vicioso</a>, on 7 March 2024.",
  "cta": "Buy on Jupiter", "cta2": "See the cards",
  "ca": "Contract", "copiar": "Copy", "copiado": "Copied",
  "h_que": "What it is",
  "p_que": "A 2017 video where a woman introduces her tegu lizard, <i>McGyver</i>, pronouncing it “magaiba”. The joke survived seven years in the internet's weirder corners until two guys made a coin out of it, live on air, with no business plan. The community raised the 10 SOL of initial liquidity in under twelve hours.",
  "hitos": [("2017","The McGyver video goes viral."),
            ("7 Mar 2024","Announced live on episode 171."),
            ("8 Mar 2024","Launches on Solana with a hard cap of 1 billion."),
            ("13 Mar 2024","All-time high: $0.02179, about 363× the launch price.")],
  "h_num": "The numbers, today",
  "n_supply": "Supply", "n_quemado": "Burned forever",
  "n_pool": "In the liquidity pool", "n_mc": "Market cap", "n_precio": "Price", "n_liq": "Liquidity",
  "p_num": "The cap is fixed: the contract cannot mint one more token. <b>Mint and freeze authorities are revoked</b>, verified on-chain. The pool's LP tokens are burned, so that liquidity can never be pulled by anyone.",
  "p_ojo": "The rest of the supply sits in private hands. That's the honest picture: no lockup or vesting schedule holds it.",
  "h_prensa": "In the press",
  "p_prensa": "March 2024, when the token went from a podcast joke to the business section.",
  "h_riesgo": "Read this before you buy",
  "p_riesgo": "This is a joke with a blockchain attached. No utility, no dev team, no promises. The price is down more than 99% from its 2024 peak and daily volume is measured in thousands of dollars, so a mid-size order moves it. Only buy money you can lose entirely, because that is the likeliest outcome. None of this is investment advice.",
  "h_com": "Community",
  "pie_lic": "Site under CC BY-SA 4.0 · On-chain data as of",
 },
}

CSS = """
:root{
  --ground:#FCE9EF; --surf:#FFF6F9; --surf-2:#FADCE6; --line:#F3BFD1; --line-2:#E894B2;
  --ink:#4A1F2E; --ink-2:#8A4C63; --ink-3:#B5798F;
  --rosa:#D6336C; --rosa-fuerte:#E8447A; --rosa-pop:#FF5C9E;
  --oro:#9A7318; --oro-soft:#FFF4D6; --oro-line:#E8C86A;
  --disp:"Fredoka",system-ui,sans-serif;
  --body:"Nunito",-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --pag:min(880px,100% - 2rem); --r:18px;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#1F0E17; --surf:#2B1420; --surf-2:#3A1B2B; --line:#4E2437; --line-2:#6B3149;
  --ink:#FBE7EE; --ink-2:#D8A5B9; --ink-3:#A97389;
  --rosa:#FF6FA5; --rosa-fuerte:#FF87B4; --rosa-pop:#FF9CC4;
  --oro:#E8C86A; --oro-soft:#33280F; --oro-line:#8A6C22;
}}
:root[data-theme="dark"]{
  --ground:#1F0E17; --surf:#2B1420; --surf-2:#3A1B2B; --line:#4E2437; --line-2:#6B3149;
  --ink:#FBE7EE; --ink-2:#D8A5B9; --ink-3:#A97389;
  --rosa:#FF6FA5; --rosa-fuerte:#FF87B4; --rosa-pop:#FF9CC4;
  --oro:#E8C86A; --oro-soft:#33280F; --oro-line:#8A6C22;
}
*{box-sizing:border-box}
html{overflow-x:hidden}
body{margin:0;max-width:100%;overflow-x:hidden;background:var(--ground);color:var(--ink);font-family:var(--body);
  font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
.pag{width:var(--pag);margin:0 auto}
a{color:var(--rosa);text-underline-offset:3px}
h1,h2{font-family:var(--disp);line-height:1.15;margin:0}
h2{font-size:clamp(1.5rem,4vw,2rem);margin:0 0 .2em}
header{padding:1.6rem 0 2.2rem;text-align:center}
.bicho{width:min(260px,58vw);height:auto;display:block;margin:0 auto .2rem;
  filter:drop-shadow(0 14px 26px rgba(214,51,108,.32))}
.marca{font-family:var(--disp);font-weight:700;font-size:clamp(2.2rem,9vw,4.4rem);
  color:var(--rosa);letter-spacing:-.02em;margin:0 0 .1em;overflow-wrap:anywhere}
.lema{font-family:var(--disp);font-weight:600;color:var(--oro);font-size:1.15rem;margin:.1rem 0 1rem}
.bajada{max-width:34rem;margin:0 auto 1.6rem;color:var(--ink-2)}
.botones{display:flex;gap:.7rem;justify-content:center;flex-wrap:wrap}
.boton{display:inline-block;padding:.75rem 1.5rem;border-radius:999px;border:0;
  background:var(--rosa);color:#fff;font-family:var(--disp);font-weight:600;font-size:1rem;
  text-decoration:none;cursor:pointer;box-shadow:0 6px 18px rgba(214,51,108,.28)}
.boton.sec{background:var(--surf);color:var(--rosa);box-shadow:none;border:2px solid var(--line)}
.ca{display:flex;gap:.5rem;align-items:center;justify-content:center;margin-top:1.4rem;
  font-family:var(--mono);font-size:.78rem;color:var(--ink-3);flex-wrap:wrap;max-width:100%}
.ca>*{min-width:0}
.ca code{background:var(--surf);border:1px solid var(--line);border-radius:8px;padding:.3rem .55rem;
  word-break:break-all;overflow-wrap:anywhere;max-width:100%;min-width:0}
.ca button{border:1px solid var(--line);background:var(--surf);color:var(--ink-2);
  border-radius:8px;padding:.3rem .6rem;font:inherit;cursor:pointer}
section{padding:2.2rem 0;border-top:2px solid var(--line)}
.dek{color:var(--ink-3);margin:0 0 1.1rem}
.hitos{list-style:none;padding:0;margin:1.2rem 0 0;display:grid;gap:.55rem}
.hitos li{display:grid;grid-template-columns:8.5rem 1fr;gap:.8rem;align-items:baseline}
.hitos b{font-family:var(--mono);font-size:.8rem;color:var(--rosa);font-weight:600}
.nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(150px,100%),1fr));gap:.7rem;margin:1.2rem 0}
.num{background:var(--surf);border:2px solid var(--line);border-radius:var(--r);
  padding:.9rem 1rem;min-width:0}
.num .k{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3)}
.num .v{font-family:var(--disp);font-weight:700;font-size:clamp(1.05rem,4.6vw,1.5rem);
  color:var(--ink);line-height:1.2;overflow-wrap:anywhere}
.num .n{font-size:.78rem;color:var(--ink-3)}
.aviso{background:var(--oro-soft);border:2px solid var(--oro-line);border-radius:var(--r);
  padding:1rem 1.1rem;color:var(--ink-2);font-size:.94rem}
.prensa{list-style:none;padding:0;margin:1rem 0 0;display:flex;gap:.5rem;flex-wrap:wrap}
.prensa a{display:inline-block;padding:.5rem .9rem;border-radius:999px;background:var(--surf);
  border:2px solid var(--line);color:var(--ink);text-decoration:none;font-weight:700;font-size:.9rem}
.prensa a:hover{border-color:var(--rosa);color:var(--rosa)}
.riesgo{border-color:var(--line-2);background:var(--surf-2)}
.enlaces{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.8rem}
footer{padding:2rem 0 3rem;border-top:2px solid var(--line);color:var(--ink-3);font-size:.85rem;
  display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.idioma{position:absolute;top:1rem;right:1rem;font-family:var(--disp);font-weight:600}
.idioma a{text-decoration:none;background:var(--surf);border:2px solid var(--line);
  border-radius:999px;padding:.3rem .8rem;color:var(--ink-2)}
img{max-width:100%;height:auto}
@media(max-width:520px){
  .hitos li{grid-template-columns:1fr;gap:.1rem}
  .num{padding:.75rem .7rem}
  .num .k{font-size:.66rem}
  .num .n{font-size:.72rem}
  .prensa a{font-size:.82rem;padding:.42rem .7rem}
  .botones{flex-direction:column}
  .boton{width:100%;text-align:center}
}
@media(max-width:360px){
  .ca{font-size:.7rem}
  .num .v{font-size:clamp(.95rem,5vw,1.2rem)}
}
"""

def num(v, dec=0, loc="es"):
    """Miles y decimales al uso de cada idioma."""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "·").replace(".", ",").replace("·", ".") if loc == "es" else s


def pct(v, loc="es"):
    s = f"{v:.1f}%"
    return s.replace(".", ",") if loc == "es" else s


def plata(v, dec, loc="es"):
    s = f"{v:,.{dec}f}"
    if loc == "es": s = s.replace(",", "·").replace(".", ",").replace("·", ".")
    return "$" + s


def pagina(idi, d):
    t = T[idi]
    es = idi == "es"
    loc = "es-AR" if es else "en-US"
    url = f"{SITIO}/{idi}/"
    hitos = "\n".join(f'    <li><b>{a}</b><span>{b}</span></li>' for a, b in t["hitos"])
    prensa = "\n".join(f'    <li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>'
                       for n, u in PRENSA)
    nums = [
        (t["n_supply"], num(d["supply"], 0, idi), "de 1.000.000.000" if es else "of 1,000,000,000"),
        (t["n_quemado"], num(d["quemado"], 0, idi), pct(d["quemado_pct"], idi)),
        (t["n_pool"], num(d["pool_tok"], 0, idi), f'{pct(d["pool_pct"], idi)} · {num(d["pool_sol"],1,idi)} SOL'),
        (t["n_precio"], plata(d["precio"], 7, idi), t["n_mc"] + " " + plata(d["mc"], 0, idi)),
    ]
    ids = ["supply", "quemado", "pool", "precio"]
    cajas = "\n".join(
        f'    <div class="num"><div class="k">{k}</div><div class="v" id="v-{i}">{v}</div>'
        f'<div class="n" id="n-{i}">{n}</div></div>'
        for (k, v, n), i in zip(nums, ids))

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebSite", "name": "MAGAIBA",
        "url": url, "inLanguage": idi, "description": t["desc"],
        "publisher": {"@type": "Organization", "name": "Círculo Vicioso",
                      "url": "https://www.youtube.com/@CirculoVicioso8"},
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="{idi}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{t["title"]}</title>
<meta name="description" content="{t["desc"]}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="es" href="{SITIO}/es/">
<link rel="alternate" hreflang="en" href="{SITIO}/en/">
<link rel="alternate" hreflang="x-default" href="{SITIO}/en/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MAGAIBA">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{t["title"]}">
<meta property="og:description" content="{t["desc"]}">
<meta property="og:image" content="{SITIO}/magaibita.webp">
<meta property="og:locale" content="{"es_AR" if es else "en_US"}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t["title"]}">
<meta name="twitter:description" content="{t["desc"]}">
<meta name="twitter:image" content="{SITIO}/magaibita.webp">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23D6336C'/%3E%3Ccircle cx='50' cy='42' r='20' fill='%23FCE9EF'/%3E%3Crect x='30' y='66' width='40' height='9' rx='4.5' fill='%23FCE9EF'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Nunito:wght@400;600;700;800&display=swap">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>

<div class="idioma"><a href="/{t["otro"]}/" hreflang="{t["otro"]}">{t["otro_nom"]}</a></div>

<header class="pag">
  <img class="bicho" src="/magaibita.webp" width="520" height="520" alt="MAGAIBA" fetchpriority="high">
  <h1 class="marca">MAGAIBA</h1>
  <p class="lema">So gentle, so good.</p>
  <p class="bajada">{t["hero_bajada"]}</p>
  <div class="botones">
    <a class="boton" href="https://jup.ag/swap/SOL-{CA}" target="_blank" rel="noopener">{t["cta"]}</a>
    <a class="boton sec" href="/{idi}/raremagaiba/">{t["cta2"]}</a>
  </div>
  <div class="ca"><span>{t["ca"]}</span><code id="ca">{CA}</code>
    <button id="copiar" data-ok="{t["copiado"]}">{t["copiar"]}</button></div>
</header>

<main class="pag">

<section>
  <h2>{t["h_que"]}</h2>
  <p>{t["p_que"]}</p>
  <ul class="hitos">
{hitos}
  </ul>
</section>

<section>
  <h2>{t["h_num"]}</h2>
  <div class="nums">
{cajas}
  </div>
  <p>{t["p_num"]}</p>
  <div class="aviso">{t["p_ojo"]}</div>
  <div class="enlaces">
    <a href="https://dexscreener.com/solana/{POOL}" target="_blank" rel="noopener">DEX Screener</a> ·
    <a href="https://solscan.io/token/{CA}" target="_blank" rel="noopener">Solscan</a> ·
    <a href="https://jup.ag/swap/SOL-{CA}" target="_blank" rel="noopener">Jupiter</a>
  </div>
</section>

<section>
  <h2>{t["h_prensa"]}</h2>
  <p class="dek">{t["p_prensa"]}</p>
  <ul class="prensa">
{prensa}
  </ul>
</section>

<section>
  <h2>{t["h_riesgo"]}</h2>
  <div class="aviso riesgo">{t["p_riesgo"]}</div>
</section>

<section>
  <h2>{t["h_com"]}</h2>
  <div class="enlaces">
    <a href="https://circulovicioso.club/" target="_blank" rel="noopener">circulovicioso.club</a> ·
    <a href="https://www.youtube.com/@CirculoVicioso8" target="_blank" rel="noopener">YouTube</a> ·
    <a href="https://twitter.com/circulovicioso8" target="_blank" rel="noopener">Twitter</a> ·
    <a href="/{idi}/raremagaiba/">RareMagaibas</a> ·
    <a href="{SITIO}/magaiba_whitepaper.pdf">Whitepaper (PDF)</a>
  </div>
</section>

</main>

<footer class="pag">
  <span>{t["pie_lic"]} {d["fecha"]}</span>
  <span><a href="/{t["otro"]}/">{t["otro_nom"]}</a></span>
</footer>

<script>
// El supply baja con cada carta acuñada, así que un número escrito al generar
// la página envejece en horas. Se lee en vivo del mismo proxy que usa el sitio
// de las cartas. Si falla, queda el valor del build, que está fechado abajo.
(async () => {{
  const loc = "{loc}";
  const fmt = (n) => Math.round(n).toLocaleString(loc);
  try {{
    const r = await fetch("/rpc", {{
      method: "POST", headers: {{ "content-type": "application/json" }},
      body: JSON.stringify({{ jsonrpc: "2.0", id: 1, method: "getTokenSupply",
                             params: ["{CA}"] }}),
    }});
    const d = await r.json();
    const s = Number(d?.result?.value?.uiAmountString);
    if (!Number.isFinite(s) || s <= 0) return;
    const q = 1000000000 - s;
    document.getElementById("v-supply").textContent = fmt(s);
    document.getElementById("v-quemado").textContent = fmt(q);
    document.getElementById("n-quemado").textContent =
      (q / 10000000).toFixed(1).replace(".", loc === "es-AR" ? "," : ".") + "%";
  }} catch (e) {{ console.warn("supply en vivo:", e); }}
}})();

document.getElementById("copiar").onclick = async (e) => {{
  await navigator.clipboard.writeText(document.getElementById("ca").textContent.trim());
  const b = e.target, o = b.textContent;
  b.textContent = b.dataset.ok;
  setTimeout(() => {{ b.textContent = o; }}, 1400);
}};
</script>
</body>
</html>
"""


def main():
    d = datos()
    if "--datos" in sys.argv:
        for k, v in d.items(): print(f"  {k:<14}{v}")
        return
    for idi in ("es", "en"):
        os.makedirs(f"{DEST}/{idi}", exist_ok=True)
        h = pagina(idi, d)
        open(f"{DEST}/{idi}/index.html", "w", encoding="utf-8").write(h)
        pal = len(__import__("re").sub(r"<[^>]+>", " ", __import__("re").sub(
            r"<(script|style)[^>]*>.*?</\1>", "", h, flags=__import__("re").S)).split())
        print(f"  {idi}/index.html  {len(h)//1024} KB · ~{pal} palabras")

    open(f"{DEST}/robots.txt", "w").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITIO}/sitemap.xml\n")
    hoy = datetime.date.today().isoformat()
    def bloque(loc, prio, alts):
        alt = "".join(f'<xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>'
                      for h, u in alts)
        return (f'  <url><loc>{loc}</loc><lastmod>{hoy}</lastmod>'
                f'<priority>{prio}</priority>{alt}</url>\n')

    home = [("es", f"{SITIO}/es/"), ("en", f"{SITIO}/en/"), ("x-default", f"{SITIO}/en/")]
    cart = [("es", f"{SITIO}/es/raremagaiba/"), ("en", f"{SITIO}/en/raremagaiba/"),
            ("x-default", f"{SITIO}/en/raremagaiba/")]
    urls = "".join(bloque(f"{SITIO}/{i}/", "1.0", home) for i in ("es", "en"))
    urls += "".join(bloque(f"{SITIO}/{i}/raremagaiba/", "0.8", cart) for i in ("es", "en"))

    open(f"{DEST}/sitemap.xml", "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n')
    print("  robots.txt · sitemap.xml")


if __name__ == "__main__":
    main()

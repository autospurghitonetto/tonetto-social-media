"""Genera la grafica di un post (PNG 1080x1350) per Autospurghi Tonetto.

Uso: python3 tools/render.py dati.json output.jpg   (usare .jpg: TikTok non accetta PNG)
dati.json: {"categoria": "...", "titolo1": "...", "titolo2": "...",
            "sottotitolo": "...", "punti": ["...", "..."], "nota": "..."}
"""
import base64, html, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BLU, ROSSO = "#2155A6", "#EE312D"


def b64(p):
    return base64.b64encode((ROOT / p).read_bytes()).decode()


def build(d):
    e = html.escape
    punti = "".join(f'<li><span class="ck">✓</span><span>{e(p)}</span></li>' for p in d.get("punti", []))
    nota = f'<div class="nota">{e(d["nota"])}</div>' if d.get("nota") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:Inter,sans-serif;background:#fff;position:relative;overflow:hidden}}
.slash{{position:absolute;right:-160px;top:-120px;width:620px;height:620px;background:linear-gradient(135deg,{BLU} 0 49.6%,transparent 49.6% 50.4%,{ROSSO} 50.4%);opacity:.08;transform:rotate(0deg);border-radius:40px}}
.top{{position:absolute;left:90px;top:80px;right:90px;display:flex;align-items:center;justify-content:space-between}}
.top img.est{{height:92px}}
.top img.at{{height:120px}}
.cat{{position:absolute;left:90px;top:300px;font-weight:800;font-size:26px;letter-spacing:6px;color:{ROSSO};text-transform:uppercase}}
.cat:before{{content:"";display:inline-block;width:46px;height:6px;background:{ROSSO};vertical-align:middle;margin-right:18px;transform:skewX(-30deg)}}
h1{{position:absolute;left:90px;right:90px;top:350px;font-weight:800;font-size:72px;line-height:1.08;color:{BLU};letter-spacing:-1px}}
h1 span{{color:{ROSSO};display:block}}
.sub{{position:absolute;left:90px;right:90px;top:580px;font-size:31px;line-height:1.4;color:#3A4A63;font-weight:500}}
.box{{position:absolute;left:90px;right:90px;top:730px;background:#F2F6FC;border-left:12px solid {BLU};border-radius:28px;padding:40px 44px}}
.box ul{{list-style:none}}
.box li{{display:flex;gap:20px;font-size:31px;line-height:1.3;color:#14233D;font-weight:600;margin:14px 0}}
.ck{{color:#fff;background:{ROSSO};min-width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;margin-top:-1px}}
.nota{{position:absolute;left:90px;right:90px;bottom:170px;font-size:22px;color:#7A889E}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:130px;background:{BLU};display:flex;align-items:center;justify-content:space-between;padding:0 90px;color:#fff}}
.foot:after{{content:"";position:absolute;left:560px;top:0;bottom:0;width:26px;background:{ROSSO};transform:skewX(-30deg)}}
.foot .tel{{font-size:40px;font-weight:800;letter-spacing:1px}}
.foot .tel small{{font-size:24px;font-weight:700;opacity:.8;margin-right:8px}}
.foot .loc{{font-size:24px;font-weight:500;opacity:.9;text-align:right;line-height:1.3}}
</style></head><body>
<div class="top"><img class="est" src="data:image/jpeg;base64,{b64('assets/logo-esteso.jpg')}"><img class="at" src="data:image/png;base64,{b64('assets/logo-at.png')}"></div>
<div class="cat">{e(d.get('categoria',''))}</div>
<h1>{e(d['titolo1'])}<span>{e(d.get('titolo2',''))}</span></h1>
<div class="sub">{e(d.get('sottotitolo',''))}</div>
<div class="box"><ul>{punti}</ul></div>
{nota}
<div class="foot"><div class="tel"><small>TEL.</small> 0421 320 269</div><div class="loc">San Donà di Piave (VE)<br>Veneto orientale</div></div>
</body></html>"""


def main():
    d = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.set_content(build(d), wait_until="networkidle")
        pg.screenshot(path=str(out), type="jpeg", quality=92) if out.suffix.lower() in (".jpg", ".jpeg") else pg.screenshot(path=str(out))
        b.close()
    print(out)


if __name__ == "__main__":
    main()

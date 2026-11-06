"""Genera un video verticale animato (1080x1920, MP4) per Reel / TikTok / Facebook Reel.

Uso: python3 tools/render_video.py dati.json output.mp4
dati.json: {
  "categoria": "Consiglio pratico",
  "hook1": "3 cose da non",           (blu, max ~18 caratteri)
  "hook2": "buttare nel WC",           (rosso, max ~18 caratteri)
  "scene": [ {"titolo": "Salviette umidificate", "testo": "Non si sciolgono e ..."}, ... ],  (2-5 scene)
  "chiusura": "Scarico intasato? Chiamateci"  (facoltativa)
}
Ogni scena dura ~3 s; il video totale resta tra 10 e 25 s.
"""
import base64, html, json, shutil, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BLU, ROSSO = "#2155A6", "#EE312D"
FPS = 30
W, H = 1080, 1920


def b64(p):
    return base64.b64encode((ROOT / p).read_bytes()).decode()


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;font-family:Inter,sans-serif;background:#fff;position:relative;overflow:hidden}}
.top{{position:absolute;left:90px;right:90px;top:110px;display:flex;justify-content:space-between;align-items:center}}
.top img.est{{height:100px}} .top img.at{{height:130px}}
.bar{{position:absolute;left:0;right:0;bottom:0;height:150px;background:{BLU};display:flex;align-items:center;padding:0 90px;color:#fff;font-weight:800;font-size:46px}}
.bar small{{font-size:28px;opacity:.8;margin-right:12px}}
.bar:after{{content:"";position:absolute;right:220px;top:0;bottom:0;width:30px;background:{ROSSO};transform:skewX(-30deg)}}
.cat{{position:absolute;left:90px;top:560px;font-weight:800;font-size:34px;letter-spacing:7px;color:{ROSSO};text-transform:uppercase;animation:inL .6s ease-out both}}
.cat:before{{content:"";display:inline-block;width:56px;height:8px;background:{ROSSO};vertical-align:middle;margin-right:22px;transform:skewX(-30deg)}}
h1{{position:absolute;left:90px;right:90px;top:640px;font-weight:800;font-size:104px;line-height:1.06;color:{BLU};letter-spacing:-2px}}
h1 .a{{display:block;animation:up .6s .15s ease-out both}}
h1 .b{{display:block;color:{ROSSO};animation:up .6s .35s ease-out both}}
.num{{position:absolute;left:90px;top:540px;width:150px;height:150px;border-radius:50%;background:{ROSSO};color:#fff;font-weight:800;font-size:84px;display:flex;align-items:center;justify-content:center;animation:pop .5s ease-out both}}
.st{{position:absolute;left:90px;right:90px;top:740px;font-weight:800;font-size:82px;line-height:1.08;color:{BLU};letter-spacing:-1px;animation:up .6s .15s ease-out both}}
.tx{{position:absolute;left:90px;right:90px;top:1000px;font-size:54px;line-height:1.38;color:#2B3A55;font-weight:500;animation:up .6s .4s ease-out both}}
.box{{position:absolute;left:90px;right:90px;top:1000px;background:#F2F6FC;border-left:14px solid {BLU};border-radius:32px;padding:50px;animation:up .6s .3s ease-out both}}
.box .t{{font-size:50px;font-weight:700;color:#14233D;line-height:1.3}}
.box .p{{margin-top:26px;font-size:70px;font-weight:800;color:{ROSSO}}}
.prog{{position:absolute;left:90px;right:90px;top:1640px;display:flex;gap:16px}}
.prog i{{flex:1;height:10px;border-radius:5px;background:#DCE4F2}} .prog i.on{{background:{BLU}}}
@keyframes up{{from{{opacity:0;transform:translateY(60px)}}to{{opacity:1;transform:none}}}}
@keyframes inL{{from{{opacity:0;transform:translateX(-80px)}}to{{opacity:1;transform:none}}}}
@keyframes pop{{0%{{opacity:0;transform:scale(.4)}}80%{{transform:scale(1.08)}}100%{{opacity:1;transform:scale(1)}}}}
"""


def page(body, show_bar=True):
    top = (f'<div class="top"><img class="est" src="data:image/jpeg;base64,{b64("assets/logo-esteso.jpg")}">'
           f'<img class="at" src="data:image/png;base64,{b64("assets/logo-at.png")}"></div>')
    bar = '<div class="bar"><small>TEL.</small>0421 320 269</div>' if show_bar else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{top}{body}{bar}</body></html>'


def scenes(d):
    e = html.escape
    n = len(d["scene"])
    out = [(page(f'<div class="cat">{e(d.get("categoria",""))}</div>'
                 f'<h1><span class="a">{e(d["hook1"])}</span><span class="b">{e(d.get("hook2",""))}</span></h1>'), 2.6)]
    for i, s in enumerate(d["scene"], 1):
        prog = "".join(f'<i class="{"on" if k <= i else ""}"></i>' for k in range(1, n + 1))
        out.append((page(f'<div class="num">{i}</div><div class="st">{e(s["titolo"])}</div>'
                         f'<div class="tx">{e(s.get("testo",""))}</div><div class="prog">{prog}</div>'), 3.4))
    chi = e(d.get("chiusura") or "Serve un intervento? Chiamateci")
    out.append((page(f'<div class="cat">Autospurghi Tonetto</div>'
                     f'<h1><span class="a">{chi}</span></h1>'
                     f'<div class="box" style="top:1150px"><div class="t">San Donà di Piave e Veneto orientale</div>'
                     f'<div class="p">0421 320 269</div></div>', show_bar=False), 3.0))
    return out


def main():
    d = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    tmp = Path(tempfile.mkdtemp())
    idx = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": W, "height": H})
        for html_s, dur in scenes(d):
            pg.set_content(html_s, wait_until="networkidle")
            pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
            for f in range(int(dur * FPS)):
                t = f * 1000 / FPS
                pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={t})")
                pg.screenshot(path=str(tmp / f"f{idx:05d}.png"))
                idx += 1
        b.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "f%05d.png"),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(tmp)
    print(out, f"{idx / FPS:.1f}s")


if __name__ == "__main__":
    main()

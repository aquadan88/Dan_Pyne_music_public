#!/usr/bin/env python3
"""Render Dan Pyne gig graphics (feed 1080x1350, story 1080x1920) from a JSON spec.

Usage: python3 render.py spec.json out.png

Spec keys:
  kind:   solo | story | weekly | monthly
  style:  solo:    spotlight | goldframe | neon | editorial
          story:   spotlight | navy
          weekly:  bigtype | sunset
          monthly: marquee | editorial
  photo:  photo stem (e.g. "riverfront-portrait-1"). Uses cutouts/<stem>.png (Dan cut out of the
          background, bottom faded) and photos/<stem>.jpg (for blurred backdrops).
          If a cutout is missing, make one:  python3 render.py --cutout <stem>
  cut:    optional overrides for the cutout: {"h": px height, "x": center x px, "bottom": px from bottom}
  gigs:   [{"date":"2026-11-14","venue":"The Wine Mill","city":"Peninsula, OH","time":"6-9 PM",
            "address":"4964 Akron-Cleveland Rd, Peninsula"}]
  month:  "November" (monthly only; defaults to the first gig's month)

Photo notes (prefer the live shots; they look best):
  greenwall-singing    close-up singing with guitar, color. Great everywhere (goldframe, editorial,
                       story, weekly bigtype, marquee).
  farmers-singing-hat  singing with guitar, hat, color, upper body. Best for spotlight, neon,
                       sunset, story spotlight.
  hob-stage-bw         B&W live shot, faded at the bottom. Spotlight, neon, bigtype.
  riverfront-portrait-1/2  older non-performance portraits (jacket). Use least often.
"""
import json, sys, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
FONTS, PHOTOS, CUTS = ROOT / "fonts", ROOT / "photos", ROOT / "cutouts"
WEB, HANDLE, TAG = "DANPYNE.COM", "@DANPYNEMUSIC", "Acoustic Top 40 Hits"

def e(s): return html.escape(str(s))
def d(g): return datetime.date.fromisoformat(g["date"])

ICON = {
 "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>',
 "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v8h4v-8h3l1-4h-4V8z"/></svg>',
}
def ic(n, cls="ic"): return f'<span class="{cls}">{ICON[n]}</span>'

def fontface():
    f = lambda fam, file: f"@font-face{{font-family:'{fam}';src:url('file://{FONTS/file}');font-weight:100 900;}}"
    return "".join([f("Bebas","BebasNeue-Regular.ttf"), f("Oswald","Oswald-VF.ttf"), f("Playfair","PlayfairDisplay-VF.ttf"),
        f("Vibes","GreatVibes-Regular.ttf"), f("Mont","Montserrat-VF.ttf"), f("Anton","Anton-Regular.ttf"),
        f("Kaushan","KaushanScript-Regular.ttf"), f("Corm","CormorantGaramond-VF.ttf")])

GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 .55 0'/></filter>"
         "<rect width='300' height='300' filter='url(%23n)'/></svg>\")")

def bokeh(n, seed, colors, area, size=(30, 120), op=(.18, .55)):
    import random
    r = random.Random(seed); out = []
    for _ in range(n):
        s = r.randint(*size); c = r.choice(colors); o = r.uniform(*op)
        out.append(f'<i style="position:absolute;left:{r.uniform(area[0],area[1]):.1f}%;top:{r.uniform(area[2],area[3]):.1f}%;'
                   f'width:{s}px;height:{s}px;border-radius:50%;background:radial-gradient(circle,rgba({c},{o:.2f}) 0%,'
                   f'rgba({c},{o*.55:.2f}) 55%,rgba({c},0) 72%);filter:blur({r.uniform(0,3):.1f}px)"></i>')
    return '<div class="lay">' + "".join(out) + "</div>"

def social(color, accent, font="600 30px Oswald", spacing=3):
    return (f'<div class="social" style="font:{font};color:{color};letter-spacing:{spacing}px">'
            f'<span class="si" style="color:{accent}">{ICON["fb"]}</span><span class="si" style="color:{accent}">{ICON["ig"]}</span>'
            f'<b>{HANDLE}</b><span style="color:{accent};margin:0 14px">|</span><b>{WEB}</b></div>')

BASE = """*{margin:0;padding:0;box-sizing:border-box}body{width:%dpx;height:%dpx;overflow:hidden;background:#000}
.c{position:relative;width:100%%;height:100%%;overflow:hidden}.lay{position:absolute;inset:0;pointer-events:none}
.grain{position:absolute;inset:0;background-image:%s;opacity:.16;mix-blend-mode:overlay;pointer-events:none;z-index:50}
.ic svg,.si svg{width:100%%;height:100%%;display:block}.ic{display:inline-block;width:46px;height:46px;flex:none}
.si{display:inline-block;width:32px;height:32px;flex:none}.social{display:flex;gap:12px;align-items:center;justify-content:center}
.cut{position:absolute;display:block}.bgp{position:absolute;inset:-40px;width:calc(100%% + 80px);height:calc(100%% + 80px);object-fit:cover}
.gold{background:linear-gradient(180deg,#fff3c4 0%%,#f2c766 28%%,#b8862d 52%%,#f7dc8c 70%%,#9a6a1f 100%%);-webkit-background-clip:text;background-clip:text;color:transparent}
"""

def cut_img(s, h, x, bottom, extra=""):
    c = s.get("cut", {})
    h, x, bottom = c.get("h", h), c.get("x", x), c.get("bottom", bottom)
    return f'<img class="cut" src="{s["_cut"]}" style="height:{h}px;left:{x}px;bottom:{bottom}px;transform:translateX(-50%);{extra}">'

def dateparts(g):
    dt = d(g); return dt, dt.strftime("%a").upper(), dt.strftime("%b").upper(), dt.day

# ======================= SOLO =======================
def solo_spotlight(s, g):
    dt, dow, mon, day = dateparts(g)
    return f"""<style>
.c{{background:radial-gradient(ellipse at 50% 38%,#4a2208 0%,#1d0c03 55%,#080302 100%)}}
.bgp{{filter:blur(18px) brightness(.35) sepia(.6) saturate(1.4);opacity:.55}}
.cone{{position:absolute;left:50%;top:-80px;width:1300px;height:1150px;transform:translateX(-50%);
  background:linear-gradient(180deg,rgba(255,214,150,.42),rgba(255,180,90,.10) 70%,rgba(255,170,80,0));clip-path:polygon(44% 0,56% 0,100% 100%,0 100%);filter:blur(6px)}}
.nm{{position:absolute;left:0;right:0;top:44px;text-align:center;line-height:.8;white-space:nowrap}}
.n1{{display:inline-block;font:400 230px Anton;letter-spacing:6px;color:transparent;-webkit-text-stroke:4px rgba(255,205,120,.9)}}
.n2{{display:inline-block;font:400 230px Anton;letter-spacing:6px;margin-left:30px;filter:drop-shadow(0 10px 30px rgba(0,0,0,.6))}}
.cut{{filter:drop-shadow(0 0 40px rgba(255,170,70,.55)) drop-shadow(0 20px 40px rgba(0,0,0,.6)) sepia(.35) saturate(1.2) contrast(1.08)}}
.floor{{position:absolute;left:0;right:0;bottom:0;height:520px;background:linear-gradient(180deg,rgba(8,3,2,0),rgba(8,3,2,.92) 38%,#080302 60%)}}
.info{{position:absolute;left:60px;right:60px;bottom:120px;text-align:center;color:#fbefd9}}
.tag{{font:400 58px Kaushan;color:#ffc560;text-shadow:0 0 24px rgba(255,170,60,.6)}}
.v{{font:400 104px/1 Anton;letter-spacing:3px;margin-top:6px}}
.row{{display:flex;justify-content:center;gap:18px;margin-top:22px}}
.chip{{display:flex;align-items:center;gap:14px;padding:14px 26px;border-radius:60px;background:rgba(255,190,100,.12);border:2px solid rgba(255,190,100,.55);font:600 40px Oswald;letter-spacing:1px}}
.chip .ic{{width:40px;height:40px;color:#ffc560}}.chip b{{color:#ffc560;font-weight:700}}
.ft{{position:absolute;left:0;right:0;bottom:44px}}
</style><div class="c"><img class="bgp" src="{s['_photo']}"><div class="cone"></div>
<div class="nm"><div class="n1">DAN</div><div class="n2 gold">PYNE</div></div>
{bokeh(20,4,("255,190,90","255,150,50","255,220,150"),(0,100,30,70))}
{cut_img(s, 760, 540, 330)}<div class="floor"></div>{bokeh(14,9,("255,190,90","255,160,60"),(0,100,78,98),(40,110))}
<div class="info"><div class="tag">live · {TAG.lower()}</div><div class="v">{e(g['venue']).upper()}</div>
<div class="row"><div class="chip">{ic('cal')}<b>{dow}</b> {mon} {day}</div><div class="chip">{ic('clock')}{e(g['time'])}</div><div class="chip">{ic('pin')}{e(g['city'].split(',')[0]).upper()}</div></div></div>
<div class="ft">{social('#fbefd9','#ffc560')}</div><div class="grain"></div></div>"""

def solo_goldframe(s, g):
    dt, dow, mon, day = dateparts(g)
    return f"""<style>
.c{{background:radial-gradient(ellipse at 70% 40%,#22365c 0%,#0d1830 50%,#060b16 100%)}}
.lines{{position:absolute;inset:0;background:repeating-linear-gradient(135deg,rgba(201,163,92,.05) 0 2px,transparent 2px 26px)}}
.frame{{position:absolute;left:430px;top:250px;width:600px;height:700px;border:7px solid transparent;
  border-image:linear-gradient(160deg,#fff0bf,#c9a35c 30%,#8a6526 55%,#f3d58a 80%,#a87d34) 1;
  background:radial-gradient(ellipse at 50% 60%,#2a4170 0%,#101c36 80%);box-shadow:0 30px 80px rgba(0,0,0,.6)}}
.cut{{filter:drop-shadow(0 18px 40px rgba(0,0,0,.7)) contrast(1.04)}}
.L{{position:absolute;left:66px;top:84px;color:#efe3c6;z-index:5}}
.n1{{font:600 190px/0.82 Playfair;letter-spacing:2px}}.n2{{font:400 170px/0.8 Vibes;margin:-10px 0 0 70px;color:#f0d792;text-shadow:0 4px 20px rgba(0,0,0,.5)}}
.lv{{font:600 34px Mont;letter-spacing:14px;color:#efe3c6;margin-top:40px}}.sb{{font:600 22px Mont;letter-spacing:6px;color:#c9a35c;margin-top:10px;line-height:1.6}}
.bot{{position:absolute;left:0;right:0;top:985px;text-align:center;color:#efe3c6}}
.at{{font:600 24px Mont;letter-spacing:12px;color:#c9a35c}}.v{{font:600 92px/1.02 Playfair;margin-top:6px}}
.det{{display:flex;justify-content:center;gap:40px;margin-top:20px;font:600 36px Mont;letter-spacing:2px}}
.det span{{display:flex;align-items:center;gap:14px}}.det .ic{{width:42px;height:42px;color:#c9a35c}}
.ft{{position:absolute;left:0;right:0;bottom:0;height:96px;background:linear-gradient(90deg,#c9a35c,#f3dc9a,#c9a35c);display:flex;align-items:center;justify-content:center}}
</style><div class="c"><div class="lines"></div><div class="frame"></div>
{bokeh(16,21,("240,200,120","255,225,160"),(40,95,20,70),(20,70),(.12,.35))}
{cut_img(s, 860, 760, 400)}
<div class="L"><div class="n1 gold">DAN</div><div class="n2">Pyne</div><div class="lv">LIVE</div><div class="sb">ACOUSTIC<br>TOP 40 HITS</div></div>
<div class="bot"><div class="at">LIVE AT</div><div class="v gold">{e(g['venue'])}</div>
<div class="det"><span>{ic('cal')}{dow}, {mon} {day}</span><span>{ic('clock')}{e(g['time'])}</span><span>{ic('pin')}{e(g['city']).upper()}</span></div></div>
<div class="ft">{social('#0d1830','#0d1830','700 28px Mont',4)}</div><div class="grain"></div></div>"""

def solo_neon(s, g):
    dt, dow, mon, day = dateparts(g)
    addr = g.get("address") or g["city"]
    return f"""<style>
.c{{background:linear-gradient(150deg,#2a0b4a 0%,#5a0f6e 45%,#b0186a 100%)}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.12) 2px,transparent 2.5px);background-size:22px 22px;
  -webkit-mask-image:linear-gradient(200deg,#000,transparent 60%)}}
.slab{{position:absolute;left:-100px;top:150px;width:1400px;height:300px;background:#ffd400;transform:rotate(-8deg);box-shadow:0 20px 0 #111}}
.nm{{position:absolute;left:0;right:0;top:178px;text-align:center;font:400 250px/1 Anton;color:#111;letter-spacing:4px;transform:rotate(-8deg)}}
.nm span{{color:#fff;text-shadow:8px 8px 0 #111}}
.cut{{filter:grayscale(1) contrast(1.25) drop-shadow(0 0 0 #fff) drop-shadow(12px 0 0 #00e5ff) drop-shadow(-12px 0 0 #ff2bd6) drop-shadow(0 30px 40px rgba(0,0,0,.6))}}
.neon{{position:absolute;right:50px;top:560px;font:400 150px Kaushan;color:#fff;transform:rotate(-10deg);
  text-shadow:0 0 6px #fff,0 0 18px #ff4fd8,0 0 40px #ff2bd6,0 0 80px #ff2bd6}}
.btm{{position:absolute;left:0;right:0;bottom:0;height:420px;background:linear-gradient(180deg,rgba(17,5,30,0),rgba(17,5,30,.95) 35%)}}
.ban{{position:absolute;left:-20px;right:-20px;bottom:250px;background:#ffd400;transform:rotate(-3deg);text-align:center;padding:14px 0 8px;
  font:400 100px/1 Anton;color:#111;letter-spacing:2px;box-shadow:0 12px 0 #111}}
.when{{position:absolute;left:0;right:0;bottom:150px;text-align:center;font:400 62px Anton;color:#fff;letter-spacing:2px}}
.when b{{color:#00e5ff;font-weight:400}}
.ad{{position:absolute;left:0;right:0;bottom:96px;display:flex;justify-content:center;align-items:center;gap:12px;font:600 30px Oswald;color:#ffc6f2;letter-spacing:2px}}
.ad .ic{{width:34px;height:34px;color:#ffd400}}.ft{{position:absolute;left:0;right:0;bottom:34px}}
</style><div class="c"><div class="dots"></div><div class="slab"></div><div class="nm"><span>DAN</span> PYNE</div>
{cut_img(s, 640, 470, 360)}<div class="neon">Live!</div><div class="btm"></div>
<div class="ban">{e(g['venue']).upper()}</div><div class="when">{dt.strftime('%A').upper()}, {mon} {day} <b>·</b> {e(g['time'])}</div>
<div class="ad">{ic('pin')}{e(addr).upper()}</div><div class="ft">{social('#fff','#ffd400')}</div><div class="grain"></div></div>"""

def solo_editorial(s, g):
    dt, dow, mon, day = dateparts(g)
    return f"""<style>
.c{{background:radial-gradient(ellipse at 60% 40%,#f6efe2,#e6dcc9)}}
.top{{position:absolute;left:60px;right:60px;top:44px;display:flex;justify-content:space-between;font:700 22px Mont;letter-spacing:6px;color:#1c2a3e}}
.top b{{color:#c0602a}}
.mast{{position:absolute;left:0;right:0;top:70px;text-align:center;font:600 420px/0.85 Playfair;color:#1c2a3e;letter-spacing:-6px}}
.cut{{filter:drop-shadow(0 20px 40px rgba(40,30,20,.35)) saturate(1.05)}}
.L{{position:absolute;left:40px;top:600px;width:470px;padding:30px 30px 26px;background:rgba(246,239,226,.9);border-left:8px solid #c0602a;color:#1c2a3e;z-index:5}}
.k{{font:800 26px Mont;letter-spacing:8px;color:#c0602a}}.v{{font:700 96px/0.98 Playfair;margin-top:10px}}
.ln{{width:120px;height:6px;background:#c0602a;margin:26px 0}}
.r{{font:800 40px Mont;letter-spacing:2px;margin:8px 0;display:flex;align-items:center;gap:14px}}.r .ic{{width:40px;height:40px;color:#c0602a}}
.cty{{font:600 26px Mont;letter-spacing:5px;color:#6b5a44;margin-top:12px}}
.qt{{position:absolute;right:60px;top:560px;width:250px;text-align:right;font:italic 500 44px/1.15 Playfair;color:#1c2a3e;z-index:5}}
.qt b{{display:block;font:800 18px Mont;letter-spacing:5px;color:#c0602a;font-style:normal;margin-top:10px}}
.ft{{position:absolute;left:0;right:0;bottom:0;height:100px;background:#1c2a3e;display:flex;align-items:center;justify-content:center}}
</style><div class="c"><div class="top"><span>ISSUE <b>{dt.strftime('%m.%d')}</b></span><span>LIVE ACOUSTIC TOP 40</span></div>
<div class="mast">PYNE</div>{cut_img(s, 960, 800, 100)}
<div class="L"><div class="k">LIVE AT</div><div class="v">{e(g['venue'])}</div><div class="cty">{e(g['city']).upper()}</div><div class="ln"></div>
<div class="r">{ic('cal')}{dow}, {mon} {day}</div><div class="r">{ic('clock')}{e(g['time'])}</div></div>
<div class="ft">{social('#f6efe2','#e0884a','700 28px Mont',4)}</div><div class="grain" style="opacity:.22;mix-blend-mode:multiply"></div></div>"""

# ======================= STORY =======================
def story(s, g, theme):
    dt, dow, mon, day = dateparts(g)
    addr = g.get("address") or g["city"]
    if theme == "spotlight":
        bg = "radial-gradient(ellipse at 50% 35%,#4a2208 0%,#1d0c03 55%,#080302 100%)"; acc = "#ffc560"; tx = "#fbefd9"
        cf = "sepia(.35) saturate(1.2) contrast(1.08) drop-shadow(0 0 50px rgba(255,170,70,.55))"; big = 'class="tn gold"'
    else:
        bg = "radial-gradient(ellipse at 50% 35%,#22365c 0%,#0d1830 55%,#060b16 100%)"; acc = "#f0d792"; tx = "#efe3c6"
        cf = "contrast(1.05) drop-shadow(0 0 50px rgba(120,170,255,.35))"; big = 'class="tn gold"'
    return f"""<style>
.c{{background:{bg}}}.bgp{{filter:blur(22px) brightness(.3);opacity:.5}}
.tn{{position:absolute;left:0;right:0;top:140px;text-align:center;font:400 300px/0.85 Anton;letter-spacing:4px}}
.sub{{position:absolute;left:0;right:0;top:80px;text-align:center;font:600 34px Oswald;letter-spacing:14px;color:{tx}}}
.cut{{filter:{cf}}}
.floor{{position:absolute;left:0;right:0;bottom:0;height:900px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(5,5,10,.85) 40%,rgba(5,5,10,.97) 60%)}}
.card{{position:absolute;left:70px;right:70px;bottom:250px;text-align:center;color:{tx}}}
.nm{{font:400 110px/0.9 Bebas;letter-spacing:8px}}.at{{font:600 34px Oswald;letter-spacing:10px;color:{acc};margin:20px 0 4px}}
.v{{font:400 120px/0.95 Anton;letter-spacing:2px}}
.t{{display:inline-flex;align-items:center;gap:18px;margin-top:30px;padding:16px 40px;border-radius:80px;border:3px solid {acc};font:600 60px Oswald;color:{acc}}}
.t .ic{{width:58px;height:58px}}.ad{{display:flex;justify-content:center;align-items:center;gap:12px;font:500 36px Oswald;margin-top:24px}}
.ad .ic{{width:40px;height:40px;color:{acc}}}.h{{font:600 32px Oswald;letter-spacing:4px;margin-top:30px;opacity:.85}}
</style><div class="c"><img class="bgp" src="{s['_photo']}"><div class="sub">{dow} · {mon} {day}</div><div {big}>TONIGHT</div>
{bokeh(18,5,("255,190,90","255,220,150") if theme=='spotlight' else ("240,200,120","170,200,255"),(0,100,25,60))}
{cut_img(s, 900, 540, 640)}<div class="floor"></div>
<div class="card"><div class="nm">DAN PYNE</div><div class="at">LIVE AT</div><div class="v">{e(g['venue']).upper()}</div>
<div class="t">{ic('clock')}{e(g['time'])}</div><div class="ad">{ic('pin')}{e(addr)}</div><div class="h">{HANDLE} · {WEB}</div></div><div class="grain"></div></div>"""

# ======================= WEEKLY =======================
def rng(gigs):
    a, b = d(gigs[0]), d(gigs[-1])
    return f"{a.strftime('%b').upper()} {a.day} – {b.day}" if a.month == b.month else f"{a.strftime('%b').upper()} {a.day} – {b.strftime('%b').upper()} {b.day}"

def weekly(s, gigs, style):
    n = len(gigs); rh = min(132, int(560 / n)); vf = min(64, int(rh * .48))
    if style == "bigtype":
        rows = "".join(f'<div class="r" style="height:{rh-14}px"><div class="dy"><b>{d(g).strftime("%a").upper()}</b><small>{d(g).month}/{d(g).day}</small></div>'
                       f'<div class="vv"><div class="vn" style="font-size:{vf}px">{e(g["venue"]).upper()}</div><div class="vc">{e(g["city"].split(",")[0]).upper()} · {e(g["time"])}</div></div></div>' for g in gigs)
        return f"""<style>
.c{{background:radial-gradient(ellipse at 70% 30%,#2b2410 0%,#0b0b0c 60%)}}
.cone{{position:absolute;left:62%;top:-80px;width:900px;height:1000px;transform:translateX(-50%);background:linear-gradient(180deg,rgba(255,220,80,.35),rgba(255,210,60,0));clip-path:polygon(42% 0,58% 0,100% 100%,0 100%);filter:blur(8px)}}
.big{{position:absolute;left:40px;top:30px;font:400 300px/0.8 Anton;color:transparent;-webkit-text-stroke:4px #ffd23f;letter-spacing:2px}}
.big b{{display:block;color:#ffd23f;-webkit-text-stroke:0;font-weight:400}}
.cut{{filter:grayscale(1) contrast(1.2) drop-shadow(0 0 40px rgba(255,210,63,.45))}}
.sh{{position:absolute;left:0;right:0;bottom:0;height:820px;background:linear-gradient(180deg,rgba(11,11,12,0),rgba(11,11,12,.9) 30%,#0b0b0c 50%)}}
.lbl{{position:absolute;left:60px;top:560px;font:600 32px Oswald;letter-spacing:10px;color:#fff}}.lbl b{{color:#ffd23f}}
.L{{position:absolute;left:60px;right:60px;top:620px}}
.r{{display:flex;align-items:center;gap:28px;margin-bottom:14px;padding:0 24px;border-radius:16px;background:rgba(255,255,255,.06);border:1px solid rgba(255,210,63,.35)}}
.dy{{width:120px;text-align:center}}.dy b{{display:block;font:400 58px/1 Anton;color:#ffd23f}}.dy small{{font:700 24px Oswald;color:#ccc}}
.vn{{font-family:Anton;color:#fff;letter-spacing:1px;line-height:1.05;white-space:nowrap}}.vc{{font:600 28px Oswald;color:#ffd23f;letter-spacing:3px}}
.ft{{position:absolute;left:0;right:0;bottom:40px}}
</style><div class="c"><div class="cone"></div><div class="big">THIS<b>WEEK</b></div>{cut_img(s, 640, 860, 600)}<div class="sh"></div>
<div class="lbl">DAN PYNE <b>LIVE</b> · {rng(gigs)}</div><div class="L">{rows}</div><div class="ft">{social('#fff','#ffd23f')}</div><div class="grain"></div></div>"""
    rows = "".join(f'<div class="r" style="height:{rh-14}px"><div class="dy"><small>{d(g).strftime("%a").upper()}</small><b>{d(g).day}</b></div>'
                   f'<div class="vv"><div class="vn" style="font-size:{min(48,vf)}px">{e(g["venue"]).upper()}</div><div class="vc">{e(g["city"].split(",")[0]).upper()} · {e(g["time"])}</div></div></div>' for g in gigs)
    return f"""<style>
.c{{background:linear-gradient(170deg,#ff9a3c 0%,#ef5a3c 40%,#7a1f5c 75%,#2a0f3a 100%)}}
.sun{{position:absolute;left:700px;top:220px;width:560px;height:560px;border-radius:50%;transform:translateX(-50%);
  background:repeating-linear-gradient(180deg,#ffd76a 0 34px,transparent 34px 46px);-webkit-mask-image:linear-gradient(180deg,#000 55%,transparent 100%);opacity:.9}}
.h{{position:absolute;left:60px;top:60px;color:#fff}}.h1{{font:400 170px/0.84 Anton;letter-spacing:2px;text-shadow:8px 8px 0 #2a0f3a}}
.h2{{font:400 80px Kaushan;color:#ffe9a8;margin:-10px 0 0 20px;transform:rotate(-4deg)}}.rg{{font:700 30px Mont;letter-spacing:6px;margin-top:10px}}
.cut{{filter:drop-shadow(0 25px 40px rgba(42,15,58,.7)) saturate(1.05)}}
.L{{position:absolute;left:60px;width:600px;top:560px}}
.r{{display:flex;align-items:center;gap:22px;margin-bottom:14px;padding:0 22px;background:#fff6e6;border-radius:14px;box-shadow:8px 8px 0 #2a0f3a}}
.dy{{width:96px;height:calc(100% - 20px);background:#2a0f3a;color:#ffd76a;border-radius:10px;display:flex;flex-direction:column;justify-content:center;text-align:center}}
.dy small{{font:800 20px Mont;letter-spacing:3px}}.dy b{{font:400 54px/1 Anton}}
.vn{{font-family:Anton;color:#2a0f3a;line-height:1.05;white-space:nowrap;letter-spacing:1px}}.vc{{font:700 22px Mont;color:#c0442e;letter-spacing:2px}}
.ft{{position:absolute;left:0;right:0;bottom:0;height:96px;background:#2a0f3a;display:flex;align-items:center;justify-content:center}}
</style><div class="c"><div class="sun"></div><div class="h"><div class="h1">DAN PYNE</div><div class="h2">this week!</div><div class="rg">{rng(gigs)}</div></div>
{cut_img(s, 900, 860, 96)}<div class="L">{rows}</div><div class="ft">{social('#fff6e6','#ffd76a','700 28px Mont',4)}</div><div class="grain"></div></div>"""

# ======================= MONTHLY =======================
def monthly(s, gigs, style):
    month = s.get("month") or d(gigs[0]).strftime("%B")
    n = len(gigs); rh = min(100, int(700 / max(n, 1))); vf = min(46, int(rh * .5))
    if style == "marquee":
        bulbs = "".join(f'<i style="left:{x}px;top:18px"></i><i style="left:{x}px;bottom:18px"></i>' for x in range(30, 1060, 52)) + \
                "".join(f'<i style="top:{y}px;left:18px"></i><i style="top:{y}px;right:18px"></i>' for y in range(70, 1300, 52))
        rows = "".join(f'<div class="r" style="height:{rh}px"><b>{d(g).month}.{d(g).day}</b><div class="vv"><div class="vn" style="font-size:{vf}px">{e(g["venue"]).upper()}</div>'
                       f'<div class="vc">{d(g).strftime("%a").upper()} · {e(g["city"].split(",")[0]).upper()} · {e(g["time"])}</div></div></div>' for g in gigs)
        mfs = 210 if len(month) <= 6 else (170 if len(month) <= 8 else 150)
        return f"""<style>
.c{{background:radial-gradient(ellipse at 75% 35%,#3a1414 0%,#160808 55%,#0a0505 100%)}}
.bl i{{position:absolute;width:14px;height:14px;border-radius:50%;background:#ffe8a8;box-shadow:0 0 10px #ffcf6a,0 0 22px #ffb030}}
.inner{{position:absolute;inset:50px;border:3px solid rgba(255,200,100,.5)}}
.m{{position:absolute;left:84px;top:80px;font:400 {mfs}px/0.85 Anton;letter-spacing:4px}}
.sh2{{position:absolute;left:96px;top:{80+int(mfs*.8)}px;font:400 96px Kaushan;color:#fff;text-shadow:0 0 10px #ff5a5a,0 0 30px #ff2a2a}}
.cut{{filter:drop-shadow(0 0 40px rgba(255,120,80,.45)) drop-shadow(0 20px 40px rgba(0,0,0,.7))}}
.fd{{position:absolute;right:50px;bottom:50px;width:600px;height:500px;background:linear-gradient(180deg,rgba(10,5,5,0),rgba(10,5,5,.9))}}
.L{{position:absolute;left:84px;top:{380 if n<=6 else 350}px;width:520px;padding:20px 28px;background:rgba(10,5,5,.72);border:1px solid rgba(255,200,100,.35);border-radius:12px}}
.r{{display:flex;align-items:center;gap:22px;border-bottom:1px solid rgba(255,220,160,.15)}}.r:last-child{{border:0}}
.r b{{font:400 44px Anton;color:#ffcf6a;width:100px}}.vn{{font-family:Bebas;color:#fff;letter-spacing:2px;line-height:1;white-space:nowrap}}
.vc{{font:500 20px Oswald;color:#d9b9a0;letter-spacing:2px}}
.ty{{position:absolute;right:90px;bottom:170px;font:400 46px/1.1 Kaushan;color:#ffcf6a;text-align:right;transform:rotate(-4deg);text-shadow:0 2px 10px #000}}
.ft{{position:absolute;left:0;right:0;bottom:78px}}
</style><div class="c"><div class="inner"></div>{cut_img(s, 900, 860, 50)}<div class="fd"></div>
<div class="m gold">{e(month).upper()}</div><div class="sh2">Shows</div><div class="L">{rows}</div>
<div class="ty">Thank you for supporting<br>live music!</div><div class="ft">{social('#fff','#ffcf6a')}</div><div class="bl">{bulbs}</div><div class="grain"></div></div>"""
    rows = "".join(f'<div class="r" style="height:{rh}px"><div class="dt"><small>{d(g).strftime("%a").upper()}</small><b>{d(g).day}</b></div>'
                   f'<div class="vv"><div class="vn" style="font-size:{min(34,vf)}px">{e(g["venue"])}</div><div class="vc">{e(g["city"].split(",")[0]).upper()} · {e(g["time"])}</div></div></div>' for g in gigs)
    return f"""<style>
.c{{background:radial-gradient(ellipse at 65% 40%,#f6efe2,#e3d8c4)}}
.top{{position:absolute;left:60px;right:60px;top:40px;display:flex;justify-content:space-between;font:700 22px Mont;letter-spacing:6px;color:#1c2a3e}}.top b{{color:#c0602a}}
.mast{{position:absolute;left:0;right:0;top:66px;text-align:center;font:600 {300 if len(month)<=5 else (230 if len(month)<=7 else 190)}px/0.85 Playfair;color:#1c2a3e;letter-spacing:-4px}}
.cut{{filter:drop-shadow(0 20px 40px rgba(40,30,20,.35))}}
.L{{position:absolute;left:60px;top:{430 if n<=6 else 400}px;width:520px;padding:16px 26px;background:rgba(246,239,226,.9);border-left:8px solid #c0602a}}
.k{{font:800 22px Mont;letter-spacing:8px;color:#c0602a;margin-bottom:8px}}
.r{{display:flex;align-items:center;gap:20px;border-bottom:1px solid rgba(28,42,62,.18)}}.r:last-child{{border:0}}
.dt{{width:74px;text-align:center;color:#1c2a3e}}.dt small{{display:block;font:800 16px Mont;letter-spacing:3px;color:#c0602a}}.dt b{{font:700 44px/1 Playfair}}
.vn{{font-family:Playfair;font-weight:700;color:#1c2a3e;line-height:1.05;white-space:nowrap}}.vc{{font:700 17px Mont;letter-spacing:3px;color:#6b5a44}}
.ft{{position:absolute;left:0;right:0;bottom:0;height:96px;background:#1c2a3e;display:flex;align-items:center;justify-content:center}}
</style><div class="c"><div class="top"><span>DAN PYNE <b>LIVE</b></span><span>ACOUSTIC TOP 40</span></div><div class="mast">{e(month)}</div>
{cut_img(s, 1000, 790, 96)}<div class="L"><div class="k">ON STAGE THIS MONTH</div>{rows}</div>
<div class="ft">{social('#f6efe2','#e0884a','700 28px Mont',4)}</div><div class="grain" style="opacity:.22;mix-blend-mode:multiply"></div></div>"""

# ======================= BUILD =======================
def build(s):
    stem = pathlib.Path(s["photo"]).stem
    s["_photo"] = "file://" + str(PHOTOS / f"{stem}.jpg")
    cut = CUTS / f"{stem}.png"
    if not cut.exists(): raise SystemExit(f"missing cutout {cut}; run: python3 render.py --cutout {stem}")
    s["_cut"] = "file://" + str(cut)
    k, gigs = s["kind"], s["gigs"]
    if k == "solo":
        body = {"spotlight": solo_spotlight, "goldframe": solo_goldframe, "neon": solo_neon, "editorial": solo_editorial}[s["style"]](s, gigs[0]); W, H = 1080, 1350
    elif k == "story": body = story(s, gigs[0], s.get("style", "spotlight")); W, H = 1080, 1920
    elif k == "weekly": body = weekly(s, gigs, s["style"]); W, H = 1080, 1350
    elif k == "monthly": body = monthly(s, gigs, s["style"]); W, H = 1080, 1350
    else: raise SystemExit("unknown kind")
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{fontface()}{BASE % (W, H, GRAIN)}</style></head><body>{body}</body></html>", W, H

def render(spec_path, out):
    from playwright.sync_api import sync_playwright
    s = json.loads(pathlib.Path(spec_path).read_text())
    doc, W, H = build(s)
    tmp = pathlib.Path(out).with_suffix(".html"); tmp.write_text(doc)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + str(tmp.resolve())); pg.wait_for_timeout(500)
        pg.screenshot(path=out, type="png"); b.close()
    tmp.unlink()

def make_cutout(stem):
    """Cut Dan out of photos/<stem>.jpg -> cutouts/<stem>.png, fading the bottom. Needs: pip install rembg[cpu]"""
    from rembg import remove, new_session
    from PIL import Image
    import numpy as np
    im = Image.open(PHOTOS / f"{stem}.jpg")
    out = remove(im, session=new_session("u2net_human_seg"), post_process_mask=True)
    out = out.crop(out.getbbox()); w, h = out.size
    a = np.array(out.split()[-1]).astype(float); ys = np.arange(h) / h
    a *= np.clip((0.95 - ys) / 0.3, 0, 1)[:, None]
    out.putalpha(Image.fromarray(a.astype("uint8"))); out.crop(out.getbbox()).save(CUTS / f"{stem}.png")
    print("wrote", CUTS / f"{stem}.png", "- check it by eye before using")

if __name__ == "__main__":
    if sys.argv[1] == "--cutout": make_cutout(sys.argv[2])
    else: render(sys.argv[1], sys.argv[2])

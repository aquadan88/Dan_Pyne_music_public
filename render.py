#!/usr/bin/env python3
"""Render Dan Pyne gig graphics (feed 1080x1350, story 1080x1920) from a JSON spec.

Usage: python3 render.py spec.json out.png
Spec keys:
  kind:   solo | story | weekly | monthly
  style:  solo: amber | navy | bold | cream
          story: amber | navy
          weekly: anton | split
          monthly: darklist | creamlist
  photo:  file name in photos/ ; focus: CSS object-position (e.g. "50% 30%")
  gigs:   [{"date":"2026-11-14","venue":"The Wine Mill","city":"Peninsula, OH","time":"6-9 PM","address":"..."}]
  month:  "November" (monthly)
"""
import json, sys, html, datetime, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
PHOTOS = ROOT / "photos"
WEB = "DANPYNE.COM"
HANDLE = "@DANPYNEMUSIC"
TAG = "Acoustic Top 40 Hits"

def e(s): return html.escape(str(s))

def d(g): return datetime.date.fromisoformat(g["date"])

ICON = {
 "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>',
 "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v8h4v-8h3l1-4h-4V8z"/></svg>',
}
def ic(n, cls="ic"): return f'<span class="{cls}">{ICON[n]}</span>'

def fontface():
    f = lambda fam, file, w="100 900": f"@font-face{{font-family:'{fam}';src:url('file://{FONTS/file}');font-weight:{w};}}"
    return "".join([f("Bebas","BebasNeue-Regular.ttf"), f("Oswald","Oswald-VF.ttf"), f("Playfair","PlayfairDisplay-VF.ttf"),
        f("Vibes","GreatVibes-Regular.ttf"), f("Mont","Montserrat-VF.ttf"), f("Anton","Anton-Regular.ttf"),
        f("Kaushan","KaushanScript-Regular.ttf"), f("Corm","CormorantGaramond-VF.ttf")])

def bokeh(n=26, seed=7, colors=("255,190,90","255,160,60","255,215,140"), area=(0,100,0,100), size=(30,120)):
    import random
    r = random.Random(seed); out = []
    for _ in range(n):
        s = r.randint(*size); c = r.choice(colors); o = r.uniform(.18,.55)
        x = r.uniform(area[0],area[1]); y = r.uniform(area[2],area[3])
        out.append(f'<i style="position:absolute;left:{x}%;top:{y}%;width:{s}px;height:{s}px;border-radius:50%;'
                   f'background:radial-gradient(circle,rgba({c},{o}) 0%,rgba({c},{o*.6}) 55%,rgba({c},0) 72%);'
                   f'filter:blur({r.uniform(0,2.5):.1f}px)"></i>')
    return '<div class="bokeh">' + "".join(out) + "</div>"

def social_line(cls="social"):
    return f'<div class="{cls}">{ic("fb","si")}{ic("ig","si")}<b>{HANDLE}</b><span class="dot">|</span><b>{WEB}</b></div>'

BASE = """*{margin:0;padding:0;box-sizing:border-box}body{width:%dpx;height:%dpx;overflow:hidden}
.c{position:relative;width:100%%;height:100%%;overflow:hidden}.ph{position:absolute;object-fit:cover}
.bokeh{position:absolute;inset:0;pointer-events:none}.ic svg,.si svg{width:100%%;height:100%%;display:block}
.ic{display:inline-block;width:46px;height:46px;flex:none}.si{display:inline-block;width:34px;height:34px;flex:none}"""

# ---------------- SOLO (feed) ----------------
def solo_amber(s, g):
    dt = d(g)
    return f"""<style>
.ph{{left:0;top:0;width:100%;height:60%;object-position:{s.get('focus','50% 25%')};filter:saturate(1.15) contrast(1.05) sepia(.25)}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(30,14,4,.0) 30%,rgba(40,18,6,.8) 50%,#22100a 60%,#22100a 100%)}}
.grain{{position:absolute;left:0;right:0;bottom:0;height:46%;opacity:.25;background:repeating-linear-gradient(90deg,rgba(255,200,140,.08) 0 3px,rgba(0,0,0,.08) 3px 9px,rgba(255,200,140,.04) 9px 15px)}}
.t{{position:absolute;left:0;right:0;bottom:70px;text-align:center;color:#f4ead8}}
.name{{font:400 150px/0.9 Bebas;letter-spacing:4px;text-shadow:0 4px 18px rgba(0,0,0,.6)}}
.tag{{font:400 60px Kaushan;color:#f2b33d;margin:4px 0 22px;display:flex;align-items:center;justify-content:center;gap:22px}}
.tag:before,.tag:after{{content:"";width:70px;height:3px;background:#e07b1f}}
.date{{display:inline-block;border:4px solid #e07b1f;padding:6px 34px 0;font:400 108px/1 Bebas;letter-spacing:2px}}
.date em{{font-style:normal;color:#fff}}
.live{{font:600 40px Oswald;color:#f08a24;letter-spacing:4px;margin-top:20px}}
.venue{{font:400 96px/1 Bebas;letter-spacing:2px;margin-top:4px}}
.city{{font:600 36px Oswald;color:#f08a24;letter-spacing:3px}}
.time{{font:600 74px Oswald;color:#f6c343;display:flex;align-items:center;justify-content:center;gap:18px;margin-top:14px}}
.time .ic{{width:66px;height:66px}}
.social{{font:600 34px Oswald;color:#f4ead8;display:flex;gap:12px;align-items:center;justify-content:center;margin-top:24px;letter-spacing:1px}}
.social .si{{color:#f08a24}}.dot{{color:#f08a24;margin:0 6px}}
</style><div class="c" style="background:#22100a"><img class="ph" src="{s['_photo']}">
{bokeh(22,3,area=(55,100,0,40))}<div class="shade"></div><div class="grain"></div>{bokeh(14,9,area=(70,100,55,95),size=(40,90))}
<div class="t"><div class="name">DAN PYNE</div><div class="tag">{TAG}</div>
<div class="date">{dt.strftime('%b').upper()} <em>{dt.day}</em></div>
<div class="live">— LIVE AT —</div><div class="venue">{e(g['venue']).upper()}</div><div class="city">{e(g['city']).upper()}</div>
<div class="time">{ic('clock')}{e(g['time'])}</div>{social_line()}</div></div>"""

def solo_navy(s, g):
    dt = d(g)
    return f"""<style>
.c{{background:#0e1726}}
.ph{{right:0;top:0;width:56%;height:100%;object-position:{s.get('focus','50% 30%')};filter:contrast(1.05)}}
.fade{{position:absolute;left:44%;top:0;width:340px;height:100%;background:linear-gradient(90deg,#0e1726,rgba(14,23,38,0))}}
.frame{{position:absolute;inset:28px;border:2px solid rgba(201,163,92,.6)}}
.L{{position:absolute;left:70px;top:90px;width:470px;color:#e9dcc0}}
.n1{{font:500 150px/0.85 Playfair;color:#efe3c6;letter-spacing:2px}}
.n2{{font:400 118px/0.9 Vibes;color:#c9a35c;margin:-6px 0 0 40px}}
.live{{font:600 40px Mont;letter-spacing:12px;margin-top:40px;color:#efe3c6}}
.sub{{font:500 22px Mont;letter-spacing:6px;color:#c9a35c;margin-top:8px}}
.box{{border:2px solid #c9a35c;margin-top:50px;padding:34px 20px;text-align:center}}
.box .v{{font:500 64px/1.05 Playfair;color:#efe3c6}}.box .cty{{font:600 22px Mont;letter-spacing:5px;color:#c9a35c;margin-top:14px}}
.row{{display:flex;align-items:center;gap:22px;margin-top:40px;color:#c9a35c}}
.row .ic{{width:76px;height:76px;padding:16px;border:2px solid #c9a35c;border-radius:50%}}
.row .a{{font:600 30px Mont;letter-spacing:5px;color:#c9a35c}}.row .b{{font:500 52px/1 Playfair;color:#efe3c6;white-space:nowrap}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:110px;background:#efe6d4;display:flex;align-items:center;justify-content:center}}
.social{{font:600 30px Mont;color:#0e1726;display:flex;gap:12px;align-items:center;letter-spacing:2px}}.social .si{{color:#0e1726}}.dot{{color:#c9a35c;margin:0 10px}}
.tagl{{position:absolute;left:0;right:0;bottom:122px;text-align:center;font:600 22px Mont;letter-spacing:8px;color:#c9a35c}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="fade"></div><div class="frame"></div>
<div class="L"><div class="n1">DAN</div><div class="n2">Pyne</div><div class="live">LIVE</div><div class="sub">ACOUSTIC TOP 40 HITS</div>
<div class="box"><div class="v">{e(g['venue'])}</div><div class="cty">{e(g['city']).upper()}</div></div>
<div class="row">{ic('cal')}<div><div class="a">{dt.strftime('%A').upper()}</div><div class="b">{dt.strftime('%B').upper()} {dt.day}</div></div></div>
<div class="row">{ic('clock')}<div class="b">{e(g['time'])}</div></div></div>
<div class="tagl">GREAT MUSIC · GOOD VIBES</div><div class="foot">{social_line()}</div></div>"""

def solo_bold(s, g):
    dt = d(g)
    addr = g.get("address") or g["city"]
    return f"""<style>
.c{{background:#1a1530}}
.ph{{left:0;top:0;width:100%;height:100%;object-position:{s.get('focus','30% 40%')};filter:sepia(.5) saturate(1.6) hue-rotate(-12deg) contrast(1.1) brightness(.9)}}
.tint{{position:absolute;inset:0;background:linear-gradient(160deg,rgba(80,60,160,.55) 0%,rgba(40,30,80,.2) 35%,rgba(20,14,40,.2) 55%,rgba(16,10,30,.92) 78%)}}
.top{{position:absolute;top:60px;right:60px;text-align:right}}
.nm{{font:400 210px/0.86 Anton;letter-spacing:2px;text-shadow:0 6px 0 rgba(0,0,0,.35)}}.nm span{{color:#f7c815}}.nm b{{font-weight:400;color:#fff}}
.tg{{font:400 64px Anton;color:#f7c815;transform:skewX(-8deg);margin-top:16px;letter-spacing:1px}}
.bot{{position:absolute;left:60px;right:60px;bottom:60px;color:#fff}}
.plate{{background:linear-gradient(#8a4b22,#5e2f12);border:4px solid #b66d36;border-radius:10px;padding:20px 30px;text-align:center;font:400 82px/1 Anton;letter-spacing:2px;box-shadow:0 10px 30px rgba(0,0,0,.5)}}
.bar{{margin-top:22px;background:linear-gradient(90deg,rgba(90,48,18,.0),rgba(90,48,18,.95) 12%,rgba(90,48,18,.95) 88%,rgba(90,48,18,0));text-align:center;font:400 70px Anton;color:#f7c815;padding:10px 0;letter-spacing:1px}}
.rows{{margin-top:18px}}.r{{display:flex;align-items:center;gap:24px;font:400 54px Anton;padding:10px 40px;border-bottom:2px solid rgba(247,200,21,.35)}}
.r .ic{{width:58px;height:58px;color:#f7c815}}
.web{{text-align:center;font:400 54px Anton;margin-top:18px;letter-spacing:2px}}.web small{{font:400 40px Anton;color:#f7c815;margin-left:22px}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="tint"></div>{bokeh(30,11,area=(0,100,30,75),size=(30,100))}
<div class="top"><div class="nm"><b>DAN</b> <span>PYNE</span></div><div class="tg">ACOUSTIC TOP 40 HITS!</div></div>
<div class="bot"><div class="plate">{e(g['venue']).upper()}</div><div class="bar">{dt.strftime('%A, %B').upper()} {dt.day}</div>
<div class="rows"><div class="r">{ic('clock')}{e(g['time'])}</div><div class="r">{ic('pin')}{e(addr).upper()}</div></div>
<div class="web">{WEB}<small>{HANDLE}</small></div></div></div>"""

def solo_cream(s, g):
    dt = d(g)
    return f"""<style>
.c{{background:#ece4d6}}
.ph{{right:0;top:0;width:62%;height:62%;object-position:{s.get('focus','50% 25%')};}}
.pfade{{position:absolute;right:0;top:0;width:62%;height:62%;background:linear-gradient(90deg,#ece4d6 0%,rgba(236,228,214,0) 30%)}}
.L{{position:absolute;left:70px;top:80px;width:480px}}
.n1{{font:400 250px/0.8 Bebas;color:#1d2a3d;letter-spacing:4px}}.n2{{font:400 118px/0.9 Bebas;color:#8b6f4e;letter-spacing:10px;margin-top:10px}}
.ln{{display:flex;align-items:center;gap:16px;color:#1d2a3d;margin:22px 0}}.ln i{{flex:1;height:2px;background:#1d2a3d}}.ln b{{font-size:30px}}
.sub{{font:600 30px Mont;color:#1d2a3d;letter-spacing:6px}}
.band{{position:absolute;left:0;right:0;top:62%;height:calc(38% - 110px);background:#1c2a3e;display:flex;align-items:center;color:#efe6d4}}
.v{{width:46%;text-align:center;padding:0 30px}}.v .vn{{font:500 70px/1.05 Playfair}}.v .vc{{font:600 22px Mont;letter-spacing:6px;color:#c9a35c;margin-top:14px}}
.sep{{width:2px;height:62%;background:#c9a35c}}
.det{{flex:1;padding-left:50px}}.det .r{{display:flex;align-items:center;gap:22px;font:700 44px Mont;margin:14px 0;letter-spacing:1px}}
.det .ic{{width:58px;height:58px;color:#c9a35c;padding:10px;border:2px solid #c9a35c;border-radius:50%}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:110px;background:#ece4d6;display:flex;align-items:center;justify-content:center}}
.social{{font:600 30px Mont;color:#1d2a3d;display:flex;gap:12px;align-items:center;letter-spacing:4px}}.dot{{color:#8b6f4e;margin:0 10px}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="pfade"></div>
<div class="L"><div class="n1">DAN</div><div class="n2">PYNE</div><div class="ln"><i></i><b>★</b><i></i></div><div class="sub">LIVE ACOUSTIC<br>TOP 40 HITS</div></div>
<div class="band"><div class="v"><div class="vn">{e(g['venue'])}</div><div class="vc">{e(g['city']).upper()}</div></div><div class="sep"></div>
<div class="det"><div class="r">{ic('cal')}{dt.strftime('%a, %b').upper()} {dt.day}</div><div class="r">{ic('clock')}{e(g['time'])}</div></div></div>
<div class="foot">{social_line()}</div></div>"""

# ---------------- STORY (day-of) ----------------
def story(s, g, theme):
    pal = {"amber": ("#22100a","#f2b33d","#f08a24","#f4ead8","sepia(.25) saturate(1.15)"),
           "navy":  ("#0e1726","#c9a35c","#c9a35c","#efe3c6","contrast(1.05)")}[theme]
    bg, acc, acc2, tx, flt = pal
    addr = g.get("address") or g["city"]
    return f"""<style>
.ph{{inset:0;width:100%;height:100%;object-position:{s.get('focus','50% 30%')};filter:{flt}}}
.sh{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 42%,{bg}ee 62%,{bg} 100%)}}
.top{{position:absolute;top:130px;left:0;right:0;text-align:center;color:{tx}}}
.tn{{font:400 230px/0.85 Anton;letter-spacing:6px;text-shadow:0 6px 24px rgba(0,0,0,.6)}}
.tg{{font:400 64px Kaushan;color:{acc}}}
.b{{position:absolute;left:70px;right:70px;bottom:300px;text-align:center;color:{tx}}}
.nm{{font:400 120px/0.9 Bebas;letter-spacing:6px}}.at{{font:600 38px Oswald;letter-spacing:8px;color:{acc2};margin:18px 0 6px}}
.v{{font:400 110px/0.95 Bebas;letter-spacing:2px}}.r{{display:flex;justify-content:center;align-items:center;gap:20px;font:600 58px Oswald;color:{acc};margin-top:22px}}
.r .ic{{width:60px;height:60px}}.ad{{font:500 34px Oswald;letter-spacing:2px;margin-top:10px;display:flex;justify-content:center;gap:12px;align-items:center}}.ad .ic{{width:40px;height:40px;color:{acc2}}}
.h{{font:600 34px Oswald;letter-spacing:3px;margin-top:40px;color:{tx};opacity:.9}}
</style><div class="c" style="background:{bg}"><img class="ph" src="{s['_photo']}"><div class="sh"></div>
{bokeh(16,5,area=(0,100,50,90),size=(30,90)) if theme=='amber' else ''}
<div class="top"><div class="tn">TONIGHT</div><div class="tg">live acoustic music</div></div>
<div class="b"><div class="nm">DAN PYNE</div><div class="at">LIVE AT</div><div class="v">{e(g['venue']).upper()}</div>
<div class="r">{ic('clock')}{e(g['time'])}</div><div class="ad">{ic('pin')}{e(addr)}</div><div class="h">{HANDLE} · {WEB}</div></div></div>"""

# ---------------- WEEKLY (short, bold) ----------------
def weekly(s, gigs, style):
    rows = "".join(f'<div class="r"><div class="dy"><b>{d(g).strftime("%a").upper()}</b><small>{d(g).month}.{d(g).day}</small></div>'
                   f'<div class="vv"><div class="vn">{e(g["venue"]).upper()}</div><div class="vc">{e(g["city"]).upper()} · {e(g["time"])}</div></div></div>' for g in gigs)
    first, last = d(gigs[0]), d(gigs[-1])
    rng = f"{first.strftime('%b').upper()} {first.day} – {last.day}" if first.month == last.month else f"{first.strftime('%b').upper()} {first.day} – {last.strftime('%b').upper()} {last.day}"
    if style == "anton":
        return f"""<style>
.c{{background:#0d0d0f}}.ph{{right:-60px;top:0;width:62%;height:100%;object-position:{s.get('focus','50% 30%')};filter:grayscale(1) contrast(1.15) brightness(.8)}}
.fd{{position:absolute;inset:0;background:linear-gradient(90deg,#0d0d0f 40%,rgba(13,13,15,.6) 62%,rgba(13,13,15,.15) 100%)}}
.H{{position:absolute;left:70px;top:80px;color:#fff}}.h1{{font:400 200px/0.82 Anton;letter-spacing:2px}}
.h2{{font:400 120px/1 Kaushan;color:#f7c815;margin:-30px 0 0 120px;transform:rotate(-4deg)}}
.rg{{font:600 34px Oswald;letter-spacing:8px;color:#bbb;margin-top:10px}}
.L{{position:absolute;left:70px;right:70px;top:560px}}
.r{{display:flex;align-items:center;gap:34px;padding:22px 0;border-bottom:2px solid rgba(247,200,21,.3)}}
.dy{{width:150px;background:#f7c815;color:#0d0d0f;text-align:center;padding:10px 0;border-radius:6px}}.dy b{{display:block;font:400 64px/1 Anton}}.dy small{{font:700 28px Oswald}}
.vn{{font:400 70px/1 Anton;color:#fff;letter-spacing:1px}}.vc{{font:600 32px Oswald;color:#f7c815;letter-spacing:3px;margin-top:6px}}
.foot{{position:absolute;left:70px;right:70px;bottom:60px;display:flex;justify-content:space-between;align-items:center;color:#fff;font:400 44px Anton;letter-spacing:2px}}
.social{{font:600 30px Oswald;color:#fff;display:flex;gap:10px;align-items:center;letter-spacing:2px}}.social .si{{color:#f7c815}}.dot{{color:#f7c815;margin:0 8px}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="fd"></div>
<div class="H"><div class="h1">THIS<br>WEEK</div><div class="h2">live!</div><div class="rg">DAN PYNE · {rng}</div></div>
<div class="L">{rows}</div><div class="foot">{social_line()}</div></div>"""
    # split: top photo band, bold list under
    return f"""<style>
.c{{background:#f3ece0}}.ph{{left:0;top:0;width:100%;height:42%;object-position:{s.get('focus','50% 30%')};filter:sepia(.2) saturate(1.1)}}
.ov{{position:absolute;left:0;top:0;width:100%;height:42%;background:linear-gradient(180deg,rgba(20,30,48,.1),rgba(20,30,48,.85))}}
.H{{position:absolute;left:70px;right:70px;top:300px;color:#fff;display:flex;justify-content:space-between;align-items:flex-end}}
.h1{{font:400 150px/0.85 Bebas;letter-spacing:4px}}.h1 span{{color:#e9a23b}}.rg{{font:700 34px Mont;letter-spacing:4px;text-align:right}}
.L{{position:absolute;left:70px;right:70px;top:46%}}
.r{{display:flex;align-items:center;gap:30px;padding:20px 0;border-bottom:3px solid #1c2a3e}}
.dy{{width:140px;text-align:center;color:#1c2a3e}}.dy b{{display:block;font:400 72px/0.9 Bebas;letter-spacing:2px}}.dy small{{font:700 26px Mont;color:#e07b1f}}
.vn{{font:400 72px/1 Bebas;color:#1c2a3e;letter-spacing:2px}}.vc{{font:600 28px Mont;color:#8b6f4e;letter-spacing:3px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:110px;background:#1c2a3e;display:flex;align-items:center;justify-content:center}}
.social{{font:600 30px Mont;color:#efe6d4;display:flex;gap:12px;align-items:center;letter-spacing:3px}}.social .si{{color:#e9a23b}}.dot{{color:#e9a23b;margin:0 10px}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="ov"></div>
<div class="H"><div class="h1">DAN PYNE<br><span>THIS WEEK</span></div><div class="rg">{rng}</div></div>
<div class="L">{rows}</div><div class="foot">{social_line()}</div></div>"""

# ---------------- MONTHLY ----------------
def monthly(s, gigs, style):
    month = s.get("month") or d(gigs[0]).strftime("%B")
    n = len(gigs)
    rowh = min(96, int(740 / max(n, 1)))
    fs = min(52, int(rowh * .55))
    if style == "darklist":
        msz = 190 if len(month) <= 6 else 150
        fs2 = min(fs, 44)
        rows = "".join(f'<div class="r" style="height:{rowh}px"><b>{d(g).month}.{d(g).day}</b><div class="vv"><div class="vn" style="font-size:{fs2}px;white-space:nowrap">{e(g["venue"]).upper()}</div>'
                       f'<div class="tm">{e(g["city"].split(",")[0]).upper()} · {e(g["time"])}</div></div></div>' for g in gigs)
        return f"""<style>
.c{{background:#111}}.ph{{right:0;top:0;width:58%;height:100%;object-position:{s.get('focus','50% 30%')};filter:contrast(1.05) saturate(.95)}}
.p{{position:absolute;left:0;top:0;width:62%;height:100%;background:linear-gradient(90deg,#0e0e0e 80%,rgba(14,14,14,0))}}
.H{{position:absolute;left:60px;top:60px;color:#f2f2f2}}.m{{font:400 {msz}px/0.82 Bebas;letter-spacing:4px}}.s{{font:400 100px/1 Kaushan;color:#e9c08a;margin:-34px 0 0 70px}}
.u{{width:300px;height:5px;background:#e9c08a;margin:6px 0 0 70px;border-radius:3px}}
.L{{position:absolute;left:60px;top:380px;width:560px}}
.r{{display:flex;align-items:center;gap:22px;border-bottom:1px solid rgba(255,255,255,.18);color:#f2f2f2}}
.r b{{font:400 46px Bebas;color:#e9c08a;width:100px;letter-spacing:1px}}.vn{{font-family:Bebas;letter-spacing:2px;flex:1;line-height:1}}
.vv{{flex:1}}.tm{{font:500 22px Oswald;color:#aaa;letter-spacing:2px}}
.tk{{position:absolute;right:50px;bottom:150px;width:400px;padding:22px 26px;background:rgba(14,14,14,.8);border:2px solid #e9c08a;transform:rotate(-3deg);
 font:400 44px/1.1 Kaushan;color:#e9c08a;text-align:center}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:96px;background:#0e0e0e;border-top:2px solid #e9c08a;display:flex;align-items:center;justify-content:center}}
.social{{font:600 28px Oswald;color:#f2f2f2;display:flex;gap:12px;align-items:center;letter-spacing:6px}}.social .si{{color:#e9c08a}}.dot{{color:#e9c08a;margin:0 10px}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="p"></div>
<div class="H"><div class="m">{e(month).upper()}</div><div class="s">Shows</div><div class="u"></div></div>
<div class="L">{rows}</div><div class="tk">Thank you for supporting live music!</div><div class="foot">{social_line()}</div></div>"""
    rows = "".join(f'<div class="r" style="height:{rowh}px"><div class="dt"><small>{d(g).strftime("%b").upper()}</small><b>{d(g).day}</b></div>'
                   f'<div><div class="vn" style="font-size:{min(32,fs)}px">{e(g["venue"]).upper()}</div><div class="vc">{e(g["city"]).upper()}</div><div class="tm">{e(g["time"])}</div></div></div>' for g in gigs)
    return f"""<style>
.c{{background:#efe8dc}}.ph{{right:0;top:0;width:50%;height:100%;object-position:{s.get('focus','50% 30%')}}}
.fd{{position:absolute;right:0;top:0;width:50%;height:100%;background:linear-gradient(90deg,#efe8dc 0%,rgba(239,232,220,.4) 25%,rgba(239,232,220,0) 45%)}}
.H{{position:absolute;left:60px;top:46px;width:540px;text-align:center}}.n1{{font:500 120px/0.85 Playfair;color:#1c2a3e}}
.n2{{font:600 44px Mont;letter-spacing:22px;color:#8b6f4e;margin-top:6px}}
.ln{{display:flex;align-items:center;gap:16px;margin-top:22px;font:700 30px Mont;letter-spacing:6px;color:#1c2a3e}}.ln i{{flex:1;height:2px;background:#1c2a3e}}
.L{{position:absolute;left:60px;top:440px;width:540px}}
.r{{display:flex;align-items:center;gap:24px;border-bottom:1px solid rgba(28,42,62,.25)}}
.dt{{width:90px;height:calc(100% - 12px);max-height:84px;background:#1c2a3e;color:#efe6d4;text-align:center;display:flex;flex-direction:column;justify-content:center}}
.dt small{{font:700 16px Mont;letter-spacing:2px}}.dt b{{font:700 36px/1 Mont}}
.vn{{font-family:Mont;font-weight:800;color:#1c2a3e;letter-spacing:1px;line-height:1.05;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:420px}}.vc{{font:600 17px Mont;color:#555;letter-spacing:2px}}.tm{{font:700 17px Mont;color:#b07a2a}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:96px;background:#efe8dc;border-top:2px solid #1c2a3e;display:flex;align-items:center;justify-content:center}}
.social{{font:600 28px Mont;color:#1c2a3e;display:flex;gap:12px;align-items:center;letter-spacing:4px}}.dot{{color:#8b6f4e;margin:0 10px}}
.sig{{position:absolute;right:60px;bottom:120px;font:400 90px Vibes;color:#f3e7c9;text-shadow:0 2px 12px rgba(0,0,0,.6)}}
</style><div class="c"><img class="ph" src="{s['_photo']}"><div class="fd"></div>
<div class="H"><div class="n1">DAN PYNE</div><div class="n2">LIVE</div><div class="ln"><i></i>IN {e(month).upper()}<i></i></div></div>
<div class="L">{rows}</div><div class="sig">Dan Pyne</div><div class="foot">{social_line()}</div></div>"""

def build(s):
    s["_photo"] = "file://" + str(PHOTOS / s["photo"])
    k = s["kind"]; gigs = s["gigs"]
    if k == "solo":
        body = {"amber": solo_amber, "navy": solo_navy, "bold": solo_bold, "cream": solo_cream}[s["style"]](s, gigs[0]); W, H = 1080, 1350
    elif k == "story":
        body = story(s, gigs[0], s.get("style", "amber")); W, H = 1080, 1920
    elif k == "weekly":
        body = weekly(s, gigs, s["style"]); W, H = 1080, 1350
    elif k == "monthly":
        body = monthly(s, gigs, s["style"]); W, H = 1080, 1350
    else:
        raise SystemExit("unknown kind")
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{fontface()}{BASE % (W, H)}</style></head><body>{body}</body></html>", W, H

def render(spec_path, out):
    s = json.loads(pathlib.Path(spec_path).read_text())
    doc, W, H = build(s)
    tmp = pathlib.Path(out).with_suffix(".html"); tmp.write_text(doc)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + str(tmp.resolve())); pg.wait_for_timeout(400)
        pg.screenshot(path=out, type="png"); b.close()
    tmp.unlink()

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
"""Génère les illustrations SVG du site (site/img/). Bibliothèque standard seulement.

Usage : python3 -I scripts/illustrations.py
Tout est dessiné ici, sans image ni ressource externe ; les dégradés sont locaux (url(#…)).
"""
import math
import os
import random

SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "img")


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def pol(cx, cy, r, a):
    t = math.radians(a)
    return cx + r * math.cos(t), cy + r * math.sin(t)


def petale(cx, cy, a, r0, r1, larg, fill, stroke, extra=""):
    """Pétale en amande, de r0 à r1 du centre, orienté selon l'angle a (degrés)."""
    x0, y0 = pol(cx, cy, r0, a)
    x1, y1 = pol(cx, cy, r1, a)
    m = (r0 + r1) / 2
    xg, yg = pol(cx, cy, m, a - larg)
    xd, yd = pol(cx, cy, m, a + larg)
    xg2, yg2 = pol(cx, cy, r1 * 0.98, a - larg * 0.45)
    xd2, yd2 = pol(cx, cy, r1 * 0.98, a + larg * 0.45)
    return (f'<path d="M{f(x0)} {f(y0)} C{f(xg)} {f(yg)} {f(xg2)} {f(yg2)} {f(x1)} {f(y1)} '
            f'C{f(xd2)} {f(yd2)} {f(xd)} {f(yd)} {f(x0)} {f(y0)}Z" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="1.2" {extra}/>')


def fleur(taille=400, detail=True, titre="", ident="fl"):
    random.seed(7)
    c = taille / 2
    k = taille / 400
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {taille} {taille}" role="img" aria-labelledby="t-{ident}">')
    o.append(f'<title id="t-{ident}">{titre}</title>')
    o.append(f'''<defs>
<radialGradient id="{ident}-pet" cx="50%" cy="50%" r="50%">
<stop offset="0" stop-color="#f6f1fb"/><stop offset="1" stop-color="#dccdf0"/></radialGradient>
<radialGradient id="{ident}-sep" cx="50%" cy="50%" r="50%">
<stop offset="0" stop-color="#eef3e6"/><stop offset="1" stop-color="#c6d8b4"/></radialGradient>
<radialGradient id="{ident}-coeur" cx="50%" cy="50%" r="50%">
<stop offset="0" stop-color="#5b2a86"/><stop offset="1" stop-color="#2a1440"/></radialGradient>
<radialGradient id="{ident}-ova" cx="40%" cy="35%" r="70%">
<stop offset="0" stop-color="#b9d98a"/><stop offset="1" stop-color="#5f8a3a"/></radialGradient>
</defs>''')
    # Sépales (derrière), puis pétales décalés de 36°.
    for i in range(5):
        a = -90 + 36 + i * 72
        o.append(petale(c, c, a, 20 * k, 178 * k, 19, f"url(#{ident}-sep)", "#8fae74"))
        if detail:
            x0, y0 = pol(c, c, 40 * k, a)
            x1, y1 = pol(c, c, 165 * k, a)
            o.append(f'<path d="M{f(x0)} {f(y0)} L{f(x1)} {f(y1)}" stroke="#9fbb86" stroke-width="{f(1.4*k)}" fill="none"/>')
    for i in range(5):
        a = -90 + i * 72
        o.append(petale(c, c, a, 20 * k, 170 * k, 19, f"url(#{ident}-pet)", "#b9a3d6"))
        if detail:
            for d in (-4, 0, 4):
                x0, y0 = pol(c, c, 50 * k, a + d * 0.6)
                x1, y1 = pol(c, c, 150 * k, a + d)
                o.append(f'<path d="M{f(x0)} {f(y0)} L{f(x1)} {f(y1)}" stroke="#cbb8e4" stroke-width="{f(0.9*k)}" fill="none"/>')
    # Couronne : filaments en trois bandes (violet foncé, blanc, violet-bleu), légèrement ondulés.
    n = 96 if detail else 48
    o.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(36*k)}" fill="url(#{ident}-coeur)"/>')
    for i in range(n):
        a = i * 360 / n + random.uniform(-1.2, 1.2)
        r_fin = (128 if i % 2 == 0 else 118) * k + random.uniform(-4, 4) * k
        bandes = [(30 * k, 58 * k, "#3b1a5c"), (58 * k, 74 * k, "#fbf7ff"), (74 * k, r_fin, "#6a4fc2")]
        for r0, r1, coul in bandes:
            ondule = 5 * math.sin(i * 1.7)
            x0, y0 = pol(c, c, r0, a)
            xm, ym = pol(c, c, (r0 + r1) / 2, a + ondule * 0.25)
            x1, y1 = pol(c, c, r1, a + ondule * 0.1)
            o.append(f'<path d="M{f(x0)} {f(y0)} Q{f(xm)} {f(ym)} {f(x1)} {f(y1)}" stroke="{coul}" '
                     f'stroke-width="{f((1.6 if detail else 2.6)*k)}" stroke-linecap="round" fill="none"/>')
    # Rangée intérieure courte (opercule).
    for i in range(48 if detail else 24):
        a = i * 7.5
        x0, y0 = pol(c, c, 18 * k, a)
        x1, y1 = pol(c, c, 32 * k, a)
        o.append(f'<path d="M{f(x0)} {f(y0)} L{f(x1)} {f(y1)}" stroke="#d9c6f0" stroke-width="{f(1.1*k)}" stroke-linecap="round"/>')
    # Androgynophore, étamines (5) et anthères.
    o.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(16*k)}" fill="#7da35a" stroke="#4d7232" stroke-width="{f(1*k)}"/>')
    for i in range(5):
        a = -90 + 36 + i * 72
        x1, y1 = pol(c, c, 62 * k, a)
        o.append(f'<path d="M{f(c)} {f(c)} L{f(x1)} {f(y1)}" stroke="#a6c77a" stroke-width="{f(5*k)}" stroke-linecap="round"/>')
        o.append(f'<ellipse cx="{f(x1)}" cy="{f(y1)}" rx="{f(15*k)}" ry="{f(6.5*k)}" transform="rotate({f(a+90)} {f(x1)} {f(y1)})" '
                 f'fill="#e9c24a" stroke="#a9852a" stroke-width="{f(1*k)}"/>')
    # Ovaire et trois styles à stigmate en tête.
    o.append(f'<ellipse cx="{f(c)}" cy="{f(c)}" rx="{f(13*k)}" ry="{f(13*k)}" fill="url(#{ident}-ova)" stroke="#4d7232" stroke-width="{f(1*k)}"/>')
    for i in range(3):
        a = -90 + i * 120
        x1, y1 = pol(c, c, 46 * k, a)
        xm, ym = pol(c, c, 26 * k, a + 14)
        o.append(f'<path d="M{f(c)} {f(c)} Q{f(xm)} {f(ym)} {f(x1)} {f(y1)}" stroke="#6b2f5e" stroke-width="{f(4*k)}" stroke-linecap="round" fill="none"/>')
        o.append(f'<circle cx="{f(x1)}" cy="{f(y1)}" r="{f(7*k)}" fill="#7a3a6b" stroke="#4a1f40" stroke-width="{f(1*k)}"/>')
    o.append("</svg>")
    return "\n".join(o)


def feuille(x, y, a, s, coul="#3f7a45", nerv="#a9cf95"):
    """Feuille à trois lobes, base en (x, y), orientée selon a (degrés), échelle s."""
    lobes = []
    for da, l in ((0, 1.0), (-48, 0.82), (48, 0.82)):
        ang = a + da
        L = 70 * s * l
        x1, y1 = pol(x, y, L, ang)
        c1g = pol(x, y, L * 0.30, ang - 34)
        c2g = pol(x, y, L * 0.80, ang - 20)
        c1d = pol(x, y, L * 0.80, ang + 20)
        c2d = pol(x, y, L * 0.30, ang + 34)
        lobes.append(f'M{f(x)} {f(y)} C{f(c1g[0])} {f(c1g[1])} {f(c2g[0])} {f(c2g[1])} {f(x1)} {f(y1)} '
                     f'C{f(c1d[0])} {f(c1d[1])} {f(c2d[0])} {f(c2d[1])} {f(x)} {f(y)}Z')
    out = [f'<path d="{" ".join(lobes)}" fill="{coul}" stroke="#244a2a" stroke-width="1"/>']
    for da, l in ((0, 0.9), (-42, 0.7), (42, 0.7)):
        x1, y1 = pol(x, y, 70 * s * l, a + da)
        out.append(f'<path d="M{f(x)} {f(y)} L{f(x1)} {f(y1)}" stroke="{nerv}" stroke-width="1.2" fill="none"/>')
    return "\n".join(out)


def vrille(x, y, s, sens=1):
    """Vrille : tige courbe qui finit en spirale."""
    pts = []
    for i in range(0, 220):
        t = i / 219
        if t < 0.45:
            u = t / 0.45
            px, py = x + sens * 60 * s * u, y - 40 * s * math.sin(u * math.pi / 2)
        else:
            u = (t - 0.45) / 0.55
            ang = u * 3.2 * math.pi
            r = 18 * s * (1 - u * 0.85)
            cx0, cy0 = x + sens * 60 * s, y - 40 * s + 18 * s
            px, py = cx0 + sens * r * math.sin(ang), cy0 - r * math.cos(ang)
        pts.append(f"{f(px)} {f(py)}")
    return f'<path d="M{" L".join(pts)}" stroke="#5f8a3a" stroke-width="2" fill="none" stroke-linecap="round"/>'


def plante():
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" aria-labelledby="t-plante">',
         '<title id="t-plante">Tige grimpante de passiflore avec des feuilles à trois lobes, des vrilles enroulées en spirale et un bouton floral</title>',
         '<defs><linearGradient id="pl-tige" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4d7232"/><stop offset="1" stop-color="#6f9a45"/></linearGradient></defs>']
    o.append('<path d="M10 260 C 90 230, 120 120, 200 140 S 330 60, 392 40" stroke="url(#pl-tige)" stroke-width="6" fill="none" stroke-linecap="round"/>')
    o.append(feuille(78, 236, -120, 0.95))
    o.append(feuille(150, 150, -75, 1.0, "#467f4b"))
    o.append(feuille(250, 118, 75, 0.9, "#3a7040"))
    o.append(feuille(330, 72, -100, 0.75, "#4c8550"))
    o.append(vrille(118, 190, 0.9, 1))
    o.append(vrille(214, 138, 0.8, 1))
    o.append(vrille(300, 86, 0.7, -1))
    # Bouton floral
    o.append('<path d="M372 46 q6 -14 2 -26" stroke="#5f8a3a" stroke-width="3" fill="none"/>')
    o.append('<ellipse cx="373" cy="14" rx="9" ry="13" fill="#c6d8b4" stroke="#6f9a45" stroke-width="1.2"/>')
    o.append('<path d="M366 18 q7 -18 14 0" stroke="#8fae74" stroke-width="1" fill="none"/>')
    o.append("</svg>")
    return "\n".join(o)


def fruit():
    random.seed(3)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 260" role="img" aria-labelledby="t-fruit">',
         '<title id="t-fruit">Fruit de la passion entier, violet et légèrement ridé, à côté d\'une moitié coupée montrant les graines sombres entourées de pulpe jaune</title>',
         '''<defs>
<radialGradient id="fr-peau" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#8a5bb0"/><stop offset="0.6" stop-color="#5b2a6e"/><stop offset="1" stop-color="#2f1238"/></radialGradient>
<radialGradient id="fr-pulpe" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#ffd45c"/><stop offset="1" stop-color="#f0a21a"/></radialGradient>
<radialGradient id="fr-arille" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#fff3b0" stop-opacity="0.95"/><stop offset="1" stop-color="#f5b52a" stop-opacity="0.9"/></radialGradient>
</defs>''']
    # Fruit entier
    o.append('<ellipse cx="120" cy="140" rx="82" ry="90" fill="url(#fr-peau)" stroke="#2a0f33" stroke-width="1.5"/>')
    for _ in range(40):
        a = random.uniform(0, 360)
        r = random.uniform(10, 78)
        x, y = 120 + r * math.cos(math.radians(a)), 140 + r * 1.08 * math.sin(math.radians(a))
        o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(random.uniform(1, 2.4))}" fill="#c9a6e0" opacity="0.55"/>')
    o.append('<path d="M70 95 q20 -30 60 -32" stroke="#ffffff" stroke-width="7" stroke-linecap="round" fill="none" opacity="0.18"/>')
    o.append('<path d="M120 52 q-4 -20 10 -34" stroke="#4d7232" stroke-width="5" stroke-linecap="round" fill="none"/>')
    o.append('<path d="M112 56 l8 -8 l8 8 z" fill="#6f9a45"/>')
    # Moitié coupée
    o.append('<ellipse cx="292" cy="150" rx="88" ry="84" fill="#3e1747" stroke="#2a0f33" stroke-width="1.5"/>')
    o.append('<ellipse cx="292" cy="150" rx="80" ry="76" fill="#f7f0d8"/>')
    o.append('<ellipse cx="292" cy="150" rx="72" ry="68" fill="url(#fr-pulpe)"/>')
    pos = []
    while len(pos) < 46:
        a = random.uniform(0, 360)
        r = 62 * math.sqrt(random.uniform(0, 1))
        x, y = 292 + r * math.cos(math.radians(a)), 150 + r * 0.94 * math.sin(math.radians(a))
        if all((x - px) ** 2 + (y - py) ** 2 > 150 for px, py in pos):
            pos.append((x, y))
    for x, y in pos:
        o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="7.5" fill="url(#fr-arille)"/>')
        rot = random.uniform(0, 180)
        o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="3.6" ry="2.4" transform="rotate({f(rot)} {f(x)} {f(y)})" fill="#1f140c"/>')
    o.append('<path d="M232 108 q30 -26 70 -24" stroke="#ffffff" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.35"/>')
    o.append("</svg>")
    return "\n".join(o)


def bandeau():
    """Frise décorative : liane, feuilles, vrilles et deux petites fleurs."""
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 150" role="img" aria-labelledby="t-bandeau">',
         '<title id="t-bandeau">Frise décorative : liane de passiflore avec feuilles, vrilles et fleurs</title>']
    o.append('<g transform="translate(0 15)">')
    o.append('<path d="M0 80 C 150 40, 250 110, 400 70 S 650 30, 800 75 S 1050 120, 1200 80" stroke="#6f9a45" stroke-width="4" fill="none"/>')
    for x, y, a, s in ((90, 62, -110, 0.6), (300, 86, 70, 0.65), (520, 52, -80, 0.6), (700, 62, 100, 0.65), (930, 92, -70, 0.6), (1120, 70, 110, 0.65)):
        o.append(feuille(x, y, a, s))
    for x, y, s, d in ((180, 66, 0.45, 1), (610, 48, 0.4, -1), (1010, 92, 0.45, 1)):
        o.append(vrille(x, y, s, d))
    o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    fichiers = {
        "fleur.svg": fleur(400, True, "Fleur de passiflore vue de face : sépales verts et pétales blancs en étoile, couronne de filaments en bandes violet foncé, blanc et violet, cinq étamines aux anthères jaunes et trois styles", "fleur"),
        "fleur-vignette.svg": fleur(200, False, "Fleur de passiflore simplifiée, vue de face", "vign"),
        "plante.svg": plante(),
        "fruit.svg": fruit(),
        "bandeau.svg": bandeau(),
    }
    for nom, svg in fichiers.items():
        with open(os.path.join(SORTIE, nom), "w", encoding="utf-8") as fh:
            fh.write(svg + "\n")
        print(f"{nom} : {len(svg) // 1024} Kio")


if __name__ == "__main__":
    main()

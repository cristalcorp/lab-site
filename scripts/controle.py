#!/usr/bin/env python3
"""Contrôles du site Lab (D-045), sans dépendance : bibliothèque standard de Python seulement.

Usage : python3 -I scripts/controle.py [dossier]   (défaut : site)
Code de sortie 1 au premier problème trouvé, après avoir tout listé.

Vérifie :
  * HTML : balises équilibrées, lang, charset, viewport, titre, un seul h1, style.css,
    en-tête / menu / main / pied de page, alt sur chaque image ;
  * rien de chargé de l'extérieur (HTML, CSS, SVG), aucun script, formulaire, iframe,
    attribut on*, @import ;
  * liens et images internes qui existent (ancres comprises) ;
  * SVG : XML valide, sans DOCTYPE, script, foreignObject ni lien externe, avec <title> ;
  * contraste (WCAG 2.2, 4,5:1 pour le texte) des paires déclarées dans style.css
    par un commentaire « contraste: texte/fond accent/fond … », en clair et en sombre ;
  * poids : 200 Kio au plus par fichier.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
         "source", "track", "wbr"}
CHARGE = {"img": "src", "script": "src", "link": "href", "iframe": "src", "source": "src",
          "video": "src", "audio": "src", "embed": "src", "object": "data", "track": "src"}
INTERDITS = {"script", "form", "iframe", "object", "embed", "input", "textarea", "select",
             "button", "base"}
POIDS_MAX = 200 * 1024
SVG = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}href"

problemes = []


def pb(fichier, msg):
    problemes.append(f"{fichier} : {msg}")


def externe(url):
    u = urlsplit(url.strip())
    return bool(u.scheme or u.netloc or url.strip().startswith("//"))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile, self.balises, self.ids = [], [], set()
        self.liens, self.images, self.h1, self.titre = [], [], 0, ""
        self.attrs_html, self.dans_titre, self.erreurs = {}, False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.balises.append((tag, a))
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.attrs_html = a
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.dans_titre = True
        if tag not in VIDES:
            self.pile.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VIDES and self.pile and self.pile[-1][0] == tag:
            self.pile.pop()

    def handle_endtag(self, tag):
        if tag == "title":
            self.dans_titre = False
        if tag in VIDES:
            return
        if not self.pile:
            self.erreurs.append(f"ligne {self.getpos()[0]} : </{tag}> sans ouverture")
            return
        ouvert, ligne = self.pile.pop()
        if ouvert != tag:
            self.erreurs.append(f"ligne {self.getpos()[0]} : </{tag}> ferme <{ouvert}> (ligne {ligne})")

    def handle_data(self, data):
        if self.dans_titre:
            self.titre += data


def cible_interne(base_dir, fichier, url, ids_par_page):
    """Vérifie qu'un lien interne mène à un fichier (et à une ancre) qui existe."""
    u = urlsplit(url)
    chemin = unquote(u.path)
    if chemin == "":
        cible = fichier
    else:
        cible = os.path.normpath(os.path.join(os.path.dirname(fichier), chemin))
        if chemin.endswith("/"):
            cible = os.path.join(cible, "index.html")
    if not cible.startswith(base_dir):
        return f"« {url} » sort du site"
    if not os.path.isfile(cible):
        return f"« {url} » : fichier absent"
    if u.fragment and cible.endswith(".html") and u.fragment not in ids_par_page.get(cible, set()):
        return f"« {url} » : ancre absente"
    return None


def controle_html(base_dir, fichier, pages):
    p = pages[fichier]
    for e in p.erreurs:
        pb(fichier, e)
    for tag, ligne in p.pile:
        pb(fichier, f"<{tag}> (ligne {ligne}) jamais fermée")
    if p.attrs_html.get("lang") != "fr":
        pb(fichier, 'lang="fr" absent sur <html>')
    noms = [t for t, _ in p.balises]
    metas = [a for t, a in p.balises if t == "meta"]
    if not any(a.get("charset", "").lower() == "utf-8" for a in metas):
        pb(fichier, "meta charset utf-8 absente")
    if not any(a.get("name") == "viewport" for a in metas):
        pb(fichier, "meta viewport absente")
    if not p.titre.strip():
        pb(fichier, "<title> vide ou absent")
    if p.h1 != 1:
        pb(fichier, f"{p.h1} titre(s) h1 au lieu d'un")
    for requis in ("header", "nav", "main", "footer"):
        if requis not in noms:
            pb(fichier, f"<{requis}> absent")
    feuilles = [a.get("href") for t, a in p.balises if t == "link" and "stylesheet" in a.get("rel", "")]
    if feuilles != ["style.css"]:
        pb(fichier, f"feuille de style attendue : style.css seule (trouvé {feuilles})")
    for tag, a in p.balises:
        if tag in INTERDITS:
            pb(fichier, f"<{tag}> interdit (charte)")
        for nom, val in a.items():
            if nom.startswith("on"):
                pb(fichier, f"attribut {nom} interdit sur <{tag}>")
            if nom == "style" and val and "url(" in val:
                pb(fichier, f"url() dans un style en ligne sur <{tag}>")
        if tag == "img" and "alt" not in a:
            pb(fichier, f"image sans alt : {a.get('src')}")
        if tag in CHARGE and a.get(CHARGE[tag]):
            url = a[CHARGE[tag]]
            if externe(url):
                pb(fichier, f"ressource externe chargée par <{tag}> : {url}")
            else:
                err = cible_interne(base_dir, fichier, url, {k: v.ids for k, v in pages.items()})
                if err:
                    pb(fichier, err)
        if tag in ("img", "source") and a.get("srcset"):
            pb(fichier, "srcset non contrôlé : à retirer ou à ajouter au contrôle")
        if tag == "a" and a.get("href") is not None:
            href = a["href"]
            if href.startswith("mailto:") or href.startswith("tel:"):
                pb(fichier, f"lien {href.split(':')[0]} interdit (donnée personnelle)")
            elif not externe(href):
                err = cible_interne(base_dir, fichier, href, {k: v.ids for k, v in pages.items()})
                if err:
                    pb(fichier, err)
    if not any(t == "a" and a.get("href") == "comment.html" for t, a in p.balises):
        pb(fichier, "lien vers comment.html absent")


def controle_css(base_dir, fichier):
    css = open(fichier, encoding="utf-8").read()
    sans_commentaires = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    if "@import" in sans_commentaires:
        pb(fichier, "@import interdit")
    if "@font-face" in sans_commentaires:
        pb(fichier, "@font-face interdit (police système seulement)")
    for url in re.findall(r"url\(\s*['\"]?([^'\")]+)", sans_commentaires):
        if externe(url):
            pb(fichier, f"url() externe : {url}")
        elif not url.startswith("#") and not os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(fichier), url))):
            pb(fichier, f"url() vers un fichier absent : {url}")
    return css


def controle_svg(fichier):
    brut = open(fichier, encoding="utf-8").read()
    if "<!DOCTYPE" in brut or "<!ENTITY" in brut:
        pb(fichier, "DOCTYPE ou ENTITY interdit")
        return
    try:
        racine = ET.fromstring(brut)
    except ET.ParseError as e:
        pb(fichier, f"XML invalide : {e}")
        return
    if racine.tag != SVG + "svg":
        pb(fichier, "la racine n'est pas <svg> (espace de noms SVG)")
    if racine.find(SVG + "title") is None:
        pb(fichier, "<title> absent (accessibilité)")
    for el in racine.iter():
        nom = el.tag.replace(SVG, "")
        if nom in ("script", "foreignObject", "iframe", "image"):
            pb(fichier, f"<{nom}> interdit dans un SVG")
        for att, val in el.attrib.items():
            if att.lower().startswith("on"):
                pb(fichier, f"attribut {att} interdit")
            if att in ("href", XLINK) and not val.startswith("#"):
                pb(fichier, f"lien non local dans le SVG : {val}")
            if "url(" in val and not re.fullmatch(r"\s*url\(#[\w-]+\)\s*", val):
                pb(fichier, f"url() non locale : {val}")


def lum(hexa):
    h = hexa.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def variables(bloc):
    return dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\b", bloc))


def controle_contraste(fichier, css):
    m = re.search(r"contraste:\s*([^*]+)\*/", css)
    if not m:
        pb(fichier, "commentaire « contraste: … » absent : paires de couleurs non déclarées")
        return []
    paires = [p.split("/") for p in m.group(1).split()]
    motif_sombre = r"@media[^{]*prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}\s*\}"
    sombre = re.findall(motif_sombre, css)
    clair = re.findall(r":root\s*\{([^}]*)\}", re.sub(motif_sombre, "", css))
    themes = {"clair": {k: v for bloc in clair for k, v in variables(bloc).items()}}
    if sombre:
        themes["sombre"] = {**themes["clair"], **{k: v for bloc in sombre for k, v in variables(bloc).items()}}
    else:
        pb(fichier, "mode sombre absent")
    lignes = []
    for theme, v in themes.items():
        for avant, fond in paires:
            if avant not in v or fond not in v:
                pb(fichier, f"{theme} : couleur --{avant} ou --{fond} absente")
                continue
            r = ratio(v[avant], v[fond])
            lignes.append(f"  {theme:6} {avant:>14} / {fond:<12} {r:5.2f}:1")
            if r < 4.5:
                pb(fichier, f"{theme} : contraste {avant}/{fond} = {r:.2f}:1 < 4,5:1")
    return lignes


def main():
    base_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "site")
    fichiers = sorted(os.path.join(d, f) for d, _, fs in os.walk(base_dir) for f in fs)
    pages = {}
    for f in fichiers:
        if os.path.getsize(f) > POIDS_MAX:
            pb(f, f"{os.path.getsize(f) // 1024} Kio > 200 Kio")
        if f.endswith(".html"):
            p = Page()
            p.feed(open(f, encoding="utf-8").read())
            p.close()
            pages[f] = p
    for f in pages:
        controle_html(base_dir, f, pages)
    contraste = []
    for f in fichiers:
        if f.endswith(".css"):
            css = controle_css(base_dir, f)
            if os.path.basename(f) == "style.css":
                contraste = controle_contraste(f, css)
        elif f.endswith(".svg"):
            controle_svg(f)
        elif not f.endswith((".html", ".css", ".svg", ".ico", ".txt", ".json")):
            pb(f, "type de fichier non prévu (charte : pages, style, illustrations)")
    print(f"{len(pages)} page(s), {sum(f.endswith('.svg') for f in fichiers)} SVG, {len(fichiers)} fichier(s).")
    if contraste:
        print("Contraste :")
        print("\n".join(contraste))
    racine = os.path.dirname(base_dir) + os.sep
    if problemes:
        print(f"\n{len(problemes)} problème(s) :")
        print("\n".join("  - " + p.replace(racine, "") for p in problemes))
        sys.exit(1)
    print("Aucun problème.")


if __name__ == "__main__":
    main()

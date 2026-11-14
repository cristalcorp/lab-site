# lab-site

Site statique du lab, publié sur Azure Static Web Apps à chaque fusion sur `main`. Lieu d'expérimentation : le contenu change régulièrement.

## Contrôles

`python3 -I scripts/controle.py site` vérifie, sans dépendance : HTML bien formé et complet, aucune ressource externe ni script ni formulaire, liens et images internes existants, SVG valides et sans script, contraste du texte (4,5:1, en clair et en sombre, paires déclarées en tête de `site/style.css`), poids des fichiers. Le workflow `controles` le lance sur chaque PR ; le ruleset de `main` l'exige.

## Illustrations

`python3 -I scripts/illustrations.py` régénère les SVG de `site/img/` (dessinés par code, dégradés locaux seulement).

## Charte

Pages statiques en français ; illustrations faites pour le site ; aucune donnée personnelle, offre commerciale, ressource externe, formulaire ni fichier à télécharger.

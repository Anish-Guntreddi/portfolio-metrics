# Engineering Portfolio — Anish Guntreddi

A single-page showcase of ten engineering projects: five full-stack applications and five
systems-programming projects in C/C++. 700 automated tests.

**Live:** https://anish-guntreddi.github.io/portfolio-metrics/

## What it is

A hand-built static site (no framework, no build step) — "Editorial Dossier" design:
Fraunces (display serif) · Hanken Grotesk (body) · JetBrains Mono (data). The five apps show
live-UI screenshots; the five systems projects are rendered as benchmark/terminal treatments,
with MicroMatch (the order-matching engine) as a full-bleed flagship.

## Run locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

…or just open `index.html` in a browser.

## Deploy

GitHub Pages, served from `main` / root. Edit `index.html` and push — Pages redeploys automatically.

## Edit

All content + styling live in the single `index.html`. Project data is in the markup;
screenshots are in `img/`.

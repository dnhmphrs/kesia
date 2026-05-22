# kes inkersole — personal site

A small static site, built with **Rollup** and deployable to **Vercel**.
No JavaScript runs on the page — it's plain HTML + CSS. The build just bundles
the stylesheet, injects it into the page, and copies static files.

## Project structure

```
kes-site/
├── package.json          # dependencies + scripts (yarn)
├── rollup.config.mjs     # build config
├── vercel.json           # Vercel deploy config
├── src/
│   ├── index.html        # the page — edit text and links here
│   ├── main.js           # tiny build entry (just imports the CSS; no page logic)
│   └── styles/
│       └── main.css      # all styling
└── public/               # static files copied as-is (favicon.ico, share image…)
```

## Prerequisites

- [Node.js](https://nodejs.org/) 18 or newer
- [Yarn](https://yarnpkg.com/) — if you don't have it: `npm install -g yarn`

## Local development

```bash
yarn install      # first time only
yarn dev          # dev server with live reload at http://localhost:5173
```

## Build for production

```bash
yarn build        # outputs the finished site to dist/
yarn preview      # optional: serve dist/ locally to check the build
```

## Editing the site

All the text and links live directly in `src/index.html` — edit it like a
normal web page. To add a project/writing/podcast link, copy an existing
`<li><a href="...">label</a></li>` line inside the right list and change the
URL and label. Styling lives in `src/styles/main.css`.

## Favicon

Put `favicon.ico` in the `public/` folder. It's already linked in the page head
(`<link rel="icon" href="/favicon.ico" />`) and gets copied to the site root on
build. If it doesn't show after deploying, visit `your-site.com/favicon.ico`
directly: if the icon loads there it's just browser caching (hard-refresh); if
you get a 404 the file isn't in `public/`.

## Share / link-preview card

When the link is pasted into iMessage, Slack, LinkedIn or X, the preview comes
from the `og:` and `twitter:` tags in the `<head>` of `src/index.html`. To make
the preview image work:

1. Put an image (e.g. `share.png`, ideally ~1200×630 or square ~1200×1200) in
   `public/`.
2. In `index.html`, set the `og:image`, `twitter:image`, `og:url` values to the
   full live URL, e.g. `https://kesinkersole.com/share.png`. Relative paths do
   not work for share cards — they must be absolute https URLs.

## Deploying to Vercel

### Option A — GitHub (recommended)
1. Push this folder to a GitHub repo.
2. vercel.com → Add New… → Project → import the repo.
3. `vercel.json` sets it up automatically (build `yarn build`, output `dist`).
4. Deploy. Every `git push` redeploys.

### Option B — Vercel CLI
```bash
npm install -g vercel
vercel            # preview deploy
vercel --prod     # production
```

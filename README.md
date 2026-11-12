# kes inkersole — the site

One html page, one stylesheet, and the words in a few json files. A small script puts
them together. Nothing to install.

## What is where

```
index.html     the page. edit this to change the html
style.css      the look. empty on purpose: start here
content/       the words. edit these to change what the site says
  site.json      name, the lines under it, email
  about.json     hello paragraphs, the about list, irl
  projects.json  projects (title, pictures, link) and the for-fun links
  writing.json   things written, podcasts
img/           the pictures
build.js       the script that fills index.html with the content (leave it alone)
dist/          the finished site, made by the script. never edit by hand
_archive/      every draft made for the site before this one. open _archive/index.html
```

## Seeing the site

```
node build.js
```

then open `dist/index.html` in a browser. Run the command again after every change.
If `node` is not on your machine, install it from https://nodejs.org (18 or newer).

## Changing things

- **Words** live in `content/`. Change a value, keep the quotes and commas as they are.
- **Pictures**: put the file in `img/l/` and point a project's `src` at it, like
  `img/l/my-picture.jpg`. `width` and `height` are the picture's real pixel size.
- **A new project**: in `content/projects.json`, copy one block inside `"projects": [ … ]`
  and change it.
- **Html** is `index.html`. It is a normal page with holes in it: `{{site.name}}` is
  filled from the content, `{{#projects}} … {{/projects}}` repeats once per project,
  `{{.}}` is the item itself when a list is just words, and `{{#text}} … {{/text}}`
  only shows when `text` is not empty.
- **Style** is `style.css`. It starts with nothing, so the page looks the way the
  browser draws plain html. Add rules and rebuild.

## Going live

The site is on Vercel, which watches the `main` branch of this repository. Push to
`main`; Vercel runs `node build.js` and publishes `dist/`.

## Learning

- https://developer.mozilla.org/en-US/docs/Learn/HTML — html, from the start
- https://developer.mozilla.org/en-US/docs/Learn/CSS — css, from the start
- https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON — what json is
- https://html.energy/ — a love letter to writing html by hand

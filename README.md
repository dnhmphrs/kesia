# kes inkersole — the site

Plain html, plain css, and the words in a few json files. One small script puts them
together. Nothing to install.

## What is where

```
content/            ← the words. edit these to change what the site says
  site.json           your name, the three lines under it, your email
  about.json          the hello paragraphs, the about list, irl
  projects.json       the projects (title, pictures, link) and the for-fun links
  writing.json        things you've written, podcasts
templates/          ← the pages. edit these to change the html
  index.html          home
  portfolio.html      projects
  writing.html        writing + podcasts
  about.html          about + contact
style.css           ← the look. empty on purpose: start here
public/             ← files copied as they are: pictures (img/), favicon, share image
build.js            ← the script that fills the templates with the content (you can leave it alone)
dist/               ← the finished site (made by the script, never edit by hand)
```

## How the templates work

A template is a normal html page with a few holes in it:

- `{{site.name}}` is filled with a value from the content files
  (`site.json` → `site.…`, `about.json` → `about.…`; the lists in `projects.json`
  and `writing.json` are reached directly: `projects`, `fun`, `written`, `podcasts`).
- `{{#projects}} … {{/projects}}` repeats what is inside once per project;
  inside it, `{{title}}` is that project's title.
- `{{.}}` is the item itself when the list is just words (the roles, the hello paragraphs).
- `{{#text}} … {{/text}}` shows what is inside only when `text` is not empty.

Want a new page? Copy one of the templates, give it a new name, and add it to the
`<nav>` in the other templates.

## Adding a project

In `content/projects.json`, copy one of the blocks inside `"projects": [ … ]` and change
it. Put the pictures in `public/img/l/` and point `src` at them (`img/l/your-picture.jpg`).
`width` and `height` are the picture's real pixel size.

## Seeing it

```
node build.js
```

Then open `dist/index.html` in a browser. Run the command again after every change.
(If `node` is not on your machine, install it from https://nodejs.org — version 18 or newer.)

## Going live

The site is on Vercel, which watches the `main` branch of this repository. Push to
`main` and Vercel runs `node build.js` and publishes `dist/`. That is all.

## The archive

Every draft made along the way, 157 pages in 26 rounds, is kept at `/archive/`
(the files live in `public/drafts/` and `public/archive/`). It is not linked from
the site and is marked noindex. The previous homepage is at `/drafts/home/`, and the
original code for it is in the git history before this version.

# kes inkersole — the site

One html page, one stylesheet, and the words in a few json files. A small script puts
them together. Nothing to install except node.

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

## First time: getting it onto your computer

1. Install **GitHub Desktop** (desktop.github.com) and sign in. On this repository's
   GitHub page press the green **Code** button → **Open with GitHub Desktop**. Pick a
   folder. That folder is now a copy of the site you can edit.
2. Install **node** from nodejs.org (the LTS one). It is the thing that runs `build.js`.
3. Get a text editor that saves plain text. **VS Code** (code.visualstudio.com) is free
   and fine. TextEdit on a Mac is not: it saves rich text and breaks the files.

## Seeing the site

1. Open the **Terminal** app (Mac: it's in Applications → Utilities).
2. Type `cd ` with a space, drag the site folder from Finder into the window, press enter.
   The terminal is now "inside" the folder.
3. Type `node build.js` and press enter. It says `built dist/`.
4. In Finder, open the `dist` folder and double-click `index.html`. That is the site.

Then the loop is: change something → save → run `node build.js` again → refresh the
browser. (Press the up arrow in the terminal to get the last command back.)

## Changing things

- **Words** live in `content/`. Change what is between the quotes, keep the quotes and
  commas as they are. If the build stops with an error, a comma or quote is missing.
- **Pictures**: put the file in `img/l/` and point a project's `src` at it, like
  `img/l/my-picture.jpg`. `width` and `height` are the picture's real pixel size.
- **A new project**: in `content/projects.json`, copy one block inside `"projects": [ … ]`,
  paste it after the last one with a comma between, and change it.
- **Html** is `index.html`. It is a normal page with holes in it: `{{site.name}}` is
  filled from the content, `{{#projects}} … {{/projects}}` repeats once per project,
  `{{.}}` is the item itself when a list is just words, and `{{#text}} … {{/text}}`
  only shows when `text` is not empty. Everything else is html you can move around.
- **Style** is `style.css`. It starts with nothing, so the page looks the way the browser
  draws plain html. Add rules, rebuild, refresh.

## Going live

In GitHub Desktop: write a line about what you changed, press **Commit to main**, then
**Push origin**. Vercel notices, runs `node build.js`, and the site is live about a minute
later at kesia-coral.vercel.app. `dist/` is not pushed; Vercel builds its own.

## Good company

- https://html.energy — html energy. a love letter to writing html by hand
- https://htmlforpeople.com — html for people. a free, friendly book: build a site in a plain text editor
- https://neocities.org — neocities. the old web, still going: tiny handmade sites by thousands of people
- https://thecreativeindependent.com/people/laurel-schwulst-my-website-is-a-shifting-house-next-to-a-river-of-knowledge-what-could-yours-be/ — laurel schwulst on what a personal website can be
- https://flukeout.github.io — css diner. a little game that teaches css selectors
- https://flexboxfroggy.com and https://cssgridgarden.com — frogs and carrots that teach layout

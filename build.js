// build.js — turns templates/*.html + content/*.json into the finished site in dist/.
// run it with:  node build.js      (no packages to install; node 18 or newer)
//
// templates can use:
//   {{site.name}}                 → a value from the content files (html-escaped)
//   {{#projects}} … {{/projects}} → repeat the inside once per item in a list
//   {{.}}                         → the current item itself, when the list holds plain strings
//   {{#text}} … {{/text}}         → show the inside only if the value is not empty
const fs = require('fs');
const path = require('path');

// 1. read every content/*.json file into one object: content/site.json → data.site, and so on.
//    projects.json and writing.json hold several lists, so their keys are merged in directly.
const data = {};
for (const file of fs.readdirSync('content')) {
  const json = JSON.parse(fs.readFileSync(path.join('content', file), 'utf8'));
  const name = path.basename(file, '.json');
  if (name === 'projects' || name === 'writing') Object.assign(data, json);
  else data[name] = json;
}

// 2. the little template language.
const escape = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function lookup(key, stack) {
  if (key === '.') return stack[stack.length - 1];
  for (let i = stack.length - 1; i >= 0; i--) {
    let value = stack[i];
    for (const part of key.split('.')) value = value != null && typeof value === 'object' ? value[part] : undefined;
    if (value !== undefined) return value;
  }
  return undefined;
}

function render(template, stack) {
  // a line holding only a {{#…}} or {{/…}} tag leaves no blank line behind
  template = template.replace(/^[ \t]*(\{\{[#/][\w.]+\}\})[ \t]*\n/gm, '$1');
  // sections first: {{#key}} … {{/key}}
  template = template.replace(/\{\{#([\w.]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (_, key, inner) => {
    const value = lookup(key, stack);
    if (Array.isArray(value)) return value.map((item) => render(inner, [...stack, item])).join('');
    if (!value) return '';
    return render(inner, typeof value === 'object' ? [...stack, value] : stack);
  });
  // then plain values: {{key}}
  return template.replace(/\{\{([\w.]+)\}\}/g, (_, key) => {
    const value = lookup(key, stack);
    return value == null ? '' : escape(value);
  });
}

// 3. write dist/: one page per template, the stylesheet, and everything in public/ copied as-is.
fs.rmSync('dist', { recursive: true, force: true });
fs.mkdirSync('dist');
for (const file of fs.readdirSync('templates')) {
  const html = render(fs.readFileSync(path.join('templates', file), 'utf8'), [data]);
  fs.writeFileSync(path.join('dist', file), html);
  console.log('wrote dist/' + file);
}
fs.copyFileSync('style.css', 'dist/style.css');
fs.cpSync('public', 'dist', { recursive: true });
console.log('copied style.css and public/ → dist/');

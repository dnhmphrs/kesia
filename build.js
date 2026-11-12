// build.js — fills index.html with the words from content/*.json and puts the finished site in dist/.
// run it with:   node build.js        (nothing to install; node 18 or newer)
//
// in index.html you can write:
//   {{site.name}}                  a value from the content files, html-escaped
//   {{#projects}} … {{/projects}}  repeat the inside once per item in a list
//   {{.}}                          the item itself, when the list is just words
//   {{#text}} … {{/text}}          show the inside only if the value is not empty
const fs = require('fs');

// 1. the content: content/site.json → site.…, content/about.json → about.…;
//    the lists in projects.json and writing.json are reached directly (projects, fun, written, podcasts)
const data = {};
for (const file of fs.readdirSync('content')) {
  const json = JSON.parse(fs.readFileSync('content/' + file, 'utf8'));
  const name = file.replace('.json', '');
  if (name === 'projects' || name === 'writing') Object.assign(data, json);
  else data[name] = json;
}

// 2. the template language
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
  // sections: {{#key}} … {{/key}}
  template = template.replace(/\{\{#([\w.]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (_, key, inner) => {
    const value = lookup(key, stack);
    if (Array.isArray(value)) return value.map((item) => render(inner, [...stack, item])).join('');
    if (!value) return '';
    return render(inner, typeof value === 'object' ? [...stack, value] : stack);
  });
  // values: {{key}}
  return template.replace(/\{\{([\w.]+)\}\}/g, (_, key) => {
    const value = lookup(key, stack);
    return value == null ? '' : escape(value);
  });
}

// 3. write dist/
fs.rmSync('dist', { recursive: true, force: true });
fs.mkdirSync('dist');
fs.writeFileSync('dist/index.html', render(fs.readFileSync('index.html', 'utf8'), [data]));
for (const f of ['style.css', 'favicon.ico', 'square.png']) fs.copyFileSync(f, 'dist/' + f);
fs.cpSync('img', 'dist/img', { recursive: true });
console.log('built dist/ — open dist/index.html in a browser');

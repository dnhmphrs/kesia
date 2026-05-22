import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

import resolvePlugin from '@rollup/plugin-node-resolve';
import postcss from 'rollup-plugin-postcss';
import html from '@rollup/plugin-html';
import serve from 'rollup-plugin-serve';
import livereload from 'rollup-plugin-livereload';
import copy from 'rollup-plugin-copy';

const __dirname = dirname(fileURLToPath(import.meta.url));
const dev = process.env.ROLLUP_WATCH === 'true';

/* We hand-wrote src/index.html, so we use it as a template and let the html
   plugin inject the built <link> tag into <head>. There is no client JS, so
   no <script> tag is injected. */
const template = readFileSync(resolve(__dirname, 'src/index.html'), 'utf8');

export default {
  input: 'src/main.js',
  output: {
    dir: 'dist',
    format: 'es',
    // the JS entry is empty-ish; we only care about the extracted CSS asset
    entryFileNames: 'assets/[name].[hash].js',
    assetFileNames: 'assets/[name].[hash][extname]',
    sourcemap: dev,
  },
  plugins: [
    resolvePlugin(),
    postcss({
      extract: 'assets/styles.css', // pull CSS out into its own file
      minimize: !dev,
      sourceMap: dev,
    }),
    html({
      fileName: 'index.html',
      template: ({ files }) => {
        const links = (files.css || [])
          .map((f) => `<link rel="stylesheet" href="/${f.fileName}" />`)
          .join('\n  ');
        // inject the built stylesheet link before </head>; no script needed
        return template.replace('</head>', `  ${links}\n</head>`);
      },
    }),
    // copy anything in /public (favicon, share image, etc.) straight to dist
    copy({
      targets: [{ src: 'public/*', dest: 'dist' }],
      copyOnce: false,
    }),
    dev && serve({ contentBase: 'dist', port: 5173, historyApiFallback: true }),
    dev && livereload('dist'),
  ].filter(Boolean),
};

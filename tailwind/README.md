# Tailwind

This directory contains files for [tailwindcss](https://tailwindcss.com/). 
This project using [tailwind standalone CLI](https://tailwindcss.com/blog/standalone-cli)

## Download tailwind standalone CLI
https://github.com/tailwindlabs/tailwindcss/releases/tag/v3.3.3

## Editing css

For editing css run the following command in the root directory of the project:
```
tailwindcss -i .\tailwind\tailwind.css -o .\static\style.css -c .\tailwind\tailwind.config.js --watch
```

Than you can edit the style using these files:
- [`tailwind\tailwind.css`](./tailwind.css)
- [`tailwind\tailwind.config.js`](./tailwind.config.js)
- [`template\layout.html`](../templates/layout.html)

After changig these files the above command automaticaly updates [`static/style.css`](../static/style.css).

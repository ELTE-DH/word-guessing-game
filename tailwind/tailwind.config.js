/** @type {import('tailwindcss').Config} */
module.exports = {
  important: false,
  content: [
    'templates/layout.html'
  ],
  theme: {
    extend: {
      colors: {
        dhbronze1: '#998675',
        dhbronze2: '#75675a',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
  safelist: [
    'dh-btn-bronze1',
    'dh-btn-disabled',
  ]
}
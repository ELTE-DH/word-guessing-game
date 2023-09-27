/** @type {import('tailwindcss').Config} */
module.exports = {
  important: false,
  content: [
    'templates/layout.html'
  ],
  theme: {
    extend: {
      colors: {
        dhgreen: '#175F37',
        dhgreen2: '#134E2D',
        dhbronze1: '#998675',
        dhbronze2: '#75675a',
      },
      animation: {
        slide: "slide 2.5s linear infinite",
      },
      keyframes: {
        slide: {
          "0%": { transform: "translateY(100%)", opacity: 0.1 },
          "15%": { transform: "translateY(0)", opacity: 1 },
          "30%": { transform: "translateY(0)", opacity: 1 },
          "45%": { transform: "translateY(-100%)", opacity: 1 },
          "100%": { transform: "translateY(-100%)", opacity: 0.1 },
        },
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
  safelist: [
    'bg-red-500',
    'bg-green-500',
    'bg-blue-500',
    'dh-btn-green1',
    'dh-btn-disabled',
    'translate-y-20',
    'opacity-0',
  ]
}
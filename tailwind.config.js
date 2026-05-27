/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/**/*.py',
    './engagement/**/*.py',
    './portfolio/**/*.py',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        'brand-bg': '#ECEDF0',
        'brand-surface': '#FFFFFF',
        'brand-alloy': '#E2E4E9',
        'brand-teal': '#007A8A',
        'brand-cyan': '#00BCD4',
        'brand-text': '#1A1A2E',
        'brand-sub': '#4A5568',
      },
    },
  },
  plugins: [],
};

module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/src/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        brand: {
          900: '#18230F',
          800: '#27391C',
          700: '#255F38',
          600: '#1F7D53',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

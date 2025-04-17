module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/blueprints/**/templates/**/*.html',
    './app/static/src/**/*.js',
    './app/static/src/**/*.html',
  ],
  safelist: [
    'bg-green-600',
    'bg-yellow-500',
    'bg-purple-600',
    'bg-gray-500',
    'hover:bg-green-700',
    'hover:bg-yellow-600',
    'hover:bg-purple-700',
    'hover:bg-gray-600',
    'focus:ring-green-500',
    'focus:ring-yellow-400',
    'focus:ring-purple-500',
    'focus:ring-gray-400',
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

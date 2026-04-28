
/** @type {import('tailwindcss').Config} */
export default {
  content: [
  './index.html',
  './src/**/*.{js,ts,jsx,tsx}'
],
  theme: {
    extend: {
      colors: {
        coral: {
          50: '#fff0eb',
          100: '#ffe0d6',
          200: '#ffc2ad',
          300: '#ffa385',
          400: '#ff845c',
          500: '#ff6b35', // Primary
          600: '#e55a2b',
          700: '#cc4b22',
          800: '#b23d18',
          900: '#993010',
        },
        navy: {
          50: '#f2f4f8',
          100: '#e6e9f0',
          200: '#c0c8d9',
          300: '#9aa7c2',
          400: '#7486ab',
          500: '#4e6594',
          600: '#3a4e7a',
          700: '#28385c',
          800: '#1b2a4a', // Secondary
          900: '#121c32',
        },
        gold: {
          400: '#fbbf24',
          500: '#f59e0b', // Accent
          600: '#d97706',
        },
        background: '#FAFAFA',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      boxShadow: {
        'warm': '0 10px 40px -10px rgba(255, 107, 53, 0.1)',
        'soft': '0 4px 20px -2px rgba(27, 42, 74, 0.05)',
      }
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cycle: {
          darkest: '#070D1F',
          dark: '#0B132B',
          card: '#141E3C',
          border: '#1F2E58',
          hover: '#19284F',
          primary: '#2563EB',
          accent: '#3A86FF',
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          text: '#F8FAFC',
          muted: '#94A3B8',
        }
      }
    },
  },
  plugins: [],
}


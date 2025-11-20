/** @type {import('tailwindcss').Config} */
export default {
  // CAMBIO CLAVE: Habilita el modo oscuro basado en una clase en el <html>
  darkMode: 'class',

  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}', // Escanea todos tus archivos de Vue
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

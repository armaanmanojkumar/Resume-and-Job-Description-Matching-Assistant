/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#f97316",
        secondary: "#64748b",
        lightOrange: "#F1DDBF",
        darkGray: "#1a1f25",
        lightGray: "#272c35",
      },
      container:{
        center: true,
        padding : {
          DEFAULT: "1rem",
          sm: "2rem",
        },
      },
    },
  },
  plugins: [],
};


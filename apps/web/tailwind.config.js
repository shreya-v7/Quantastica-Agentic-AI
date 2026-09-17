/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    borderRadius: {
      none: "0",
      sm: "0",
      DEFAULT: "0",
      md: "0",
      lg: "0",
      xl: "0",
      "2xl": "0",
      full: "9999px",
    },
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["IBM Plex Sans Condensed", "IBM Plex Sans", "sans-serif"],
        serif: ["IBM Plex Sans Condensed", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "Menlo", "monospace"],
      },
      colors: {
        paper: {
          50: "rgb(var(--paper-50) / <alpha-value>)",
          100: "rgb(var(--paper-100) / <alpha-value>)",
          200: "rgb(var(--paper-200) / <alpha-value>)",
          300: "rgb(var(--paper-300) / <alpha-value>)",
        },
        ink: {
          50: "rgb(var(--ink-50) / <alpha-value>)",
          100: "rgb(var(--ink-100) / <alpha-value>)",
          200: "rgb(var(--ink-200) / <alpha-value>)",
          400: "rgb(var(--ink-400) / <alpha-value>)",
          500: "rgb(var(--ink-500) / <alpha-value>)",
          600: "rgb(var(--ink-600) / <alpha-value>)",
          700: "rgb(var(--ink-700) / <alpha-value>)",
          800: "rgb(var(--ink-800) / <alpha-value>)",
          900: "rgb(var(--ink-900) / <alpha-value>)",
        },
        pine: {
          50: "rgb(var(--pine-50) / <alpha-value>)",
          100: "rgb(var(--pine-100) / <alpha-value>)",
          500: "rgb(var(--pine-500) / <alpha-value>)",
          600: "rgb(var(--pine-600) / <alpha-value>)",
          700: "rgb(var(--pine-700) / <alpha-value>)",
        },
        copper: {
          400: "rgb(var(--volt) / <alpha-value>)",
          500: "rgb(var(--volt) / <alpha-value>)",
          700: "rgb(var(--volt) / <alpha-value>)",
        },
        brand: {
          50: "rgb(var(--pine-50) / <alpha-value>)",
          100: "rgb(var(--pine-100) / <alpha-value>)",
          500: "rgb(var(--pine-500) / <alpha-value>)",
          600: "rgb(var(--pine-600) / <alpha-value>)",
          700: "rgb(var(--pine-700) / <alpha-value>)",
        },
      },
      boxShadow: {
        desk: "inset 0 0 0 1px var(--line)",
        glow: "0 0 28px var(--glow)",
        "glow-sm": "0 0 16px var(--glow-sm)",
      },
      letterSpacing: {
        label: "0.18em",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        blink: {
          "0%, 49%": { opacity: "1" },
          "50%, 100%": { opacity: "0" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "1", boxShadow: "0 0 0 0 var(--glow)" },
          "50%": { opacity: "0.45", boxShadow: "0 0 0 7px transparent" },
        },
      },
      animation: {
        scan: "scan 7s linear infinite",
        blink: "blink 1.1s step-end infinite",
        pulseDot: "pulseDot 2.2s ease-out infinite",
      },
    },
  },
  plugins: [],
};

import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#050505",
        panel: "#101010",
        border: "#202020",
        cyan: {
          DEFAULT: "#00D8FF",
          bright: "#00FFFF",
        },
        green: "#2EEA7D",
        muted: "#BBBBBB",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      backgroundImage: {
        "grid-glow":
          "radial-gradient(circle at 50% 0%, rgba(0,216,255,0.08), transparent 60%)",
      },
      keyframes: {
        pulseOnce: {
          "0%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.06)" },
          "100%": { transform: "scale(1)" },
        },
        flow: {
          "0%": { strokeDashoffset: "24" },
          "100%": { strokeDashoffset: "0" },
        },
      },
      animation: {
        pulseOnce: "pulseOnce 0.4s ease-out",
        flow: "flow 1.2s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;

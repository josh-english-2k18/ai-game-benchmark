import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "board-dark": "#0f172a",
        "board-light": "#1e293b",
        "accent-cpu": "#60a5fa",
        "accent-gpu": "#f97316",
        "accent-tpu": "#34d399"
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"]
      },
      boxShadow: {
        glow: "0 0 40px rgba(99, 102, 241, 0.4)"
      }
    }
  },
  plugins: []
} satisfies Config;

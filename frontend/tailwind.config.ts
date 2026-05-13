import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#E23744",
          hover: "#C52F3B",
          muted: "#FDE8EA",
          foreground: "#FFFFFF",
        },
        surface: {
          DEFAULT: "#FAFAFA",
          card: "#FFFFFF",
        },
        ink: {
          DEFAULT: "#1C1C1C",
          secondary: "#696969",
        },
      },
      borderRadius: {
        card: "16px",
        pill: "9999px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.05), 0 8px 24px rgba(0,0,0,0.06)",
        preferences: "0 1px 3px rgba(0,0,0,0.05), 0 10px 40px rgba(0,0,0,0.06)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Aqua Regia brand colors
        aqua: {
          50: '#e0fffe',
          100: '#b3fffc',
          200: '#80fff9',
          300: '#4dfff6',
          400: '#1afff3',
          500: '#00CED1',
          600: '#00a8aa',
          700: '#008B8B',
          800: '#006666',
          900: '#004444',
        },
        gold: {
          400: '#FFD700',
          500: '#DAA520',
          600: '#B8860B',
        },
        void: {
          900: '#0a0a0f',
          800: '#12121a',
          700: '#1a1a25',
        },
        // Scout-specific
        scout: {
          primary: '#6366f1',  // Indigo
          secondary: '#8b5cf6', // Purple
        },
      },
    },
  },
  plugins: [],
};

export default config;

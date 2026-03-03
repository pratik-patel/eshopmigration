import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // eShop custom colors (extracted from legacy CSS)
        'eshop-primary': '#0066cc',
        'eshop-secondary': '#6c757d',
        'eshop-danger': '#dc3545',
      },
    },
  },
  plugins: [],
} satisfies Config

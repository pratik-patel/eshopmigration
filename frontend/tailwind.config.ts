import type { Config } from 'tailwindcss'

/**
 * Tailwind CSS configuration for eShop Catalog Management
 * Generated from design-tokens.json
 *
 * Design System Features:
 * - Color palette: Primary green, secondary red, accent teal, neutral grays
 * - Typography: Montserrat font family with responsive sizes
 * - Spacing: Consistent padding/margin system
 * - Components: Buttons, tables, images, loaders, pagers, links
 */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          green: '#83D01B',
          'green-hover': '#4A760f',
          'green-link-hover': '#75b918',
          DEFAULT: '#83D01B',
        },
        secondary: {
          red: '#E52638',
          'red-hover': '#b20000',
          DEFAULT: '#E52638',
        },
        accent: {
          teal: '#00A69C',
          DEFAULT: '#00A69C',
        },
        neutral: {
          white: '#FFFFFF',
          black: '#000000',
          'gray-light': '#EEEEEE',
          'gray-medium': '#888888',
          'gray-dark': '#333333',
          'gray-table-border': '#eee',
          'gray-loader': '#f3f3f3',
        },
      },
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
        primary: ['Montserrat', 'sans-serif'],
      },
      fontSize: {
        'h1': '4vw',
        'h1-large': '4rem',
        'h2': '3rem',
        'link': '2rem',
        'pager-small': '0.85rem',
      },
      fontWeight: {
        light: '300',
        normal: '400',
        semibold: '600',
      },
      spacing: {
        'section': '2.5rem',
        'body-title-h': '3rem',
        'body-title-v-top': '1rem',
        'body-title-v-bottom': '1.5rem',
        'button': '1rem',
        'button-h': '1.5rem',
        'table-top': '10px',
        'form-info-top': '7px',
        'pager-h': '5vw',
        'pager-h-small': '2.5vw',
      },
      maxWidth: {
        'container': '1440px',
        'thumbnail': '120px',
        'picture': '370px',
      },
      borderRadius: {
        'loader': '50%',
      },
      transitionDuration: {
        '350': '350ms',
      },
      keyframes: {
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'spin-loader': 'spin 2s linear infinite',
      },
    },
    screens: {
      'sm': '1024px',
      'md': '1280px',
      'lg': '1800px',
    },
  },
  plugins: [],
} satisfies Config

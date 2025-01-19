/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  important: true,
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1677ff',
          dark: '#0958d9',
          light: '#4096ff',
        },
        secondary: {
          DEFAULT: '#d9d9d9',
          dark: '#8c8c8c',
          light: '#f0f0f0',
        },
        success: {
          DEFAULT: '#52c41a',
          dark: '#389e0d',
          light: '#73d13d',
        },
        warning: {
          DEFAULT: '#faad14',
          dark: '#d48806',
          light: '#ffc53d',
        },
        error: {
          DEFAULT: '#ff4d4f',
          dark: '#f5222d',
          light: '#ff7875',
        },
      },
      spacing: {
        '128': '32rem',
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  },
}

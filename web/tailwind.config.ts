import type { Config } from 'tailwindcss';
import stellarPreset from '@stellar-ui-kit/shared/tailwind-preset';

const config: Config = {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './node_modules/@stellar-ui-kit/web/dist/**/*.{js,mjs}',
  ],
  presets: [stellarPreset],
  theme: {
    borderRadius: {
      none: '0',
      sm: '0.5rem',
      DEFAULT: '0.5rem',
      md: '0.5rem',
      lg: '0.5rem',
      xl: '0.5rem',
      '2xl': '0.5rem',
      '3xl': '1rem',
      full: '0.5rem',
    },
    extend: {
      colors: {
        'border-strong': 'var(--color-border-strong)',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
};

export default config;

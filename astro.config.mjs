import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://cyanalyst.github.io',
  base: '/cyanalyst/',
  vite: {
    plugins: [tailwindcss()],
  },
  build: {
    format: 'directory',
  },
});

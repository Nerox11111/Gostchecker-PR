/* eslint-env node */
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import legacy from '@vitejs/plugin-legacy';

function handleModuleDirectivesPlugin() {
  return {
    name: 'handle-module-directives-plugin',
    transform(code, id) {
      if (id.includes('@vkontakte/icons')) {
        code = code.replace(/"use-client";?/g, '');
      }
      return { code };
    },
  };
}

/**
 * Some chunks may be large.
 * This will not affect the loading speed of the site.
 * We collect several versions of scripts that are applied depending on the browser version.
 * This is done so that your code runs equally well on the site and in the odr.
 * The details are here: https://dev.vk.ru/mini-apps/development/on-demand-resources.
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  if (mode === 'production' && !env.VITE_API_BASE_URL && !process.env.VITE_API_BASE_URL) {
    throw new Error('VITE_API_BASE_URL is required for production build');
  }

  return {
    base: './',

    plugins: [
      react(),
      handleModuleDirectivesPlugin(),
      legacy({
        targets: ['defaults', 'not IE 11'],
      }),
    ],

    build: {
      outDir: 'build',
    },
  };
});

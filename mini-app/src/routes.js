import {
  createHashRouter,
  createPanel,
  createRoot,
  createView,
  RoutesConfig,
} from '@vkontakte/vk-mini-apps-router';

export const DEFAULT_ROOT = 'default_root';
export const DEFAULT_VIEW = 'default_view';

export const DEFAULT_VIEW_PANELS = {
  HOME: 'home',
  RESULT: 'result',
  ML: 'ml',
  GOST: 'gost',
  AUTOFIX: 'autofix',
};

export const routes = RoutesConfig.create([
  createRoot(DEFAULT_ROOT, [
    createView(DEFAULT_VIEW, [
      createPanel(DEFAULT_VIEW_PANELS.HOME, '/', []),
      createPanel(DEFAULT_VIEW_PANELS.RESULT, '/result', []),
      createPanel(DEFAULT_VIEW_PANELS.ML, '/ml-model', []),
      createPanel(DEFAULT_VIEW_PANELS.GOST, '/gost-732', []),
      createPanel(DEFAULT_VIEW_PANELS.AUTOFIX, '/autofix', []),
    ]),
  ]),
]);

export const router = createHashRouter(routes.getRoutes());

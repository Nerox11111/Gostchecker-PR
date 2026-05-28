import bridge from '@vkontakte/vk-bridge';

const DEFAULT_DEV_API = 'http://127.0.0.1:8000';

export const getApiBaseUrl = () => {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_DEV_API;
  return configuredUrl.replace(/\/+$/, '');
};

export const getLaunchParamsFromLocation = () => window.location.search || '';

export const getLaunchParams = async () => {
  const fromLocation = getLaunchParamsFromLocation();
  if (fromLocation) return fromLocation;

  try {
    const params = await bridge.send('VKWebAppGetLaunchParams');
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null) query.set(key, String(value));
    });
    const queryString = query.toString();
    return queryString ? `?${queryString}` : '';
  } catch {
    return '';
  }
};

const getVkSignHeader = (launchParams) => (launchParams ? { 'X-VK-Sign': launchParams } : {});

const readError = async (response) => {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === 'string') return payload.detail;
    if (Array.isArray(payload?.detail)) {
      return payload.detail.map((item) => item.msg || JSON.stringify(item)).join(', ');
    }
    return payload?.error || payload?.error?.message || JSON.stringify(payload);
  } catch {
    return response.statusText;
  }
};

const normalizeNetworkError = (error, path) => {
  const message = error?.message || '';
  if (/load failed|failed to fetch|networkerror|network request failed/i.test(message)) {
    throw new Error(
      `Не удалось получить ответ от API (${path}). Проверь backend: uvicorn server:app --host 127.0.0.1 --port 8000, CORS и reverse proxy.`,
    );
  }
  throw error;
};

const requestJson = async (path, { launchParams, headers, ...options } = {}) => {
  let response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...options,
      headers: {
        ...getVkSignHeader(launchParams),
        ...headers,
      },
    });
  } catch (error) {
    normalizeNetworkError(error, path);
  }

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
};

const appendRunParams = (path, { mode, scopeId, profile, customChecks }) => {
  const query = new URLSearchParams({
    mode,
    scope_id: scopeId,
  });
  if (profile) query.set('profile', profile);
  if (profile === 'CUSTOM' && customChecks?.length) {
    query.set('custom_checks', customChecks.join(','));
  }
  return `${path}?${query.toString()}`;
};

export const fetchHealth = () => requestJson('/api/health');

export const fetchModules = () => requestJson('/api/modules');

export const classifyDocument = (file, launchParams) => {
  const form = new FormData();
  form.append('file', file);

  return requestJson('/api/classify', {
    method: 'POST',
    body: form,
    launchParams,
  });
};

export const runDocumentValidation = (file, { profile, customChecks = [] } = {}, launchParams) => {
  const form = new FormData();
  form.append('file', file);

  return requestJson(appendRunParams('/api/run', {
    mode: 'validate',
    scopeId: 'validate_all_key',
    profile,
    customChecks,
  }), {
    method: 'POST',
    body: form,
    launchParams,
  });
};

export const runDocumentCorrection = (file, { profile, customChecks = [] } = {}, launchParams) => {
  const form = new FormData();
  form.append('file', file);

  return requestJson(appendRunParams('/api/run', {
    mode: 'correct',
    scopeId: 'correct_all',
    profile,
    customChecks,
  }), {
    method: 'POST',
    body: form,
    launchParams,
  });
};

export const filePayloadToBlob = (fixedFile) => {
  const binary = atob(fixedFile.base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: fixedFile.content_type });
};

export const saveFixedFile = (fixedFile) => {
  const blob = filePayloadToBlob(fixedFile);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fixedFile.filename || 'fixed-document.docx';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

export const fetchCurrentVkUser = async () => bridge.send('VKWebAppGetUserInfo');

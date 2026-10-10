// Клиент для бэкенда MeDoc. Все запросы идут на /api/... (serve.py пересылает их на FastAPI).
const BASE = '/api';

export class ApiError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

// ---------- сессия ----------
const KEY = 'medoc_session';
export const session = {
  data: (() => { try { return JSON.parse(sessionStorage.getItem(KEY)); } catch { return null; } })(),
  save(d) { this.data = d; try { sessionStorage.setItem(KEY, JSON.stringify(d)); } catch {} },
  clear() { this.data = null; try { sessionStorage.removeItem(KEY); } catch {} cache.clear(); },
  get token() { return this.data?.token; },
  get role() { return this.data?.role; },
  get uid() { return this.data?.uid; },
  get login() { return this.data?.login; },
  get isAdmin() { return this.data?.role === 'admin'; },
};

function parseJwt(t) {
  const p = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
  return JSON.parse(decodeURIComponent(escape(atob(p))));
}

function formatDetail(d) {
  if (!d) return 'Что-то пошло не так';
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) {
    return d.map(e => {
      const f = Array.isArray(e.loc) ? e.loc.filter(x => x !== 'body').join('.') : '';
      return f ? `${f}: ${e.msg}` : e.msg;
    }).join('; ');
  }
  return JSON.stringify(d);
}

let refreshing = null;
async function refreshToken() {
  refreshing ??= (async () => {
    const r = await fetch(BASE + '/refresh', { method: 'POST', credentials: 'same-origin' });
    if (!r.ok) throw new ApiError(401, 'Сессия истекла. Войдите заново');
    const j = await r.json();
    const c = parseJwt(j.access_token);
    session.save({ ...session.data, token: j.access_token, role: c.role, uid: Number(c.sub) });
  })().finally(() => { refreshing = null; });
  return refreshing;
}

export let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) { onUnauthorized = fn; }

export async function req(method, path, body, retry = true) {
  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (session.token) headers.Authorization = 'Bearer ' + session.token;
  let r;
  try {
    r = await fetch(BASE + path, { method, headers, credentials: 'same-origin', body: body !== undefined ? JSON.stringify(body) : undefined });
  } catch {
    throw new ApiError(0, 'Нет связи с сервером. Проверьте, что запущен serve.py и бэкенд');
  }
  if (r.status === 401 && retry && path !== '/login' && session.token) {
    try { await refreshToken(); return req(method, path, body, false); }
    catch { session.clear(); onUnauthorized(); throw new ApiError(401, 'Сессия истекла. Войдите заново'); }
  }
  if (r.status === 204) return null;
  const text = await r.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!r.ok) {
    let msg = formatDetail(data?.detail ?? data);
    if (r.status === 500) msg = 'Ошибка на сервере. Подробности — в логе бэкенда';
    if (r.status === 502 && data?.detail) msg = data.detail;
    if (r.status === 403) msg = 'Недостаточно прав для этого действия';
    throw new ApiError(r.status, msg);
  }
  return data;
}

export async function login(loginName, password) {
  const j = await req('POST', '/login', { login: loginName, password });
  const c = parseJwt(j.access_token);
  session.save({ token: j.access_token, role: c.role, uid: Number(c.sub), login: loginName });
}

export function logout() { session.clear(); }

// ---------- списки ----------
// В списках бэкенда нет поля id, поэтому, если его нет, достаём записи по одной через GET /<res>/<id>.
const cache = new Map();
export function invalidate(res) { cache.delete(res); }

export function listAll(res, { force = false } = {}) {
  if (!force && cache.has(res)) return cache.get(res);
  const p = loadAll(res).catch(e => { cache.delete(res); throw e; });
  cache.set(res, p);
  return p;
}

async function loadAll(res) {
  const items = [];
  let total = 0;
  for (let page = 1; page < 50; page++) {
    const r = await req('GET', `/${res}/?page=${page}&page_size=100&ordering=id`);
    total = r.total_count;
    items.push(...r.founds);
    if (items.length >= total || !r.founds.length) break;
  }
  if (items.every(i => i.id != null)) return items;
  // запасной путь: перебор id
  const found = [];
  const limit = total * 4 + 40;
  for (let id = 1; id <= limit && found.length < total; id += 8) {
    const ids = Array.from({ length: 8 }, (_, k) => id + k);
    const got = await Promise.all(ids.map(i => req('GET', `/${res}/${i}`).catch(e => { if (e.status === 404) return null; throw e; })));
    found.push(...got.filter(Boolean));
  }
  return found.sort((a, b) => a.id - b.id);
}

export async function create(res, body) { const r = await req('POST', `/${res}/`, body); invalidate(res); return r; }
export async function patch(res, id, body) { const r = await req('PATCH', `/${res}/${id}`, body); invalidate(res); return r; }
export async function remove(res, id) { await req('DELETE', `/${res}/${id}`); invalidate(res); }

// ---------- приёмы и статистика ----------
export const inspections = {
  createAdmin: b => req('POST', '/inspection/admin/', b),
  createDoctor: b => req('POST', '/inspection/doctor/', b),
  patchAdmin: (id, b) => req('PATCH', `/inspection/admin/${id}`, b),
  patchDoctor: (id, b) => req('PATCH', `/inspection/doctor/${id}`, b),
  // Если в бэкенде появится GET /inspection/ — фронтенд подхватит его сам.
  async tryList() {
    try { const r = await req('GET', '/inspection/?page=1&page_size=100&ordering=-id'); return r.founds ?? r; }
    catch (e) { if ([404, 405].includes(e.status)) return null; throw e; }
  },
  perDate: b => req('PUT', '/inspection/statistics/inspection_per_date/', b),
  patientsByDisease: id => req('GET', `/inspection/statistics/disease_per_patient/${id}`),
};

import { h, icon, icons, toast, roleLabel } from './ui.js';
import * as api from './api.js';
import { dashboard } from './pages/dashboard.js';
import { patients, medicines, diseases, employees } from './pages/lists.js';
import { inspectionsPage } from './pages/inspections.js';

const app = document.getElementById('app');

const ROUTES = [
  { path: 'dashboard', label: 'Сводка', icon: 'dash', page: dashboard },
  { path: 'inspections', label: 'Приёмы', icon: 'visit', page: inspectionsPage },
  { path: 'patients', label: 'Пациенты', icon: 'patient', page: patients },
  { path: 'medicines', label: 'Лекарства', icon: 'pill', page: medicines },
  { path: 'diseases', label: 'Болезни', icon: 'disease', page: diseases },
  { path: 'employees', label: 'Сотрудники', icon: 'staff', page: employees, admin: true },
];

api.setUnauthorizedHandler(() => { toast('Сессия истекла. Войдите заново', 'err'); go(); });

// ---------- вход ----------
const ECG = 'M0 120 H150 l18 -4 l14 4 H260 l14 -10 l12 10 H340 l12 14 l24 -112 l30 176 l20 -78 H520 l14 -14 l16 14 H640 l12 -26 l14 26 H760 H1200';

function loginView() {
  const err = h('div', { class: 'form-error', role: 'alert' });
  const user = h('input', { id: 'l_user', autocomplete: 'username', required: true, placeholder: 'например, admintest' });
  const pass = h('input', { id: 'l_pass', type: 'password', autocomplete: 'current-password', required: true, placeholder: '••••••••' });
  const btn = h('button', { class: 'btn primary lg', type: 'submit' }, 'Войти');
  const form = h('form', { class: 'login-form', onsubmit: async e => {
    e.preventDefault(); err.textContent = ''; btn.disabled = true; btn.classList.add('busy');
    try { await api.login(user.value.trim(), pass.value); location.hash = '#/dashboard'; go(); }
    catch (ex) { err.textContent = ex.status === 401 || ex.status === 404 ? 'Неверный логин или пароль' : ex.message; }
    finally { btn.disabled = false; btn.classList.remove('busy'); }
  } },
    h('h1', {}, 'Вход в MeDoc'),
    h('p', { class: 'sub' }, 'Для врачей и администраторов кооператива'),
    h('div', { class: 'field' }, h('label', { for: 'l_user' }, 'Логин'), user),
    h('div', { class: 'field' }, h('label', { for: 'l_pass' }, 'Пароль'), pass),
    err, btn);
  return h('main', { class: 'login' },
    h('section', { class: 'login-art', 'aria-hidden': 'true' },
      h('div', { class: 'brand light' }, h('span', { class: 'brand-mark', html: icons.logo }), h('span', {}, 'MeDoc')),
      h('div', { class: 'art-copy' }, h('h2', {}, 'Медицинский кооператив'), h('p', {}, 'Пациенты, приёмы и лекарства в одном месте')),
      h('div', { class: 'ecg', html: `<svg viewBox="0 0 1200 240" preserveAspectRatio="none"><defs><filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><path class="ecg-base" d="${ECG}"/><path class="ecg-live" d="${ECG}" filter="url(#glow)" pathLength="1"/></svg>` })),
    h('section', { class: 'login-panel' }, form));
}

// ---------- каркас ----------
function shellView(route) {
  const routes = ROUTES.filter(r => !r.admin || api.session.isAdmin);
  const nav = h('nav', { 'aria-label': 'Разделы' }, routes.map(r =>
    h('a', { href: '#/' + r.path, class: r.path === route.path ? 'active' : '', 'aria-current': r.path === route.path ? 'page' : null }, icon(r.icon), r.label)));
  const side = h('aside', { class: 'side', id: 'side' },
    h('div', { class: 'brand light' }, h('span', { class: 'brand-mark', html: icons.logo }), h('span', {}, 'MeDoc')),
    nav,
    h('div', { class: 'who' },
      h('div', { class: 'avatar' }, (api.session.login || '?')[0].toUpperCase()),
      h('div', {}, h('strong', {}, api.session.login), h('small', {}, roleLabel(api.session.role))),
      h('button', { class: 'icon-btn light', title: 'Выйти', 'aria-label': 'Выйти', onclick: () => { api.logout(); location.hash = ''; go(); } }, icon('out'))));
  const scrim = h('div', { class: 'scrim', onclick: () => document.body.classList.remove('nav-open') });
  const top = h('div', { class: 'topbar' },
    h('button', { class: 'icon-btn', 'aria-label': 'Меню', onclick: () => document.body.classList.toggle('nav-open') }, icon('menu')),
    h('div', { class: 'brand' }, h('span', { class: 'brand-mark', html: icons.logo }), h('span', {}, 'MeDoc')));
  const main = h('main', { class: 'content', id: 'main', tabindex: '-1' });
  app.replaceChildren(h('div', { class: 'shell' }, side, scrim, h('div', { class: 'col' }, top, main)));
  return main;
}

let renderToken = 0;
async function go() {
  document.body.classList.remove('nav-open');
  document.querySelectorAll('.overlay').forEach(o => o.remove());
  if (!api.session.token) { app.replaceChildren(loginView()); document.title = 'Вход — MeDoc'; return; }
  const name = (location.hash.replace(/^#\//, '') || 'dashboard').split('?')[0];
  let route = ROUTES.find(r => r.path === name);
  if (!route || (route.admin && !api.session.isAdmin)) route = ROUTES[0];
  const token = ++renderToken;
  const main = shellView(route);
  document.title = `${route.label} — MeDoc`;
  try { await route.page(main); }
  catch (e) { if (token === renderToken) toast(e.message, 'err'); }
  main.focus({ preventScroll: true });
}

window.addEventListener('hashchange', go);
go();

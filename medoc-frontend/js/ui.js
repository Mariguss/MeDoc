// Маленькие помощники для интерфейса: создание элементов, тосты, окна, иконки, формы.
export function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'html') el.innerHTML = v;
    else if (k === 'value') el.value = v;
    else if (v === true) el.setAttribute(k, '');
    else el.setAttribute(k, v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(kid));
  }
  return el;
}

export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export const icons = {
  logo: '<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#0b2a66"/><path d="M3 17h7l3-8 5 15 3-7h8" fill="none" stroke="#19e3ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  dash: '<svg viewBox="0 0 24 24"><path d="M4 13h4l2-6 4 12 2-6h4"/></svg>',
  patient: '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-3.6 3.4-5.5 7-5.5s6.2 1.9 7 5.5"/></svg>',
  pill: '<svg viewBox="0 0 24 24"><rect x="3.5" y="8.5" width="17" height="7" rx="3.5" transform="rotate(-35 12 12)"/><path d="M9.5 8.7l5 6.6"/></svg>',
  disease: '<svg viewBox="0 0 24 24"><path d="M12 3c3 3.2 5.5 5.8 5.5 9a5.5 5.5 0 11-11 0c0-3.200 2.500-5.800 5.500-9z"/></svg>',
  staff: '<svg viewBox="0 0 24 24"><circle cx="9" cy="8.5" r="3"/><path d="M3.5 19c.6-3 2.700-4.500 5.500-4.500s4.900 1.500 5.500 4.500"/><path d="M17 6.500v5M14.500 9h5"/></svg>',
  visit: '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="3"/><path d="M8 3v4M16 3v4M4 10h16M12 13v4M10 15h4"/></svg>',
  plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  edit: '<svg viewBox="0 0 24 24"><path d="M4 20h4L19 9l-4-4L4 16v4z"/></svg>',
  trash: '<svg viewBox="0 0 24 24"><path d="M5 7h14M10 7V4h4v3M7 7l1 13h8l1-13"/></svg>',
  search: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4-4"/></svg>',
  out: '<svg viewBox="0 0 24 24"><path d="M14 4h5v16h-5M10 8l-4 4 4 4M6 12h9"/></svg>',
  close: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  menu: '<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
};
export const icon = (name, cls = '') => h('span', { class: 'ico ' + cls, html: icons[name] });

// ---------- форматирование ----------
export const fmtDate = d => { if (!d) return '—'; const [y, m, day] = String(d).slice(0, 10).split('-'); return `${day}.${m}.${y}`; };
export const fmtDateTime = d => { if (!d) return '—'; const s = String(d); return `${fmtDate(s)} ${s.slice(11, 16)}`.trim(); };
export const sexLabel = v => (/^m/i.test(String(v)) ? 'Мужской' : v ? 'Женский' : '—');
export const roleLabel = r => (String(r).toLowerCase() === 'admin' ? 'Администратор' : 'Врач');
export const statusLabel = { scheduled: 'Запланирован', completed: 'Завершён', cancelled: 'Отменён', no_show: 'Неявка' };
export const fmtPhone = p => { const s = String(p ?? ''); return s.length === 11 ? `+7 (${s.slice(1, 4)}) ${s.slice(4, 7)}-${s.slice(7, 9)}-${s.slice(9)}` : (s || '—'); };
export const toIso = local => (local ? (local.length === 16 ? local + ':00' : local) : null);
export const toLocalInput = iso => (iso ? String(iso).slice(0, 16) : '');
export const todayStr = () => new Date().toLocaleDateString('sv');

// ---------- уведомления ----------
export function toast(text, kind = 'ok') {
  const t = h('div', { class: 'toast ' + kind, role: 'status' }, text);
  document.getElementById('toasts').append(t);
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 300); }, kind === 'err' ? 6000 : 3200);
}

// ---------- модальные окна ----------
export function modal(title, body, { wide = false } = {}) {
  const prevFocus = document.activeElement;
  const close = () => { ov.classList.add('out'); setTimeout(() => ov.remove(), 180); document.removeEventListener('keydown', onKey); prevFocus?.focus?.(); };
  const onKey = e => { if (e.key === 'Escape') close(); };
  const box = h('div', { class: 'modal' + (wide ? ' wide' : ''), role: 'dialog', 'aria-modal': 'true', 'aria-label': title },
    h('header', {}, h('h2', {}, title), h('button', { class: 'icon-btn', 'aria-label': 'Закрыть', onclick: close }, icon('close'))),
    body);
  const ov = h('div', { class: 'overlay', onmousedown: e => { if (e.target === ov) close(); } }, box);
  document.body.append(ov);
  document.addEventListener('keydown', onKey);
  setTimeout(() => (box.querySelector('input,select,textarea,button.primary') || box).focus(), 30);
  return { close, box };
}

export function confirmBox(title, text, okLabel = 'Удалить') {
  return new Promise(res => {
    let done = false;
    const finish = v => { if (!done) { done = true; res(v); m.close(); } };
    const body = h('div', { class: 'modal-body' }, h('p', {}, text),
      h('div', { class: 'actions' },
        h('button', { class: 'btn ghost', onclick: () => finish(false) }, 'Отмена'),
        h('button', { class: 'btn danger', onclick: () => finish(true) }, okLabel)));
    const m = modal(title, body);
    m.box.parentElement.addEventListener('mousedown', e => { if (e.target === m.box.parentElement) finish(false); });
  });
}

// ---------- форма ----------
// fields: [{name,label,type,required,options:[{value,label}],hint,full,pattern,min,max,custom}]
export function buildForm(fields, values = {}) {
  const inputs = {};
  const rows = fields.map(f => {
    let control;
    const v = values[f.name] ?? '';
    const common = { id: 'f_' + f.name, name: f.name, required: f.required, placeholder: f.placeholder, pattern: f.pattern, maxlength: f.maxlength, minlength: f.minlength, title: f.title };
    if (f.type === 'select') {
      control = h('select', common, h('option', { value: '' }, f.required ? 'Выберите…' : '— не выбрано —'),
        f.options.map(o => h('option', { value: o.value, selected: String(o.value) === String(v) }, o.label)));
    } else if (f.type === 'textarea') {
      control = h('textarea', { ...common, rows: 3 }, v);
    } else if (f.type === 'chips') {
      const sel = new Set((values[f.name] || []).map(String));
      control = h('div', { class: 'chips' }, f.options.length ? f.options.map(o => {
        const cb = h('input', { type: 'checkbox', value: o.value, checked: sel.has(String(o.value)) });
        return h('label', { class: 'chip' }, cb, h('span', {}, o.label));
      }) : h('span', { class: 'hint' }, f.emptyText || 'Список пуст'));
    } else if (f.custom) {
      control = f.custom(values);
    } else {
      control = h('input', { ...common, type: f.type || 'text', value: v, min: f.min, max: f.max, autocomplete: f.type === 'password' ? 'new-password' : 'off' });
    }
    inputs[f.name] = control;
    return h('div', { class: 'field' + (f.full ? ' full' : '') },
      h('label', { for: 'f_' + f.name }, f.label, f.required ? h('b', { class: 'req', title: 'Обязательное поле' }, ' *') : null),
      control.el || control,
      f.hint ? h('small', { class: 'hint' }, f.hint) : null);
  });
  const read = () => {
    const out = {};
    for (const f of fields) {
      const c = inputs[f.name];
      if (f.custom) out[f.name] = c.get();
      else if (f.type === 'chips') out[f.name] = [...c.querySelectorAll('input:checked')].map(i => Number(i.value));
      else out[f.name] = c.value.trim();
    }
    return out;
  };
  return { el: h('div', { class: 'grid' }, rows), read };
}

export function formModal({ title, fields, values, submitLabel = 'Сохранить', onSubmit, wide }) {
  const form = buildForm(fields, values);
  const err = h('div', { class: 'form-error', role: 'alert' });
  const btn = h('button', { class: 'btn primary', type: 'submit' }, submitLabel);
  const formEl = h('form', { class: 'modal-body', novalidate: false }, form.el, err,
    h('div', { class: 'actions' }, h('button', { class: 'btn ghost', type: 'button', onclick: () => m.close() }, 'Отмена'), btn));
  const m = modal(title, formEl, { wide });
  formEl.addEventListener('submit', async e => {
    e.preventDefault();
    err.textContent = '';
    btn.disabled = true; btn.classList.add('busy');
    try { await onSubmit(form.read()); m.close(); }
    catch (ex) { err.textContent = ex.message || String(ex); }
    finally { btn.disabled = false; btn.classList.remove('busy'); }
  });
  return m;
}

// ---------- мелочи ----------
export const empty = (title, text, action) => h('div', { class: 'empty' },
  h('span', { class: 'empty-line', html: '<svg viewBox="0 0 120 24"><path d="M2 12h30l6-9 9 18 7-12 6 3h58" /></svg>' }),
  h('strong', {}, title), text ? h('p', {}, text) : null, action || null);

export const skeleton = (n = 5) => h('div', { class: 'skeleton' }, Array.from({ length: n }, () => h('i')));

export function countUp(el, to, ms = 900) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || to < 2) { el.textContent = to; return; }
  const t0 = performance.now();
  const step = t => { const k = Math.min(1, (t - t0) / ms); el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}

import { h, icon, countUp, skeleton, empty, fmtDate, toast, todayStr, statusLabel } from '../ui.js';
import * as api from '../api.js';

const plural = (n, [a, b, c]) => { const m = n % 100, d = n % 10; return m > 10 && m < 15 ? c : d === 1 ? a : d > 1 && d < 5 ? b : c; };

function bars(rows, { max, fmt = x => x } = {}) {
  const top = max ?? Math.max(1, ...rows.map(r => r.value));
  return h('ul', { class: 'bars' }, rows.map((r, i) => h('li', { style: `--i:${i}` },
    h('span', { class: 'bar-label' }, r.label),
    h('span', { class: 'bar-track' }, h('span', { class: 'bar-fill', style: `--w:${Math.max(r.value ? 4 : 0, r.value / top * 100)}%` })),
    h('b', { class: 'bar-val' }, fmt(r.value)))));
}

export async function dashboard(root) {
  const isAdmin = api.session.isAdmin;
  const hello = h('div', { class: 'page-head' },
    h('div', {}, h('h1', {}, 'Сводка'), h('p', { class: 'sub' }, isAdmin ? 'Отчёты по вызовам, болезням и лекарствам' : 'Отчёты и справочники для вашей работы')));
  const tiles = h('div', { class: 'tiles' });
  root.append(hello, tiles);

  // --- плитки ---
  const tileDefs = [
    ['patient', 'Пациентов', 'patient', '#/patients'],
    ['pill', 'Лекарств', 'medicine', '#/medicines'],
    ['disease', 'Болезней', 'disease', '#/diseases'],
    ...(isAdmin ? [['staff', 'Сотрудников', 'employee', '#/employees']] : []),
  ];
  tileDefs.forEach(([ic, label, res, href], i) => {
    const num = h('span', { class: 'big' }, '·');
    tiles.append(h('a', { class: 'tile', href, style: `--i:${i}` }, icon(ic), num, h('span', { class: 'tile-label' }, label)));
    api.req('GET', `/${res}/?page=1&page_size=1`).then(r => countUp(num, r.total_count)).catch(() => { num.textContent = '—'; });
  });

  const grid = h('div', { class: 'reports' });
  root.append(grid);

  // --- 1. Вызовы по дате ---
  {
    const from = h('input', { type: 'date', id: 'r_from' });
    const to = h('input', { type: 'date', id: 'r_to' });
    const st = h('select', { id: 'r_st' }, [['completed', 'Завершённые'], ['', 'Все статусы'], ...Object.entries(statusLabel).filter(([k]) => k !== 'completed')].map(([v, l]) => h('option', { value: v }, l)));
    const out = h('div', { class: 'report-out' });
    const run = async () => {
      out.replaceChildren(skeleton(3));
      try {
        const body = { status: st.value || null };
        // бэкенд сравнивает даты строками, поэтому начало сдвигаем на секунду назад, чтобы первый день вошёл в отчёт
        if (from.value) { const d = new Date(from.value + 'T00:00:00'); d.setSeconds(-1); body.start_date = d.toLocaleDateString('sv') + 'T' + d.toLocaleTimeString('sv'); }
        if (to.value) body.end_date = to.value + 'T00:00:00';
        const rows = await api.inspections.perDate(body);
        const total = rows.reduce((s, r) => s + r.count, 0);
        if (!rows.length) { out.replaceChildren(empty('Вызовов не найдено', 'Попробуйте другой период или статус.')); return; }
        const num = h('span', { class: 'big' }, '0');
        out.replaceChildren(
          h('div', { class: 'result-line' }, num, h('span', {}, ` ${plural(total, ['вызов', 'вызова', 'вызовов'])} ${from.value && from.value === to.value ? 'за ' + fmtDate(from.value) : 'за выбранный период'}`)),
          bars(rows.slice(0, 14).map(r => ({ label: r.date ? fmtDate(r.date) : 'Без даты', value: r.count }))));
        countUp(num, total);
      } catch (e) { out.replaceChildren(empty('Отчёт не построен', e.message)); }
    };
    grid.append(h('section', { class: 'card report wide-card' },
      h('h2', {}, 'Количество вызовов по дате'),
      h('p', { class: 'sub' }, 'Для одного дня укажите одну и ту же дату в обоих полях.'),
      h('div', { class: 'filters' },
        h('div', { class: 'field' }, h('label', { for: 'r_from' }, 'С даты'), from),
        h('div', { class: 'field' }, h('label', { for: 'r_to' }, 'По дату'), to),
        h('div', { class: 'field' }, h('label', { for: 'r_st' }, 'Статус приёма'), st),
        h('button', { class: 'btn primary', onclick: run }, 'Показать')),
      out));
    run();
  }

  // --- 2. Больные по болезням ---
  {
    const out = h('div', { class: 'report-out' }, skeleton(4));
    grid.append(h('section', { class: 'card report' },
      h('h2', {}, 'Больные по болезням'),
      h('p', { class: 'sub' }, 'Сколько разных пациентов болело каждой болезнью'), out));
    (async () => {
      try {
        const ds = await api.listAll('disease', { force: true });
        if (!ds.length) { out.replaceChildren(empty('Болезней нет', 'Добавьте болезни в справочник.')); return; }
        const counts = await Promise.all(ds.map(d => api.inspections.patientsByDisease(d.id).catch(() => 0)));
        const rows = ds.map((d, i) => ({ label: d.name, value: counts[i] })).sort((a, b) => b.value - a.value);
        out.replaceChildren(bars(rows, { fmt: v => `${v} ${plural(v, ['чел.', 'чел.', 'чел.'])}` }));
      } catch (e) { out.replaceChildren(empty('Отчёт не построен', e.message)); }
    })();
  }

  // --- 3. Побочные эффекты ---
  {
    const sel = h('select', { id: 'r_med', 'aria-label': 'Лекарство' }, h('option', { value: '' }, 'Выберите лекарство…'));
    const out = h('div', { class: 'report-out' });
    let meds = [];
    api.listAll('medicine', { force: true }).then(m => {
      meds = m; m.forEach(x => sel.append(h('option', { value: x.id }, x.name)));
      if (!m.length) out.replaceChildren(empty('Справочник пуст', 'Лекарств пока нет.'));
    }).catch(e => out.replaceChildren(empty('Не удалось загрузить лекарства', e.message)));
    sel.addEventListener('change', () => {
      const m = meds.find(x => String(x.id) === sel.value);
      out.replaceChildren(m ? h('div', { class: 'med' },
        h('h3', {}, m.name),
        h('div', { class: 'kv' }, h('b', {}, 'Действие'), h('p', {}, m.properties)),
        h('div', { class: 'kv warn' }, h('b', {}, 'Побочные эффекты'), h('p', {}, m.side_effects))) : '');
    });
    grid.append(h('section', { class: 'card report' },
      h('h2', {}, 'Побочные эффекты лекарства'),
      h('p', { class: 'sub' }, 'Выберите препарат — покажем его действие и побочные эффекты'),
      h('div', { class: 'field' }, sel), out,
      isAdmin ? h('a', { class: 'btn ghost sm', href: '#/medicines' }, icon('plus'), 'Добавить новое лекарство') : null));
  }
}
